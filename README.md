# pyFOAM_hexBlockMesh

`pyFOAM_hexBlockMesh` is a Python library designed to help create and manipulate hexahedral block meshes for OpenFOAM simulations.

## Features

- Methods to create hexahedral block meshes
- Support for combining multiple hex blocks by merging quadrilateral surfaces
- Integration with numpy to customize hexahedra to any shape
- Some documentation and examples

## Installation

To install `pyFOAM_hexBlockMesh` after cloning the repository:

```bash
git clone https://github.com/Souritra-Garai/pyFOAM_hexBlockMesh
cd pyFOAM_hexBlockMesh
pip install .
```

## Post-Generation Renumbering

The cells are numbered in a column major style. This is not ideal during simulations since the diagonal bandwidth of the matrix A (in `A.x = b`) will be huge. Hence, the `renumberMesh` program in OpenFOAM must be run to optimize performance.

## Example

An example on how to use the library to generate the following mesh is provided in the directory `examples/nozzle_jet`. Certain excerpts from the script `py_scripts/nozzle_jet.py` are illustrated here to demonstrate the features of the library :

```python
# Creating 2 hex blocks with number of cell divisions
# along each of the 3 axes
center_block = HexBlock(n_core, n_core, n_z)
px_block = HexBlock(n_shell, n_core, n_z)
...
# Setting coordinates of node points in the blocks
coordinates = np.stack((X, Y, Z), axis=-1)

center_block.setPointCoordinates(coordinates)
...
# Setting up a hex block collection to merge faces
hex_collection = ConnectedHexCollection()

center_block_ID	= hex_collection.addHexBlock(center_block)
px_block_ID	= hex_collection.addHexBlock(px_block)

hex_collection.connectHexBlocks(
	center_block_ID, px_block_ID,
	(1, 2, 6, 5), (0, 3, 7, 4)
)
...
# Generating the polyMesh
hex_collection.assignCellIDs()
hex_collection.assignPointIDs()

points	= hex_collection.getPoints()
faces	= hex_collection.getFaces()

points_writer	= PointsWriter(polyMesh_dir)
faces_writer	= FacesWriter(polyMesh_dir)

points_writer.write(points)
faces_writer.write(faces)
```
