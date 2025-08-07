from dataclasses import dataclass

import numpy as np

from pyFOAM_hexBlockMesh.HexBlock import HexBlock
from pyFOAM_hexBlockMesh.FaceCollection import NDFaceCollection
from pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap import hex_face_vertices

def verticesFormHexBlockFace(vertices:tuple[int, int, int, int]) -> bool :
	'''
	Check if the vertices form a hex block face
	'''

	assert isinstance(vertices, tuple), 'Invalid vertices'

	flag = False

	for face_vertices in hex_face_vertices :

		if set(vertices) == set(face_vertices) :
			
			flag = True
			break

	return flag

def getOrderedHexFaceVertices(vertices:tuple[int, int, int, int]) -> tuple[int, int, int, int] :
	'''
	Get the ordered hex face vertices
	'''

	assert isinstance(vertices, tuple), 'Invalid vertices'

	for face_vertices in hex_face_vertices :

		if set(vertices) == set(face_vertices) :
			
			return face_vertices

	# If no match found, return the original vertices
	return vertices

def mapVertices(
	original_vertices_0 :tuple[int, int, int, int],
	mapped_vertices_0   :tuple[int, int, int, int],
	original_vertices_1 :tuple[int, int, int, int]
) -> tuple[int, int, int, int] :
	'''
	Map the original vertices to the new vertices
	'''

	mapped_vertices_1 = [-1, -1, -1, -1]

	for original_vertex_0, original_vertex_1 in zip(original_vertices_0, original_vertices_1) :

		i = mapped_vertices_0.index(original_vertex_0)

		mapped_vertices_1[i] = original_vertex_1

	return tuple(mapped_vertices_1)

@dataclass
class ConnectInfo :

	hex_block_id_0 : int
	hex_block_id_1 : int

	face_vertices_0 : tuple[int, int, int, int]
	face_vertices_1 : tuple[int, int, int, int]

	def __init__(
		self,
		hex_block_id_0:int,
		hex_block_id_1:int,
		face_vertices_0:tuple[int, int, int, int],
		face_vertices_1:tuple[int, int, int, int]
	) -> None :
		'''
		Initialize the connect info
		'''

		assert isinstance(hex_block_id_0, int), 'Invalid hex block id 1'
		assert isinstance(hex_block_id_1, int), 'Invalid hex block id 2'
		
		assert verticesFormHexBlockFace(face_vertices_0), 'Invalid face vertices 1'
		assert verticesFormHexBlockFace(face_vertices_1), 'Invalid face vertices 2'

		assert hex_block_id_0 != hex_block_id_1, 'Hex blocks are the same'

		self.hex_block_id_0 = hex_block_id_0
		self.hex_block_id_1 = hex_block_id_1

		self.face_vertices_0 = getOrderedHexFaceVertices(face_vertices_0)
		self.face_vertices_1 = mapVertices(
			face_vertices_0,
			self.face_vertices_0,
			face_vertices_1
		)

		pass

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
		
		if	self.hex_block_id_0 == hex_block_id and \
			set(self.face_vertices_0) == set(face_vertices) :
			
			return True
		
		elif	self.hex_block_id_1 == hex_block_id and \
			set(self.face_vertices_1) == set(face_vertices) :
			
			return True
		
		# If no connection found, return False
		return False
	
	def assignVertexPointIDs(self, hex_blocks:list[HexBlock], start_ID:int=0) -> int :
		'''
		Assign vertex point IDs to vertices of connected hex blocks
		'''

		assert isinstance(start_ID, int), 'Invalid start ID'

		ID = start_ID

		for j in range(4) :
			
			vertex_ID_1 = \
			hex_blocks[self.hex_block_id_0].getVertexPointID(self.face_vertices_0[j])
			vertex_ID_2 = \
			hex_blocks[self.hex_block_id_1].getVertexPointID(self.face_vertices_1[j])

			if vertex_ID_1 == -1 and vertex_ID_2 == -1 :
				
				# Assign new ID to the vertex
				hex_blocks[self.hex_block_id_0].setVertexPointID(
					self.face_vertices_0[j], ID
				)
				hex_blocks[self.hex_block_id_1].setVertexPointID(
					self.face_vertices_1[j], ID
				)

				ID += 1

			elif vertex_ID_1 == -1 and vertex_ID_2 != -1 :

				# Assign the ID of the vertex to the other hex block
				hex_blocks[self.hex_block_id_0].setVertexPointID(
					self.face_vertices_0[j], vertex_ID_2
				)

			elif vertex_ID_1 != -1 and vertex_ID_2 == -1 :

				# Assign the ID of the vertex to the other hex block
				hex_blocks[self.hex_block_id_1].setVertexPointID(
					self.face_vertices_1[j], vertex_ID_1
				)

			elif vertex_ID_1 != -1 and vertex_ID_2 != -1 :

				assert vertex_ID_1 == vertex_ID_2, \
				f'Vertex IDs are different: ' \
				f'Hex block {self.hex_block_id_0} ID {vertex_ID_1}, ' \
				f'Hex block {self.hex_block_id_1} ID {vertex_ID_2}'

		return ID

	def assignEdgePointIDs(self, hex_blocks:list[HexBlock], start_ID:int=0) -> int :
		'''
		Assign edge point IDs to edges of connected hex blocks
		'''

		assert isinstance(start_ID, int), 'Invalid start ID'

		ID = start_ID

		for j0 in range(4) :

			j1 = (j0 + 1) % 4
			
			edge_IDs_1 = hex_blocks[self.hex_block_id_0].getEdgePointIDs(
				self.face_vertices_0[j0],
				self.face_vertices_0[j1]
			)
			edge_IDs_2 = hex_blocks[self.hex_block_id_1].getEdgePointIDs(
				self.face_vertices_1[j0],
				self.face_vertices_1[j1]
			)

			if np.all(edge_IDs_1 == -1) and np.all(edge_IDs_2 == -1) :

				new_edge_IDs = np.arange(ID, ID + edge_IDs_1.shape[0])
				
				# Assign new ID to the edge
				hex_blocks[self.hex_block_id_0].setEdgePointIDs(
					self.face_vertices_0[j0],
					self.face_vertices_0[j1],
					new_edge_IDs
				)
				hex_blocks[self.hex_block_id_1].setEdgePointIDs(
					self.face_vertices_1[j0],
					self.face_vertices_1[j1],
					new_edge_IDs
				)

				ID += edge_IDs_1.shape[0]

			elif np.all(edge_IDs_1 == -1) and np.all(edge_IDs_2 != -1) :

				# Assign the ID of the edge to the other hex block
				hex_blocks[self.hex_block_id_0].setEdgePointIDs(
					self.face_vertices_0[j0],
					self.face_vertices_0[j1],
					edge_IDs_2
				)

			elif np.all(edge_IDs_1 != -1) and np.all(edge_IDs_2 == -1) :

				# Assign the ID of the edge to the other hex block
				hex_blocks[self.hex_block_id_1].setEdgePointIDs(
					self.face_vertices_1[j0],
					self.face_vertices_1[j1],
					edge_IDs_1
				)

			elif np.all(edge_IDs_1 != -1) and np.all(edge_IDs_2 != -1) :

				assert np.all(edge_IDs_1 == edge_IDs_2), \
				f'Edge IDs are different: ' \
				f'Hex block {self.hex_block_id_0} ID {edge_IDs_1}, ' \
				f'Hex block {self.hex_block_id_1} ID {edge_IDs_2}'

		return ID
		
	def assignFacePointIDs(self, hex_blocks:list[HexBlock], start_ID:int=0) -> int :
		'''
		Assign face point IDs to faces of connected hex blocks
		'''

		assert isinstance(start_ID, int), 'Invalid start ID'

		ID = start_ID

		face_point_IDs_1 = \
		hex_blocks[self.hex_block_id_0].getSurfacePointIDs(self.face_vertices_0)
		face_point_IDs_2 = \
		hex_blocks[self.hex_block_id_1].getSurfacePointIDs(self.face_vertices_1)

		assert np.all(face_point_IDs_1 == -1) and np.all(face_point_IDs_2 == -1), \
		f'Face point IDs are not -1: ' \
		f'Hex block {self.hex_block_id_0} ID {face_point_IDs_1}, ' \
		f'Hex block {self.hex_block_id_1} ID {face_point_IDs_2}'

		# Assign new ID to the face
		new_face_point_IDs = \
		np.arange(ID, ID + face_point_IDs_1.size).reshape(face_point_IDs_1.shape)

		hex_blocks[self.hex_block_id_0].setSurfacePointIDs(
			self.face_vertices_0,
			new_face_point_IDs
		)
		hex_blocks[self.hex_block_id_1].setSurfacePointIDs(
			self.face_vertices_1,
			new_face_point_IDs
		)

		ID += face_point_IDs_1.size

		return ID
	
	def isValid(self, hex_blocks:list[HexBlock]) -> bool :
		'''
		Check if the connect info is valid
		'''

		assert isinstance(hex_blocks, list), 'Invalid hex blocks'
		assert len(hex_blocks) > 0, 'Hex blocks are empty'

		points_1 = \
		hex_blocks[self.hex_block_id_0].getSurfacePointCoordinates(self.face_vertices_0)
		points_2 = \
		hex_blocks[self.hex_block_id_1].getSurfacePointCoordinates(self.face_vertices_1)

		return bool(np.isclose(points_1, points_2).all())
	
	def getFaces(self, hex_blocks:list[HexBlock]) -> NDFaceCollection :
		'''
		Get the faces of the connected hex blocks
		'''

		assert isinstance(hex_blocks, list), 'Invalid hex blocks'
		assert len(hex_blocks) > 0, 'Hex blocks are empty'

		faces_1 = hex_blocks[self.hex_block_id_0].getSurface(self.face_vertices_0)
		faces_2 = hex_blocks[self.hex_block_id_1].getSurface(self.face_vertices_1)

		assert np.all(faces_1.vertices == faces_2.vertices), \
		f'Faces are different: ' \
		f'Hex block {self.hex_block_id_0} faces {faces_1}, ' \
		f'Hex block {self.hex_block_id_1} faces {faces_2}'

		faces_1.assignNeighbour(faces_2.owner)

		return faces_1
	
	