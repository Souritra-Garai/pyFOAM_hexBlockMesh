import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap

from pyFOAM_hexBlockMesh.FaceCollection import NDFaceCollection

class Slice2D :
	'''
	Slice of a 2D array
	'''

	slices	: list[slice|int]
	axes	: list[int]

	def __init__(self) -> None :
		'''
		Initialize the surface slice
		'''

		self.slices	= [slice(None)] * 2
		self.axes	= [0, 1]

		pass

	def isValid(self) -> bool :
		'''
		Check if the slice is valid
		'''

		flag = set(self.axes) == {0, 1}
		flag = flag and len(self.slices) == 2 and len(self.axes) == 2
		flag = flag and all([isinstance(s, (int, slice)) for s in self.slices])

		return flag

	def getCellsView(self, cells:np.ndarray) -> np.ndarray :
		'''
		Get the array view of the points array
		'''

		# Check if the input is valid
		assert isinstance(cells, np.ndarray)
		assert self.isValid(), 'Invalid slice'
		assert cells.ndim >= 2, 'Invalid input'

		# Get the array view of the points array
		points_view = np.moveaxis(cells, self.axes, (0, 1))
		points_view = points_view[tuple(self.slices)]

		return points_view

	def getPointsView(self, points:np.ndarray, vertex) -> np.ndarray :
		'''
		Get the array view of the points array
		'''

		# Check if the input is valid
		assert isinstance(points, np.ndarray)
		assert self.isValid(), 'Invalid slice'
		assert points.ndim >= 5, 'Invalid input'

		# Get the array view of the points array
		points_view = np.moveaxis(points, self.axes, (0, 1))
		points_view = points_view[tuple(self.slices) + \
			    		  HexBlockMap.vertex_map[vertex]]

		return points_view

def getSurfaceSlice(vertices:tuple[int, int, int, int]) -> Slice2D :

	surface = HexBlockVertices.SurfaceProperties(vertices)

	surface_slice = Slice2D()

	surface_slice.axes[0]	= surface.axes[0].dimension
	surface_slice.slices[0]	= surface.axes[0].getSlice()

	surface_slice.axes[1]	= surface.axes[1].dimension
	surface_slice.slices[1]	= surface.axes[1].getSlice()

	if surface.constant_axis != 2 :

		index				= surface_slice.axes.index(2)

		surface_slice.axes[index]	= surface.constant_axis
		surface_slice.slices[index]	= surface.constant_axis_index

	return surface_slice


class SingleCell2DGrid :
	'''
	Class to represent 2D array of cells
	where the vertices do not co-incide with neighbouring cells
	'''
	cell_ID			: np.ndarray
	point_ID		: np.ndarray

	def __init__(self, n0:int, n1:int) -> None:
		'''
		n0, n1: number of cells along each axis
		'''

		# Check if the input is valid
		assert all(isinstance(n, int) and n > 0 for n in (n0, n1)), \
		'Invalid input : n0, n1 must be positive integers'

		self.cell_ID		= np.full((n0, n1), -1, dtype=int)
		self.point_ID		= np.full((n0, n1, 2, 2, 2), -1, dtype=int)

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

	def getSurface(self, vertices:tuple[int, int, int, int]) -> NDFaceCollection :

		surface_slice = getSurfaceSlice(vertices)

		cells		= surface_slice.getCellsView(self.cell_ID)
		face_points	= np.stack([
			surface_slice.getPointsView(self.point_ID, vertex) \
			for vertex in vertices
		], axis=-1)

		return NDFaceCollection(cells, face_points)

	def getAllFaces(self, vertices:tuple[int, int, int, int]) -> NDFaceCollection :

		face_points	= np.stack([
			self.point_ID[:, :][HexBlockMap.vertex_map[vertex]]
			for vertex in vertices
		], axis=-1)

		return NDFaceCollection(self.cell_ID, face_points)
