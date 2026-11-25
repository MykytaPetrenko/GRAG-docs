"""Window collision detail levels: the same window with each level's collision wires."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import camera, render, reset, show_collisions  # noqa: E402
from grag.services.presets import window_layout_preset  # noqa: E402

LEVELS = ('BLOCK', 'SASHES', 'FRAME_GLASS', 'GLASS_BODIES')

reset()
assert bpy.ops.grag.apply_preset(asset='window', filepath=window_layout_preset('TRIPLE_SASH')) == {'FINISHED'}
assert bpy.ops.grag.window_build(action='NEW') == {'FINISHED'}
window = bpy.context.object
settings = window.grag_window
settings.preview = .35
settings.sill_collision = True
camera((1.9, 3.3, 1.9), (0, 0, .55), lens=55)
render('window_visual', 800, 640)
for level in LEVELS:
    settings.collision_detail = level
    assert settings.last_error == '', settings.last_error
    show_collisions(window, settings, visible=True, visuals=True)
    render(f'window_detail_{level.lower()}', 800, 640)
