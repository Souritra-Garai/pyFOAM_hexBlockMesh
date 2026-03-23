import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap

class SingleCell2DGrid :

	cell_ID			: np.ndarray
	point_ID		: np.ndarray
	point_coordinates	: np.ndarray

	def __init__(self, n0:int, n1:int) -> None:

		self.cell_ID		= np.zeros((n0, n1), dtype=int)
		self.point_ID		= np.full((n0, n1, 2, 2, 2), -1, dtype=int)
		self.point_coordinates	= np.zeros((n0, n1, 2, 2, 2, 3), dtype=float)

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

		surface = HexBlockVertices.SurfaceProperties(vertices)
		
		ax0 = surface.axes[0].dimension
		ax1 = surface.axes[1].dimension

		cell_shape = self.cell_ID.shape + (1,)

		shape = (cell_shape[ax0], cell_shape[ax1])

		return shape

	def getVertexPointID(self, vertex:int) -> np.ndarray :
		'''
		Get the point ID of the vertex
		'''

		# Check if the input is valid
		assert vertex in range(8), 'Invalid input'

		point_index	= HexBlockMap.vertex_map[vertex]
		point_ID	= self.point_ID[(slice(None), slice(None)) + point_index]

		return point_ID

	def setVertexPointID(self, vertex:int, point_ID:np.ndarray) -> None :
		'''
		Set the point ID of the vertex
		'''

		# Check if the input is valid
		assert vertex in range(8), 'Invalid input'
		assert	isinstance(point_ID, np.ndarray) and \
			np.issubdtype(point_ID.dtype, np.integer) and \
			point_ID.shape == self.cell_ID.shape and \
			np.all(point_ID >= 0), \
		f'Invalid input: {point_ID} of type {type(point_ID)}'

		point_index = HexBlockMap.vertex_map[vertex]

		idx = (slice(None), slice(None)) + point_index
		assert np.all(self.point_ID[idx] == -1), 'Point ID is already set'

		self.point_ID[idx] = point_ID

	def getVertexPointCoordinates(self, vertex:int) -> np.ndarray :
		'''
		Get the point coordinates of the vertex
		'''

		# Check if the input is valid
		assert vertex in range(8), 'Invalid input'

		point_index = HexBlockMap.vertex_map[vertex]

		return self.point_coordinates[(slice(None), slice(None)) + point_index]

	def setVertexPointCoordinates(self, vertex:int, point_coordinates:np.ndarray) -> None :
		'''
		Set the point coordinates of the vertex
		'''

		# Check if the input is valid
		assert vertex in range(8), 'Invalid input'
		assert	isinstance(point_coordinates, np.ndarray) and \
			point_coordinates.shape == (self.cell_ID.shape + (3,)) , \
		f'Invalid input: {point_coordinates} of type {type(point_coordinates)}'

		point_index = HexBlockMap.vertex_map[vertex]

		self.point_coordinates[(slice(None), slice(None)) + point_index] = point_coordinates
