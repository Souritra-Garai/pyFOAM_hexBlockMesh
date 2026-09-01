# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
