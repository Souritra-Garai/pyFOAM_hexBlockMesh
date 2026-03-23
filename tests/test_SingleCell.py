import unittest

import numpy as np

from pyFOAM_hexBlockMesh.expansion_utils.SingleCell import SingleCell2DGrid


class TestSingleCell2DGrid_Init(unittest.TestCase) :

	def test_cell_ID_shape(self) :
		grid = SingleCell2DGrid(2, 3)
		self.assertEqual(grid.cell_ID.shape, (2, 3))

	def test_point_ID_shape(self) :
		grid = SingleCell2DGrid(2, 3)
		self.assertEqual(grid.point_ID.shape, (2, 3, 2, 2, 2))

	def test_point_coordinates_shape(self) :
		grid = SingleCell2DGrid(2, 3)
		self.assertEqual(grid.point_coordinates.shape, (2, 3, 2, 2, 2, 3))

	def test_point_ID_sentinel(self) :
		# All point IDs must be initialised to -1 so the guard in setVertexPointID fires
		grid = SingleCell2DGrid(2, 3)
		np.testing.assert_array_equal(grid.point_ID, np.full((2, 3, 2, 2, 2), -1))

	def test_point_coordinates_zero(self) :
		grid = SingleCell2DGrid(2, 3)
		np.testing.assert_array_equal(grid.point_coordinates, np.zeros((2, 3, 2, 2, 2, 3)))


class TestSingleCell2DGrid_SetCellIDs(unittest.TestCase) :

	def test_fortran_ordering(self) :
		# Fortran order: axis-0 varies fastest
		# arange(0,6).reshape((2,3), order='F') = [[0,2,4],[1,3,5]]
		grid = SingleCell2DGrid(2, 3)
		grid.setCellIDs(start_ID=0)
		expected = np.array([[0, 2, 4], [1, 3, 5]])
		np.testing.assert_array_equal(grid.cell_ID, expected)

	def test_offset(self) :
		grid = SingleCell2DGrid(2, 3)
		grid.setCellIDs(start_ID=10)
		expected = np.array([[10, 12, 14], [11, 13, 15]])
		np.testing.assert_array_equal(grid.cell_ID, expected)

	def test_returns_next_start_ID(self) :
		grid = SingleCell2DGrid(2, 3)
		next_id = grid.setCellIDs(start_ID=5)
		self.assertEqual(next_id, 11)  # 5 + 2*3

	def test_invalid_negative(self) :
		grid = SingleCell2DGrid(2, 3)
		with self.assertRaises(AssertionError) :
			grid.setCellIDs(start_ID=-1)

	def test_invalid_type(self) :
		grid = SingleCell2DGrid(2, 3)
		with self.assertRaises(AssertionError) :
			grid.setCellIDs(start_ID=0.0)


class TestSingleCell2DGrid_GetFaceShape(unittest.TestCase) :
	'''
	cell_shape = (n0, n1, 1) — the dummy third axis is always size 1.

	Face (0,3,2,1): v0->v1 along axis1, v1->v2 along axis0  → shape (n1, n0)
	Face (0,1,5,4): v0->v1 along axis0, v1->v2 along axis2  → shape (n0,  1)
	Face (0,4,7,3): v0->v1 along axis2, v1->v2 along axis1  → shape ( 1, n1)
	'''

	def setUp(self) :
		self.grid = SingleCell2DGrid(2, 3)

	def test_face_in_plane(self) :
		# Face (0,3,2,1): axes 1 and 0 → shape (n1, n0) = (3, 2)
		shape = self.grid.getFaceShape((0, 3, 2, 1))
		self.assertEqual(shape, (3, 2))

	def test_face_perpendicular_axis1(self) :
		# Face (0,1,5,4): axes 0 and 2 → shape (n0, 1) = (2, 1)
		shape = self.grid.getFaceShape((0, 1, 5, 4))
		self.assertEqual(shape, (2, 1))

	def test_face_perpendicular_axis0(self) :
		# Face (0,4,7,3): axes 2 and 1 → shape (1, n1) = (1, 3)
		shape = self.grid.getFaceShape((0, 4, 7, 3))
		self.assertEqual(shape, (1, 3))


class TestSingleCell2DGrid_VertexPointID(unittest.TestCase) :

	def setUp(self) :
		self.grid = SingleCell2DGrid(2, 3)

	def test_set_and_get_roundtrip(self) :
		# vertex 0 → index (0,0,0) → grid.point_ID[:,:,0,0,0]
		self.grid.setVertexPointID(0, np.full((2, 3), 42, dtype=int))
		result = self.grid.getVertexPointID(0)
		expected = np.full((2, 3), 42)
		np.testing.assert_array_equal(result, expected)

	def test_set_all_vertices_independent(self) :
		for v in range(8) :
			self.grid.setVertexPointID(v, np.full((2, 3), v * 10, dtype=int))
		for v in range(8) :
			result = self.grid.getVertexPointID(v)
			np.testing.assert_array_equal(result, np.full((2, 3), v * 10))

	def test_guard_double_set(self) :
		self.grid.setVertexPointID(3, np.full((2, 3), 7, dtype=int))
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointID(3, np.full((2, 3), 8, dtype=int))

	def test_invalid_vertex_high(self) :
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointID(8, np.full((2, 3), 0, dtype=int))

	def test_invalid_vertex_negative(self) :
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointID(-1, np.full((2, 3), 0, dtype=int))

	def test_invalid_point_id_negative(self) :
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointID(0, np.full((2, 3), -1, dtype=int))

	def test_invalid_point_id_type(self) :
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointID(0, np.full((2, 3), 1.0))


class TestSingleCell2DGrid_VertexPointCoordinates(unittest.TestCase) :

	def setUp(self) :
		self.grid = SingleCell2DGrid(2, 3)

	def _make_coords(self, value:float) -> np.ndarray :
		# shape (2, 3, 3) — one xyz triple per cell
		return np.full((2, 3, 3), value)

	def test_set_and_get_roundtrip(self) :
		coords = self._make_coords(1.5)
		self.grid.setVertexPointCoordinates(0, coords)
		result = self.grid.getVertexPointCoordinates(0)
		np.testing.assert_array_equal(result, coords)

	def test_set_does_not_clobber_instance(self) :
		# Regression: getVertexPointCoordinates must not overwrite self.point_coordinates
		coords = self._make_coords(2.0)
		self.grid.setVertexPointCoordinates(0, coords)
		_ = self.grid.getVertexPointCoordinates(0)
		# After the get, coordinates for vertex 0 must still be intact
		result = self.grid.getVertexPointCoordinates(0)
		np.testing.assert_array_equal(result, coords)
		# And the full point_coordinates array shape must be unchanged
		self.assertEqual(self.grid.point_coordinates.shape, (2, 3, 2, 2, 2, 3))

	def test_set_all_vertices_independent(self) :
		for v in range(8) :
			coords = self._make_coords(float(v))
			self.grid.setVertexPointCoordinates(v, coords)
		for v in range(8) :
			result = self.grid.getVertexPointCoordinates(v)
			np.testing.assert_array_equal(result, np.full((2, 3, 3), float(v)))

	def test_invalid_vertex(self) :
		coords = self._make_coords(0.0)
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointCoordinates(8, coords)

	def test_invalid_type(self) :
		with self.assertRaises(AssertionError) :
			self.grid.setVertexPointCoordinates(0, np.array([[1, 2, 3]]))


if __name__ == '__main__' :
	unittest.main()
