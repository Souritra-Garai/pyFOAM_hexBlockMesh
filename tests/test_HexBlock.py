import unittest

import numpy as np

import pyFOAM_hexBlockMesh.HexBlock as HexBlock

from pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap import vertex_connectivity, hex_face_vertices

def setUpBlock(block:HexBlock.HexBlock) :
	'''
	Set up the point IDs of a 3x3x3 HexBlock
	'''

	block.setVertexPointID(0, 0)
	block.setEdgePointIDs(0, 1, np.array([1]))
	block.setVertexPointID(1, 2)
	block.setEdgePointIDs(0, 3, np.array([3]))
	block.setSurfacePointIDs((0, 1, 2, 3), np.array([[4]]))
	block.setEdgePointIDs(1, 2, np.array([5]))
	block.setVertexPointID(3, 6)
	block.setEdgePointIDs(3, 2, np.array([7]))
	block.setVertexPointID(2, 8)

	block.setEdgePointIDs(0, 4, np.array([9]))
	block.setSurfacePointIDs((0, 1, 5, 4), np.array([[10]]))
	block.setEdgePointIDs(1, 5, np.array([11]))
	block.setSurfacePointIDs((0, 3, 7, 4), np.array([[12]]))
	block.setInternalPointIDs(start_ID=13)
	block.setSurfacePointIDs((1, 5, 6, 2), np.array([[14]]))
	block.setEdgePointIDs(3, 7, np.array([15]))
	block.setSurfacePointIDs((3, 2, 6, 7), np.array([[16]]))
	block.setEdgePointIDs(2, 6, np.array([17]))

	block.setVertexPointID(4, 18)
	block.setEdgePointIDs(4, 5, np.array([19]))
	block.setVertexPointID(5, 20)
	block.setEdgePointIDs(4, 7, np.array([21]))
	block.setSurfacePointIDs((4, 5, 6, 7), np.array([[22]]))
	block.setEdgePointIDs(5, 6, np.array([23]))
	block.setVertexPointID(7, 24)
	block.setEdgePointIDs(7, 6, np.array([25]))
	block.setVertexPointID(6, 26)

	pass

class TestHexBlock(unittest.TestCase) :
	'''
	Test the HexBlock class
	'''

	def test_setCellIDs(self) :
		'''
		Test the setCellIDs method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)

		expected_cell_ID = np.array([
			[[0, 4], [2, 6]],
			[[1, 5], [3, 7]]
		])

		np.testing.assert_array_equal(block.cell_ID, expected_cell_ID)

		pass

	def test_setPointIDs(self) :
		'''
		Test the setInternalPointIDs method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		setUpBlock(block)

		expected_point_ID = np.array([
			[[ 0,  9, 18], [ 3, 12, 21], [ 6, 15, 24]],
			[[ 1, 10, 19], [ 4, 13, 22], [ 7, 16, 25]],
			[[ 2, 11, 20], [ 5, 14, 23], [ 8, 17, 26]]
		])
			
		np.testing.assert_array_equal(block.point_ID, expected_point_ID)

		pass

	def test_getEdgePointIDs(self) :
		'''
		Test the getEdgePointIDs method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		block.setInternalPointIDs(start_ID=0)

		block.setEdgePointIDs(3, 7, np.array([15]))

		edge_point_IDs = block.getEdgePointIDs(7, 3)

		expected_edge_point_IDs = np.array([15])

		np.testing.assert_array_equal(edge_point_IDs, expected_edge_point_IDs)

		pass

	def test_getSurfacePointIDs(self) :
		'''
		Test the getSurfacePointIDs method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		block.setInternalPointIDs(start_ID=0)
		block.setSurfacePointIDs((0, 1, 5, 4), np.array([[15]]))

		surface_point_IDs = block.getSurfacePointIDs((1, 5, 4, 0))

		expected_surface_point_IDs = np.array([[15]])

		np.testing.assert_array_equal(surface_point_IDs, expected_surface_point_IDs)
		
		pass

	def test_getSurface(self) :
		'''
		Test the getSurface method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		setUpBlock(block)

		surface = block.getSurface((1, 5, 4, 0))

		expected_surface_owner = np.array([[1, 0], [5, 4]])
		expected_surface_vertices = np.array([
			[[ 2, 11, 10,  1], [ 1, 10,  9,  0]],
			[[11, 20, 19, 10], [10, 19, 18,  9]],
		])

		np.testing.assert_array_equal(surface.owner, expected_surface_owner)
		np.testing.assert_array_equal(surface.vertices, expected_surface_vertices)
		
		pass

	def test_getInteriorFaces_1(self) :
		'''
		Test the getInteriorFaces method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		setUpBlock(block)

		faces_collection = block.getInteriorFaces()

		expected_face_owners_0 = np.array([
			[[0], [4]], [[2], [6]],
		])

		expected_face_neighbours_0 = np.array([
			[[1], [5]], [[3], [7]],
		])

		expected_face_vertices_0 = np.array([
			[
				[[ 1,  4, 13, 10]],
				[[10, 13, 22, 19]],
			],
			[
				[[ 4, 7, 16, 13]],
				[[13, 16, 25, 22]],
			]
		])

		expected_face_owners_1 = np.array([
			[[0], [1]], [[4], [5]],
		])

		expected_face_neighbours_1 = np.array([
			[[2], [3]], [[6], [7]],
		])

		expected_face_vertices_1 = np.array([
			[
				[[ 3, 12, 13,  4]],
				[[ 4, 13, 14,  5]],
			],
			[
				[[12, 21, 22, 13]],
				[[13, 22, 23, 14]],
			]
		])

		expected_face_owners_2 = np.array([
			[[0], [2]], [[1], [3]],
		])

		expected_face_neighbours_2 = np.array([
			[[4], [6]], [[5], [7]],
		])

		expected_face_vertices_2 = np.array([
			[
				[[ 9, 10, 13, 12]],
				[[12, 13, 16, 15]],
			],
			[
				[[10, 11, 14, 13]],
				[[13, 14, 17, 16]],
			]
		])

		np.testing.assert_array_equal(faces_collection[0].owner, expected_face_owners_0)
		np.testing.assert_array_equal(faces_collection[0].vertices, expected_face_vertices_0)
		np.testing.assert_array_equal(faces_collection[0].neighbour, expected_face_neighbours_0)

		np.testing.assert_array_equal(faces_collection[1].owner, expected_face_owners_1)
		np.testing.assert_array_equal(faces_collection[1].vertices, expected_face_vertices_1)
		np.testing.assert_array_equal(faces_collection[1].neighbour, expected_face_neighbours_1)

		np.testing.assert_array_equal(faces_collection[2].owner, expected_face_owners_2)
		np.testing.assert_array_equal(faces_collection[2].vertices, expected_face_vertices_2)
		np.testing.assert_array_equal(faces_collection[2].neighbour, expected_face_neighbours_2)

		pass

	def test_getInteriorFaces_2(self) :
		'''
		Test the getInteriorFaces method
		with a larger block
		'''

		block = HexBlock.HexBlock(2, 3, 2)

		block.setCellIDs(start_ID=0)
		
		point_ID = 0
		
		for v in range(8) :
			
			block.setVertexPointID(v, point_ID)
			point_ID += 1

		for vertex_pair in vertex_connectivity.keys() :
			
			n = block.getEdgePointIDs(vertex_pair[0], vertex_pair[1]).size
			block.setEdgePointIDs(*vertex_pair, np.arange(point_ID, point_ID + n))
			point_ID += n

		for surface_vertices in hex_face_vertices :
			
			shape = block.getSurfacePointIDs(surface_vertices).shape
			n = np.prod(shape, dtype=int)
			block.setSurfacePointIDs(surface_vertices, np.arange(point_ID, point_ID + n).reshape(shape))
			point_ID += n

		block.setInternalPointIDs(start_ID=int(point_ID))
		block.setCellIDs(start_ID=0)

		expected_vertex_ID = np.array([
			[
				[ 0, 20,  4],
				[12, 30, 18],
				[13, 31, 19],
				[ 3, 23,  7],
				
			],
			[
				[ 8, 28, 11],
				[24, 34, 26],
				[25, 35, 27],
				[ 9, 29, 10],
			],
			[
				[ 1, 21,  5],
				[14, 32, 16],
				[15, 33, 17],
				[ 2, 22,  6],
			],
		])

		expected_cell_ID = np.array([
			[
				[ 0,  6],
				[ 2,  8],
				[ 4, 10],
			],
			[
				[ 1,  7],
				[ 3,  9],
				[ 5, 11],
			]
		])

		np.testing.assert_array_equal(block.point_ID, expected_vertex_ID)
		np.testing.assert_array_equal(block.cell_ID, expected_cell_ID)

		faces_collection = block.getInteriorFaces()

		expected_face_owners_0 = np.array([
			[[ 0], [ 6]],
			[[ 2], [ 8]],
			[[ 4], [10]],
		])

		expected_face_neighbours_0 = np.array([
			[[ 1], [ 7]],
			[[ 3], [ 9]],
			[[ 5], [11]],
		])

		expected_vertices_0 = np.array([
			[
				[[ 8, 24, 34, 28]],
				[[28, 34, 26, 11]],
			],
			[
				[[24, 25, 35, 34]],
				[[34, 35, 27, 26]],
			],
			[
				[[25,  9, 29, 35]],
				[[35, 29, 10, 27]],
			]
		])

		expected_face_owners_1 = np.array([
			[
				[ 0,  2],
				[ 1,  3],
			],
			[
				[ 6,  8],
				[ 7,  9],
			],

		])

		expected_face_neighbours_1 = np.array([
			[
				[ 2,  4],
				[ 3,  5],
			],
			[
				[ 8, 10],
				[ 9, 11],
			],
		])

		expected_vertices_1 = np.array([
			[
				[
					[12, 30, 34, 24],
					[13, 31, 35, 25],
				],
				[
					[24, 34, 32, 14],
					[25, 35, 33, 15],
				],
			],
			[
				[
					[30, 18, 26, 34],
					[31, 19, 27, 35],
				],
				[
					[34, 26, 16, 32],
					[35, 27, 17, 33],
				],
			]
		])

		np.testing.assert_array_equal(faces_collection[0].owner, expected_face_owners_0)
		np.testing.assert_array_equal(faces_collection[0].vertices, expected_vertices_0)
		np.testing.assert_array_equal(faces_collection[0].neighbour, expected_face_neighbours_0)

		np.testing.assert_array_equal(faces_collection[1].owner, expected_face_owners_1)
		np.testing.assert_array_equal(faces_collection[1].vertices, expected_vertices_1)
		np.testing.assert_array_equal(faces_collection[1].neighbour, expected_face_neighbours_1)

		pass

	def test_getSurfacePointCoordinates(self) :
		'''
		Test the getSurfaceCoordinates method
		'''

		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		setUpBlock(block)

		x = np.linspace(0, 1, 3)
		y = np.linspace(1, 2, 3)
		z = np.linspace(2, 3, 3)

		grid_x, grid_y, grid_z = np.meshgrid(x, y, z, indexing='ij')
		volume_coordinates = np.stack((grid_x, grid_y, grid_z), axis=-1)

		block.setPointCoordinates(volume_coordinates)

		expected_coordinates = np.array([
			[
				[
					[0.0, 1.0, 2.0],
					[0.0, 1.0, 2.5],
					[0.0, 1.0, 3.0],
				],
				[
					[0.0, 1.5, 2.0],
					[0.0, 1.5, 2.5],
					[0.0, 1.5, 3.0],
				],
				[
					[0.0, 2.0, 2.0],
					[0.0, 2.0, 2.5],
					[0.0, 2.0, 3.0],
				],
			],
			[
				[
					[0.5, 1.0, 2.0],
					[0.5, 1.0, 2.5],
					[0.5, 1.0, 3.0],
				],
				[
					[0.5, 1.5, 2.0],
					[0.5, 1.5, 2.5],
					[0.5, 1.5, 3.0],
				],
				[
					[0.5, 2.0, 2.0],
					[0.5, 2.0, 2.5],
					[0.5, 2.0, 3.0],
				],
			],
			[
				[
					[1.0, 1.0, 2.0],
					[1.0, 1.0, 2.5],
					[1.0, 1.0, 3.0],
				],
				[
					[1.0, 1.5, 2.0],
					[1.0, 1.5, 2.5],
					[1.0, 1.5, 3.0],
				],
				[
					[1.0, 2.0, 2.0],
					[1.0, 2.0, 2.5],
					[1.0, 2.0, 3.0],
				],
			], 
		])

		np.testing.assert_array_equal(block.point_coordinates, expected_coordinates)

		surface_coordinates = block.getSurfacePointCoordinates((7, 3, 2, 6))

		expected_surface_coordinates = np.array([
			[
				[0.0, 2.0, 3.0],
				[0.5, 2.0, 3.0],
				[1.0, 2.0, 3.0],
			],
			[
				[0.0, 2.0, 2.5],
				[0.5, 2.0, 2.5],
				[1.0, 2.0, 2.5],
			],
			[
				[0.0, 2.0, 2.0],
				[0.5, 2.0, 2.0],
				[1.0, 2.0, 2.0],
			],
		])

		np.testing.assert_array_equal(surface_coordinates, expected_surface_coordinates)

		pass

	def test_pointCoordinates(self) :
		'''
		Test the setPointCoordinates and getCellCenterCoordinates methods
		'''
		block = HexBlock.HexBlock(2, 2, 2)

		block.setCellIDs(start_ID=0)
		setUpBlock(block)

		x = np.linspace(0, 1, 3)
		y = np.linspace(1, 2, 3)
		z = np.linspace(2, 3, 3)

		grid_x, grid_y, grid_z = np.meshgrid(x, y, z, indexing='ij')
		volume_coordinates = np.stack((grid_x, grid_y, grid_z), axis=-1)

		block.setPointCoordinates(volume_coordinates)

		expected_coordinates = np.array([
			[
				[
					[0.0, 1.0, 2.0],
					[0.0, 1.0, 2.5],
					[0.0, 1.0, 3.0],
				],
				[
					[0.0, 1.5, 2.0],
					[0.0, 1.5, 2.5],
					[0.0, 1.5, 3.0],
				],
				[
					[0.0, 2.0, 2.0],
					[0.0, 2.0, 2.5],
					[0.0, 2.0, 3.0],
				],
			],
			[
				[
					[0.5, 1.0, 2.0],
					[0.5, 1.0, 2.5],
					[0.5, 1.0, 3.0],
				],
				[
					[0.5, 1.5, 2.0],
					[0.5, 1.5, 2.5],
					[0.5, 1.5, 3.0],
				],
				[
					[0.5, 2.0, 2.0],
					[0.5, 2.0, 2.5],
					[0.5, 2.0, 3.0],
				],
			],
			[
				[
					[1.0, 1.0, 2.0],
					[1.0, 1.0, 2.5],
					[1.0, 1.0, 3.0],
				],
				[
					[1.0, 1.5, 2.0],
					[1.0, 1.5, 2.5],
					[1.0, 1.5, 3.0],
				],
				[
					[1.0, 2.0, 2.0],
					[1.0, 2.0, 2.5],
					[1.0, 2.0, 3.0],
				],
			], 
		])

		np.testing.assert_array_equal(block.point_coordinates, expected_coordinates)

		cell_centers = block.getCellCenterCoordinates()

		expected_coordinates = np.array([
			[
				[
					[0.25, 1.25, 2.25],
					[0.25, 1.25, 2.75],
				],
				[
					[0.25, 1.75, 2.25],
					[0.25, 1.75, 2.75],
				],
			],
			[
				[
					[0.75, 1.25, 2.25],
					[0.75, 1.25, 2.75],
				],
				[
					[0.75, 1.75, 2.25],
					[0.75, 1.75, 2.75],
				],
			]
		])

		np.testing.assert_array_equal(cell_centers, expected_coordinates)

		pass


if __name__ == '__main__' :
	
	unittest.main()