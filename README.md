# GRAG Docs

Public documentation for GRAG, the Game Ready Assets Generator: a Blender extension that builds game-ready doors, windows and stairs with collisions, UVs and exports for Godot and Substance 3D Painter.

The site is built with Sphinx and the Wagtail theme, from Markdown pages parsed by MyST. Source pages live in `docs/`, and a GitHub Actions workflow deploys the generated site to the `gh-pages` branch for GitHub Pages.

## Local build

```powershell
python -m pip install -r requirements.txt
python -m sphinx -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` to preview the site.

## Media

Images and GIFs in `docs/images` are made from the GRAG source in the sibling `GRAG` folder by the scripts in `tools/`:

| Script | Makes |
| --- | --- |
| `tools/render_*.py` | EEVEE renders with a transparent background, run with `blender --background --factory-startup --python tools/render_<name>.py` |
| `tools/capture_panels.py` | Screenshots of panel sections for insets, run with the Blender interface |
| `tools/capture_gif.py` | Interface frames while settings change, run with the Blender interface |
| `tools/compose.py` | Figures on the page colour with insets, arrows and labels, run with Python and Pillow |
| `tools/make_gifs.py` | GIFs from the captured frames |

Intermediate files go to `tools/_renders`, which is not committed.

The textured figures read their maps from two local texture libraries. `GRAG_DOCS_TEXTURES` holds `Veneers/angli_veneer_2k`, `Veneers/black_walnut_veneer_02_2k` and `goldenblack_2-4K`; `GRAG_DOCS_PROCESSED` holds `grave_concrete_03`.
