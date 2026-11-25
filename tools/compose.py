"""Compose the documentation figures from the renders and panel screenshots.

Run with any Python that has Pillow:

    python tools/compose.py

Every figure is a plain dark page with the subject, an optional panel inset,
thin arrows and short labels. Output goes to docs/images as WebP.
"""

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

TOOLS = Path(__file__).resolve().parent
RENDERS = TOOLS / '_renders'
IMAGES = TOOLS.parent / 'docs' / 'images'
BACKGROUND = (57, 57, 57, 255)
ARROW = (242, 177, 52, 255)
LABEL = (232, 232, 232, 255)
FONT = 'C:/Windows/Fonts/segoeui.ttf'


def render(name, width=None, pad=12, trim=True):
    """A transparent render, trimmed to its content with a small margin."""
    image = Image.open(RENDERS / f'{name}.png').convert('RGBA')
    if trim:
        left, top, right, bottom = image.getchannel('A').getbbox()
        image = image.crop((max(0, left - pad), max(0, top - pad), right + pad, bottom + pad))
    if width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    return image


def panel(name, box):
    """A section of a panel screenshot, cropped from the sidebar region."""
    full = Image.open(RENDERS / f'panel_{name}_full.png').convert('RGBA')
    x, y, width, height, _, area_height = map(int, (RENDERS / f'panel_{name}.txt').read_text().split())
    region = full.crop((x, area_height - y - height, x + width, area_height - y))
    return region.crop(box)


def font(size):
    return ImageFont.truetype(FONT, size)


def label(draw, center, text, size=24):
    draw.text(center, text, fill=LABEL, font=font(size), anchor='mm')


def arrow(draw, start, end, width=3, head=9):
    draw.line([start, end], fill=ARROW, width=width)
    x, y = end
    # Arrows in these figures point straight down.
    draw.polygon([(x - head, y - head * 1.4), (x + head, y - head * 1.4), (x, y)], fill=ARROW)


def tree(draw, top, bottom, xs, stem_x):
    """One stem from the subject splitting into arrows that point down at each result."""
    middle = (top + bottom) // 2
    draw.line([(stem_x, top), (stem_x, middle)], fill=ARROW, width=3)
    draw.line([(min(xs), middle), (max(xs), middle)], fill=ARROW, width=3)
    for x in xs:
        arrow(draw, (x, middle), (x, bottom))


def save(image, name, quality=88):
    IMAGES.mkdir(parents=True, exist_ok=True)
    image.convert('RGB').save(IMAGES / f'{name}.webp', 'WEBP', quality=quality, method=6)
    print('wrote', IMAGES / f'{name}.webp', image.size)


def window_collision_detail():
    levels = (('block', 'Solid Block'), ('sashes', 'Sash Boxes'), ('frame_glass', 'Frame and Glass'),
              ('glass_bodies', 'Frame and Glass Bodies'))
    tile = 420
    width = tile * len(levels)
    subject = render('window_visual', 400)
    inset = panel('window_collisions', (16, 362, 245, 509))
    tiles = [render(f'window_detail_{key}', tile - 70) for key, _ in levels]
    top = 20
    stem_top = top + subject.height + 14
    labels_y = stem_top + 100
    tiles_y = labels_y + 30
    image = Image.new('RGBA', (width, tiles_y + max(t.height for t in tiles) + 20), BACKGROUND)
    image.alpha_composite(subject, ((width - subject.width) // 2, top))
    image.alpha_composite(inset, (width - inset.width - 30, top + 10))
    draw = ImageDraw.Draw(image)
    centers = [tile * index + tile // 2 for index in range(len(levels))]
    tree(draw, stem_top, labels_y - 26, centers, width // 2)
    for (key, text), x, picture in zip(levels, centers, tiles):
        label(draw, (x, labels_y), text)
        image.alpha_composite(picture, (x - picture.width // 2, tiles_y))
    save(image, 'window-collision-detail')


FIGURES = {'window-collision-detail': window_collision_detail}

if __name__ == '__main__':
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
