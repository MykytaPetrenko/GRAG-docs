"""Stair figures: presets, railing types, mounting, tread finish, collisions and the hero stairs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy  # noqa: E402

from studio import (asset_meshes, clear, concrete, frame, ghost_material, marble, render, repaint,  # noqa: E402
                    reset, show_collisions, veneer)
from grag.services.presets import builtin_preset  # noqa: E402

PRESETS = ('Straight Concrete Stairs', 'L-Turn with Timber Balusters', 'U-Turn with Tubular Railing',
           'Metal Balusters with Tread Plates')
TYPES = ('TYPE_1', 'TYPE_2', 'TYPE_3', 'TYPE_4')
VIEW = (1.25, 1.35, 1.0)


def stairs(preset=None, **settings):
    clear()
    template = bpy.context.scene.grag_stairs
    if preset:
        assert bpy.ops.grag.apply_preset(asset='stairs', filepath=builtin_preset('stairs', preset)) == {'FINISHED'}
    assert bpy.ops.grag.stairs_build() == {'FINISHED'}
    root = bpy.context.object
    root.grag_stairs.auto_rebuild = False
    for key, value in settings.items():
        setattr(root.grag_stairs, key, value)
    root.grag_stairs.auto_rebuild = True
    assert bpy.ops.grag.stairs_rebuild() == {'FINISHED'}, root.grag_stairs.last_error
    # Presets change the scene template; the next figure starts from the defaults again.
    for prop in template.bl_rna.properties:
        if not prop.is_readonly and prop.identifier not in {'rna_type', 'name'}:
            template.property_unset(prop.identifier)
    return root


def presets():
    for preset in PRESETS:
        root = stairs(preset)
        frame(asset_meshes(root), VIEW, width=900, height=900)
        render('stairs_preset_' + preset.split()[0].lower().replace('-', '_'))


def railings():
    """Each railing type on a U-turn, framed on the landing where its fittings show."""
    for rail_type in TYPES:
        root = stairs(flight_count=2, turn_angle='180', step_count=6, width=1.0, rail_enabled=True,
                      rail_type=rail_type, rail_inner_mount='NONE', rail_outer_mount='FLIGHT')
        railing = [obj for obj in asset_meshes(root) if obj != root and obj.get('grag_part') != 'tread_plates']
        frame(railing, (.35, -1.2, .75), lens=60, margin=1.02, width=800, height=800)
        render(f'stairs_railing_{rail_type.lower()}')


def mounting():
    variants = {'flight': dict(rail_inner_mount='FLIGHT', rail_outer_mount='FLIGHT'),
                'wall': dict(rail_inner_mount='FLIGHT', rail_outer_mount='WALL', rail_preview_walls=True)}
    for name, settings in variants.items():
        root = stairs(flight_count=2, step_count=6, rail_enabled=True, rail_type='TYPE_3', **settings)
        # Preview walls are viewport-only; show them as a faint ghost for the figure.
        walls = [obj for obj in root.children if obj.get('grag_part') == 'preview_walls']
        for wall in walls:
            wall.hide_render = False
            wall.data.materials.clear()
            wall.data.materials.append(ghost_material())
        frame(asset_meshes(root), VIEW, width=900, height=900)
        render(f'stairs_mounting_{name}')


def finish():
    for name, value in (('original', 'ORIGINAL'), ('plates', 'PLATES')):
        root = stairs(step_count=5, width=1.0, tread_finish=value, use_top_bevel=True, use_bottom_bevel=True)
        repaint(root, {'Concrete': concrete(), 'Tread Finish': marble()})
        frame(asset_meshes(root), (1.6, .9, .8), lens=70, width=800, height=600)
        render(f'stairs_finish_{name}')


def collisions():
    for profile in ('STEPS', 'RAMP'):
        root = stairs('U-Turn with Tubular Railing', collision_profile=profile)
        show_collisions(root, root.grag_stairs)
        frame(asset_meshes(root, collisions=True), VIEW, width=900, height=900)
        render(f'stairs_collisions_{profile.lower()}')


def hero():
    """The L-turn with marble tread plates on a concrete body and walnut handrails."""
    root = stairs('L-Turn with Timber Balusters', tread_finish='PLATES')
    # Stair atlases lay the grain along V; the veneer image has it along U.
    repaint(root, {'Concrete': concrete(), 'Tread Finish': marble(), 'Timber Handrail': veneer('WALNUT', rotate=True)})
    frame(asset_meshes(root), VIEW, width=900, height=900)
    render('hero_stairs')
    # The same stairs from the other side, for the texturing page.
    frame(asset_meshes(root), (-1.1, 1.5, 1.2), width=900, height=900)
    render('stairs_ready')


reset()
JOBS = {'presets': presets, 'railings': railings, 'mounting': mounting, 'finish': finish,
        'collisions': collisions, 'hero': hero}
for job in (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else JOBS):
    JOBS[job]()
