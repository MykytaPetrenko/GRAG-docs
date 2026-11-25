"""Capture the Blender interface frame by frame while settings change, for the documentation GIFs.

Run with the Blender interface (not in background mode):

    blender --factory-startup --python tools/capture_gif.py -- stairs_rebuild

Frames go to tools/_renders/gif_<name>/; `make_gifs.py` turns them into GIFs.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

from studio import RENDERS, grag  # noqa: E402

PANELS = {'door': 'GRAG_PT_door_generator', 'window': 'GRAG_PT_window_generator', 'stairs': 'GRAG_PT_stairs_generator'}


def stairs_rebuild():
    """Auto Rebuild: a second flight, its turn and each railing type change the stairs at once."""
    bpy.ops.grag.stairs_build()
    root = bpy.context.object
    settings = root.grag_stairs
    settings.auto_rebuild = False
    settings.flight_count, settings.step_count, settings.width = 1, 8, 1.1
    settings.auto_rebuild = True
    flights = ('landings_expanded',)
    railing = ('railings_expanded',)
    steps = [
        (flights, {}, 1.2),
        (flights, {'flight_count': 2}, 1.2),
        (flights, {'turn_angle': '90'}, 1.2),
        (flights, {'turn_angle': '180'}, 1.0),
        (railing, {'rail_enabled': True}, 1.2),
        (railing, {'rail_type': 'TYPE_2'}, 1.2),
        (railing, {'rail_type': 'TYPE_3'}, 1.2),
        (railing, {'rail_type': 'TYPE_4'}, 1.8),
    ]
    return 'stairs', root, (60, 0, 40), steps


SEQUENCES = {'stairs_rebuild': stairs_rebuild}
name = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'stairs_rebuild'
FRAMES = RENDERS / f'gif_{name}'
state = {'step': -2, 'durations': []}


def view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                return window, area
    return None, None


def bounds(root):
    points = [obj.matrix_world @ Vector(corner) for obj in (root, *root.children_recursive)
              if obj.type == 'MESH' and not obj.get('grag_collision') for corner in obj.bound_box]
    return (Vector([min(p[i] for p in points) for i in range(3)]),
            Vector([max(p[i] for p in points) for i in range(3)]))


def setup(window, area):
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    asset, root, rotation, steps = SEQUENCES[name]()
    state.update(asset=asset, root=root, steps=steps)
    # Frame every state of the sequence at once, so the view stays still.
    settings = getattr(root, 'grag_' + asset)
    initial = {key: getattr(settings, key) for _, values, _ in steps for key in values}
    low, high = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for index in range(len(steps)):
        apply(index, record=False)
        a, b = bounds(root)
        low = Vector([min(x, y) for x, y in zip(low, a)])
        high = Vector([max(x, y) for x, y in zip(high, b)])
    settings.auto_rebuild = False
    for key, value in initial.items():
        setattr(settings, key, value)
    settings.auto_rebuild = True
    bpy.ops.grag.stairs_rebuild() if asset == 'stairs' else None
    apply(0, record=False)
    for panel_asset, idname in PANELS.items():
        if panel_asset != asset and hasattr(bpy.types, idname):
            bpy.utils.unregister_class(getattr(bpy.types, idname))
    # The root stays active for the panel, but unselected so it has no outline.
    root.select_set(False)
    bpy.context.view_layer.objects.active = root
    space = area.spaces.active
    space.show_region_ui = True
    space.show_region_header = False
    space.show_region_toolbar = False
    space.show_region_tool_header = False
    space.shading.type = 'MATERIAL'
    overlay = space.overlay
    overlay.show_cursor = overlay.show_text = overlay.show_stats = False
    overlay.show_axis_x = overlay.show_axis_y = False
    space.show_gizmo = False
    # Shift the target left so the asset is centred in the part of the view the sidebar leaves free.
    center = (low + high) / 2
    radius = (high - low).length / 2
    region_3d = space.region_3d
    region_3d.view_rotation = Euler([value * 3.14159265 / 180 for value in rotation]).to_quaternion()
    region_3d.view_distance = radius * 2.4
    right = region_3d.view_rotation @ Vector((1, 0, 0))
    region_3d.view_location = center + right * radius * .45


def apply(index, record=True):
    sections, values, hold = state['steps'][index]
    settings = getattr(state['root'], 'grag_' + state['asset'])
    for prop in settings.bl_rna.properties.keys():
        if prop.endswith('_expanded'):
            setattr(settings, prop, prop in sections)
    for key, value in values.items():
        setattr(settings, key, value)
    if record:
        state['durations'].append(hold)


def tick():
    window, area = view3d()
    if area is None:
        return .5
    step = state['step']
    if step == -2:
        with bpy.context.temp_override(window=window, area=area):
            setup(window, area)
        state['step'] = -1
        return 1.0
    if step == -1:
        for region in area.regions:
            if region.type == 'UI':
                try:
                    region.active_panel_category = 'GRAG'
                except (AttributeError, TypeError):
                    pass
        state['step'] = 0
        apply(0)
        area.tag_redraw()
        return 1.0
    with bpy.context.temp_override(window=window, area=area):
        bpy.ops.screen.screenshot_area(filepath=str(FRAMES / f'{step:03d}.png'))
    step += 1
    if step >= len(state['steps']):
        (FRAMES / 'durations.json').write_text(json.dumps(state['durations']), encoding='utf-8')
        bpy.ops.wm.quit_blender()
        return None
    apply(step)
    state['step'] = step
    area.tag_redraw()
    return .8


bpy.context.preferences.view.show_splash = False
grag.register()
for cls in [getattr(bpy.types, idname) for idname in PANELS.values()]:
    bpy.utils.unregister_class(cls)
    cls.bl_options = set()
    bpy.utils.register_class(cls)
FRAMES.mkdir(parents=True, exist_ok=True)
for old in FRAMES.glob('*.png'):
    old.unlink()
bpy.app.timers.register(tick, first_interval=1.0)
