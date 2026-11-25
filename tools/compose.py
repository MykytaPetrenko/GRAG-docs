"""Compose the documentation figures from the renders and panel screenshots.

Run with any Python that has Pillow:

    python tools/compose.py

Every figure is a plain dark page with the subject, an optional panel inset,
thin arrows and short labels. Output goes to docs/images as WebP.
"""

import json
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


def fit(image, width, height):
    image = image.copy()
    image.thumbnail((width, height), Image.LANCZOS)
    return image


def grid(name, tiles, columns, cell=(420, 420), labels=None, gap=24, label_size=22):
    """Tiles in a grid, each centred in its cell, with an optional label under it."""
    width, height = cell
    label_height = 44 if labels else 0
    rows = (len(tiles) + columns - 1) // columns
    image = Image.new('RGBA', (columns * width + (columns + 1) * gap,
                               rows * (height + label_height) + (rows + 1) * gap), BACKGROUND)
    draw = ImageDraw.Draw(image)
    for index, tile in enumerate(tiles):
        tile = fit(tile, width, height)
        column, row = index % columns, index // columns
        x = gap + column * (width + gap)
        y = gap + row * (height + label_height + gap)
        image.alpha_composite(tile, (x + (width - tile.width) // 2, y + (height - tile.height) // 2))
        if labels:
            label(draw, (x + width // 2, y + height + label_height // 2), labels[index], label_size)
    save(image, name)


def door_styles():
    styles = (('flush', 'Flush Wood'), ('slats', 'Horizontal Slats'), ('steel', 'Steel Panel'),
              ('reference', 'Original Four-Panel'), ('rounded_four', 'Rounded Four-Panel'),
              ('classic_three', 'Classic Three-Panel'), ('modern_two', 'Modern Two-Panel'))
    grid('door-styles', [render(f'door_style_{key}') for key, _ in styles], 4, (300, 460),
         [text for _, text in styles])


def door_handles():
    handles = (('square', 'Square Lever'), ('knob', 'Round Knob'), ('tube', 'Return Lever'),
               ('reference', 'Original Lever'), ('swept', 'Swept Lever'), ('blade', 'Blade Lever'),
               ('turned', 'Turned Lever'), ('wave', 'Wave Lever'))
    grid('door-handles', [render(f'door_handle_{key}', trim=False) for key, _ in handles], 4, (380, 380),
         [text for _, text in handles])


def door_layouts():
    layouts = (('single', 'Single Leaf'), ('double', 'Double Leaf'), ('sections', 'Side Sections and Transom'))
    grid('door-layouts', [render(f'door_layout_{key}') for key, _ in layouts], 3, (460, 460),
         [text for _, text in layouts])


def window_presets():
    presets = (('single_fixed', 'Single Fixed Pane'), ('double_fixed', 'Two Fixed Panes'),
               ('double_sash', 'Two Panes, Right Sash'), ('triple_fixed', 'Three Fixed Panes'),
               ('triple_sash', 'Three Panes, Center Sash'), ('french', 'French Pair'))
    grid('window-presets', [render(f'window_preset_{key}') for key, _ in presets], 3, (460, 370),
         [text for _, text in presets])


def stairs_presets():
    presets = (('straight', 'Straight Concrete'), ('l_turn', 'L-Turn, Timber Balusters'),
               ('u_turn', 'U-Turn, Tubular Railing'), ('metal', 'Metal Balusters, Tread Plates'))
    grid('stairs-presets', [render(f'stairs_preset_{key}') for key, _ in presets], 4, (400, 400),
         [text for _, text in presets], label_size=20)


def stairs_finish():
    grid('stairs-finish', [render('stairs_finish_original'), render('stairs_finish_plates')], 2, (560, 420),
         ['Original Bevel', 'Tread Plates'])


def stairs_collisions():
    grid('stairs-collisions', [render('stairs_collisions_steps'), render('stairs_collisions_ramp')], 2, (600, 560),
         ['Flight Shape: Steps', 'Flight Shape: Ramp'])


def railing_types():
    types = (('type_1', 'Type 1 · Tubular'), ('type_2', 'Type 2 · Rectangular'),
             ('type_3', 'Type 3 · Vertical Balusters'), ('type_4', 'Type 4 · Metal Balusters'))
    grid('railing-types', [render(f'stairs_railing_{key}') for key, _ in types], 2, (560, 520),
         [text for _, text in types])


def railing_mounting():
    grid('railing-mounting', [render('stairs_mounting_flight'), render('stairs_mounting_wall')], 2, (600, 560),
         ['Flight Mounted on both sides', 'Wall Mounted outer side, with Preview Wall'])


def hero():
    tiles = [render('hero_door'), render('hero_window'), render('hero_stairs')]
    grid('hero', tiles, 3, (440, 440), gap=30)


def texturing_atlas():
    """The door with a checker on its atlas, and the atlas itself."""
    door = fit(render('door_uv_grid'), 420, 640)
    size = 600
    atlas = Image.new('RGBA', (size, size), (46, 46, 46, 255))
    draw = ImageDraw.Draw(atlas)
    for polygon in json.loads((RENDERS / 'door_atlas.json').read_text(encoding='utf-8')):
        points = [(u * size, (1 - v) * size) for u, v in polygon]
        draw.polygon(points, fill=(150, 142, 128, 255), outline=(225, 220, 205, 255))
    gap = 40
    image = Image.new('RGBA', (door.width + size + gap * 3, max(door.height, size) + gap * 2), BACKGROUND)
    image.alpha_composite(door, (gap, (image.height - door.height) // 2))
    image.alpha_composite(atlas, (door.width + gap * 2, (image.height - size) // 2))
    save(image, 'texturing-atlas')


def texturing_ready():
    """The draft atlas with a wood veneer, straight out of Rebuild."""
    grid('texturing-ready', [render('door_veneer'), render('door_veneer_close', trim=False),
                              render('stairs_ready')], 3, (440, 600), gap=30)


def painter_bake():
    grid('painter-bake', [render('door_painter_high')], 1, (1400, 620))


FIGURES = {'window-collision-detail': window_collision_detail, 'door-styles': door_styles,
           'door-handles': door_handles, 'door-layouts': door_layouts, 'window-presets': window_presets,
           'stairs-presets': stairs_presets, 'stairs-finish': stairs_finish, 'stairs-collisions': stairs_collisions,
           'railing-types': railing_types, 'railing-mounting': railing_mounting, 'hero': hero,
           'texturing-atlas': texturing_atlas, 'painter-bake': painter_bake, 'texturing-ready': texturing_ready}

if __name__ == '__main__':
    for name in sys.argv[1:] or FIGURES:
        FIGURES[name]()
