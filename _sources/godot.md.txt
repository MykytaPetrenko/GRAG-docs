# Godot

## Export for Godot

**Export for Godot** writes `<name>.glb` and `<name>.godot.json` from the asset's origin, always in the closed pose; opening angles in Blender are only a preview. The parts are at the top of the GLB scene with no node for the asset itself: Godot's **Import → Root Type** chooses the root type. The manifest, schema `grag_asset/1`, describes the collision shapes and the moving bodies in Godot coordinates; the [GRAG add-on for Godot](#the-grag-add-on-for-godot) builds them on import. Keep both files together and reimport the GLB after updating either one.

Every export option is on the panel and saved with the asset, so the export dialogs ask only for the destination, `//<name>.glb` or `//<name>.obj` by default, and **Overwrite Existing Files** (off by default). Nodes, meshes and OBJ objects use the part names without Blender's numeric suffixes, so `Door Leaf`, not `Door Leaf.001`. Exports work on copies and never change the scene.


## The GRAG add-on for Godot

`addons/grag` is the Godot 4 counterpart of the GRAG Blender extension. When a
GLB exported by **Export for Godot** is imported, the add-on reads the
`<name>.godot.json` manifest next to it. It then adds the collision shapes and
turns door leaves, window sashes and panes of glass into physics bodies. GLB
files without a manifest are left alone.

## Install

1. Copy the `addons/grag` folder that comes with GRAG into the Godot project's `addons` folder.
2. Enable **GRAG** in **Project → Project Settings → Plugins**.
3. Put each `.glb` and its `.godot.json` in the same folder of the project. If
   the GLB was imported before the plugin was enabled, reimport it.

No import script is needed. Optionally set **Import → Root Type** to
`StaticBody3D` for the GLB. The root then carries the fixed collision shapes
itself; otherwise they go into a `StaticCollision` child.

## What the import builds

```text
Door                         Node3D, or StaticBody3D with Root Type
├── DoorMesh                 MeshInstance3D from the GLB
├── StaticCollision          StaticBody3D for the root shapes (only without a body root)
│   ├── JambLeftCollision    CollisionShape3D
│   └── …
└── PrimaryLeafPivot         AnimatableBody3D, closed pose
    ├── PrimaryLeafPivotMesh
    └── PrimaryLeafCollision
```

- A body with a `motion` (door leaf, window sash) becomes an
  `AnimatableBody3D`; a fixed body (a pane of glass) becomes a `StaticBody3D`.
  The existing node from the GLB is replaced, so its meshes stay in place. A body
  without visual parts, such as a pane, is created at the manifest `origin`.
- Each body keeps the metadata `grag_body_id`, `grag_body_kind` (`leaf`,
  `sash`, `glass`) and, for moving bodies, `grag_motion`.
- The scene root gets `grag_asset` metadata with the asset type and the
  number of bodies and shapes, which the dock and CLI use to check the import.

Assets are always exported in the closed pose. `grag_motion` describes the hinge:

| Key | Meaning |
| --- | --- |
| `type` | `hinge` |
| `axis` | Rotation axis in the body's local space, `[0, 1, 0]` for doors and windows |
| `closed_degrees` | `0`, the exported pose |
| `open_degrees` | Fully open angle; the sign gives the direction |
| `requires_open` | Optional `grag_body_id` that must open first, as in a French window pair |

Rotate the body around `axis` between the two angles in game code, or pin it to
the parent with a `HingeJoint3D` and replace it with a `RigidBody3D` for
force-driven motion.

## Dock

The **GRAG** dock lists every manifest in the project with its asset type and
the number of bodies and shapes. A red mark lists the problems: a missing GLB, an
invalid manifest, a scene imported without the plugin, or an import older than
the manifest. **Reimport All** reimports every GRAG GLB. Double-click an entry to
open the scene.

## Command line

The same checks run without the editor, with short output for scripts and agents:

```text
godot --headless --path <project> --import
godot --headless --path <project> --script res://addons/grag/cli.gd -- check
godot --headless --path <project> --script res://addons/grag/cli.gd -- check --json res://doors/door.glb
godot --headless --path <project> --script res://addons/grag/cli.gd -- list
```

`check` prints `OK` or `FAIL` per asset, the problems under each failure, and a
summary line. It exits with code 1 when an asset fails. `list` reads only the
manifests. `--json` prints one JSON array instead. Run `--import` first, so the
scenes are imported with the plugin enabled.

## Manifest `grag_asset/1`

Blender writes the manifest from the collision objects in the asset's
**Collisions** collection, so hand edits to those objects reach Godot. All values
are in metres in Godot axes: X right, Y up, and Blender's −Y becomes +Z.

```json
{
  "schema": "grag_asset/1",
  "asset": "door",
  "scene": "door.glb",
  "coordinates": "godot_y_up_meters",
  "root_shapes": [
    {"name": "JambLeftCollision", "type": "BoxShape3D", "size": [0.032, 2.43, 0.34],
     "origin": [-0.494, 1.215, 0.07], "basis": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
  ],
  "bodies": [
    {"id": "PrimaryLeafPivot", "kind": "leaf", "origin": [0.4765, 0.0, -0.1055],
     "motion": {"type": "hinge", "axis": [0, 1, 0], "closed_degrees": 0, "open_degrees": -90},
     "shapes": [], "bodies": []}
  ]
}
```

| Shape `type` | Fields |
| --- | --- |
| `BoxShape3D` | `size`, `origin` and `basis` (three column vectors) of the shape node |
| `ConvexPolygonShape3D` | `points` in the space of the owning body |
| `ConcavePolygonShape3D` | `faces`, three points per triangle, in the space of the owning body |

Shapes in `root_shapes` belong to the asset root. Each entry in `bodies` holds the
shapes of that body and its nested `bodies`, such as a pane of glass on an opening
sash. A body's `origin` is relative to its parent body in the closed pose. Names
are unique within the manifest and become node names.
