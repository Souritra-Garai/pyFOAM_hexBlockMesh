import unittest

import numpy as np
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices

def getBlock() -> np.ndarray :
	'''
	Create a 3D block of shape (2, 4, 3)
	'''

	block = np.array([
		[[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9], [10, 11, 12]],
		[[13, 14, 15], [16, 17, 18], [19, 20, 21], [22, 23, 24]]
	], dtype=int)

	return block

class TestHexBlockVertices(unittest.TestCase) :

	def test_getArrayView_1(self) :
		'''
		Test the getArrayView method of Slice3D class
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.Slice3D()
		slice_3d.slices	= [slice(0, 2), slice(0, 2), slice(0, 2)]
		slice_3d.axes	= [0, 1, 2]
		
		view = slice_3d.getArrayView(block)

		expected_view = np.array([
			[[ 1,  2], [ 4,  5]],
			[[13, 14], [16, 17]]
		], dtype=int)

		np.testing.assert_array_equal(view, expected_view)

		pass

	def test_getArrayView_2(self) :
		'''
		Test the getArrayView method of Slice3D class with a different slice
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.Slice3D()
		slice_3d.slices	= [slice(0, 2), slice(0, None), slice(1, -1)]
		slice_3d.axes	= [2, 0, 1]

		view = slice_3d.getArrayView(block)

		expected_view = np.array([
			[[4, 7], [16, 19]],
			[[5, 8], [17, 20]],
		], dtype=int)

		np.testing.assert_array_equal(view, expected_view)

		pass

	def test_getEdgeInteriorSlice_1(self) :
		'''
		Test the getEdgeInteriorSlice method
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.getEdgeInteriorSlice(0, 4)

		block_view	= slice_3d.getArrayView(block)
		expected_view	= np.array([2], dtype=int)

		np.testing.assert_array_equal(block_view, expected_view)

		pass

	def test_getEdgeInteriorSlice_2(self) :
		'''
		Test the getEdgeInteriorSlice method with a different edge
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.getEdgeInteriorSlice(5, 6)

		block_view	= slice_3d.getArrayView(block)
		expected_view	= np.array([18, 21])

		np.testing.assert_array_equal(block_view, expected_view)

		pass

	def test_getSurfaceInteriorSlice_1(self) :
		'''
		Test the getSurfaceInteriorSlice method
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.getSurfaceInteriorSlice((0, 1, 5, 4))

		block_view	= slice_3d.getArrayView(block)
		expected_view	= np.zeros((0, 1), dtype=int) # No interior points for this slice

		np.testing.assert_array_equal(block_view, expected_view)

		pass

	def test_getSurfaceInteriorSlice_2(self) :
		'''
		Test the getSurfaceInteriorSlice method with a different surface
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d = HexBlockVertices.getSurfaceInteriorSlice((2, 6, 5, 1))

		block_view	= slice_3d.getArrayView(block)
		expected_view	= np.array([
			[ 20,  17],
		], dtype=int)

		np.testing.assert_array_equal(block_view, expected_view)

		pass

	def test_getSurfaceCompleteSlice_1(self) :
		'''
		Test the getSurfaceCompleteSlice method
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d	= HexBlockVertices.getSurfaceCompleteSlice((0, 1, 5, 4))
		surface		= slice_3d.getArrayView(block)
		
		expected_surface = np.array([
			[ 1,  2,  3],
			[13, 14, 15]
		], dtype=int)

		np.testing.assert_array_equal(surface, expected_surface)

		pass

	def test_getSurfaceCompleteSlice_2(self) :
		'''
		Test the getSurfaceCompleteSlice method with a different surface
		'''

		# Create a 3D array of shape (2, 4, 3)
		block = getBlock()

		slice_3d	= HexBlockVertices.getSurfaceCompleteSlice((2, 6, 5, 1))
		surface		= slice_3d.getArrayView(block)

		expected_surface = np.array([
			[22, 19, 16, 13],
			[23, 20, 17, 14],
			[24, 21, 18, 15]
		], dtype=int)

		np.testing.assert_array_equal(surface, expected_surface)

		pass


if __name__ == "__main__":

	unittest.main()