# V3 failure report

Honest split. Fixing one column by damaging another was treated as a failure, not a win.

These notes are about the renders on disk under `out/v3/` (2048 EEVEE, downsampled to 1024). Blender 4.2.9, CPU / llvmpipe via `xvfb-run`. No image API key was set.

## Recognition failures

- General recognition is not implemented. `lab/v3/recognize.py` picks a handler from the corpus `category` hint. A rocket saved as `blob` would not be recognized. The handlers are an explicit POC shortcut.
- The messy doodle's open stroke is star-like. The handler keeps confidence **LOW** and the hypothesis `unresolved_gesture` on purpose. That is the correct refusal, and it is also the limit of the recognizer: it cannot tell "unfinished star" from "three marks" without the hint, so it refuses the object reading entirely.
- Rocket confidence stays **HIGH** even though the flame was not in the ink. The drawn body, fins, and window match. The flame is only a completion. Reporting HIGH for the whole blueprint overstates certainty about parts the user did not draw.
- The rose "spiral" is whatever stroke is named `spiral`. It is a loose cord that leaves the bloom on the left. The handler does not recover a botanical spiral the user did not draw. It also does not reject the stroke when it fails to sit inside the bloom.

## Reconstruction failures

- **Flame is invented geometry.** `06_rocket` has no flame stroke. A small separate exhaust was added under the body, between the fins, and tagged `completed: true` / `features_may_complete`. It changes the silhouette versus the doodle. It is not fused into the body, but it is still an object the user did not draw.
- The nose is split out of the body taper. The original stroke is one pentagon-like outline. The seam at the shoulders is a reconstruction edge, not a line the user drew. The outer silhouette is the user's; the part boundary is ours.
- Fins are separate meshes. Their attachment edge is nudged a short distance into the body so they don't hover. They are not boolean-unioned. The overlap can still read as a join if the light is flat.
- Open strokes become tubes: plant stem, rose stem, rose spiral, messy partial, messy scribble. The plant stem is almost a vertical hairline in the doodle. The tube gives it a round stalk (listed as may-complete) and is thicker than the ink.
- Heart cleft and bottom point are pinned, and there is no subsurf shrink. A small bevel still softens the sharpest notch. The wonky asymmetry is kept; it is not mirrored.
- The first rose framing clipped the stem on the bottom row (alpha touched y=1023). The shipped rose renders use a wider, lower camera (`margin` 1.72). Padding is about 130px at 1024. The rose is smaller in frame than the heart because the spiral's wide bounding box has to fit.

## Rendering failures

- Gummy is only partly gelatin. EEVEE transmission here reads as shiny translucent plastic. Interior bubble spheres help on large volumes (heart, teddy body, rocket body). They do not read as deep colored jelly with internal caustics. The heart gummy's broad face still clips the red channel (median red 255 in the 1024 downsample) so the highlight is flatter than the darker rim.
- No ground plane and no horizontal light strips were used. A row-luminance "band score" still spikes on the messy tubes (about 15, versus about 1–7 on the filled shapes). That score is the thin strokes crossing rows, not a softbox stripe. Filled stickers do not show a repeating horizontal ripple. There is no wave modifier and no Y-only displacement.
- Thin tubes (messy strokes, rose spiral, plant stem) show more aliasing than the filled volumes, even after 2048 → 1024 premultiplied downsampling.
- Square area lights and a mostly frontal camera keep the side wall small. Volume reads more from the dome and the material than from a turned edge. That was intentional. It also means clay shading stays quiet.
- Plush fiber is a field of small icospheres, not hair curves. Zoomed in, the pile can look beady. It does change the surface. It does not always change the alpha footprint: plush-minus-clay fill is about −0.002 (heart) to +0.02 (messy). See style failures.

## Style failures

- **Plush vs clay is the weak pair at thumbnail size.** Up close, plush has a fiber shell and a darker stitch, and clay is smoother with low-frequency dents and a broader, duller shade. In the contact sheet those cues shrink. Clay dents are easy to miss. The two styles are not the same shader, and they are not as far apart as gummy vs glossy.
- **Gummy vs glossy can both read as "shiny plastic"** on the rocket, where the body is thin and the bubbles are small. The glossy key is a small hard highlight with clearcoat and less inflate. The gummy key is broader, with transmission and bubbles. On the heart the difference is clearer (bubbles, softer body, clipped pink face versus a tight specular dot).
- Clay micro-geometry was kept mild so it would not turn into another lumpy noise and would not bring back horizontal ripples. The cost is a style that sometimes looks like "smooth matte" rather than "thumb-printed play-doh."
- The completed rocket flame picks up the style (gummy flame, fuzzy plush flame, hard glossy flame). That makes the invention more visible, not less.
- Messy is styled rather than reinterpreted. Four materials on the same three strokes is the right low-confidence behavior. It will not look like a polished character, and it should not.

## Per example

| Example | What holds | What does not |
|---|---|---|
| heart | Upright, cleft, asymmetric lobes, one contour | Gummy face is hot; clay dents are quiet |
| rocket | Fins, nose, window stay separate meshes | Flame was not drawn; gummy/glossy both skew shiny |
| teddy | Head, body, two ears, two eyes; no invented mouth | Ears overlap the head by design; the join is an overlap, not a fusion, but it is a join |
| plant | Pot, stem, two leaves stay separate | Stem thickness is reconstructed; leaves are small |
| rose | Bloom, loose spiral cord, stem, one leaf | Spiral is not a botanical rose; framing is looser so nothing clips |
| messy | Stays three marks, open strokes stay open, LOW banner on the blueprint | Corners are rounder than the ink; not a finished symbol, on purpose |
