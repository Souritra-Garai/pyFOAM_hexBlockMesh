from dataclasses import dataclass

import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap

@dataclass
class Slice5D :
	'''
	Slice of a 5D array.
	Used for SingleCell2DGrid point_ID arrays of shape (n0, n1, 2, 2, 2),
	where axes 0-1 are the cell-grid dimensions and axes 2-4 are the local
	hex-vertex dimensions (analogous to Slice3D for HexBlock).

	Only axes 0 and 1 (cell-grid) can interchange via the axes field.
	Axes 2-4 (local vertex) are always fixed and addressed directly by slices[2-4].
	'''

	slices	: list[slice|int]
	axes	: list[int]

	def __init__(self) -> None :
		'''
		Initialize the 5D slice
		'''

		self.slices	= [slice(None)] * 5
		self.axes	= [0, 1]

		pass

	def isValid(self) -> bool :
		'''
		Check if the slice is valid
		'''

		flag = set(self.axes) == {0, 1}
		flag = flag and len(self.slices) == 5 and len(self.axes) == 2
		flag = flag and all([isinstance(s, (int, slice)) for s in self.slices])

		return flag

	def getArrayView(self, points:np.ndarray) -> np.ndarray :
		'''
		Get the array view of the 5D (or higher) points array.
		Only axes 0 and 1 are reordered via moveaxis; axes 2-4 are indexed directly.
		'''

		assert isinstance(points, np.ndarray)
		assert self.isValid(), 'Invalid slice'
		assert points.ndim >= 5, 'Invalid input'

		points_view = np.moveaxis(points, self.axes, (0, 1))
		points_view = points_view[tuple(self.slices)]

		return points_view

def getInteriorSlice(vertex:int, axis:HexBlockVertices.AxisProperties) -> slice :
	'''
	Returns a slice for an axis based on the vertex
	if vertex[axis]=0 and axis is oriented along positive direction
	then interior slice would be slice(1, None) to exclude the starting point
	'''

	# Check if the input is valid
	assert vertex in range(8), 'Invalid input: vertex must be in range(8)'
	assert isinstance(axis, HexBlockVertices.AxisProperties), \
	'Invalid input: axis must be an AxisProperties instance'

	match (HexBlockMap.vertex_map[vertex][axis.dimension], axis.orientation) :

		# start of axis, forward direction → skip first (boundary) point
		case ( 0, True)		: return slice(1, None)
		# end of axis, forward direction → skip last (boundary) point
		case (-1, True)		: return slice(0, -1)
		# start of axis, backward direction → reverse traversal, stop before first point
		case ( 0, False)	: return slice(-1, 0, -1)
		# end of axis, backward direction → reverse traversal, skip last (boundary) point
		case (-1, False)	: return slice(-2, None, -1)
		# Raise error when no match
		case _			: raise \
		ValueError('Unexpected combination: ' \
		f'vertex_map={HexBlockMap.vertex_map[vertex][axis.dimension]}, ' \
		f'orientation={axis.orientation}')

def getInteriorEdgeSlice(vertex:int, axis:HexBlockVertices.AxisProperties) -> Slice5D :
	'''
	Returns a 5D Slice for obtaining specified vertex
	along all interior edge cells of the specified axis
	'''

	# Check if the input is valid
	assert vertex in range(8), 'Invalid input: vertex must be in range(8)'
	assert isinstance(axis, HexBlockVertices.AxisProperties), \
	'Invalid input: axis must be an AxisProperties instance'
	assert axis.dimension in (0, 1), \
	'Invalid input: axis dimension must be 0 or 1 for SingleCell2DGrid'

	vertex_slice				= Slice5D()
	vertex_slice.slices[2:]			= HexBlockMap.vertex_map[vertex]
	vertex_slice.slices[axis.dimension]	= getInteriorSlice(vertex, axis)

	return vertex_slice

def getInteriorSurafceSlice5D(vertex:int, axes:tuple[HexBlockVertices.AxisProperties, ...]) -> Slice5D :
	'''
	Returns a 5D Slice to obtain the specified vertex
	of the interior cells on the specified surface
	'''

	# Check if the input is valid
	assert vertex in range(8), 'Invalid input: vertex must be in range(8)'
	assert len(axes) == 2 and \
	all(isinstance(ax, HexBlockVertices.AxisProperties) for ax in axes), \
	'Invalid input: axes must be a sequence of exactly 2 AxisProperties instances'
	assert axes[0].dimension in (0, 1) and axes[1].dimension in (0, 1), \
	'Invalid input: both axis dimensions must be 0 or 1 for SingleCell2DGrid'
	assert axes[0].dimension != axes[1].dimension, \
	'Invalid input: axes must span different dimensions'

	vertex_slice = Slice5D()

	vertex_slice.axes[0] = axes[0].dimension
	vertex_slice.axes[1] = axes[1].dimension

	vertex_slice.slices[0] = getInteriorSlice(vertex, axes[0])
	vertex_slice.slices[1] = getInteriorSlice(vertex, axes[1])

	return vertex_slice

class SingleCell2DGrid :
	'''
	Class to represent 2D array of cells
	where the vertices do not co-incide with neighbouring cells
	'''
	cell_ID			: np.ndarray
	point_ID		: np.ndarray
	point_coordinates	: np.ndarray

	def __init__(self, n0:int, n1:int) -> None:
		'''
		n0, n1: number of cells along each axis
		'''

		# Check if the input is valid
		assert all(isinstance(n, int) and n > 0 for n in (n0, n1)), \
		'Invalid input : n0, n1 must be positive integers'

		self.cell_ID		= np.full((n0, n1), -1, dtype=int)
		self.point_ID		= np.full((n0, n1, 2, 2, 2), -1, dtype=int)
		self.point_coordinates	= np.zeros((n0, n1, 2, 2, 2, 3), dtype=float)

		pass

	def setCellIDs(self, start_ID:int=0) -> int :
		'''
		Set the cell IDs
		start_ID: Starting ID for the cells
		Return the starting ID for the next cell
		'''

		# Check if the input is valid
		assert isinstance(start_ID, int) and start_ID >= 0, 'Invalid input'

		cells_shape = self.cell_ID.shape
		num_cells = np.prod(cells_shape)

		# Assign consecutive cell IDs to the cells
		# Varying fastest along axis 0, then axis 1, then axis 2
		self.cell_ID = np.arange(
			start_ID,
			start_ID + num_cells
		).reshape(cells_shape, order='F')

		return start_ID + int(num_cells)

	def getFaceShape(self, vertices:tuple[int, int, int, int]) -> tuple[int, int] :
		'''
		Get the shape (cells) of the face
		'''

		surface = HexBlockVertices.SurfaceProperties(vertices)

		ax0 = surface.axes[0].dimension
		ax1 = surface.axes[1].dimension

		cell_shape = self.cell_ID.shape + (1,)

		shape = (cell_shape[ax0], cell_shape[ax1])

		return shape

	def getPointIDs(self, point_slice: Slice5D) -> np.ndarray :
		'''
		Returns a view of the point IDs
		'''

		# Check if the input is valid
		assert isinstance(point_slice, Slice5D), 'Invalid input'

		return point_slice.getArrayView(self.point_ID)
	
	def setPointIDs(self, point_slice:Slice5D, point_IDs:np.ndarray) -> None :
		'''
		Sets the point IDs to the specified slice of point IDs array
		'''

		# Check if the input is valid
		assert isinstance(point_slice, Slice5D), 'Invalid input'
		assert isinstance(point_IDs, np.ndarray) and point_IDs.dtype == int, \
		'Invalid input'

		point_IDs_view		= point_slice.getArrayView(self.point_ID)
		point_IDs_view[:]	= point_IDs

		pass
