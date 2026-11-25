# Doors

## Creating doors

1. Choose the **Door Style**: **Flush Wood**, **Horizontal Slats**, **Steel Panel**, **Original Four-Panel** (the leaf from `door.blend`, fitted to the opening), **Rounded Four-Panel**, **Classic Three-Panel** or **Modern Two-Panel**. Then choose the handle and hinge side.
2. For a standalone door, set the rough opening in **Opening and Walls** and press **Build at Cursor**. The cursor marks the centre of the opening at floor level.
3. To place a door in a Room Builder plan, select a door opening in **Rooms → Openings** and press **Build in Room Opening**. The door takes the width, height, position, angle, finished floor level and the wall depth on both sides. After the plan changes, select the door and press **Sync to Room Opening**.

Built-in presets: **Interior Flush Door**, **Classic Four-Panel Door**, **Steel Utility Door** and **Glazed Double Entrance**.

## Parameters

**Opening and Walls.** **Interior Wall Depth** and **Exterior / Opposite Wall Depth** are the distances from the plan contour to the two wall faces; between rooms the second is the neighbouring room's wall. The backs of the casings lie on these faces, and **Casing Overlap** sets how far they cover the wall. **Opening Bottom** and **Finished Floor Height** are measured from the level datum. The frame and casing start from the higher of the two, and **Floor Gap** lifts the leaf above it. Between two rooms, the higher finished floor applies so the leaf clears both.

**Frame and Leaf.** **Jamb Width**, **Casing Thickness**, **Leaf Thickness** and **Jamb Clearance** shape the frame and leaf. When the profile leaves room behind the leaf, the jamb and the dividers get a stop rebate. **Horizontal Slats** use **Slats** and **Slat Gap**. In the panelled styles, **Original Four-Panel** and **Steel Panel** mark the profile breaks as sharp; **Rounded Four-Panel** rounds the panel corners with **Panel Corner Radius** and **Panel Corner Segments**, sharp along the profile outlines and smooth across the arcs; **Classic Three-Panel** has smooth profile transitions set by **Bevel Width** and **Bevel Segments**; **Modern Two-Panel** has a tall upper and a shorter lower panel.

**Hardware.** **Handle Style** offers **Square Lever**, **Round Knob**, **Return Lever**, **Original Lever** (the lever and plate from `door.blend`), **Swept Lever**, **Blade Lever**, **Turned Lever**, **Wave Lever** and **None**. **Long Backplate** extends the mounting plate in the handle's style and adds a lock; **Lock Style** is **Key / Key**, **Key / Thumbturn** or **Privacy**, which has a thumbturn on one side and a slot for a flat screwdriver on the other. **Thumbturn Side** chooses the thumbturn's side. **Handle Height**, **Hardware Finish** and **Hinges** complete the hardware.

**Opening Layout.** **Double Leaf** adds a second leaf; **Secondary Bay Width** is its share of the door bay after the frame and gaps. Each leaf has its own pivot and **Swing** angle, a preview only. **Secondary Handle** adds a handle to the second leaf; by default it is passive and carries the strike plate for the main leaf's latch. **Left Section**, **Right Section** and **Transom** can be **Solid** panels or **Glazed** frames. Side section widths come out of the opening width: a 2 m opening with two 0.5 m sections leaves a 1 m door bay. The transom spans the whole width and its height comes out of the opening height. **Divider Width** and **Divider Depth** size the dividers. Each glazed section has its own **Glass Frame Width**; **Left Bottom Offset** and **Right Bottom Offset** raise the glass and fill the bottom with a solid panel; **Transom Columns** splits the transom into equal parts. Each section is **Simple** (a plain panel or glazed frame) or **Match Door**, which aligns slat joints, panels and recesses with the main leaf. A solid transom has vertical slats, as many as its width fits at the leaf's slat spacing; a panelled one has one row of rectangular panels.

**Mesh Detail.** **Cylinder Sides**, **Segments per Handle Bend**, **Bevel Width** and **Bevel Segments** (0 turns procedural bevels off). The reference leaf and handle keep their topology, UVs and sharp edges. The panel shows the face count.

## Axes and origin

The origin is the centre of the rough opening at floor level, on the wall's plan contour. X runs along the wall, +Y points into the room and +Z up, in metres. **Hinge Side** is seen looking toward +Y. Each leaf turns around its **Door Hinge Pivot** empty; the handles turn around their spindles, stored in `grag_handle_origin`. In Godot, +Y is up and the room side is −Z.

## UV and texturing

The generator marks seams on the diagonal joints of the frame, casings and glass frames, between rails, stiles and panels, and the grain direction of each wooden face. **Texture Grain** chooses whether wood grain runs along **Horizontal (U)** or **Vertical (V)** in the texture; the atlas keeps the islands' rotation so the grain stays aligned. In **Original Four-Panel** and **Rounded Four-Panel** the centre stile has two islands on each face and every rail is one island from stile to stile. The authored UVs of the reference leaf stay as **ReferenceUV**.

**Bake Groups** choose which parts bake together:

- **Bake Hinges**: **With Frame and Leaves** (default) keeps each moving hinge plate with its leaf and the pins and fixed plates with the frame; **Separate** moves every hinge part apart.
- **Bake Handle**: **With Backplate** (default) keeps the grip, backplate and lock together, apart from the leaf; **With Backplate and Leaf** bakes them in place on their leaf; **Separate** moves each one apart.
- **Bake Latch**: **Separate** (default) moves the latch and strike plate apart; **With Frame and Leaves** keeps the latch with its leaf and the strike plate with the part it is mounted on, the frame or, in a double door, the second leaf.

Doors have no helper geometry for ambient occlusion.

## Collisions

| Part | Switch | Shapes |
| --- | --- | --- |
| Frame | **Frame**, on | Three boxes through the wall depth (`JambLeft`, `JambRight`, `JambHead`) and three narrow stop boxes behind the leaf (`JambStop…`). There are no stops when the leaf leaves no room behind it. |
| Side sections and transom | **Fixed Sections**, on | Boxes for each divider, its stop and its infill at leaf depth (`LeftDivider…`, `LeftSection…`, `TopSection…`). Glazed infills have collisions too. |
| Leaves | **Leaves**, on | One box per leaf (`PrimaryLeafCollision`, `SecondaryLeafCollision`) in its pivot's space. It matches the closed leaf and turns with it. |
| Casings | **Casing**, off | Three thin boxes on each wall face (`InsideCasing…`, `OutsideCasing…`). |

All shapes are boxes. Handles, hinges, the latch and the strike plate have no collisions. The gaps around the leaf stay open, so a leaf swings from closed to 90° without touching the frame, sections or casings. Without **Generate Collisions** the manifest still has the leaf bodies and their motion, but no shapes.

## Export for Godot

With **Merge**, the scene and the GLB hold these meshes:

| Mesh | Parent | Parts |
| --- | --- | --- |
| `DoorMesh` | Door root | Frame, casings, dividers, side sections, transom, fixed hinge parts and pins, strike plate (on the second leaf in a double door) |
| `PrimaryLeafPivotMesh` | `Door Hinge Pivot` | Leaf, moving hinge plates, latch, backplates, lock |
| `PrimaryHandlePivotMesh` | `Door Hinge Pivot` | Handles, turning around the spindle in `grag_handle_origin` |
| `SecondaryLeafPivotMesh`, `SecondaryHandlePivotMesh` | `Secondary Door Hinge Pivot` | The same for the second leaf |

The GLB has an empty for each leaf pivot (`PrimaryLeafPivot`, `SecondaryLeafPivot`) and each handle pivot (`PrimaryHandlePivot`, `SecondaryHandlePivot`); handles turn around their local −Z. **One Material** also writes one material to the GLB. Imported in Godot:

```text
Door                         Node3D, or StaticBody3D with Root Type
├── DoorMesh                 MeshInstance3D of the fixed parts (with Merge)
├── StaticCollision          StaticBody3D for the fixed shapes
│   ├── JambLeftCollision    CollisionShape3D
│   ├── JambRightCollision
│   ├── JambHeadCollision
│   └── JambStopLeftCollision …
└── PrimaryLeafPivot         AnimatableBody3D on the hinge axis
    ├── PrimaryLeafPivotMesh
    ├── PrimaryHandlePivot
    └── PrimaryLeafCollision
```

Each leaf's `grag_motion` has `type` `hinge`, the local `axis` `[0, 1, 0]`, `closed_degrees` `0` and `open_degrees` ±90°, signed toward the room.

## Export for Substance Painter

Every part is its own mesh in both files, even when the scene is merged, and the bake groups above are moved apart along X. With **One Material** the low file has one texture set, `Door_Paint`.

## Use in a game scene

1. Place the door at the centre of the opening at floor level, with +Y toward the room. For another opening size, generate a matching door in Blender.
2. Check the imported tree and collisions: the closed leaf fills the opening and swings to its limit without touching the frame.
3. Drive the leaf body found by `grag_body_id` between `closed_degrees` and `open_degrees` around `axis`. For force-driven motion, replace the body with a `RigidBody3D` and pin it with a `HingeJoint3D` on the hinge axis. [HingeJoint3D](https://docs.godotengine.org/en/stable/classes/class_hingejoint3d.html)
