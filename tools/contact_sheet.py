"""Preview renders side by side: python tools/contact_sheet.py <glob> [tile] [columns]."""

from pathlib import Path
import sys

from PIL import Image

TOOLS = Path(__file__).resolve().parent
pattern = sys.argv[1]
tile = int(sys.argv[2]) if len(sys.argv) > 2 else 360
columns = int(sys.argv[3]) if len(sys.argv) > 3 else 5
paths = sorted((TOOLS / '_renders').glob(pattern))
print('\n'.join(path.name for path in paths))
rows = (len(paths) + columns - 1) // columns
sheet = Image.new('RGBA', (tile * columns, tile * rows), (57, 57, 57, 255))
for index, path in enumerate(paths):
    image = Image.open(path).convert('RGBA')
    image.thumbnail((tile, tile))
    sheet.alpha_composite(image, ((index % columns) * tile, (index // columns) * tile))
sheet.convert('RGB').save(TOOLS / '_renders' / 'check.png')
