"""Texturing figures: the draft atlas on a door and the Painter bake meshes."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import RENDERS, asset_meshes, clear, frame, render, reset  # noqa: E402

ROOM_SIDE = (.9, 2.4, .55)


def door(style='CLASSIC_THREE', **settings):
    clear()
    assert bpy.ops.grag.door_build(action='NEW') == {'FINISHED'}
    root = bpy.context.object
    root.grag_door.style = style
    root.grag_door.one_material = True
    for key, value in settings.items():
        setattr(root.grag_door, key, value)
    assert root.grag_door.last_error == '', root.grag_door.last_error
    return root


def checker():
    """The door with a UV grid on its atlas, and the atlas itself as polygons for compose.py."""
    root = door()
    image = bpy.data.images.new('Docs UV Grid', 512, 512)
    # A calm checker: island scale and orientation show without colour noise.
    cells, pixels = 64, []
    for y in range(512):
        for x in range(512):
            light = ((x // (512 // cells)) + (y // (512 // cells))) % 2
            line = False
            value = .18 if line else (.62 if light else .45)
            pixels += [value * 1.05, value, value * .92, 1]
    image.pixels = pixels
    material = bpy.data.materials.new('Docs UV Grid')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    texture.interpolation = 'Closest'
    mapping = nodes.new('ShaderNodeUVMap')
    mapping.uv_map = 'UVMap'
    material.node_tree.links.new(mapping.outputs[0], texture.inputs[0])
    material.node_tree.links.new(texture.outputs[0], nodes['Principled BSDF'].inputs['Base Color'])
    polygons = []
    for obj in asset_meshes(root):
        for slot in obj.material_slots:
            slot.link = 'OBJECT'
            slot.material = material
        layer = obj.data.uv_layers.get('UVMap')
        if layer is None:
            continue
        polygons += [[tuple(layer.data[index].uv) for index in face.loop_indices] for face in obj.data.polygons]
    (RENDERS / 'door_atlas.json').write_text(json.dumps(polygons), encoding='utf-8')
    frame(asset_meshes(root), ROOM_SIDE, width=560, height=900)
    render('door_uv_grid')


def painter():
    """The high bake file: each source material in its ID colour, bake groups moved apart."""
    root = door('SLATS', handle_finish='BLACK', long_backplate=True, one_material=False)
    path = RENDERS / 'painter' / 'door.obj'
    path.parent.mkdir(parents=True, exist_ok=True)
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    assert bpy.ops.grag.door_export_painter(filepath=str(path), overwrite=True) == {'FINISHED'}
    clear()
    bpy.ops.wm.obj_import(filepath=str(path.with_name('door_high.obj')), forward_axis='NEGATIVE_Z', up_axis='Y')
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in meshes:
        for slot in obj.material_slots:
            if slot.material:
                # OBJ materials keep the ID colour in Kd; show it as the surface colour.
                shader = slot.material.node_tree.nodes.get('Principled BSDF')
                if shader:
                    shader.inputs['Roughness'].default_value = .7
    frame(meshes, (.15, 2.0, .35), lens=50, width=1600, height=900)
    render('door_painter_high')


reset()
JOBS = {'checker': checker, 'painter': painter}
for job in (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else JOBS):
    JOBS[job]()
