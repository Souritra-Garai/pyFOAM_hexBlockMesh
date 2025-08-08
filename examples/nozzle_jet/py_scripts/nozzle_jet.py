from pathlib import Path

import numpy as np

from scipy.interpolate import CubicHermiteSpline

from pyFOAM_hexBlockMesh.ConnectedHexCollection import \
ConnectedHexCollection, HexBlock
from pyFOAM_hexBlockMesh.Writer import PointsWriter, FacesWriter

###################################################################################################
# Domain Parameters
axial_length	= 1.0
inlet_radius	= 0.4
outlet_radius	= 0.1

# Mesh parameters
n_core	= 25
n_shell	= 25
n_z	= 100

# Ratio of core radius to shell radius
ratio_radii = 0.6

###################################################################################################
# Create splines

side_length = 1 / np.sqrt(2)

tanp15 = np.tan(np.deg2rad(15))
tanm15 = np.tan(np.deg2rad(-15))

spline = CubicHermiteSpline(
	[-side_length, side_length],
	[ side_length, side_length],
	[tanp15, tanm15]
)

o_grid_curve_x = np.linspace(-side_length, side_length, n_core + 1)
o_grid_curve_y = spline(o_grid_curve_x)

spline = CubicHermiteSpline(
	[0, axial_length],
	[inlet_radius, outlet_radius],
	[0, 0]
)

axial_profile_z = np.linspace(0, axial_length, n_z + 1)
axial_profile_r = spline(axial_profile_z)

# import matplotlib.pyplot as plt
# plt.plot(o_grid_curve_x, o_grid_curve_y, label='Outer grid curve')
# plt.plot(axial_profile_r, axial_profile_z, label='Axial profile')
# ax = plt.gca()
# ax.set_aspect('equal', adjustable='datalim')
# plt.show()

###################################################################################################
# Declare hex blocks

center_block	= HexBlock(n_core,	n_core,		n_z)
px_block	= HexBlock(n_shell,	n_core,		n_z)
py_block	= HexBlock(n_core,	n_shell,	n_z)
nx_block	= HexBlock(n_core,	n_core,		n_z)
ny_block	= HexBlock(n_core,	n_shell,	n_z)

###################################################################################################
# Set Coordinates

# Center block
edge_0 = - o_grid_curve_y
edge_1 = o_grid_curve_y

x = np.linspace(edge_0, edge_1, n_core + 1, axis=0)
y = np.linspace(edge_0, edge_1, n_core + 1, axis=1)

X = x[:, :, np.newaxis] * ratio_radii * axial_profile_r[np.newaxis, np.newaxis, :]
Y = y[:, :, np.newaxis] * ratio_radii * axial_profile_r[np.newaxis, np.newaxis, :]
Z = np.tile(axial_profile_z, (n_core + 1, n_core + 1, 1))

coordinates = np.stack((X, Y, Z), axis=-1)

center_block.setPointCoordinates(coordinates)

# Positive X block
surface_0 = center_block.getSurfacePointCoordinates((1, 2, 6, 5))

theta = np.linspace(-np.pi / 4, np.pi / 4, n_core + 1)

x = axial_profile_r[np.newaxis, :] * np.cos(theta[:, np.newaxis])
y = axial_profile_r[np.newaxis, :] * np.sin(theta[:, np.newaxis])
z = np.tile(axial_profile_z, (n_core + 1, 1))

surface_1 = np.stack((x, y, z), axis=-1)

volume_px = np.linspace(surface_0, surface_1, n_shell + 1)

px_block.setPointCoordinates(volume_px)

# Positive Y block
volume_py = volume_px.copy()

# Reflect (..., 3) shape ndarray containing the coordinates of points
# about x = y plane
volume_py[..., 0] = volume_px[..., 1]
volume_py[..., 1] = volume_px[..., 0]

volume_py = np.moveaxis(volume_py, [0, 1, 2], [1, 0, 2])

py_block.setPointCoordinates(volume_py)

# Negative X block
volume_nx = volume_px.copy()

# Reflect (..., 3) shape ndarray containing the coordinates of points
# about x = 0 plane
volume_nx[..., 0] = -volume_nx[..., 0]

volume_nx = volume_nx[::-1, ...]

nx_block.setPointCoordinates(volume_nx)

# Negative Y block
volume_ny = volume_py.copy()

# Reflect (..., 3) shape ndarray containing the coordinates of points
# about y = 0 plane
volume_ny[..., 1] = -volume_ny[..., 1]

volume_ny = volume_ny[:, ::-1, ...]

ny_block.setPointCoordinates(volume_ny)

###################################################################################################
# Set up collection of hex blocks

hex_collection = ConnectedHexCollection()

center_block_ID	= hex_collection.addHexBlock(center_block)
px_block_ID	= hex_collection.addHexBlock(px_block)
py_block_ID	= hex_collection.addHexBlock(py_block)
nx_block_ID	= hex_collection.addHexBlock(nx_block)
ny_block_ID	= hex_collection.addHexBlock(ny_block)

hex_collection.connectHexBlocks(
	center_block_ID, px_block_ID,
	(1, 2, 6, 5), (0, 3, 7, 4)
)

hex_collection.connectHexBlocks(
	center_block_ID, py_block_ID,
	(3, 2, 6, 7), (0, 1, 5, 4)
)
hex_collection.connectHexBlocks(
	px_block_ID, py_block_ID,
	(3, 2, 6, 7), (1, 2, 6, 5)
)

hex_collection.connectHexBlocks(
	center_block_ID, nx_block_ID,
	(0, 3, 7, 4), (1, 2, 6, 5)
)
hex_collection.connectHexBlocks(
	py_block_ID, nx_block_ID,
	(0, 3, 7, 4), (2, 3, 7, 6)
)

hex_collection.connectHexBlocks(
	center_block_ID, ny_block_ID,
	(0, 1, 5, 4), (3, 2, 6, 7)
)
hex_collection.connectHexBlocks(
	nx_block_ID, ny_block_ID,
	(0, 1, 5, 4), (0, 3, 7, 4)
)
hex_collection.connectHexBlocks(
	px_block_ID, ny_block_ID,
	(0, 1, 5, 4), (2, 1, 5, 6)
)

hex_collection.assignCellIDs()
hex_collection.assignPointIDs()

###################################################################################################
# Write polyMesh

points	= hex_collection.getPoints()
faces	= hex_collection.getFaces()

polyMesh_dir = Path(__file__).parent.parent / 'constant' / 'polyMesh'
polyMesh_dir.mkdir(parents=True, exist_ok=True)

points_writer	= PointsWriter(polyMesh_dir)
faces_writer	= FacesWriter(polyMesh_dir)

points_writer.write(points)
faces_writer.write(faces)

