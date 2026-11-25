"""Screenshots of the GRAG panels with one section open, for the insets in the documentation.

Run with the Blender interface (not in background mode):

    blender --factory-startup --python tools/capture_panels.py

Each shot builds an asset, opens one section of its panel and saves the
sidebar region to tools/_renders/panel_<name>.png.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import RENDERS, grag  # noqa: E402
from grag.services.presets import builtin_preset, window_layout_preset  # noqa: E402

PANELS = {'door': 'GRAG_PT_door_generator', 'window': 'GRAG_PT_window_generator', 'stairs': 'GRAG_PT_stairs_generator'}


def window_collisions():
    bpy.ops.grag.apply_preset(asset='window', filepath=window_layout_preset('TRIPLE_SASH'))
    bpy.ops.grag.window_build(action='NEW')
    return 'window', bpy.context.object, ('collisions_expanded',)


def door_texturing():
    bpy.ops.grag.door_build(action='NEW')
    return 'door', bpy.context.object, ('baking_expanded',)


def door_header():
    bpy.ops.grag.door_build(action='NEW')
    return 'door', bpy.context.object, ()


def stairs_railings():
    bpy.ops.grag.apply_preset(asset='stairs', filepath=builtin_preset('stairs', 'U-Turn with Tubular Railing'))
    bpy.ops.grag.stairs_build()
    return 'stairs', bpy.context.object, ('railings_expanded',)


SHOTS = {'window_collisions': window_collisions, 'door_texturing': door_texturing, 'door_header': door_header,
         'stairs_railings': stairs_railings}
selection = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else list(SHOTS)
queue = list(selection)
state = {}


def view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                return window, area
    return None, None


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def show_only(asset):
    for name, idname in PANELS.items():
        cls = grag_panels[name]
        registered = hasattr(bpy.types, idname)
        if name == asset and not registered:
            bpy.utils.register_class(cls)
        elif name != asset and registered:
            bpy.utils.unregister_class(cls)


def tick():
    window, area = view3d()
    if area is None:
        return .5
    if 'shot' not in state:
        if not queue:
            bpy.ops.wm.quit_blender()
            return None
        name = queue.pop(0)
        with bpy.context.temp_override(window=window, area=area):
            area.spaces.active.show_region_ui = True
            area.spaces.active.overlay.show_overlays = True
            clear_scene()
            asset, root, sections = SHOTS[name]()
            settings = getattr(root, 'grag_' + asset)
            for prop in settings.bl_rna.properties.keys():
                if prop.endswith('_expanded'):
                    setattr(settings, prop, prop in sections)
            show_only(asset)
        state['shot'] = name
        state['tab'] = False
        area.tag_redraw()
        return 1.0
    if not state['tab']:
        # The tab can only change once the region has drawn its panels.
        for region in area.regions:
            if region.type == 'UI':
                try:
                    region.active_panel_category = 'GRAG'
                    state['tab'] = True
                except (AttributeError, TypeError):
                    pass
        area.tag_redraw()
        return 1.0
    name = state.pop('shot')
    region = next(region for region in area.regions if region.type == 'UI')
    path = RENDERS / f'panel_{name}_full.png'
    with bpy.context.temp_override(window=window, area=area):
        bpy.ops.screen.screenshot_area(filepath=str(path))
    # Keep the sidebar only; the screenshot covers the whole 3D View area.
    image = bpy.data.images.load(str(path))
    state.setdefault('regions', {})[name] = (region.x - area.x, region.y - area.y, region.width, region.height,
                                             area.width, area.height)
    (RENDERS / f'panel_{name}.txt').write_text(' '.join(map(str, state['regions'][name])), encoding='utf-8')
    bpy.data.images.remove(image)
    return .5


bpy.context.preferences.view.show_splash = False
grag.register()
# The panels start closed; open them for the screenshots.
grag_panels = {name: getattr(bpy.types, idname) for name, idname in PANELS.items()}
for cls in grag_panels.values():
    bpy.utils.unregister_class(cls)
    cls.bl_options = set()
    bpy.utils.register_class(cls)
RENDERS.mkdir(parents=True, exist_ok=True)
bpy.app.timers.register(tick, first_interval=1.0)
