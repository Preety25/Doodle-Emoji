# Style sheets for production

Canonical paths expected by style configs:

- `docs/refs/style_sheets/sheet_gummy.png`
- `docs/refs/style_sheets/sheet_clay.png`
- `docs/refs/style_sheets/sheet_plush.png`
- `docs/refs/style_sheets/sheet_glossy.png`

Those files were referenced by V4.3/V4.4 lab runners but were not present on
`stylization/v4-ai-rendering` at foundation time. Place versioned material-only
boards there (or under this directory) before live multi-style quality gates.

Until then, style JSON `sheet_fallbacks` may resolve to older tracked refs
(e.g. `docs/refs/ref2_gummy_star_gradient.png`, `docs/refs/ref1_glossy_blob.png`).
Clay/plush have no good tracked fallback — text style language still applies.
