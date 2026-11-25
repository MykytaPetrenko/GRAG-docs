"""Window figures: layout presets, collision detail levels, the French pair opening and the hero window."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import RENDERS, asset_meshes, clear, frame, render, reset, show_collisions  # noqa: E402
from grag.services.presets import window_layout_preset  # noqa: E402

PRESETS = ('SINGLE_FIXED', 'DOUBLE_FIXED', 'DOUBLE_SASH', 'TRIPLE_FIXED', 'TRIPLE_SASH', 'FRENCH')
LEVELS = ('BLOCK', 'SASHES', 'FRAME_GLASS', 'GLASS_BODIES')
ROOM_SIDE = (.75, 2.0, .7)


def window(preset, **settings):
    clear()
    assert bpy.ops.grag.apply_preset(asset='window', filepath=window_layout_preset(preset)) == {'FINISHED'}
    assert bpy.ops.grag.window_build(action='NEW') == {'FINISHED'}
    root = bpy.context.object
    for key, value in settings.items():
        setattr(root.grag_window, key, value)
    assert root.grag_window.last_error == '', root.grag_window.last_error
    return root


def presets():
    for preset in PRESETS:
        root = window(preset, preview=.3)
        frame(asset_meshes(root), ROOM_SIDE, width=900, height=720)
        render(f'window_preset_{preset.lower()}')


def detail():
    root = window('TRIPLE_SASH', preview=.35, sill_collision=True)
    frame(asset_meshes(root), (1.0, 1.75, 1.0), width=800, height=640)
    render('window_visual')
    for level in LEVELS:
        root.grag_window.collision_detail = level
        assert root.grag_window.last_error == '', root.grag_window.last_error
        show_collisions(root, root.grag_window)
        render(f'window_detail_{level.lower()}')


def french():
    """Preview Opening sweeps the pair open: the left sash first, then the one with the meeting stile."""
    root = window('FRENCH')
    settings = root.grag_window
    settings.preview = 1
    frame(asset_meshes(root), (.6, 2.0, .9), width=720, height=640)
    folder = RENDERS / 'frames_window_french'
    folder.mkdir(parents=True, exist_ok=True)
    values = [index / 16 for index in range(17)]
    values += values[::-1][1:-1]
    for index, value in enumerate(values):
        settings.preview = value
        bpy.context.scene.render.filepath = str(folder / f'{index:03d}.png')
        bpy.ops.render.render(write_still=True)


def hero():
    root = window('TRIPLE_SASH', preview=.35)
    frame(asset_meshes(root), ROOM_SIDE, width=900, height=720)
    render('hero_window')


reset()
JOBS = {'presets': presets, 'detail': detail, 'french': french, 'hero': hero}
for job in (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else JOBS):
    JOBS[job]()
