"""Headless EEVEE render of one V3 job JSON.

Run:
  blender --background --python lab/v3/procedural/blender_render.py -- job.json

Builds each semantic component as its own mesh. Does not voxel-remesh,
does not union parts, does not use a wave/ripple displacement.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
import traceback
from pathlib import Path


def _job_path():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = argv[1:]
    if not argv:
        raise SystemExit("missing job json path")
    return Path(argv[0])


def stable_hash(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def srgb_to_linear(rgb):
    def f(u):
        u = float(u)
        if u <= 0.04045:
            return u / 12.92
        return ((u + 0.055) / 1.055) ** 2.4

    return tuple(f(c) for c in rgb)


def dedupe_ring(pts, tol=1e-5):
    out = []
    for p in pts:
        x, y = float(p[0]), float(p[1])
        if not out or math.hypot(x - out[-1][0], y - out[-1][1]) > tol:
            out.append((x, y))
    if len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out = out[:-1]
    return out


def point_segment_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_to_edges(x, y, ring):
    n = len(ring)
    dmin = 1e9
    for i in range(n):
        ax, ay = ring[i]
        bx, by = ring[(i + 1) % n]
        dmin = min(dmin, point_segment_dist(x, y, ax, ay, bx, by))
    return dmin


def point_in_poly(x, y, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def set_input(node, name, value):
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def make_material(name, color_srgb, params, *, rough=None, trans=None, coat=None, sheen=None, emit=0.0):
    import bpy

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    lin = srgb_to_linear(color_srgb)
    set_input(bsdf, "Base Color", (*lin, 1.0))
    set_input(bsdf, "Metallic", float(params["metallic"]))
    set_input(bsdf, "Roughness", float(params["roughness"] if rough is None else rough))
    set_input(bsdf, "IOR", float(params["ior"]))
    set_input(bsdf, "Transmission Weight", float(params["transmission"] if trans is None else trans))
    set_input(bsdf, "Subsurface Weight", float(params["subsurface"] if trans is None else 0.0))
    set_input(bsdf, "Subsurface Radius", tuple(params["sss_radius"]))
    set_input(bsdf, "Subsurface Scale", float(params["sss_scale"] if trans is None else 0.0))
    set_input(bsdf, "Specular IOR Level", float(params["specular"]))
    set_input(bsdf, "Coat Weight", float(params["coat"] if coat is None else coat))
    set_input(bsdf, "Coat Roughness", float(params["coat_roughness"]))
    set_input(bsdf, "Sheen Weight", float(params["sheen"] if sheen is None else sheen))
    set_input(bsdf, "Sheen Roughness", float(params["sheen_roughness"]))
    tint = srgb_to_linear([min(1.0, c * 1.1) for c in color_srgb])
    set_input(bsdf, "Sheen Tint", (*tint, 1.0))
    if emit:
        set_input(bsdf, "Emission Color", (*lin, 1.0))
        set_input(bsdf, "Emission Strength", float(emit))
    mat.diffuse_color = (*lin, 1.0)
    return mat


def link_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def clear_scene(bpy):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(block):
            try:
                block.remove(b)
            except Exception:
                pass


def realize(bpy, obj):
    name = obj.name
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(ev, depsgraph=depsgraph)
    new_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(new_obj)
    bpy.data.objects.remove(obj, do_unlink=True)
    return new_obj


def shade_and_sharp(obj, angle_deg=52):
    import bmesh

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    limit = math.radians(angle_deg)
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > limit:
            e.smooth = False
        else:
            e.smooth = True
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def dome_inflate(obj, ring, amount):
    """Pillow along Z using distance-to-boundary. Silhouette (d=0) stays put.
    The field is radial in the component, not a function of Y, so it does not
    paint horizontal bands.
    """
    if amount <= 1e-6 or len(ring) < 3:
        return
    import bmesh

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if not bm.verts:
        bm.free()
        return
    zs = sorted(v.co.z for v in bm.verts)
    zmid = zs[len(zs) // 2]
    ds = [dist_to_edges(v.co.x, v.co.y, ring) for v in bm.verts]
    dmax = max(ds) or 1e-4
    for v, d in zip(bm.verts, ds):
        t = max(0.0, min(1.0, d / dmax))
        dome = t * t * (3.0 - 2.0 * t)
        if v.co.z >= zmid - 1e-6:
            v.co.z += amount * dome
        else:
            v.co.z -= amount * 0.7 * dome
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def _noise(ix, iy, iz):
    n = (int(ix) * 374761393 + int(iy) * 668265263 + int(iz) * 1274126177) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n & 0x7FFFFFFF) / float(0x7FFFFFFF)) * 2.0 - 1.0


def value_noise(x, y, z):
    def fade(t):
        return t * t * (3.0 - 2.0 * t)

    x0 = math.floor(x)
    y0 = math.floor(y)
    z0 = math.floor(z)
    tx, ty, tz = fade(x - x0), fade(y - y0), fade(z - z0)

    def lerp(a, b, t):
        return a + (b - a) * t

    c00 = lerp(_noise(x0, y0, z0), _noise(x0 + 1, y0, z0), tx)
    c10 = lerp(_noise(x0, y0 + 1, z0), _noise(x0 + 1, y0 + 1, z0), tx)
    c01 = lerp(_noise(x0, y0, z0 + 1), _noise(x0 + 1, y0, z0 + 1), tx)
    c11 = lerp(_noise(x0, y0 + 1, z0 + 1), _noise(x0 + 1, y0 + 1, z0 + 1), tx)
    c0 = lerp(c00, c10, ty)
    c1 = lerp(c01, c11, ty)
    return lerp(c0, c1, tz)


def clay_lumps(obj, ring, amount, seed):
    """Low-frequency 3D dents. Amplitude falls off at the boundary.
    Not a sine of Y — that was the horizontal-ripple failure mode.
    """
    if amount <= 0 or len(ring) < 3:
        return
    import bmesh

    phase = (seed % 997) * 0.017
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    ds = [dist_to_edges(v.co.x, v.co.y, ring) for v in bm.verts]
    dmax = max(ds) or 1e-4
    for v, d in zip(bm.verts, ds):
        edge = max(0.0, min(1.0, d / dmax))
        n = value_noise(v.co.x * 3.2 + phase, v.co.y * 3.2 - phase, v.co.z * 2.4)
        n2 = value_noise(v.co.x * 7.5, v.co.y * 6.8, v.co.z * 5.0 + 2.0)
        disp = amount * edge * (0.85 * n + 0.25 * n2)
        v.co.z += disp
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def curve_to_filled_mesh(bpy, name, ring):
    cu = bpy.data.curves.new(name + "_cu", type="CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.resolution_u = 2
    sp = cu.splines.new("POLY")
    sp.points.add(len(ring) - 1)
    for i, (x, y) in enumerate(ring):
        sp.points[i].co = (float(x), float(y), 0.0, 1.0)
    sp.use_cyclic_u = True
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active
    if len(obj.data.polygons) == 0:
        # fan fallback
        mesh = bpy.data.meshes.new(name + "_fan")
        verts = [(x, y, 0.0) for x, y in ring]
        faces = []
        # triangle fan around centroid — ok for convex parts
        cx = sum(v[0] for v in verts) / len(verts)
        cy = sum(v[1] for v in verts) / len(verts)
        verts.append((cx, cy, 0.0))
        c = len(verts) - 1
        for i in range(len(ring)):
            faces.append((i, (i + 1) % len(ring), c))
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        new = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(new)
        bpy.data.objects.remove(obj, do_unlink=True)
        obj = new
    return obj


def build_volume(bpy, prim, params):
    ring = dedupe_ring(prim["polygon"])
    if len(ring) < 3:
        return None
    obj = curve_to_filled_mesh(bpy, prim["id"], ring)
    thickness = max(0.008, float(prim["thickness"]))
    solid = obj.modifiers.new("Solid", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0.0
    solid.use_even_offset = False
    bevel_w = min(float(prim.get("bevel") or 0.0), thickness * 0.28)
    if bevel_w > 0.001:
        bevel = obj.modifiers.new("Bevel", "BEVEL")
        bevel.width = bevel_w
        bevel.segments = 2
        bevel.limit_method = "ANGLE"
        bevel.angle_limit = math.radians(38)
        try:
            bevel.affect = "EDGES"
        except Exception:
            pass
    try:
        obj = realize(bpy, obj)
    except Exception as exc:
        print("realize failed, retry without bevel", prim["id"], exc)
        # object may be half-realized; rebuild plainly
        raise
    obj.location.z = float(prim.get("z_lift") or 0.0)
    dome_inflate(obj, ring, float(prim.get("inflate") or 0.0))
    if params.get("lumps") and prim.get("allow_lump"):
        scale = {"primary": 0.03, "secondary": 0.016, "detail": 0.0}.get(prim.get("feature_scale"), 0.01)
        clay_lumps(obj, ring, scale, stable_hash(prim["id"]))
    shade_and_sharp(obj, 50 if prim.get("feature_scale") != "detail" else 35)
    role = prim.get("role")
    rough = None
    trans = None
    coat = None
    sheen = None
    if role == "eye":
        rough = 0.45
        trans = 0.0
        coat = 0.05
        sheen = 0.0
    elif role == "window":
        rough = min(0.18, params["roughness"])
        trans = max(params["transmission"], 0.35) if params["transmission"] > 0 else 0.15
    mat = make_material(prim["id"] + "_mat", prim["color"], params, rough=rough, trans=trans, coat=coat, sheen=sheen)
    link_material(obj, mat)
    obj["v3_part"] = prim["id"]
    return obj


def build_tube(bpy, name, path, radius, z, color, params, *, rough=None, sheen=None):
    pts = [(float(p[0]), float(p[1])) for p in path]
    if len(pts) < 2 or radius <= 0:
        return None
    cu = bpy.data.curves.new(name + "_cu", type="CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = float(radius)
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    cu.resolution_u = 4
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, (x, y) in enumerate(pts):
        sp.points[i].co = (x, y, float(z), 1.0)
    obj = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active
    shade_and_sharp(obj, 60)
    mat = make_material(name + "_mat", color, params, rough=rough, trans=0.0 if rough else None, sheen=sheen, coat=0.0 if sheen else None)
    link_material(obj, mat)
    obj["v3_part"] = name
    return obj


def scatter_points(ring, count, rng, margin=0.004):
    if len(ring) < 3 or count <= 0:
        return []
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    found = []
    tries = 0
    limit = count * 40
    while len(found) < count and tries < limit:
        tries += 1
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        if point_in_poly(x, y, ring) and dist_to_edges(x, y, ring) > margin:
            found.append((x, y))
    return found


def build_bubbles(bpy, prim, params, rng):
    ring = dedupe_ring(prim["polygon"])
    area = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        area += x1 * y2 - x2 * y1
    area = abs(area) * 0.5
    count = max(6, min(16, int(area * 40)))
    pts = scatter_points(ring, count, rng, margin=0.02)
    import bmesh
    from mathutils import Matrix

    bm = bmesh.new()
    thickness = float(prim["thickness"])
    z0 = float(prim["z_lift"])
    for i, (x, y) in enumerate(pts):
        rad = rng.uniform(0.008, 0.02)
        z = z0 + rng.uniform(-thickness * 0.15, thickness * 0.2)
        bmesh.ops.create_icosphere(
            bm,
            subdivisions=1,
            radius=rad,
            matrix=Matrix.Translation((x, y, z)),
        )
    if not bm.verts:
        bm.free()
        return None
    mesh = bpy.data.meshes.new(prim["id"] + "_bubbles")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(prim["id"] + "_bubbles", mesh)
    bpy.context.collection.objects.link(obj)
    # air-like beads inside the gelatin
    bubble_params = dict(params)
    mat = make_material(
        prim["id"] + "_bubble_mat",
        (0.95, 0.97, 1.0),
        bubble_params,
        rough=0.04,
        trans=1.0,
        coat=0.4,
        sheen=0.0,
    )
    # lower IOR so they read as pockets, not solid pearls
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "IOR", 1.05)
    set_input(bsdf, "Subsurface Weight", 0.0)
    link_material(obj, mat)
    return obj


def build_fur(bpy, prim, params, rng):
    ring = dedupe_ring(prim["polygon"])
    area = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % len(ring)]
        area += x1 * y2 - x2 * y1
    area = abs(area) * 0.5
    count = int(max(90, min(780, area * 3600)))
    margin = 0.006 if prim.get("feature_scale") == "primary" else 0.004
    pts = scatter_points(ring, count, rng, margin=margin)
    if not pts:
        return None
    import bmesh
    from mathutils import Matrix

    dmax = 1e-4
    cx = sum(p[0] for p in ring) / len(ring)
    cy = sum(p[1] for p in ring) / len(ring)
    dmax = max(dmax, dist_to_edges(cx, cy, ring))
    bm = bmesh.new()
    z_base = float(prim["z_lift"]) + float(prim["thickness"]) * 0.5
    inflate = float(prim.get("inflate") or 0.0)
    for x, y in pts:
        d = dist_to_edges(x, y, ring)
        t = max(0.0, min(1.0, d / dmax))
        dome = t * t * (3 - 2 * t)
        # nudge outward so the pile changes the silhouette, not only the front face
        vx, vy = x - cx, y - cy
        norm = math.hypot(vx, vy) or 1.0
        reach = 0.008 + 0.01 * (1.0 - t)
        x = x + vx / norm * reach
        y = y + vy / norm * reach
        length = (0.016 if prim.get("feature_scale") == "primary" else 0.011) * (0.7 + 0.45 * rng.random())
        rad = length * 0.34
        z = z_base + inflate * dome + length * 0.45
        mat = Matrix.Translation((x, y, z)) @ Matrix.Scale(1.35, 4, (0.0, 0.0, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rad, matrix=mat)
    mesh = bpy.data.meshes.new(prim["id"] + "_fur")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(prim["id"] + "_fur", mesh)
    bpy.context.collection.objects.link(obj)
    # lighter, very rough pile — the thing that separates plush from clay
    col = [min(1.0, c * 1.12 + 0.04) for c in prim["color"]]
    mat = make_material(prim["id"] + "_fur_mat", col, params, rough=0.98, trans=0.0, coat=0.0, sheen=0.85)
    link_material(obj, mat)
    shade_and_sharp(obj, 70)
    return obj


def build_seam(bpy, prim, params):
    path = prim.get("seam_path") or []
    if len(path) < 2:
        return None
    z = float(prim["z_lift"]) + float(prim["thickness"]) * 0.5 + float(prim.get("inflate") or 0.0) * 0.35
    dark = [c * 0.55 for c in prim["color"]]
    return build_tube(
        bpy,
        prim["id"] + "_seam",
        path,
        radius=0.0045,
        z=z,
        color=dark,
        params=params,
        rough=0.7,
        sheen=0.2,
    )


def world_bbox(objects):
    from mathutils import Vector

    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    any_ok = False
    for obj in objects:
        if obj is None or obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            lo.x, lo.y, lo.z = min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)
            hi.x, hi.y, hi.z = max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)
            any_ok = True
    if not any_ok:
        from mathutils import Vector as V

        return V((0, 0, 0)), V((1, 1, 1))
    return lo, hi


def setup_camera(bpy, objects, camcfg):
    from mathutils import Vector

    lo, hi = world_bbox(objects)
    center = (lo + hi) * 0.5
    sx = max(hi.x - lo.x, 1e-3)
    sy = max(hi.y - lo.y, 1e-3)
    sz = max(hi.z - lo.z, 1e-3)
    lens = float(camcfg.get("lens_mm", 70))
    margin = float(camcfg.get("margin", 1.3))
    fov = 2.0 * math.atan(18.0 / lens)
    half = 0.5 * max(sx, sy, sz) * margin
    dist = half / math.tan(fov * 0.5)
    dist = max(dist, 1.15)
    yaw = math.radians(float(camcfg.get("yaw_deg", 0)))
    pitch = math.radians(float(camcfg.get("pitch_deg", 0)))
    direction = Vector((math.sin(yaw), math.sin(pitch), math.cos(yaw) * math.cos(pitch)))
    direction.normalize()
    loc = center + direction * dist

    cam_data = bpy.data.cameras.new("HeroCam")
    cam_data.lens = lens
    cam_data.clip_start = 0.01
    cam_data.clip_end = max(100.0, dist * 8)
    cam = bpy.data.objects.new("HeroCam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = center
    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, center, dist


def add_area(bpy, name, location, energy, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.shape = "SQUARE"
    light.size = float(size)
    light.energy = float(energy)
    light.color = color
    obj = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    # point the light at the origin-ish by a track later; area lights need -Z toward subject
    return obj


def aim_light(bpy, light_obj, target):
    track = light_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"


def setup_lights(bpy, center, dist, params):
    from mathutils import Vector

    key = params["key"]
    fill = params["fill"]
    rim = params["rim"]
    # square lights only — no wide horizontal strips
    key_obj = add_area(
        bpy,
        "Key",
        center + Vector((dist * 0.18, dist * 0.28, dist * 0.55)),
        key["energy"],
        key["size"],
        tuple(key["color"]),
    )
    fill_obj = add_area(
        bpy,
        "Fill",
        center + Vector((-dist * 0.22, -dist * 0.05, dist * 0.4)),
        fill["energy"],
        fill["size"],
        tuple(fill["color"]),
    )
    rim_obj = add_area(
        bpy,
        "Rim",
        center + Vector((-dist * 0.05, dist * 0.02, -dist * 0.45)),
        rim["energy"],
        rim["size"],
        tuple(rim["color"]),
    )
    target = bpy.data.objects.new("LightTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = center
    for obj in (key_obj, fill_obj, rim_obj):
        aim_light(bpy, obj, target)


def setup_world(bpy, strength):
    world = bpy.data.worlds.new("V3World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs[1].default_value = float(strength)


def configure_render(bpy, job, output):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    res = int(job.get("resolution") or 2048)
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.filter_size = 1.5
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.filepath = str(output)
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Base Contrast"
    except Exception:
        pass
    scene.view_settings.exposure = float(job["style_params"].get("exposure", 0.2))
    samples = int(job.get("samples") or 32)
    scene.eevee.taa_render_samples = samples
    scene.eevee.use_raytracing = True
    if hasattr(scene.eevee, "use_ssr"):
        scene.eevee.use_ssr = True
    if hasattr(scene.eevee, "use_ssr_refraction"):
        scene.eevee.use_ssr_refraction = job["style"] == "gummy"
    scene.eevee.use_shadows = True
    if hasattr(scene.eevee, "use_soft_shadows"):
        scene.eevee.use_soft_shadows = True
    if hasattr(scene.eevee, "use_gtao"):
        scene.eevee.use_gtao = True
        scene.eevee.gtao_factor = float(job["style_params"].get("gtao", 0.6))
    scene.eevee.use_bloom = False
    return scene


def mesh_stats(objects):
    verts = 0
    for obj in objects:
        if obj and obj.type == "MESH":
            verts += len(obj.data.vertices)
    return verts


def main():
    import bpy

    t0 = time.time()
    job_path = _job_path()
    job = json.loads(job_path.read_text())
    output = Path(job["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    result_path = output.with_suffix(".result.json")
    try:
        clear_scene(bpy)
        params = job["style_params"]
        seed = int(job.get("seed") or 1)
        objects = []
        for prim in job["primitives"]:
            rng = random.Random(seed + stable_hash(prim["id"]))
            if prim["kind"] == "volume":
                obj = build_volume(bpy, prim, params)
                if obj:
                    objects.append(obj)
                if params.get("bubbles") and prim.get("allow_bubbles"):
                    bub = build_bubbles(bpy, prim, params, rng)
                    if bub:
                        objects.append(bub)
                if params.get("fur") and prim.get("allow_fur"):
                    fur = build_fur(bpy, prim, params, rng)
                    if fur:
                        objects.append(fur)
                if params.get("seam") and prim.get("allow_seam"):
                    seam = build_seam(bpy, prim, params)
                    if seam:
                        objects.append(seam)
            elif prim["kind"] == "tube":
                obj = build_tube(
                    bpy,
                    prim["id"],
                    prim.get("path") or [],
                    float(prim.get("radius") or 0.015),
                    float(prim.get("z_lift") or 0.0),
                    prim["color"],
                    params,
                )
                if obj:
                    objects.append(obj)
        if not objects:
            raise RuntimeError("no meshes built")
        _cam, center, dist = setup_camera(bpy, objects, job["camera"])
        setup_lights(bpy, center, dist, params)
        setup_world(bpy, params.get("world", 0.1))
        configure_render(bpy, job, output)
        bpy.ops.render.render(write_still=True)
        lo, hi = world_bbox(objects)
        payload = {
            "ok": True,
            "output": str(output),
            "seconds": round(time.time() - t0, 2),
            "verts": mesh_stats(objects),
            "parts": [o.name for o in objects],
            "bbox": [list(lo), list(hi)],
            "style": job.get("style"),
            "source_id": job.get("source_id"),
        }
        result_path.write_text(json.dumps(payload, indent=2))
        print("V3_RENDER_OK", json.dumps(payload))
    except Exception:
        err = traceback.format_exc()
        print(err)
        result_path.write_text(json.dumps({"ok": False, "error": err, "output": str(output)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
