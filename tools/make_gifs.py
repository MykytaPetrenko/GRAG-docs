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


for name in sys.argv[1:] or CROPS:
    make(name)
