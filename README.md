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


