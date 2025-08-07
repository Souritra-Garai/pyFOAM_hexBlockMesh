import unittest

import numpy as np
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockFaces as HexBlockFaces

class TestHexBlockFaces(unittest.TestCase) :

	def test_FaceSlices(self) :
		'''
		Test the FaceSlices class
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.FaceSlices()
		
		owner		= face_slices.getOwner(cell_IDs)
		neighbor	= face_slices.getNeighbor(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_vertices = np.array([
			[
				[[ 0,  9, 12,  3], [ 1, 10, 13,  4], [ 2, 11, 14,  5]],
				[[ 3, 12, 15,  6], [ 4, 13, 16,  7], [ 5, 14, 17,  8]]
			],
			[
				[[ 9, 18, 21, 12], [10, 19, 22, 13], [11, 20, 23, 14]],
				[[12, 21, 24, 15], [13, 22, 25, 16], [14, 23, 26, 17]]
			],
		])

		np.testing.assert_array_equal(owner, cell_IDs)
		np.testing.assert_array_equal(neighbor, cell_IDs)
		np.testing.assert_array_equal(vertices, expected_vertices)

		pass

	def test_getSurfaceFaces_1(self) :
		'''
		Test the getSurfaceFaces function
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.getSurfaceFaces((0, 1, 2, 3))

		owner		= face_slices.getOwner(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_owner = np.array([
			[0, 2],
			[4, 6]
		])

		expected_vertices = np.array([
			[[ 0,  9, 12,  3], [ 3, 12, 15,  6]],
			[[ 9, 18, 21, 12], [12, 21, 24, 15]],
		])

		np.testing.assert_array_equal(owner, expected_owner)
		np.testing.assert_array_equal(vertices, expected_vertices)

		pass

	def test_getSurfaceFaces_2(self) :
		'''
		Test the getSurfaceFaces function with a different set of vertices
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.getSurfaceFaces((5, 6, 7, 4))

		owner		= face_slices.getOwner(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_owner = np.array([
			[5, 1],
			[7, 3]
		])

		expected_vertices = np.array([
			[[20, 23, 14, 11], [11, 14,  5,  2]],
			[[23, 26, 17, 14], [14, 17,  8,  5]],
		])

		np.testing.assert_array_equal(owner, expected_owner)
		np.testing.assert_array_equal(vertices, expected_vertices)

		pass

	def test_getInteriorFaces_1(self) :
		'''
		Test the getInteriorFaces function
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.getInteriorFaces(0)

		owner		= face_slices.getOwner(cell_IDs)
		neighbor	= face_slices.getNeighbor(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_owner = np.array([
			[[0], [1]],
			[[2], [3]]
		])

		expected_neighbor = np.array([
			[[4], [5]],
			[[6], [7]]
		])

		expected_vertices = np.array([
			[[[ 9, 12, 13, 10]], [[10, 13, 14, 11]]],
			[[[12, 15, 16, 13]], [[13, 16, 17, 14]]]
		])

		np.testing.assert_array_equal(owner, expected_owner)
		np.testing.assert_array_equal(neighbor, expected_neighbor)
		np.testing.assert_array_equal(vertices, expected_vertices)

		pass
	
	def test_getInteriorFaces_2(self) :
		'''
		Test the getInteriorFaces function with a different set of vertices
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.getInteriorFaces(1)

		owner		= face_slices.getOwner(cell_IDs)
		neighbor	= face_slices.getNeighbor(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_owner = np.array([
			[[0], [4]],
			[[1], [5]]
		])

		expected_neighbor = np.array([
			[[2], [6]],
			[[3], [7]]
		])

		expected_vertices = np.array([
			[[[ 3,  4, 13, 12]], [[12, 13, 22, 21]]],
			[[[ 4,  5, 14, 13]], [[13, 14, 23, 22]]]
		])

		np.testing.assert_array_equal(owner, expected_owner)
		np.testing.assert_array_equal(neighbor, expected_neighbor)
		np.testing.assert_array_equal(vertices, expected_vertices)

		pass

	def test_getInteriorFaces_3(self) :
		'''
		Test the getInteriorFaces function with a different set of vertices
		'''

		cell_IDs	= np.arange(8).reshape((2, 2, 2))
		point_IDs	= np.arange(27).reshape((3, 3, 3))

		face_slices	= HexBlockFaces.getInteriorFaces(2)

		owner		= face_slices.getOwner(cell_IDs)
		neighbor	= face_slices.getNeighbor(cell_IDs)
		vertices	= face_slices.getVertices(point_IDs)

		expected_owner = np.array([
			[[0], [2]],
			[[4], [6]]
		])

		expected_neighbor = np.array([
			[[1], [3]],
			[[5], [7]]
		])

		expected_vertices = np.array([
			[[[ 1, 10, 13,  4]], [[ 4, 13, 16,  7]]],
			[[[10, 19, 22, 13]], [[13, 22, 25, 16]]]
		])

		np.testing.assert_array_equal(owner, expected_owner)
		np.testing.assert_array_equal(neighbor, expected_neighbor)
		np.testing.assert_array_equal(vertices, expected_vertices)

if __name__ == '__main__' :
	
	unittest.main()