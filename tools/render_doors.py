"""Door figures: styles, handles, layouts, the hero door and the swinging leaf with its collisions."""

import sys
from math import radians
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import asset_meshes, clear, frame, render, reset, show_collisions  # noqa: E402

STYLES = ('FLUSH', 'SLATS', 'STEEL', 'REFERENCE', 'ROUNDED_FOUR', 'CLASSIC_THREE', 'MODERN_TWO')
HANDLES = ('SQUARE', 'KNOB', 'TUBE', 'REFERENCE', 'SWEPT', 'BLADE', 'TURNED', 'WAVE')
ROOM_SIDE = (.9, 2.4, .55)


def door(**settings):
    clear()
    assert bpy.ops.grag.door_build(action='NEW') == {'FINISHED'}
    root = bpy.context.object
    root.grag_door.auto_rebuild = False
    for key, value in settings.items():
        setattr(root.grag_door, key, value)
    root.grag_door.auto_rebuild = True
    assert bpy.ops.grag.door_build(action='REBUILD') == {'FINISHED'}, root.grag_door.last_error
    return root


def styles():
    for style in STYLES:
        root = door(style=style)
        frame(asset_meshes(root), ROOM_SIDE, width=560, height=900)
        render(f'door_style_{style.lower()}')


def handles():
    for handle in HANDLES:
        root = door(handle=handle, long_backplate=handle in {'SWEPT', 'TURNED'})
        grips = [obj for obj in asset_meshes(root) if obj.get('grag_part') in {'grips', 'plates', 'lock'}
                 and obj.matrix_world.translation.y + max(v.co.y for v in obj.data.vertices) > 0]
        frame(grips, (.55, 1.6, .25), lens=85, margin=1.25, width=600, height=600)
        render(f'door_handle_{handle.lower()}')


def layouts():
    variants = {
        'single': {},
        'double': dict(width=1.5, double_leaf=True, secondary_width=.45, secondary_handle=True),
        'sections': dict(width=2.0, left_section='GLAZED', left_width=.45, right_section='SOLID', right_width=.45,
                         left_style='MATCH_DOOR', right_style='MATCH_DOOR', top_section='GLAZED', top_columns=2,
                         style='CLASSIC_THREE'),
    }
    for name, settings in variants.items():
        root = door(**settings)
        frame(asset_meshes(root), ROOM_SIDE, width=900, height=900)
        render(f'door_layout_{name}')


def hero():
    root = door(style='CLASSIC_THREE', swing=radians(28))
    frame(asset_meshes(root), ROOM_SIDE, width=560, height=900)
    render('hero_door')


def swing_frames():
    """The leaf opens and closes; its amber box turns with it, the frame boxes stay."""
    root = door(style='CLASSIC_THREE', casing_collision=True)
    show_collisions(root, root.grag_door)
    folder = Path(__file__).resolve().parent / '_renders' / 'frames_door_swing'
    folder.mkdir(parents=True, exist_ok=True)
    pivot = next(obj for obj in root.children if obj.get('grag_part') == 'pivot')
    base = pivot.rotation_euler.copy()
    # The leaf opens toward the room, as its grag_motion says.
    sign = 1 if root.grag_door.hinge_side == 'LEFT' else -1

    def pose(angle):
        pivot.rotation_euler = (base.x, base.y, radians(sign * angle))
        bpy.context.view_layer.update()

    # Frame the closed and the fully open door together.
    pose(90)
    open_meshes = asset_meshes(root, collisions=True)
    frame(open_meshes, (1.5, 1.6, 1.25), width=720, height=720)
    angles = [90 * index / 14 for index in range(15)]
    angles += angles[::-1][1:-1]
    for index, angle in enumerate(angles):
        # Turning the pivot is what the game does; the export stays closed.
        pose(angle)
        bpy.context.scene.render.filepath = str(folder / f'{index:03d}.png')
        bpy.ops.render.render(write_still=True)


reset()
JOBS = {'styles': styles, 'handles': handles, 'layouts': layouts, 'hero': hero, 'swing': swing_frames}
for job in (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else JOBS):
    JOBS[job]()
