import unittest

import numpy as np

import pyFOAM_hexBlockMesh.expansion_utils.SingleCell as SingleCell
import pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap as HexBlockMap

class TestSlice2D(unittest.TestCase) :

	def test_default_axes(self) :
		'''
		Test the default axes of Slice2D
		'''

		self.assertEqual(SingleCell.Slice2D().axes, [0, 1])

		pass

	def test_default_slices(self) :
		'''
		Test the default slices of Slice2D
		'''

		self.assertEqual(SingleCell.Slice2D().slices, [slice(None), slice(None)])

		pass

	def test_isValid_default(self) :
		'''
		Test that a freshly initialized Slice2D is valid
		'''

		self.assertTrue(SingleCell.Slice2D().isValid())

		pass

	def test_isValid_wrong_axes_set(self) :
		'''
		Test that axes not covering {0, 1} are invalid
		'''

		slice_2d = SingleCell.Slice2D()
		slice_2d.axes = [0, 2]

		self.assertFalse(slice_2d.isValid())

		pass

	def test_isValid_duplicate_axes(self) :
		'''
		Test that duplicate axes are invalid
		'''

		slice_2d = SingleCell.Slice2D()
		slice_2d.axes = [1, 1]

		self.assertFalse(slice_2d.isValid())

		pass

	def test_getCellsView_default_is_full_array(self) :
		'''
		Test that the default slice returns the full array unchanged
		'''

		cells = np.arange(6).reshape(2, 3)

		np.testing.assert_array_equal(SingleCell.Slice2D().getCellsView(cells), cells)

		pass

	def test_getCellsView_swapped_axes(self) :
		'''
		Test that swapping axes transposes the view
		'''

		cells = np.arange(6).reshape(2, 3)

		slice_2d = SingleCell.Slice2D()
		slice_2d.axes = [1, 0]

		np.testing.assert_array_equal(slice_2d.getCellsView(cells), cells.T)

		pass

	def test_getCellsView_invalid_ndim(self) :
		'''
		Test that an array with fewer than 2 dimensions raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.Slice2D().getCellsView(np.arange(3))

		pass

	def test_getPointsView_vertex_0(self) :
		'''
		Test that vertex 0 (local coordinates (0, 0, 0)) selects the correct slab
		'''

		points = np.arange(2 * 3 * 2 * 2 * 2).reshape(2, 3, 2, 2, 2)

		view = SingleCell.Slice2D().getPointsView(points, 0)

		np.testing.assert_array_equal(view, points[:, :, 0, 0, 0])

		pass

	def test_getPointsView_vertex_6(self) :
		'''
		Test that vertex 6 (local coordinates (-1, -1, -1)) selects the correct slab
		'''

		points = np.arange(2 * 3 * 2 * 2 * 2).reshape(2, 3, 2, 2, 2)

		view = SingleCell.Slice2D().getPointsView(points, 6)

		np.testing.assert_array_equal(view, points[:, :, -1, -1, -1])

		pass

	def test_getPointsView_invalid_ndim(self) :
		'''
		Test that an array with fewer than 5 dimensions raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.Slice2D().getPointsView(np.zeros((2, 3)), 0)

		pass


class TestGetSurfaceSlice(unittest.TestCase) :
	'''
	Verify getSurfaceSlice for each of the 6 hex faces.
	Faces (0,3,2,1) and (4,5,6,7) lie entirely in the grid's own axes 0/1,
	so both axes stay unconstrained (full range slices).
	The remaining 4 lateral faces involve axis 2, which the 2D grid does not
	physically store, so that axis collapses to a single fixed index (0 or -1).
	'''

	def test_ax2_0_face(self) :
		'''
		Test the ax2=0 face (0, 3, 2, 1)
		'''

		surface_slice = SingleCell.getSurfaceSlice((0, 3, 2, 1))

		self.assertEqual(surface_slice.axes, [1, 0])
		self.assertEqual(surface_slice.slices, [slice(None, None, 1), slice(None, None, 1)])

		pass

	def test_ax2_last_face(self) :
		'''
		Test the ax2=last face (4, 5, 6, 7)
		'''

		surface_slice = SingleCell.getSurfaceSlice((4, 5, 6, 7))

		self.assertEqual(surface_slice.axes, [0, 1])
		self.assertEqual(surface_slice.slices, [slice(None, None, 1), slice(None, None, 1)])

		pass

	def test_ax1_0_face(self) :
		'''
		Test the ax1=0 face (0, 1, 5, 4): axis 1 collapses to index 0
		'''

		surface_slice = SingleCell.getSurfaceSlice((0, 1, 5, 4))

		self.assertEqual(surface_slice.axes, [0, 1])
		self.assertEqual(surface_slice.slices, [slice(None, None, 1), 0])

		pass

	def test_ax1_last_face(self) :
		'''
		Test the ax1=last face (2, 3, 7, 6): axis 1 collapses to index -1
		'''

		surface_slice = SingleCell.getSurfaceSlice((2, 3, 7, 6))

		self.assertEqual(surface_slice.axes, [0, 1])
		self.assertEqual(surface_slice.slices, [slice(None, None, -1), -1])

		pass

	def test_ax0_0_face(self) :
		'''
		Test the ax0=0 face (0, 4, 7, 3): axis 0 collapses to index 0
		'''

		surface_slice = SingleCell.getSurfaceSlice((0, 4, 7, 3))

		self.assertEqual(surface_slice.axes, [0, 1])
		self.assertEqual(surface_slice.slices, [0, slice(None, None, 1)])

		pass

	def test_ax0_last_face(self) :
		'''
		Test the ax0=last face (1, 2, 6, 5): axis 0 collapses to index -1
		'''

		surface_slice = SingleCell.getSurfaceSlice((1, 2, 6, 5))

		self.assertEqual(surface_slice.axes, [1, 0])
		self.assertEqual(surface_slice.slices, [slice(None, None, 1), -1])

		pass


class TestSingleCell2DGrid_Init(unittest.TestCase) :

	def test_invalid_zero_n0(self) :
		'''
		Test that n0 = 0 raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.SingleCell2DGrid(0, 3)

		pass

	def test_invalid_zero_n1(self) :
		'''
		Test that n1 = 0 raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.SingleCell2DGrid(2, 0)

		pass

	def test_invalid_negative_n(self) :
		'''
		Test that a negative n raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.SingleCell2DGrid(-1, 3)

		pass

	def test_invalid_float_n(self) :
		'''
		Test that a float n raises an assertion error
		'''

		with self.assertRaises(AssertionError) :
			SingleCell.SingleCell2DGrid(2.0, 3)

		pass

	def test_cell_ID_shape(self) :
		'''
		Test the shape of the cell_ID array
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		self.assertEqual(grid.cell_ID.shape, (2, 3))

		pass

	def test_point_ID_shape(self) :
		'''
		Test the shape of the point_ID array
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		self.assertEqual(grid.point_ID.shape, (2, 3, 2, 2, 2))

		pass

	def test_cell_ID_sentinel(self) :
		'''
		Test that cell IDs are initialized to -1
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		np.testing.assert_array_equal(grid.cell_ID, np.full((2, 3), -1))

		pass

	def test_point_ID_sentinel(self) :
		'''
		Test that point IDs are initialized to -1
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		np.testing.assert_array_equal(grid.point_ID, np.full((2, 3, 2, 2, 2), -1))

		pass


class TestSingleCell2DGrid_SetCellIDs(unittest.TestCase) :

	def test_fortran_ordering(self) :
		'''
		Test that cell IDs vary fastest along axis 0
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)
		grid.setCellIDs(start_ID=0)

		expected = np.array([
			[0, 2, 4],
			[1, 3, 5]
		])

		np.testing.assert_array_equal(grid.cell_ID, expected)

		pass

	def test_offset(self) :
		'''
		Test that setCellIDs honours a non-zero start_ID
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)
		grid.setCellIDs(start_ID=10)

		expected = np.array([
			[10, 12, 14],
			[11, 13, 15]
		])

		np.testing.assert_array_equal(grid.cell_ID, expected)

		pass

	def test_returns_next_start_ID(self) :
		'''
		Test that setCellIDs returns start_ID + number of cells
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)
		next_ID = grid.setCellIDs(start_ID=5)

		self.assertEqual(next_ID, 11)

		pass

	def test_invalid_negative_start_ID(self) :
		'''
		Test that a negative start_ID raises an assertion error
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		with self.assertRaises(AssertionError) :
			grid.setCellIDs(start_ID=-1)

		pass

	def test_invalid_float_start_ID(self) :
		'''
		Test that a float start_ID raises an assertion error
		'''

		grid = SingleCell.SingleCell2DGrid(2, 3)

		with self.assertRaises(AssertionError) :
			grid.setCellIDs(start_ID=0.0)

		pass


class TestSingleCell2DGrid_GetFaceShape(unittest.TestCase) :
	'''
	cell_shape = (n0, n1, 1) -- the missing third axis is always size 1.
	'''

	def setUp(self) :

		self.grid = SingleCell.SingleCell2DGrid(2, 3)

		pass

	def test_ax2_face(self) :
		'''
		Test the shape of an ax2 face: both grid axes vary
		'''

		self.assertEqual(self.grid.getFaceShape((0, 3, 2, 1)), (3, 2))

		pass

	def test_ax1_face(self) :
		'''
		Test the shape of an ax1 face: axis 2 collapses to size 1
		'''

		self.assertEqual(self.grid.getFaceShape((0, 1, 5, 4)), (2, 1))

		pass

	def test_ax0_face(self) :
		'''
		Test the shape of an ax0 face: axis 2 collapses to size 1
		'''

		self.assertEqual(self.grid.getFaceShape((0, 4, 7, 3)), (1, 3))

		pass


class TestSingleCell2DGrid_GetSurface(unittest.TestCase) :
	'''
	Build a 2x2 grid, stamp each cell's 8 local vertices with a unique ID
	(1000 + 100 * flat_cell_index + local_vertex_index), and check that
	getSurface extracts the right owner cells and vertex IDs for a few faces.
	'''

	def setUp(self) :

		self.grid = SingleCell.SingleCell2DGrid(2, 2)
		self.grid.setCellIDs(start_ID=0)

		for i in range(2) :

			for j in range(2) :

				for vi, local_vertex in enumerate(HexBlockMap.vertex_map) :

					self.grid.point_ID[i, j][local_vertex] = 1000 + 100 * (i * 2 + j) + vi

		pass

	def test_ax2_0_face(self) :
		'''
		Test getSurface for the ax2=0 face (0, 3, 2, 1)
		'''

		faces = self.grid.getSurface((0, 3, 2, 1))

		expected_owner = np.array([
			[0, 1],
			[2, 3]
		])
		expected_vertices = np.array([
			[[1000, 1003, 1002, 1001], [1200, 1203, 1202, 1201]],
			[[1100, 1103, 1102, 1101], [1300, 1303, 1302, 1301]]
		])

		np.testing.assert_array_equal(faces.owner, expected_owner)
		np.testing.assert_array_equal(faces.vertices, expected_vertices)

		pass

	def test_ax1_0_face(self) :
		'''
		Test getSurface for the ax1=0 face (0, 1, 5, 4)
		'''

		faces = self.grid.getSurface((0, 1, 5, 4))

		expected_owner = np.array([0, 1])
		expected_vertices = np.array([
			[1000, 1001, 1005, 1004],
			[1200, 1201, 1205, 1204]
		])

		np.testing.assert_array_equal(faces.owner, expected_owner)
		np.testing.assert_array_equal(faces.vertices, expected_vertices)

		pass

	def test_ax0_0_face(self) :
		'''
		Test getSurface for the ax0=0 face (0, 4, 7, 3)
		'''

		faces = self.grid.getSurface((0, 4, 7, 3))

		expected_owner = np.array([0, 2])
		expected_vertices = np.array([
			[1000, 1004, 1007, 1003],
			[1100, 1104, 1107, 1103]
		])

		np.testing.assert_array_equal(faces.owner, expected_owner)
		np.testing.assert_array_equal(faces.vertices, expected_vertices)

		pass


class TestSingleCell2DGrid_GetAllFaces(unittest.TestCase) :
	'''
	getAllFaces skips getSurfaceSlice entirely: it returns one face per cell
	(no merging across neighbours), using the raw cell_ID array as owner.
	'''

	def test_ax2_0_face(self) :
		'''
		Test getAllFaces for the ax2=0 face (0, 3, 2, 1)
		'''

		grid = SingleCell.SingleCell2DGrid(2, 2)
		grid.setCellIDs(start_ID=0)

		for i in range(2) :

			for j in range(2) :

				for vi, local_vertex in enumerate(HexBlockMap.vertex_map) :

					grid.point_ID[i, j][local_vertex] = 1000 + 100 * (i * 2 + j) + vi

		faces = grid.getAllFaces((0, 3, 2, 1))

		expected_owner = np.array([
			[0, 2],
			[1, 3]
		])
		expected_vertices = np.array([
			[[1000, 1100, 1300, 1200], [1004, 1104, 1304, 1204]],
			[[1003, 1103, 1303, 1203], [1007, 1107, 1307, 1207]]
		])

		np.testing.assert_array_equal(faces.owner, expected_owner)
		np.testing.assert_array_equal(faces.vertices, expected_vertices)

		pass


if __name__ == '__main__' :

	unittest.main()
