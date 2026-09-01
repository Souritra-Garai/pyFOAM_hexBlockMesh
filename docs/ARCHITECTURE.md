# Architecture Reference

Detailed reference for how `pyFOAM_hexBlockMesh`'s core primitives fit together. `CLAUDE.md`
has the condensed version and the current work-in-progress status; this file is the fuller
walkthrough, meant as onboarding context before diving into a specific extension (e.g. the
Schneider expansion layer — see `SchneiderExpansion.md` once that exists).

## The primitive: `HexBlock`

A `HexBlock(n0, n1, n2)` is a structured grid of `n0 x n1 x n2` cells. It owns three arrays:

- `cell_ID` — shape `(n0, n1, n2)`, one entry per cell.
- `point_ID` — shape `(n0+1, n1+1, n2+1)`, one entry per grid point (`n` cells along an axis
  span `n+1` bounding points).
- `point_coordinates` — shape `(n0+1, n1+1, n2+1, 3)`, floats.

All three start filled with `-1` (IDs) or `NaN` (coordinates) and get filled in later.
`setPointCoordinates()` validates right-handedness via `checkCoordinatesOrientation`.
`setCellIDs(start_ID)` assigns consecutive IDs via `np.arange(...).reshape(shape, order='F')`
— **Fortran order** (fastest-varying axis 0, then 1, then 2) shows up everywhere IDs are
assigned, including point IDs later.

## The coordinate system (`geometry_utils/HexBlockMap.py`)

Everything about "which vertex/edge/face is this" is answered through a small shared
abstraction, not hardcoded index arithmetic scattered through the codebase:

- `vertex_map` — 8 vertices -> `(0/-1, 0/-1, 0/-1)` array-index tuples. This is the Rosetta
  stone; every other lookup (edges, faces) derives from it.
- `vertex_connectivity` — `(v0, v1) -> axis`, meaning "walking from v0 to v1 moves along
  `axis` in the positive direction." Looked up both ways (swapped tuple => negative
  orientation) so any edge can be queried regardless of which vertex is named first.
- `hex_face_vertices` — 6 canonical CCW-ordered 4-tuples, one per face, normal pointing
  outward.
- `face_axes` — for a face normal along `axis`, the two in-plane axes (ordered so their
  cross product gives that outward normal).
- `face_vertex_slices` — turns a 2D grid of point IDs into the 4 per-cell face corners in CCW
  order; this is what produces a whole plane of quads from one array in one shot.

`geometry_utils/HexBlockVertices.py` builds on this:

- `Slice3D` — an `(axes, slices)` pair, reorderable via `np.moveaxis` so "axis 0/1/2 of the
  slice" doesn't have to match "axis 0/1/2 of the underlying array".
- `AxisProperties(v0, v1)` — dimension + orientation of an edge; gives both a full slice and
  an **interior** slice (endpoints excluded).
- `SurfaceProperties(vertices)` — two `AxisProperties` for the face's in-plane axes, plus the
  constant (normal) axis/index.
- `getEdgeInteriorSlice`, `getSurfaceInteriorSlice` — exclude vertices/edges; used for ID
  assignment, since those must not double-count boundary points already assigned elsewhere.
- `getSurfaceCompleteSlice` — includes vertices/edges; used for coordinate comparison and
  face matching.

`geometry_utils/HexBlockFaces.py` reuses the same `SurfaceProperties`/`AxisProperties`
machinery to build `FaceSlices` (owner/neighbor/vertices triples), producing whole
`NDFaceCollection`s for a block's boundary face (`getSurfaceFaces`) or its interior faces
along one axis (`getInteriorFaces`, owner = cell at `i`, neighbour = cell at `i+1`).

**The pattern to carry forward**: one set of vertex/edge/axis definitions, reused via
composition for vertex IDs, edge IDs, face IDs, face geometry, and face-to-face matching —
rather than reinventing index arithmetic per feature.

## Connecting blocks (`ConnectInfo`, `ConnectedHexCollection`)

`connectHexBlocks(id0, id1, fv0, fv1)` builds a `ConnectInfo`, which normalizes
`face_vertices_0` to canonical `hex_face_vertices` order and remaps `face_vertices_1`
correspondingly (`mapVertices`) so **index j in each tuple refers to the same physical
vertex** on both sides. It then asserts `isValid()` — the two faces' complete coordinate
slices must match — before the connection is accepted.

**ID assignment cascade** (`ConnectedHexCollection.assignPointIDs`), strictly ordered because
each stage assumes the previous is complete:

1. `assignCellIDs` — each block's cells get consecutive IDs, block by block.
2. Vertices — each `ConnectInfo.assignVertexPointIDs` visits its 4 shared vertices: new ID
   if neither side is set, propagate if one side is set, assert-equal if both are set. Any
   vertex still unset afterwards (unshared) gets a fresh ID.
3. Edges — same three-way logic per shared edge, then unshared edges.
4. Faces (`assignFacePointIDs`) — shared faces must be entirely unset on both sides (no
   partial-match case), then unshared faces get fresh IDs.
5. `setInternalPointIDs` — everything else (each block's own interior volume) gets
   consecutive IDs.

This vertex -> edge -> face -> interior order is why interior corners shared by 4 blocks must
be connected in **spanning-tree order** — a corner touched by 4 blocks is visited once per
`ConnectInfo`; connecting in a cycle-closing order too early risks a conflict where two
different paths would produce different IDs for what should be a single shared point/edge.

`getFaces()` collects **interior** faces (each `ConnectInfo.getFaces` plus each block's own
internal faces) into one `FlatFaceCollection`, then one boundary `FlatFaceCollection` per
still-unconnected block face, named `Hex_{i}_Face_{vertices}`.

`getPoints()`/`getCellCenters()` scatter each block's local arrays into one global array
indexed by `point_ID`/`cell_ID`, asserting consistency where blocks overlap.

## Face collections (`FaceCollection.py`)

- `NDFaceCollection` — an N-D array of quads (owner/vertices/neighbour, neighbour optional),
  with `.flatten(order='F')` to linearize.
- `FlatFaceCollection` — the 1D accumulator; `.isBoundary()` is `size > 0 and neighbour is
  empty`. `appendNDFaceCollection`/`appendFlatFaceCollection` refuse to mix boundary and
  interior data.
- `checkInteriorFaces`/`checkBoundaryFaces` — geometric sanity checks: the face normal (cross
  product of edge vectors) must point from owner toward neighbour (interior) or away from
  owner (boundary). This is the test suite's main correctness oracle, not hand-checked ID
  tables.

## Output (`writer_utils/PolyMeshFile.py`, `Writer.py`)

Straight OpenFOAM `polyMesh` ASCII writer — header/dictionary formatting helpers, then
`PointsWriter`/`FacesWriter`, which require interior faces to appear before boundary faces
and consistent owner/neighbour/vertices arrays.

## The expansion-layer pattern (`expansion_utils/SingleCell.py`)

This is the piece most relevant to extending the repo with new expansion layers.
`SingleCell2DGrid(n0, n1)` is a lightweight analogue of `HexBlock` for grids of cells that
**don't share vertices with their neighbours** — `point_ID` has shape `(n0, n1, 2, 2, 2)`,
i.e. every cell owns its own 8 corners independently, unlike `HexBlock` where adjacent cells
share a face of points. It reuses `SurfaceProperties`/`vertex_map` (via a 2D analogue,
`Slice2D`) for:

- `getSurface(vertices)` — a genuine shared boundary face, sliced from neighbouring cells'
  matching corners.
- `getAllFaces(vertices)` — every cell's own face independently; used for interior faces
  between whole grids of independent cells.

`SchneiderExpansion.py`'s `SchneiderExpansionLayer` composes one `HexBlock` (`cells_base`,
`3n0 x 3n1 x 1`) with four `SingleCell2DGrid`s (`cells_hat`, `cells_hidden`,
`cells_lateral[0/1]`) that taper the base's 9 fine top-face patches up to progressively fewer,
independent single cells. It reuses `cells_base`'s vertex/edge/face ID accessors for the parts
that align with `HexBlock`'s own vertex map (delegating vertex/edge IDs straight to
`cells_base`), special-casing only where the hat/lateral geometry departs from a plain block
face (e.g. slicing out every-third-point for the coarse-face boundary). `getInteriorFaces`
stitches the base <-> lateral/hidden <-> hat internal faces by hand, matching cell-ID arrays
with matching strides (`::3`, `1::3`, `2::3`) rather than through a generic `ConnectInfo`-style
mechanism — there's no reusable "connect two `SingleCell2DGrid`s" abstraction yet; it's all
bespoke slicing in this one class. See `CLAUDE.md` for the current status/known gaps of this
work in progress.
