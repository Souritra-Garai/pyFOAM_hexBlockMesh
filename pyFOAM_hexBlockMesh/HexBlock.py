import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockFaces as HexBlockFaces
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices

from pyFOAM_hexBlockMesh.geometry_utils.CoordinatesOrientation import checkCoordinatesOrientation
from pyFOAM_hexBlockMesh.FaceCollection import NDFaceCollection
import warnings

class HexBlock :

	def __init__(self, n0:int, n1:int, n2:int) -> None :
		'''
		n0, n1, n2: Number of cells along each axis
		'''

		# Check if the input is valid
		assert all(isinstance(n, int) and n > 0 for n in (n0, n1, n2)), \
		'Invalid input : n0, n1, n2 must be positive integers'

		cells_shape	= (n0, n1, n2)
		points_shape	= (n0+1, n1+1, n2+1)

		# Initialize arrays to store cell IDs, point IDs and point coordinates
		self.cell_ID		= np.zeros(cells_shape, dtype=int)
		self.point_ID		= np.zeros(points_shape, dtype=int)
		self.point_coordinates	= np.zeros(points_shape + (3,), dtype=float)

		# Initialize the cell and point IDs to -1
		self.cell_ID.fill(-1)
		self.point_ID.fill(-1)

		# Initialize the point coordinates to NaN
		self.point_coordinates.fill(np.nan)

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

	def setInternalPointIDs(self, start_ID:int=0) -> int :
		'''
		Set the point IDs for the internal points
		'''

		# Check if the input is valid
		assert isinstance(start_ID, int) and start_ID >= 0, 'Invalid input'

		# Skip the points on the boundary surfaces
		# The first and last indices along each axis represent the boundary points
		points_shape = tuple(np.array(self.point_ID.shape) - 2)
		num_points = np.prod(points_shape)

		# Assign consecutive point IDs to the internal points
		# Varying fastest along axis 0, then axis 1, then axis 2
		# Skip the points on the boundary surfaces
		# The first and last indices along each axis represent the boundary points
		self.point_ID[1:-1, 1:-1, 1:-1]	= np.arange(
			start_ID,
			start_ID + num_points
		).reshape(points_shape, order='F')

		return start_ID + int(num_points)

	def getFaceShape(self, vertices:tuple) -> tuple :
		'''
		Get the shape (cells) of the face
		'''

		surface = HexBlockVertices.SurfaceProperties(vertices)

		ax0 = surface.axes[0].dimension
		ax1 = surface.axes[1].dimension

		shape = (self.cell_ID.shape[ax0], self.cell_ID.shape[ax1])

		return shape
	
	def getVertexPointID(self, vertex:int) -> int :
		'''
		Get the point ID of the vertex
		'''
		
		# Check if the input is valid
		assert vertex in list(range(8)), 'Invalid input'

		point_index	= HexBlockMap.vertex_map[vertex]
		point_ID	= self.point_ID[point_index]

		return point_ID

	def setVertexPointID(self, vertex:int, point_ID:int) -> None :
		'''
		Set the point ID of the vertex
		'''

		# Check if the input is valid
		assert vertex in list(range(8)), 'Invalid input'
		assert isinstance(point_ID, (int, np.integer)) and point_ID >= 0, \
		f'Invalid input: {point_ID} of type {type(point_ID)}'

		point_index = HexBlockMap.vertex_map[vertex]

		assert self.point_ID[point_index] == -1, 'Point ID is already set'
		
		self.point_ID[point_index] = point_ID

		pass

	def getEdgePointIDs(self, v0:int, v1:int) -> np.ndarray :
		'''
		Get the IDs of points along the edge
		from v0 to v1.
		Excludes the vertices.
		'''

		slice_3d	= HexBlockVertices.getEdgeInteriorSlice(v0, v1)
		point_IDs	= slice_3d.getArrayView(self.point_ID)

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

		slice_3d = HexBlockVertices.getEdgeInteriorSlice(v0, v1)
		point_ID_view = slice_3d.getArrayView(self.point_ID)

		# Check if the input is valid
		assert point_IDs.shape == point_ID_view.shape, 'Invalid input'

		point_ID_view[:] = point_IDs

		pass

	def getSurfacePointIDs(self, vertices:tuple[int, int, int, int]) -> np.ndarray :
		'''
		Get the IDs of points on the face formed by the 4 vertices.
		Excludes the vertices and the edges.
		'''

		# Check if the input is valid
		assert len(vertices) == 4, 'Invalid input'

		# Get the slice of the points array for the face
		slice_3d = HexBlockVertices.getSurfaceInteriorSlice(vertices)
		point_IDs = slice_3d.getArrayView(self.point_ID)

		return point_IDs

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

		# Get the slice of the points array for the face
		slice_3d = HexBlockVertices.getSurfaceInteriorSlice(vertices)

		point_ID_view = slice_3d.getArrayView(self.point_ID)

		# Check if the input is valid
		assert point_IDs.shape == point_ID_view.shape, 'Invalid input'

		point_ID_view[:, :] = point_IDs

		pass

	def getSurface(self, vertices:tuple[int, int, int, int]) -> NDFaceCollection :
		'''
		Get collection of faces on the surface
		formed by the 4 vertices.
		'''

		# Check if the input is valid
		assert len(vertices) == 4, 'Invalid input'

		face_slices = HexBlockFaces.getSurfaceFaces(vertices)

		face_owners	= face_slices.getOwner(self.cell_ID)
		face_vertices	= face_slices.getVertices(self.point_ID)

		faces = NDFaceCollection(face_owners, face_vertices)

		return faces

	def getInteriorFaces(self) -> tuple[NDFaceCollection, NDFaceCollection, NDFaceCollection] :
		'''
		Get the interior faces of the block
		'''

		face_collections = []

		for ax in range(3) :
			
			face_slices = HexBlockFaces.getInteriorFaces(ax)

			face_owners	= face_slices.getOwner(self.cell_ID)
			face_vertices	= face_slices.getVertices(self.point_ID)
			face_neighbors	= face_slices.getNeighbor(self.cell_ID)
			
			faces = NDFaceCollection(face_owners, face_vertices, face_neighbors)

			face_collections.append(faces)

		return tuple(face_collections)

	def setPointCoordinates(
		self,
		coordinates:np.ndarray
	) -> None :
		'''
		Set the coordinates of the points
		'''

		# Check if the input is valid
		assert isinstance(coordinates, np.ndarray), 'Invalid input'
		assert np.issubdtype(coordinates.dtype, np.floating), 'Invalid input'
		assert coordinates.shape == self.point_coordinates.shape, 'Invalid input'

		assert checkCoordinatesOrientation(coordinates), \
		'Coordinates are not oriented correctly!'

		self.point_coordinates[:, :, :, :] = coordinates.copy()

		pass

	def getCellCenterCoordinates(self) -> np.ndarray :
		'''
		Get the coordinates of the cell centers
		'''

		cell_centers = np.mean(np.stack((
			self.point_coordinates[:-1, :-1, :-1, :],
			self.point_coordinates[:-1, :-1, 1:, :],
			self.point_coordinates[:-1, 1:, :-1, :],
			self.point_coordinates[:-1, 1:, 1:, :],
			self.point_coordinates[1:, :-1, :-1, :],
			self.point_coordinates[1:, :-1, 1:, :],
			self.point_coordinates[1:, 1:, :-1, :],
			self.point_coordinates[1:, 1:, 1:, :]
		), axis=-1), axis=-1)

		return cell_centers

	def getSurfacePointCoordinates(
		self,
		vertices:tuple[int, int, int, int]
	) -> np.ndarray :
		'''
		Get the coordinates of the points on the face
		formed by the 4 vertices.
		Excludes the vertices and the edges.
		'''

		# Check if the input is valid
		assert len(vertices) == 4, 'Invalid input'

		slice_3d = HexBlockVertices.getSurfaceCompleteSlice(vertices)
		point_coordinates = slice_3d.getArrayView(self.point_coordinates)

		return point_coordinates
	