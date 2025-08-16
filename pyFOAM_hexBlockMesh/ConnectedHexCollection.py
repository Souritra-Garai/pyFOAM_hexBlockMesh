import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap

from pyFOAM_hexBlockMesh.HexBlock import HexBlock
from pyFOAM_hexBlockMesh.FaceCollection import FlatFaceCollection
from pyFOAM_hexBlockMesh.connect_utils.ConnectInfo import ConnectInfo
from pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap import hex_face_vertices

class ConnectedHexCollection :
	'''
	A collection of connected hex blocks
	'''

	def __init__(self) -> None :
		'''
		Initialize the collection
		'''
		# List of hex blocks
		self.hex_blocks:list[HexBlock]		= []
		
		# List of ConnectInfo
		self.connect_infos:list[ConnectInfo]	= []

		pass

	def addHexBlock(self, hex_block:HexBlock) -> int :
		'''
		Add a hex block to the collection.
		Return the index of the hex block in the collection.
		'''
		
		assert isinstance(hex_block, HexBlock), 'Invalid hex block'
		
		self.hex_blocks.append(hex_block)
		
		return len(self.hex_blocks) - 1
	
	def isHexFaceConnected(
		self,
		hex_block_id:int,
		face_vertices:tuple[int, int, int, int]
	) -> bool :
		'''
		Check if the face is connected to another hex block
		'''
		
		assert isinstance(hex_block_id, int), 'Invalid hex block id'
		assert isinstance(face_vertices, tuple), 'Invalid face vertices'
		
		flag = False

		# Check if the face is connected to another hex block
		for connect_info in self.connect_infos :
			
			if connect_info.isHexFaceConnected(hex_block_id, face_vertices) :

				flag = True
				break
			
		return flag
	
	def connectHexBlocks(
		self,
		hex_block_id_0:int,
		hex_block_id_1:int,
		face_vertices_0:tuple[int, int, int, int],
		face_vertices_1:tuple[int, int, int, int]
	) -> None :
		'''
		Connect two hex blocks
		'''
		
		connect_info = ConnectInfo(
			hex_block_id_0,
			hex_block_id_1,
			face_vertices_0,
			face_vertices_1
		)

		assert not self.isHexFaceConnected(hex_block_id_0, face_vertices_0), \
			'Hex block 1 is already connected to the face'
		assert not self.isHexFaceConnected(hex_block_id_1, face_vertices_1), \
			'Hex block 2 is already connected to the face'
		
		assert connect_info.isValid(self.hex_blocks), 'Invalid connect info'
		
		self.connect_infos.append(connect_info)
		
		pass

	def assignCellIDs(self, start_ID:int=0) -> int :
		'''
		Assign cell IDs to cells in the hex blocks
		Parameter start_index is the starting index
		Return the number of cells assigned
		'''

		assert isinstance(start_ID, int), 'Invalid start index'

		i = start_ID

		for hex_block in self.hex_blocks :

			# Assign cell indices to the hex block
			i = hex_block.setCellIDs(i)

		self.num_cells = i - start_ID

		return i
	
	def __assignHexVertexPointIDs(self, start_ID:int=0) -> int :
		'''
		Assign IDs to the vertices of hex blocks
		Parameter start_index is the starting index
		Return the number of points + start_index
		'''

		assert isinstance(start_ID, int), 'Invalid start index'

		ID = start_ID

		# Loop over the vertices shared by 2 or more hex blocks
		for connect_info in self.connect_infos :
			
			ID = connect_info.assignVertexPointIDs(self.hex_blocks, ID)

		for hex_block in self.hex_blocks :

			for j in range(8) :
				
				# Check if the vertex is already assigned
				if hex_block.getVertexPointID(j) == -1 :
					
					# Assign the vertex ID
					hex_block.setVertexPointID(j, ID)
					
					ID += 1

		return ID
	
	def __assignHexEdgePointIDs(self, start_ID:int=0) -> int :
		'''
		Assign IDs to the edges of hex blocks
		Parameter start_index is the starting index
		Return the number of points + start_index
		'''

		assert isinstance(start_ID, int), 'Invalid start index'

		ID = start_ID

		# Loop over the edges shared by 2 or more hex blocks
		for connect_info in self.connect_infos :
			
			ID = connect_info.assignEdgePointIDs(self.hex_blocks, ID)

		for hex_block in self.hex_blocks :

			for vertex_pair in HexBlockMap.vertex_connectivity :
				
				# Get the vertex IDs
				vertex_0 = hex_block.getVertexPointID(vertex_pair[0])
				vertex_1 = hex_block.getVertexPointID(vertex_pair[1])

				edge_IDs = \
				hex_block.getEdgePointIDs(vertex_pair[0], vertex_pair[1])

				# Check if the edge is already assigned
				if np.all(edge_IDs == -1) :
					
					# Assign the edge ID
					edge_IDs = np.arange(ID, ID + edge_IDs.shape[0])
					
					hex_block.setEdgePointIDs(
						vertex_pair[0],
						vertex_pair[1],
						edge_IDs
					)
					
					ID += edge_IDs.shape[0]

				else :
					
					# Check if the edge is already assigned
					assert np.all(edge_IDs != -1), f'Edge IDs contain -1!'

		return ID
	
	def __assignFacePointIDs(self, start_ID:int=0) -> int :
		'''
		Assign IDs to the faces of hex blocks
		Parameter start_index is the starting index
		Return the number of points + start_index
		'''

		assert isinstance(start_ID, int), 'Invalid start index'

		ID = start_ID

		for connect_info in self.connect_infos :
			
			ID = connect_info.assignFacePointIDs(self.hex_blocks, ID)

		for hex_block in self.hex_blocks :

			for face_vertices in HexBlockMap.hex_face_vertices :
				
				face_point_IDs = hex_block.getSurfacePointIDs(face_vertices)

				# Check if the face is already assigned
				if np.all(face_point_IDs == -1) :
					
					# Assign the face ID
					face_point_IDs = \
					np.arange(ID, ID + face_point_IDs.size). \
					reshape(face_point_IDs.shape)
					
					hex_block.setSurfacePointIDs(
						face_vertices,
						face_point_IDs
					)
					
					ID += face_point_IDs.size

				else :
					
					# Check if the face is already assigned
					assert np.all(face_point_IDs != -1), \
					f'Face IDs contain -1!'

		return ID
	
	def assignPointIDs(self, start_ID:int=0) -> int :
		'''
		Assign IDs to the points of hex blocks
		Parameter start_index is the starting index
		Return the number of points + start_index
		'''

		assert isinstance(start_ID, int), 'Invalid start index'

		ID = start_ID

		ID = self.__assignHexVertexPointIDs(ID)
		ID = self.__assignHexEdgePointIDs(ID)
		ID = self.__assignFacePointIDs(ID)

		for hex_block in self.hex_blocks :

			ID = hex_block.setInternalPointIDs(ID)

		self.num_points = ID - start_ID

		return ID
	
	def getFaces(self) -> list[FlatFaceCollection] :
		'''
		Get the faces of the hex blocks
		'''

		interior_faces = FlatFaceCollection(name='InteriorFaces')

		for connect_info in self.connect_infos :

			interior_faces.appendNDFaceCollection(
				connect_info.getFaces(self.hex_blocks)
			)

		for hex_block in self.hex_blocks :

			for face_collection in hex_block.getInteriorFaces() :
				
				interior_faces.appendNDFaceCollection(face_collection)

		# Collect the boundary faces
		returned_faces = [interior_faces]

		for i, hex_block in enumerate(self.hex_blocks) :

			for face_vertices in hex_face_vertices :
				
				if not self.isHexFaceConnected(i, face_vertices) :
					
					# Hex_1_Face_0123
					name  = f'Hex_{i}_Face_{"".join(map(str, face_vertices))}'

					faces = FlatFaceCollection(name=name)
					faces.appendNDFaceCollection(
						hex_block.getSurface(face_vertices)
					)

					returned_faces.append(faces)

		return returned_faces

	def getPoints(self) -> np.ndarray :
		'''
		Get the points of the hex blocks
		'''

		points = np.zeros((self.num_points, 3), dtype=float)
		points.fill(np.nan)

		for hex_block in self.hex_blocks :

			points_view = points[hex_block.point_ID, :]
			points_non_nan = ~np.isnan(points_view)
			
			# Assert that the points already assigned are the same
			assert np.all(np.isclose(
				points_view[points_non_nan],
				hex_block.point_coordinates[points_non_nan]
			)), 'Points already assigned are not the same!'

			# Assign the points
			points[hex_block.point_ID, :] = hex_block.point_coordinates

		return points
	
	def getCellCenters(self) -> np.ndarray :
		'''
		Get the centers of the hex blocks
		'''

		cell_centers = np.zeros((self.num_cells, 3), dtype=float)
		cell_centers.fill(np.nan)

		for hex_block in self.hex_blocks :

			cell_centers_view = cell_centers[hex_block.cell_ID, :]
			
			assert np.all(np.isnan(cell_centers_view)), \
			'Cell centers already assigned! Possible overlapping cell IDs'

			# Assign the cell centers
			cell_centers[hex_block.cell_ID, :] = \
			hex_block.getCellCenterCoordinates()

		return cell_centers

	
