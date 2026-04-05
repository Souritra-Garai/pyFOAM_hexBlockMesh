import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices

from pyFOAM_hexBlockMesh.HexBlock import HexBlock
from pyFOAM_hexBlockMesh.FaceCollection import NDFaceCollection
from pyFOAM_hexBlockMesh.expansion_utils.SingleCell import SingleCell2DGrid, getInteriorEdgeSlice, getInteriorSurafceSlice5D

class SchneiderExpansionLayer :

	cells_base	: HexBlock
	cells_hat	: SingleCell2DGrid
	cells_hidden	: SingleCell2DGrid
	cells_lateral	: tuple[SingleCell2DGrid, SingleCell2DGrid]
	# Lateral direction is axis 0
	# Expansion direction is axis 2

	def __init__(self, n0:int, n1:int) -> None :
		'''
		n0, n1: Number of cells along lateral directions
		Base cells are 3x n
		'''
		# Check if the input is valid
		assert	all(isinstance(n, int) and (n > 0) for n in (n0, n1)), \
		'Invalid input : n0, n1 must be positive integers'

		self.cells_base		= HexBlock(3*n0, 3*n1, 1)
		self.cells_hat		= SingleCell2DGrid(n0, n1)
		self.cells_hidden	= SingleCell2DGrid(n0, n1)
		self.cells_lateral	= (SingleCell2DGrid(n0, n1), SingleCell2DGrid(n0, n1)) 

		pass

	def setCellIDs(self, start_ID:int=0) -> int :
		'''
		Set the cell IDs
		start_ID: Starting ID for the cells
		Return the starting ID for the next cell
		'''

		start_ID = self.cells_base.setCellIDs(start_ID)

		start_ID = self.cells_hat.setCellIDs(start_ID)
		start_ID = self.cells_hidden.setCellIDs(start_ID)
		start_ID = self.cells_lateral[0].setCellIDs(start_ID)
		start_ID = self.cells_lateral[1].setCellIDs(start_ID)

		return start_ID

	def setInternalPointIDs(self, start_ID:int=0) -> int :
		'''
		Set the point IDs for the internal points
		'''
		points_shape = self.getFaceShape((4, 5, 6, 7))
		num_points = np.prod(points_shape)

		# Assign consecutive point IDs to the internal points
		# Varying fastest along axis 0, then axis 1, then axis 2
		# Skip the points on the boundary surfaces
		# The first and last indices along each axis represent the boundary points
		point_ID = np.arange(
			start_ID,
			start_ID + num_points
		).reshape(points_shape, order='F')

		self.cells_base.setSurfacePointIDs((4, 5, 6, 7), point_ID)

		return start_ID + int(num_points)

	def getFaceShape(self, vertices:tuple) -> tuple :
		'''
		Get the shape (cells) of the face
		'''
		surface = HexBlockVertices.SurfaceProperties(vertices)

		if surface.constant_axis == 2 :

			if surface.constant_axis_index == 0 :

				return self.cells_base.getFaceShape(vertices)
			
			elif surface.constant_axis_index == -1 :

				return self.cells_hat.getFaceShape(vertices)
			
			else :
				raise RuntimeError(
					'Invalid constant axis index :'\
		       			f'{surface.constant_axis_index}'
				)
			
		else :
			raise RuntimeError('Requesting lateral faces of Expansion Layer!!')

	def getFaceShapeExpLayer(self, vertices:tuple) -> tuple :

		raise NotImplementedError

	def getVertexPointID(self, vertex:int) -> int :
		'''
		Get the point ID of the vertex
		'''
		# Check if the input is valid
		assert vertex in list(range(8)), 'Invalid input'

		return self.cells_base.getVertexPointID(vertex)		

	def setVertexPointID(self, vertex:int, point_ID:int) -> None :
		'''
		Set the point ID of the vertex
		'''
		# Check if the input is valid
		assert vertex in list(range(8)), 'Invalid input'
		assert isinstance(point_ID, (int, np.integer)) and point_ID >= 0, \
		f'Invalid input: {point_ID} of type {type(point_ID)}'

		self.cells_base.setVertexPointID(vertex, point_ID)

		if vertex in (4, 5, 6, 7) :

			vertex_map = HexBlockMap.vertex_map[vertex]
			point_index = vertex_map[:2] + vertex_map

			self.cells_hat.point_ID[point_index] = point_ID
			self.cells_lateral[vertex_map[1]].point_ID[point_index] = point_ID

		pass

	def getEdgePointIDs(self, v0:int, v1:int) -> np.ndarray :
		'''
		Get the IDs of points along the edge from v0 to v1.
		Excludes the vertices.
		'''
		point_IDs = self.cells_base.getEdgePointIDs(v0, v1)

		if set((v0, v1)).issubset(set((4, 5, 6, 7))) :

			return point_IDs[2::3]

		else :

			return point_IDs

	def setEdgePointIDs(self, v0:int, v1:int, point_IDs:np.ndarray) -> None :
		'''
		Set the IDs of points along the edge
		from v0 to v1.
		Excludes the vertices.
		'''
		# Check if the input is valid
		assert isinstance(point_IDs, np.ndarray) and point_IDs.dtype == int,	\
		'Invalid input'

		if set((v0, v1)).issubset(set((4, 5, 6, 7))) :

			point_IDs_view = self.cells_base.getEdgePointIDs(v0, v1)[2::3]

			assert point_IDs.shape == point_IDs_view.shape, 'Invalid input'
			
			point_IDs_view[:] = point_IDs

			axis = HexBlockVertices.AxisProperties(v0, v1)

			for vertex in (v0, v1) :

				edge_slice = getInteriorEdgeSlice(vertex, axis)

				self.cells_hat.setPointIDs(edge_slice, point_IDs)
				self.cells_lateral[HexBlockMap.vertex_map[vertex][1]] \
				.setPointIDs(edge_slice, point_IDs)

		else :

			self.cells_base.setEdgePointIDs(v0, v1, point_IDs)

	def getSurfacePointIDs(self, vertices:tuple[int, int, int, int]) -> np.ndarray :
		'''
		Get the IDs of points on the face formed by the 4 vertices.
		Excludes the vertices and the edges.
		'''
		# Check if the input is valid
		assert len(vertices) == 4, 'Invalid input'

		point_IDs = self.cells_base.getSurfacePointIDs(vertices)

		match set(vertices) :

			case set((0, 1, 2, 3))	: return point_IDs
			case set((4, 5, 6, 7))	: return point_IDs[2::3, 2::3]
			case _			: raise NotImplementedError

	def setSurfacePointIDs(
		self,
		vertices:tuple[int, int, int, int],
		point_IDs:np.ndarray
	) -> None :
		'''
		Set the IDs of points on the face formed by the 4 vertices.
		Excludes the vertices and the edges.
		'''
		# Check if the input is valid
		assert isinstance(point_IDs, np.ndarray) and point_IDs.dtype == int,	\
		'Invalid input'

		match set(vertices) :

			case set((0, 1, 2, 3))	:

				self.cells_base.setSurfacePointIDs(vertices, point_IDs)

			case set((4, 5, 6, 7))	:
				# Check if the input is valid
				assert point_IDs.shape == self.cells_hat.cell_ID.shape

				surface_axes = HexBlockVertices.SurfaceProperties(vertices)

				for vertex in vertices :

					surface_slice = \
					getInteriorSurafceSlice5D(vertex, surface_axes.axes)

					self.cells_hat.setPointIDs(surface_slice, point_IDs)
					self.cells_lateral[HexBlockMap.vertex_map[vertex][1]] \
					.setPointIDs(surface_slice, point_IDs)

			case _	: raise NotImplementedError

	def getSurface(self, vertices:tuple[int, int, int, int]) -> NDFaceCollection :
		'''
		Get collection of faces on the surface
		formed by the 4 vertices.
		'''
		raise NotImplementedError

	def getInteriorFaces(self) -> tuple[NDFaceCollection, NDFaceCollection, NDFaceCollection] :
		'''
		Get the interior faces of the block
		'''
		raise NotImplementedError

	def setPointCoordinates(
		self,
		coordinates:np.ndarray
	) -> None :
		'''
		Set the coordinates of the points
		'''
		raise NotImplementedError

	def getCellCenterCoordinates(self) -> np.ndarray :
		'''
		Get the coordinates of the cell centers
		'''
		raise NotImplementedError

	def getSurfacePointCoordinates(
		self,
		vertices:tuple[int, int, int, int]
	) -> np.ndarray :
		'''
		Get the coordinates of the points on the face
		formed by the 4 vertices.
		Excludes the vertices and the edges.
		'''
		raise NotImplementedError

