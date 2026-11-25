# Stair Railings

The **Railing System** section of the **Stairs Generator** panel builds four types of railing. This page describes each of them; the [Stairs](stairs.md) page covers the stairs themselves.

Turn on **Enable Railing**, choose the **Type** and the mounting of each side. The railing follows the flights and the inner and outer landing routes, including 90° and 180° turns in either direction. On 90° turns with a wide **Flight Gap**, the inner route follows the exposed edges of the landing at **Edge Inset**; the handrail, infill rails and landing posts share that route. Overhanging landing routes first level out from the flight slope, then turn in plan; the outgoing route levels with the next flight before it climbs, so slope and direction never change at the same fitting.

Terminology: the **handrail** is the upper member you hold; the **railing system** is the whole assembly. The thin rails below it are **infill rails**, the uprights are **posts**, their thin top connections are **handrail supports**, and the sleeves at elbows are **coupling sleeves**. Each type keeps its own section dimensions when you switch between types, and selecting any railing part opens its stairs in the panel.

## Mounting and coverage

Each side, **Inner** and **Outer**, has its own mounting and **Include Landings** switch. Inner and outer follow **Turn Direction**; the panel also shows which side is left or right.

- **None** builds nothing on that side.
- **Flight Mounted** builds the chosen type with posts and infill on the stairs.
- **Wall Mounted** builds only the handrail of the chosen type, with wall brackets and mounting plates. **Wall Clearance** is measured from the handrail surface to the wall face; bracket spacing, plate radius and bracket stem radius and sides are adjustable.

With **Include Landings** the side continues around the intermediate landings. Without it every flight has its own capped section and there is no level handrail over the landings. The two sides choose their coverage independently of their mounting.

**Preview Wall** shows wireframe guide walls on wall-mounted sides, following their coverage, with adjustable thickness and height above the handrail. The walls are viewport-only, excluded from renders and the GLB, and are helper geometry for ambient occlusion in the Painter export. The button rebuilds at once, even with **Auto Rebuild** off.

## Posts

All four types share the post layout:

- **Steps per Post** sets the interval in treads, independently of the metric spacing on landings.
- **Flight Distribution**: **Balanced Treads** spreads the posts over whole treads as evenly as possible; **Every N Steps** keeps the exact interval and leaves any remainder in the last bay. Both always include the first and last tread.
- Each landing starts and ends with a post. The post before each upper flight stands half a tread back on the landing, clear of the first riser. Without **Include Landings**, every flight behaves like the first: its posts stay on its treads.
- Landing corners normally get posts too. Nearby corner and elbow points share one post when they are within half a tread or the post's footprint; tread posts and the post before an upper flight win, so short returns never get doubled posts. Tight inner gaps may leave out extra corner posts.
- **Calculate from Steps per Post** (on by default) sets the landing spacing to the tread depth times **Steps per Post**; turn it off to enter **Landing Post Spacing**. Each straight landing span is divided into equal intervals near that length.

## Type 1 · Tubular

A round handrail with rounded elbows and coupling sleeves, round posts and continuous round infill rails.

- **Railing Height** and **Edge Inset** place the handrail centreline above the sloping stair line and landings, and inward from the stair edge.
- **Handrail Radius** and **Elbow Radius** set the main tube and its rounded elbows. Short landing segments limit the elbow size; a configuration too tight for the tube reports an error.
- **Coupling Length** and **Coupling Thickness** set the hollow sleeves at both ends of each elbow.
- **Infill Rail Count** sets the number of thin continuous rails (4 by default, 0 allowed), with their own radius and clearance above the steps. They have rounded turns and no couplings.
- **Post Radius** sets the posts. Base flange, shaft and upper collar form one closed, connected mesh per post, joined by flat ring shoulders, with no overlapping cylinders or hidden caps.
- **Support Construction** is **Separate Support**, a child mesh, or **Integral Stem**, which joins the upper collar through a flat shoulder and shares its rings. **Support Stem Radius** and **Support Stem Length** size it.
- The cylinder resolution is set per component; disabled fields show the inherited count, and **Elbow Segments** sets the bend resolution:

  | Component | Default sides | Inheritance |
  | --- | ---: | --- |
  | Handrail and coupling sleeves | 16 | Own setting |
  | Infill rails | 8 | Own setting |
  | Posts, with flange and collar | 16 | **Same as Handrail**, on by default |
  | Separate handrail supports | 8 | **Same as Post**, off by default |
  | Integral support stems | Post count | Always follows the posts |

## Type 2 · Rectangular

Square posts, a rectangular handrail and straight round infill rails. Every change of direction has one fixed, one-piece corner connector for the handrail and one for each infill rail, with no hinged parts; straight members are trimmed at the fittings instead of running through the corner.

- **Handrail Width** and **Handrail Thickness** set the handrail section, 50 × 25 mm by default.
- **Square Post Width** sets the posts, 40 mm by default. Flange, shaft and collar stay one connected mesh with flat shoulders.
- **Corner Connector Length** sets the target length of each fitting leg; it adapts to the section size and the space available, and impossible combinations keep the previous geometry and report an error.
- **Connector Allowance** adds material around the member's section at the fitting, 2 mm by default.
- Infill rail radius, sides, count and clearance, post spacing and the inner and outer controls work as in Type 1. Integral stems are square and share the post topology through a flat shoulder.

## Type 3 · Vertical Balusters

A metal balustrade with vertical rectangular bars, a continuous sloping bottom rail, square posts with integral base plates and a contrasting rectangular handrail. The handrail and bottom rail share mitre rings at direction changes instead of separate elbows. Bars stay vertical and their ends are cut to the slope of the rails.

A continuous metal **top rail** sits flush beneath the handrail, including slopes and landing turns. It shares **Bottom Rail Width** and has its own **Top Rail Thickness**, 15 mm by default, less than the 35 mm bottom rail. Bars end at its underside and the wider posts reach its top, directly beneath the handrail. Wall-mounted Type 3 handrails have the top rail too, with the brackets meeting its underside.

The **Vertical Baluster Railing** has exactly two material slots, stored with the stairs and kept through rebuilds, type and mounting switches, copies and saving:

1. **Metal**: posts, base plates, bars, bottom and top rail; dark powder-coated metal by default.
2. **Handrail**: the handrail; warm timber by default.

Set them in **Materials · 2 Slots** or in the railing's ordinary material slots; edits made with **Auto Rebuild** off survive saving.

**Baluster Spacing** is the fixed distance between neighbouring bars. Each bay between posts gets a centred group of bars at that spacing; the two gaps at the posts may differ. By default the group has one bar fewer than fits; **Dense Infill** adds it back, for smaller gaps at the posts. **Baluster Width** and **Baluster Depth** set the bar section across and along the railing, and **Bottom Clearance** keeps the bottom rail above the step noses.

**Handrail Boards and Bevels** offers **Top Edge Bevel**, **Bottom Edge Bevel** and **Start/End Cap Bevel**, each with its own width and a shared segment count and profile. End bevels follow the edge bevels: with only the top one, the bottom edge of each end stays square, and the other way round; with neither or both, the whole end outline is bevelled. Widths are clamped below half the smaller side of the handrail section. With smooth shading, the whole handrail shades smoothly and only unrounded corners and end outlines are sharp. **Split into Boards** makes separate closed timber pieces at each change of direction, with long runs divided by **Maximum Board Length** and **Joint Gap** (3 mm by default) measured across the joint, mitres included. The metal rails stay continuous.

## Type 4 · Metal Balusters

A flat metal handrail over the same bars and square posts as Type 3, without a timber handrail or top rail. The railing has one **Metal** material slot, shared with its posts, bottom rail and wall brackets.

The defaults are a 50 × 12 mm handrail, 40 mm posts, a 30 mm bottom rail and 16 mm bars; the widths must grow in that order from bar to bottom rail to post to handrail. Posts and bars meet the handrail's underside with cuts matching the slope.

Every open handrail end turns down in a half-circle return. **Ends and Extensions → End Return Radius** sets its centreline radius, 40 mm by default, larger than half the handrail thickness, and **End Return Segments** its resolution, 12 by default. The return is fitted to the vertical boundary at the first and last tread, allowing for the slope and the arc's thickness. With **Include Landings**, the handrail continues through the landing mitres and has returns only at its two open ends; without it, every flight is a separate section with returns at both ends. Wall-mounted sections use the same returned handrail.

## Ends and extensions

In every type, the lower members stop at the actual end posts, with ends cut vertically through their centres even on slopes, and only the handrail extends past the first and last post. Bars stay between the posts, and a section with a single post has no bottom rail or bars.

For Types 1–3, **Handrail Start Extension** and **Handrail End Extension** move the open handrail ends beyond the route, and **Infill Start Setback** and **Infill End Setback** shorten the infill rails (Types 1 and 2) or the metal frame (Type 3, labelled **Metal Start Setback** and **Metal End Setback**). Each defaults to 50 mm and follows the local slope or level direction. With flight-only coverage they apply to each flight's free ends, while landing corners keep their continuous route. Type 4 fits its ends automatically.
