"""Shared studio for the documentation renders: GRAG from the sibling folder, lights and a camera.

Run the media scripts with Blender 5.2 in background mode, for example:

    blender --background --factory-startup --python tools/render_doors.py

Renders have a transparent background; `compose.py` puts them on the page colour.
"""

from math import atan, radians, sin
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

DOCS = Path(__file__).resolve().parents[1]
GRAG = DOCS.parent / 'GRAG'
BUILDER = DOCS.parent / 'BlenderBuilder'
RENDERS = DOCS / 'tools' / '_renders'
sys.path[:0] = [str(GRAG)]

import grag  # noqa: E402


def reset():
    """An empty scene with GRAG registered, EEVEE, a neutral view transform and soft studio light."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not hasattr(bpy.types.Scene, 'grag_door'):
        grag.register()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.eevee.taa_render_samples = 64
    world = bpy.data.worlds.new('Studio')
    world.use_nodes = True
    background = world.node_tree.nodes['Background']
    background.inputs['Color'].default_value = (.5, .52, .55, 1)
    background.inputs['Strength'].default_value = .35
    scene.world = world
    for name, location, energy, size in (('Key', (3.5, 4.5, 4.0), 350, 3.0), ('Fill', (-4.5, 3.0, 2.5), 90, 4.0),
                                         ('Rim', (0.0, -5.0, 4.0), 150, 3.0)):
        light = bpy.data.lights.new(name, 'AREA')
        light.energy = energy
        light.size = size
        obj = bpy.data.objects.new(name, light)
        scene.collection.objects.link(obj)
        obj.location = location
        look_at(obj, Vector((0, 0, 1)))
    return scene


def wall(width, height, back, front, margin=.9, top=.6, bottom=0, name='Wall'):
    """A plain wall around a rough opening centred on X, from Y = -back to Y = front.

    `bottom` adds wall below the opening, as under a window.
    """
    material = bpy.data.materials.get('Docs Wall') or bpy.data.materials.new('Docs Wall')
    material.diffuse_color = (.62, .62, .6, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (.62, .62, .6, 1)
    shader.inputs['Roughness'].default_value = .9
    half = width / 2
    boxes = [(-half - margin, -half, -bottom, height + top), (half, half + margin, -bottom, height + top),
             (-half, half, height, height + top)]
    if bottom:
        boxes.append((-half, half, -bottom, 0))
    mesh = bpy.data.meshes.new(name)
    vertices, faces = [], []
    for x0, x1, z0, z1 in boxes:
        start = len(vertices)
        vertices += [(x, y, z) for x in (x0, x1) for y in (-back, front) for z in (z0, z1)]
        faces += [tuple(start + i for i in face) for face in
                  ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))]
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


def camera(location, target, lens=50, ortho_scale=None):
    scene = bpy.context.scene
    data = bpy.data.cameras.new('Camera')
    data.lens = lens
    if ortho_scale:
        data.type = 'ORTHO'
        data.ortho_scale = ortho_scale
    obj = bpy.data.objects.new('Camera', data)
    scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, Vector(target))
    scene.camera = obj
    return obj


def bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (Vector([min(p[i] for p in points) for i in range(3)]),
            Vector([max(p[i] for p in points) for i in range(3)]))


def asset_meshes(root, collisions=False):
    objects = [root, *root.children_recursive]
    return [obj for obj in objects if obj.type == 'MESH' and not obj.hide_render
            and (collisions or not obj.get('grag_collision'))]


def frame(objects, direction=(1, 2.2, .9), lens=60, margin=1.08, width=900, height=900, target_offset=(0, 0, 0)):
    """A camera looking along -direction whose view fits the objects' bounding boxes with a small margin."""
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = width, height
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    low, high = bounds(objects)
    center = (low + high) / 2 + Vector(target_offset)
    direction = Vector(direction).normalized()
    distance = (high - low).length * 2
    obj = camera(center + direction * distance, center, lens=lens)
    for _ in range(6):
        bpy.context.view_layer.update()
        points = [world_to_camera_view(scene, obj, corner) for corner in corners]
        # Distance from the frame centre, as a share of the half frame on each axis.
        extent = max(max(abs(point.x - .5), abs(point.y - .5)) for point in points) * 2
        distance *= extent * margin
        obj.location = center + direction * distance
    return obj


def clear():
    """Remove every object except lights, keeping GRAG registered."""
    for obj in list(bpy.data.objects):
        if obj.type != 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def render(name, width=None, height=None):
    scene = bpy.context.scene
    if width:
        scene.render.resolution_x, scene.render.resolution_y = width, height or width
    scene.render.resolution_percentage = 100
    RENDERS.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(RENDERS / f'{name}.png')
    bpy.ops.render.render(write_still=True)
    return RENDERS / f'{name}.png'


def deselect():
    context = bpy.context
    context.view_layer.objects.active = None
    for obj in context.selected_objects:
        obj.select_set(False)


# Collision colours by the engine body a shape belongs to: fixed, moving, separate glass.
BODY_COLORS = {'': (.05, .85, .2), 'leaf': (1.0, .45, .02), 'sash': (1.0, .45, .02), 'glass': (.02, .45, 1.0)}


def _body_kind(obj):
    parent = obj.parent
    while parent is not None and not parent.get('grag_asset'):
        if parent.get('grag_body_id'):
            return parent.get('grag_body_kind', '')
        parent = parent.parent
    return ''


def show_collisions(root, settings, visible=True, ghost=True):
    """Collision shapes as bold coloured solids, and the asset as a faint ghost around them."""
    settings.show_collisions = visible
    settings.show_visuals = True
    ghost_shader = ghost_material()
    for obj in root.children_recursive:
        if obj.type == 'MESH' and obj.get('grag_collision'):
            obj.hide_render = not visible
            fill, edge = _collision_materials(_body_kind(obj))
            obj.data.materials.clear()
            obj.data.materials.append(fill)
            obj.data.materials.append(edge)
            if not any(modifier.type == 'WIREFRAME' for modifier in obj.modifiers):
                wire = obj.modifiers.new('Wire', 'WIREFRAME')
                wire.thickness = .006
                wire.use_replace = False
                wire.material_offset = 1
    if ghost:
        for obj in [root, *root.children_recursive] if root.type == 'MESH' else root.children_recursive:
            if obj.type == 'MESH' and not obj.get('grag_collision'):
                obj['docs_materials'] = [slot.material.name if slot.material else '' for slot in obj.material_slots]
                for slot in obj.material_slots:
                    slot.link = 'OBJECT'
                    slot.material = ghost_shader


def ghost_material():
    material = bpy.data.materials.get('Docs Ghost')
    if material is None:
        material = bpy.data.materials.new('Docs Ghost')
        material.use_nodes = True
        material.surface_render_method = 'BLENDED'
        material.use_backface_culling = True
        shader = material.node_tree.nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value = (.8, .8, .8, 1)
        shader.inputs['Alpha'].default_value = .16
        shader.inputs['Roughness'].default_value = .8
    return material


def _collision_materials(kind):
    color = BODY_COLORS.get(kind, BODY_COLORS[''])
    fill = bpy.data.materials.get(f'Docs Collision Fill {kind}')
    if fill is None:
        fill = bpy.data.materials.new(f'Docs Collision Fill {kind}')
        fill.use_nodes = True
        fill.surface_render_method = 'BLENDED'
        shader = fill.node_tree.nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value = (*color, 1)
        shader.inputs['Emission Color'].default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = .25
        shader.inputs['Alpha'].default_value = .8
        shader.inputs['Roughness'].default_value = .5
    edge = bpy.data.materials.get(f'Docs Collision Edge {kind}')
    if edge is None:
        edge = bpy.data.materials.new(f'Docs Collision Edge {kind}')
        edge.use_nodes = True
        nodes = edge.node_tree.nodes
        nodes.clear()
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (*(value * .35 for value in color), 1)
        emission.inputs['Strength'].default_value = 1.0
        output = nodes.new('ShaderNodeOutputMaterial')
        edge.node_tree.links.new(emission.outputs[0], output.inputs[0])
    return fill, edge


DEG = radians
