# Stylization Lab Versions

| Component | Version | Notes |
|-----------|---------|-------|
| Blender | **4.2.9 LTS** | Official linux-x64 tarball from download.blender.org |
| BLENDER_BIN | `/workspace/tools/blender/blender-4.2.9-linux-x64/blender` | Symlinked as `/workspace/bin/blender` |
| transformation_version | **tx.v1.0.0** | Stroke normalize → interpret → curve/mesh → recipe materials → EEVEE RGBA |
| style gummy | **gummy.v1** | recipes/gummy.v1.json |
| style clay | **clay.v1** | recipes/clay.v1.json |
| style plush | **plush.v1** | recipes/plush.v1.json |
| lab package | **0.1.0** | POC |
| evaluation rubric | **lab_auto_v1** | Heuristic + visual subset inspection |
| corpus | **corpus.v1** | 20 hand-drawn-ish stroke JSONs |

Pinned install command:
```bash
# Already extracted under /workspace/tools/blender/
export PATH="/workspace/bin:$PATH"
# or: export BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender
blender --version
```

- Visual refs: Batch-1 in docs/refs/; Batch-2 in docs/refs/batch2/ (see visual_language.md synthesis).

