import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices

from pyFOAM_hexBlockMesh.HexBlock import HexBlock
from pyFOAM_hexBlockMesh.FaceCollection import NDFaceCollection
from pyFOAM_hexBlockMesh.expansion_utils.SingleCell import SingleCell2DGrid

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

	def setUpSingleCellGridPoints(self) -> None :

		point_IDs = self.cells_base.point_ID[:, :, -1]
		# Top hat
		self.cells_hat.point_ID[:, :, 0, 0, 0] = point_IDs[1::3, :-1:3]
		self.cells_hat.point_ID[:, :, 1, 0, 0] = point_IDs[2::3, :-1:3]
		self.cells_hat.point_ID[:, :, 0, 1, 0] = point_IDs[1::3, 3::3]
		self.cells_hat.point_ID[:, :, 1, 1, 0] = point_IDs[2::3, 3::3]
		self.cells_hat.point_ID[:, :, 0, 0, 1] = point_IDs[:-1:3, :-1:3]
		self.cells_hat.point_ID[:, :, 1, 0, 1] = point_IDs[ 3::3, :-1:3]
		self.cells_hat.point_ID[:, :, 0, 1, 1] = point_IDs[:-1:3, 3::3]
		self.cells_hat.point_ID[:, :, 1, 1, 1] = point_IDs[ 3::3, 3::3]
		# Hidden
		self.cells_hidden.point_ID[:, :, 0, 0, 0] = point_IDs[1::3, 1::3]
		self.cells_hidden.point_ID[:, :, 1, 0, 0] = point_IDs[2::3, 1::3]
		self.cells_hidden.point_ID[:, :, 0, 1, 0] = point_IDs[1::3, 2::3]
		self.cells_hidden.point_ID[:, :, 1, 1, 0] = point_IDs[2::3, 2::3]
		self.cells_hidden.point_ID[:, :, 0, 0, 1] = point_IDs[1::3, :-1:3]
		self.cells_hidden.point_ID[:, :, 1, 0, 0] = point_IDs[2::3, :-1:3]
		self.cells_hidden.point_ID[:, :, 0, 1, 0] = point_IDs[1::3, 3::3]
		self.cells_hidden.point_ID[:, :, 1, 1, 0] = point_IDs[2::3, 3::3]
		# Lateral 0
		self.cells_lateral[0].point_ID[:, :, 0, 0, 0] = point_IDs[:-1:3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 1, 0, 0] = point_IDs[ 1::3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 0, 1, 0] = point_IDs[:-1:3, 2::3]
		self.cells_lateral[0].point_ID[:, :, 1, 1, 0] = point_IDs[ 1::3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 0, 0, 1] = point_IDs[:-1:3, :-1:3]
		self.cells_lateral[0].point_ID[:, :, 1, 0, 1] = point_IDs[ 1::3, :-1:3]
		self.cells_lateral[0].point_ID[:, :, 0, 1, 1] = point_IDs[:-1:3, 3::3]
		self.cells_lateral[0].point_ID[:, :, 1, 1, 1] = point_IDs[ 1::3, 3::3]
		# Lateral 0
		self.cells_lateral[0].point_ID[:, :, 0, 0, 0] = point_IDs[:-1:3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 1, 0, 0] = point_IDs[ 1::3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 0, 1, 0] = point_IDs[:-1:3, 2::3]
		self.cells_lateral[0].point_ID[:, :, 1, 1, 0] = point_IDs[ 1::3, 1::3]
		self.cells_lateral[0].point_ID[:, :, 0, 0, 1] = point_IDs[:-1:3, :-1:3]
		self.cells_lateral[0].point_ID[:, :, 1, 0, 1] = point_IDs[ 1::3, :-1:3]
		self.cells_lateral[0].point_ID[:, :, 0, 1, 1] = point_IDs[:-1:3, 3::3]
		self.cells_lateral[0].point_ID[:, :, 1, 1, 1] = point_IDs[ 1::3, 3::3]
		# Lateral 1
		self.cells_lateral[1].point_ID[:, :, 0, 0, 0] = point_IDs[2::3, 1::3]
		self.cells_lateral[1].point_ID[:, :, 1, 0, 0] = point_IDs[3::3, 1::3]
		self.cells_lateral[1].point_ID[:, :, 0, 1, 0] = point_IDs[2::3, 2::3]
		self.cells_lateral[1].point_ID[:, :, 1, 1, 0] = point_IDs[3::3, 1::3]
		self.cells_lateral[1].point_ID[:, :, 0, 0, 1] = point_IDs[2::3, :-1:3]
		self.cells_lateral[1].point_ID[:, :, 1, 0, 1] = point_IDs[3::3, :-1:3]
		self.cells_lateral[1].point_ID[:, :, 0, 1, 1] = point_IDs[2::3, 3::3]
		self.cells_lateral[1].point_ID[:, :, 1, 1, 1] = point_IDs[3::3, 3::3]

		pass

	def setInternalPointIDs(self, start_ID:int=0) -> int :
		'''
		Set the point IDs for the internal points
		'''
		points_shape = self.cells_base.point_ID.shape[:2]
		num_points = np.prod([n-2 for n in points_shape])

		# Assign consecutive point IDs to the internal points
		# Varying fastest along axis 0, then axis 1, then axis 2
		# Skip the points on the boundary surfaces
		# The first and last indices along each axis represent the boundary points
		point_IDs = np.arange(
			start_ID,
			start_ID + num_points
		).reshape(points_shape, order='F')

		self.cells_base.setSurfacePointIDs((4, 5, 6, 7), point_IDs)

		self.setUpSingleCellGridPoints()

		return start_ID + int(num_points)

	def getFaceShape(self, vertices:tuple) -> tuple :
		'''
		Get the shape (cells) of the face
		'''
		# Check if the input is valid
		assert len(vertices) == 4, 'Invalid input'

		if set(vertices) == set((0, 1, 2, 3)) :

			return self.cells_base.getFaceShape(vertices)

		else :

			return self.cells_hat.getFaceShape(vertices)

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
		Set the IDs of points along the edge from v0 to v1.
		Excludes the vertices.
		'''
		# Check if the input is valid
		assert isinstance(point_IDs, np.ndarray) and point_IDs.dtype == int,	\
		'Invalid input'

		if set((v0, v1)).issubset(set((4, 5, 6, 7))) :

			point_IDs_view = self.cells_base.getEdgePointIDs(v0, v1)[2::3]

			assert point_IDs.shape == point_IDs_view.shape, 'Invalid input'

			point_IDs_view[:] = point_IDs

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
			case _ :
				# Lateral face — use the top edge of the base cells
				# (at coarse end, ax2=last),
				# slicing out the Schneider cell boundaries
				# (positions where index % 3 == 0)

				surface_slice = HexBlockVertices.getSurfaceCompleteSlice(vertices)
				surface_slice.slices[surface_slice.axes.index(2)] = -1

				point_IDs = surface_slice.getArrayView(self.cells_base.point_ID)

				return point_IDs[np.arange(point_IDs.shape[0]) % 3 != 0]

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

				point_IDs_view = self.cells_base.getSurfacePointIDs(vertices)
				point_IDs_view[2::3, 2::3] = point_IDs

			case _ :

				surface_slice = HexBlockVertices.getSurfaceCompleteSlice(vertices)
				surface_slice.slices[surface_slice.axes.index(2)] = -1

				edge_view = surface_slice.getArrayView(self.cells_base.point_ID)
				mask      = np.arange(len(edge_view)) % 3 != 0

				assert point_IDs.shape == (mask.sum(),), \
				f'Shape mismatch : expected {(mask.sum(),)}, got {point_IDs.shape}'

				edge_view[mask] = point_IDs

	def getSurface(
		self,
		vertices:tuple[int, int, int, int]
	) -> NDFaceCollection | tuple[NDFaceCollection, NDFaceCollection] :
		'''
		Get collection of faces on the surface formed by the 4 vertices.
		'''
		match set(vertices) :

			case set((0, 1, 2, 3)) : return self.cells_base.getSurface(vertices)

			case set((4, 5, 6, 7)) : return self.cells_hat.getSurface(vertices)

			case set((0, 1, 5, 4)) | set((3, 2, 6, 7)) :

				return	self.cells_base.getSurface(vertices), \
					self.cells_hat.getSurface(vertices)

			case set((0, 3, 7, 4)) :

				return	self.cells_base.getSurface(vertices), \
					self.cells_lateral[0].getSurface(vertices)

			case set((1, 2, 6, 5)) :

				return	self.cells_base.getSurface(vertices), \
					self.cells_lateral[1].getSurface(vertices)

			case _ : raise NotImplementedError

	def getInteriorFaces(self) -> tuple[NDFaceCollection, ...] :
		'''
		Get the interior faces of the block
		'''

		face_collections = []

		face_collections.extend(self.cells_base.getInteriorFaces())

		base_faces = self.cells_base.getSurface((4, 5, 6, 7))

		neighbours = np.full_like(base_faces.owner, -1)

		neighbours[::3,  ::3] = self.cells_lateral[0].cell_ID
		neighbours[::3, 1::3] = self.cells_lateral[0].cell_ID
		neighbours[::3, 2::3] = self.cells_lateral[0].cell_ID

		neighbours[1::3,  ::3] = self.cells_hidden.cell_ID
		neighbours[1::3, 1::3] = self.cells_hidden.cell_ID
		neighbours[1::3, 2::3] = self.cells_hidden.cell_ID

		neighbours[2::3,  ::3] = self.cells_lateral[1].cell_ID
		neighbours[2::3, 1::3] = self.cells_lateral[1].cell_ID
		neighbours[2::3, 2::3] = self.cells_lateral[1].cell_ID

		base_faces.assignNeighbour(neighbours)

		face_collections.append(base_faces)

		interior_lateral_0_hidden = self.cells_lateral[0].getAllFaces((1, 2, 6, 5))
		interior_lateral_0_hidden.assignNeighbour(self.cells_hidden.cell_ID)

		face_collections.append(interior_lateral_0_hidden)

		interior_hidden_lateral_1 = self.cells_hidden.getAllFaces((1, 2, 6, 5))
		interior_hidden_lateral_1.assignNeighbour(self.cells_lateral[1].cell_ID)

		face_collections.append(interior_hidden_lateral_1)

		interior_lateral_1_lateral_0 = self.cells_lateral[1].getAllFaces((1, 2, 6, 5))
		interior_lateral_1_lateral_0.owner = interior_lateral_1_lateral_0.owner[:-1, :]
		interior_lateral_1_lateral_0.vertices = interior_lateral_1_lateral_0.vertices[:-1, :, :]
		interior_lateral_1_lateral_0.assignNeighbour(self.cells_lateral[0].cell_ID[1:, :])

		face_collections.append(interior_lateral_1_lateral_0)

		interior_lateral_0_hat = self.cells_lateral[0].getAllFaces((4, 5, 6, 7))
		interior_lateral_0_hat.assignNeighbour(self.cells_hat.cell_ID)

		face_collections.append(interior_lateral_0_hat)

		interior_hat_lateral_1 = self.cells_hat.getAllFaces((4, 5, 6, 7))
		interior_hat_lateral_1.assignNeighbour(self.cells_lateral[1].cell_ID)

		face_collections.append(interior_hat_lateral_1)

		interior_hat_hat = self.cells_hat.getAllFaces((2, 6, 7, 3))
		interior_hat_hat.owner = interior_hat_hat.owner[:, :-1]
		interior_hat_hat.vertices = interior_hat_hat.vertices[:, :-1, :]
		interior_hat_hat.assignNeighbour(self.cells_hat.cell_ID[:, 1:])

		face_collections.append(interior_hat_hat)

		return tuple(face_collections)

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
