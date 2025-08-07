import unittest
import numpy as np

from pyFOAM_hexBlockMesh.HexBlock import HexBlock
from pyFOAM_hexBlockMesh.connect_utils.ConnectInfo import ConnectInfo

def setUpHexBlocks() -> list[HexBlock] :
	'''
	Set up a list of hex blocks for testing
	'''
	
	hex_blocks = [
		HexBlock(2, 2, 2),
		HexBlock(2, 2, 2)
	]

	return hex_blocks

class TestConnectInfo(unittest.TestCase) :

	def test_isHexFaceConnected(self) :

		hex_blocks = setUpHexBlocks()
		connect_info = ConnectInfo(
			0, 1,
			(0, 1, 2, 3), (4, 5, 6, 7)
		)

		self.assertTrue(connect_info.isHexFaceConnected(0, (3, 2, 1, 0)))

		pass

	def test_assignVertexPointIDs(self) :
		'''
		Test the assignVertexPointIDs method
		'''

		hex_blocks = setUpHexBlocks()
		connect_info = ConnectInfo(
			0, 1,
			(0, 1, 2, 3), (4, 5, 6, 7)
		)

		hex_blocks[0].setVertexPointID(0, 0)
		hex_blocks[1].setVertexPointID(5, 1)
		hex_blocks[0].setVertexPointID(2, 2)
		hex_blocks[1].setVertexPointID(6, 2)

		connect_info.assignVertexPointIDs(hex_blocks, 1)

		self.assertEqual(
			hex_blocks[1].getVertexPointID(4),
			hex_blocks[0].getVertexPointID(0)
		)
		self.assertEqual(
			hex_blocks[1].getVertexPointID(5),
			hex_blocks[0].getVertexPointID(1)
		)
		self.assertEqual(
			hex_blocks[1].getVertexPointID(6),
			hex_blocks[0].getVertexPointID(2)
		)
		self.assertEqual(
			hex_blocks[1].getVertexPointID(7),
			hex_blocks[0].getVertexPointID(3)
		)

		pass		

	def test_assignEdgePointIDs(self) :
		'''
		Test the assignEdgePointIDs method
		'''
		
		hex_blocks = setUpHexBlocks()
		connect_info = ConnectInfo(
			0, 1,
			(0, 1, 2, 3), (4, 5, 6, 7)
		)

		point_ID = connect_info.assignVertexPointIDs(hex_blocks)

		hex_blocks[0].setEdgePointIDs(
			0, 1,
			np.array([point_ID])
		)
		point_ID += 1

		hex_blocks[1].setEdgePointIDs(
			5, 6,
			np.array([point_ID])
		)
		point_ID += 1

		hex_blocks[0].setEdgePointIDs(
			2, 3,
			np.array([point_ID])
		)
		hex_blocks[1].setEdgePointIDs(
			6, 7,
			np.array([point_ID])
		)
		point_ID += 1

		connect_info.assignEdgePointIDs(hex_blocks, point_ID)

		for j0 in range(4) :
			j1 = (j0 + 1) % 4
			
			edge_IDs_0 = hex_blocks[0].getEdgePointIDs(
				connect_info.face_vertices_0[j0],
				connect_info.face_vertices_0[j1]
			)
			edge_IDs_1 = hex_blocks[1].getEdgePointIDs(
				connect_info.face_vertices_1[j0],
				connect_info.face_vertices_1[j1]
			)

			np.testing.assert_array_equal(
				edge_IDs_0,
				edge_IDs_1
			)

		pass

	def test_assignFacePointIDs(self) :
		'''
		Test the assignFacePointIDs method
		'''

		hex_blocks = setUpHexBlocks()
		connect_info = ConnectInfo(
			0, 1,
			(0, 1, 2, 3), (4, 5, 6, 7)
		)

		point_ID = connect_info.assignVertexPointIDs(hex_blocks)

		point_ID = connect_info.assignEdgePointIDs(hex_blocks, point_ID)

		connect_info.assignFacePointIDs(hex_blocks, point_ID)

		self.assertEqual(
			hex_blocks[0].getSurfacePointIDs((0, 1, 2, 3)),
			np.array([[8]])
		)
		self.assertEqual(
			hex_blocks[1].getSurfacePointIDs((4, 5, 6, 7)),
			np.array([[8]])
		)

		pass

	def test_getFaces(self) :
		'''
		Test the getFaces method
		'''

		hex_blocks = setUpHexBlocks()
		connect_info = ConnectInfo(
			0, 1,
			(0, 1, 2, 3), (4, 5, 6, 7)
		)
		
		point_ID = connect_info.assignVertexPointIDs(hex_blocks)
		point_ID = connect_info.assignEdgePointIDs(hex_blocks, point_ID)
		point_ID = connect_info.assignFacePointIDs(hex_blocks, point_ID)

		point_ID = hex_blocks[0].setInternalPointIDs(point_ID)
		point_ID = hex_blocks[1].setInternalPointIDs(point_ID)

		cell_ID = hex_blocks[0].setCellIDs()
		cell_ID = hex_blocks[1].setCellIDs(cell_ID)

		faces = connect_info.getFaces(hex_blocks)

		expected_owner = np.array([
			[0, 1],
			[2, 3],
		])

		expected_neighbour = np.array([
			[12, 13],
			[14, 15],
		])

		expected_vertices = np.array([
			[
				[0, 4, 8, 7],
				[7, 8, 6, 3],
			],
			[
				[4, 1, 5, 8],
				[8, 5, 2, 6],
			],
		])

		np.testing.assert_array_equal(
			faces.owner,
			expected_owner
		)
		np.testing.assert_array_equal(
			faces.neighbour,
			expected_neighbour
		)
		np.testing.assert_array_equal(
			faces.vertices,
			expected_vertices
		)

		pass

if __name__ == '__main__':
		
	unittest.main()