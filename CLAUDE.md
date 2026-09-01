# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Motivation

OpenFOAM's native meshing tools (`blockMesh`, `snappyHexMesh`) have no way to place mesh points by
an arbitrary rule — e.g. a cylindrically axisymmetric nozzle whose cross-sectional area changes along
its axis, meshed with a butterfly O-grid. `pyFOAM_hexBlockMesh` fills that gap: every point coordinate
is specified explicitly via numpy, structured hex blocks are stitched together by matching their shared
faces, and the result is written directly to OpenFOAM's `polyMesh` format. It is a low-level primitive
library (blocks + face-merging + ID assignment), not a parametric mesher — geometry-specific logic
(e.g. butterfly O-grid nozzles) is built on top by the calling script.

## Status: SchneiderExpansionLayer (active work, as of 2026-08-17)

`SchneiderExpansionLayer` (`SchneiderExpansion.py`) is a generic, nozzle-independent building block —
not specific to the nozzle use case above. It's one layer of hex cells with a single coarse square
face exposed on top and a 3×3 grid of fine square faces exposed on the bottom (Schneider 1-to-9
octree refinement). It's composed of a `cells_base` `HexBlock` (3n0 × 3n1 × 1) plus four
`SingleCell2DGrid` groups — `cells_hat`, `cells_hidden`, `cells_lateral[0]`, `cells_lateral[1]` —
that sit above the base and taper the 9 fine faces up to the 1 coarse face.

**Implemented + tested:**
- Cell ID assignment (`setCellIDs`)
- Vertex / edge point-ID get/set on the base block, with correct delegation for hat-face vertices/edges
- `setUpSingleCellGridPoints` — wires shared point IDs between `cells_base`'s boundary and the hat/
  hidden/lateral grids (worth a second look: a couple of assignment lines in the `cells_lateral[0]`
  and `cells_lateral[1]` blocks look like accidental copy/paste duplicates — not yet confirmed as a bug)

**Implemented, not yet tested:**
- `getInteriorFaces` — stitches together the internal faces between base/hat/hidden/lateral cells
- `setPointCoordinates(face_0, height)` — sets coordinates for `cells_base`'s 2 stored axis-2 layers
  (z=0 and z=height) from a given fine-resolution face array
- `getPointsL0`..`getPointsL3` — accessors for the 4 conceptual height levels (see gap below)

**Known gap — coordinate assignment above the base layer:** `cells_base` only physically stores 2
axis-2 layers, but the Schneider template has 4 height levels, and the hat/hidden/lateral
`SingleCell2DGrid` groups hold no coordinates of their own. Intended scheme (confirmed with the
project owner, not yet implemented): the 4 levels sit at 0, 0.33, 0.67, and 1.0 of the layer height.
`getPointsL1`–`L3` as currently written only slice `cells_base.point_coordinates`, which doesn't have
those extra layers — so they are placeholders pending this.

**Not implemented:** `getCellCenterCoordinates`, `getSurfacePointCoordinates` (`raise NotImplementedError`).

**`LateralFace.py` (new, untracked):** an M-shaped cross-section face that joins two
`SchneiderExpansionLayer` instances side-by-side along the layer's own lateral axes 0 and 1 (not the
nozzle axis — layers are nozzle-agnostic). Implements vertex/edge/interior-surface/hat-top point-ID
get/set across the same 4 height levels, mirroring the `ConnectInfo` pattern. No coordinate handling
yet, no tests yet. Confirmed next step: wire it into `SchneiderExpansionLayer` /
`ConnectedHexCollection`'s connection cascade.

## Commands

**Run all tests:**
```bash
C:\Users\souri\.virtualenvs\pymesh\Scripts\python.exe -m unittest discover -s tests -v
```

**Run a single test file:**
```bash
C:\Users\souri\.virtualenvs\pymesh\Scripts\python.exe -m unittest tests.test_SchneiderExpansion -v
```

**Run a specific test:**
```bash
C:\Users\souri\.virtualenvs\pymesh\Scripts\python.exe -m unittest tests.test_SchneiderExpansion.TestSchneiderExpansionLayer.test_name -v
```

**Install package in dev mode:**
```bash
C:\Users\souri\.virtualenvs\pymesh\Scripts\pip.exe install -e .
```

## Code Style

- Indentation: 8-character wide tabs
- Use blank lines and spaces liberally to organize code into logical blocks
- Max line length: 100 characters

## Architecture

This library generates OpenFOAM polyMesh files containing structured hexahedral blocks.
See `docs/ARCHITECTURE.md` for the fuller walkthrough (shape conventions, the vertex/edge/
face abstraction, the ID-assignment cascade, and the `SingleCell2DGrid` expansion-layer
pattern) — the summary below is the condensed version.

### Core workflow

1. Create `HexBlock(n0, n1, n2)` objects — each represents a structured block with `n0×n1×n2` cells and an `(n0+1, n1+1, n2+1, 3)` coordinate array
2. Call `block.setPointCoordinates(coords)` — validates right-handedness
3. Add blocks to `ConnectedHexCollection`, then call `connectHexBlocks(id0, id1, fv0, fv1)` with face vertex tuples
4. Call `assignCellIDs()` then `assignPointIDs()` on the collection
5. Write output with `PointsWriter` and `FacesWriter`

### ID assignment cascade (ConnectedHexCollection.assignPointIDs)

The order is critical: shared vertices → shared edges → shared face interiors → unshared per-block points. Connections are processed via `ConnectInfo` objects that manage shared boundaries. Interior corners shared by 4 blocks must be connected in spanning-tree order (not closing cycles prematurely) to avoid ID conflicts.

### Vertex and face indexing (geometry_utils/HexBlockMap.py)

`vertex_map` maps the 8 vertex labels (0–7) to array indices using 0 (first) and -1 (last):
- v0=(0,0,0), v1=(-1,0,0), v2=(-1,-1,0), v3=(0,-1,0)
- v4=(0,0,-1), v5=(-1,0,-1), v6=(-1,-1,-1), v7=(0,-1,-1)

Six face vertex tuples define outward normals:
- `(0,3,2,1)` = ax2=0 face, `(4,5,6,7)` = ax2=last
- `(0,1,5,4)` = ax1=0 face, `(2,3,7,6)` = ax1=last
- `(0,4,7,3)` = ax0=0 face, `(1,2,6,5)` = ax0=last

### ConnectInfo and face matching

`ConnectInfo` validates that two faces match via `getSurfaceCompleteSlice` — which returns coordinate arrays shaped by traversal order determined by the face vertex tuple. The vertex tuple ordering sets the traversal direction; both sides must yield the same coordinate arrays for `isValid()` to pass.

### Expansion layers (expansion_utils/)

- `SchneiderExpansionLayer` in `SchneiderExpansion.py`: implements Schneider 1-to-9 octree refinement — 9 `HexBlock` objects in a 3×3 grid bridging 1 coarse macro-face to 9 fine faces
  - Corner ordering: `corners[0]`=(R=0,C=0), `corners[1]`=(R=0,C=last), `corners[2]`=(R=last,C=last), `corners[3]`=(R=last,C=0) where R=axis1, C=axis2, expansion=axis0
  - Internal row-direction connection: `(2,3,7,6)` ↔ `(1,0,4,5)`; col-direction: `(4,5,6,7)` ↔ `(0,1,2,3)`
- `SingleCell2DGrid` in `SingleCell.py`: 2D grid of independent single cells (vertices not shared between neighbors)
- `LateralFace.py`: partially implemented M-shaped lateral face for connecting two expansion layers

### Face collections (FaceCollection.py)

- `NDFaceCollection`: N-dimensional array of quad faces with owner/neighbour arrays
- `FlatFaceCollection`: 1D face list tagged with boundary name; `isBoundary()` returns True when no neighbours
- `mergeFaceCollections()` combines boundary face collections into the final list

### File output (Writer.py, writer_utils/PolyMeshFile.py)

Writes standard OpenFOAM polyMesh files: `points`, `faces`, `owner`, `neighbour`, `boundary`. The `FacesWriter` requires interior faces to appear before boundary faces, and face/owner/neighbour arrays must be consistent.
