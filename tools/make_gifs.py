"""Turn the captured interface frames into GIFs for the documentation.

    python tools/make_gifs.py [stairs_rebuild ...]
"""

import json
from pathlib import Path
import sys

from PIL import Image

TOOLS = Path(__file__).resolve().parent
RENDERS = TOOLS / '_renders'
IMAGES = TOOLS.parent / 'docs' / 'images'
# Frames are cropped (left, top, right, bottom) and scaled to WIDTH.
CROPS = {'stairs_rebuild': (40, 28, 1574, 888)}
WIDTH = 1000


BACKGROUND = (57, 57, 57, 255)
# Rendered frame folders: transparent PNGs, trimmed together and put on the page colour.
RENDERED = {'door_swing': 'door-collision-swing', 'window_french': 'window-french'}


def make_rendered(name, width=720, seconds=.07, hold=.9):
    folder = RENDERS / f'frames_{name}'
    frames = [Image.open(path).convert('RGBA') for path in sorted(folder.glob('*.png'))]
    boxes = [frame.getchannel('A').getbbox() for frame in frames]
    pad = 16
    box = (max(0, min(b[0] for b in boxes) - pad), max(0, min(b[1] for b in boxes) - pad),
           max(b[2] for b in boxes) + pad, max(b[3] for b in boxes) + pad)
    result = []
    for frame in frames:
        page = Image.new('RGBA', frame.size, BACKGROUND)
        page.alpha_composite(frame)
        page = page.crop(box).convert('RGB')
        if page.width > width:
            page = page.resize((width, round(page.height * width / page.width)), Image.LANCZOS)
        result.append(page)
    palette = result[len(result) // 2].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    result = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in result]
    # Pause at the closed and fully open poses.
    durations = [round(seconds * 1000)] * len(result)
    durations[0] = durations[len(result) // 2] = round(hold * 1000)
    path = IMAGES / f'{RENDERED[name]}.gif'
    result[0].save(path, save_all=True, append_images=result[1:], loop=0, optimize=True, duration=durations)
    print('wrote', path, f'{path.stat().st_size // 1024} KB')


def make(name):
    folder = RENDERS / f'gif_{name}'
    durations = json.loads((folder / 'durations.json').read_text(encoding='utf-8'))
    frames = []
    for index in range(len(durations)):
        frame = Image.open(folder / f'{index:03d}.png').convert('RGB').crop(CROPS[name])
        frame = frame.resize((WIDTH, round(frame.height * WIDTH / frame.width)), Image.LANCZOS)
        frames.append(frame)
    # One shared palette keeps the background from flickering between frames.
    palette = frames[-1].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    IMAGES.mkdir(parents=True, exist_ok=True)
    path = IMAGES / f'{name.replace("_", "-")}.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], loop=0, optimize=True,
                   duration=[round(seconds * 1000) for seconds in durations])
    print('wrote', path, f'{path.stat().st_size // 1024} KB')


for name in sys.argv[1:] or [*CROPS, *RENDERED]:
    make_rendered(name) if name in RENDERED else make(name)
