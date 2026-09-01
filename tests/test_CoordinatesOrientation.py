import unittest

import numpy as np

from pyFOAM_hexBlockMesh.geometry_utils.CoordinatesOrientation import checkCoordinatesOrientation

class TestCoordinatesOrientation(unittest.TestCase) :

	def test_checkCoordinatesOrientation_positive_volume(self) :
		'''
		Test that checkCoordinatesOrientation returns True for coordinates
		with positive volume determinant.
		'''

		x = np.linspace(0, -1, 3, dtype=float)
		y = np.linspace(0, 1, 3, dtype=float)
		z = np.linspace(0, -1, 3, dtype=float)

		coordinates = np.stack(np.meshgrid(x, y, z, indexing='ij'), axis=-1)
		result = checkCoordinatesOrientation(coordinates)

		self.assertTrue(result, 'Coordinates should have positive orientation')

		pass

	def test_checkCoordinatesOrientation_negative_volume(self) :
		'''
		Test that checkCoordinatesOrientation returns False for coordinates
		with negative volume determinant.
		'''

		# Reversed compared to the positive case
		x = np.linspace(0, 1, 3, dtype=float)
		y = np.linspace(0, 1, 3, dtype=float)
		z = np.linspace(0, -1, 3, dtype=float)

		coordinates = np.stack(np.meshgrid(x, y, z, indexing='ij'), axis=-1)
		result = checkCoordinatesOrientation(coordinates)

		self.assertFalse(result, 'Coordinates should have negative orientation')

		pass

	def test_checkCoordinatesOrientation_simple_cube(self) :
		'''
		Test with a simple cube configuration.
		'''

		# Create a simple 2x2x2 cube
		x = np.array([0., 1.])
		y = np.array([0., 1.])
		z = np.array([0., 1.])

		coordinates = np.stack(np.meshgrid(x, y, z, indexing='ij'), axis=-1)
		result = checkCoordinatesOrientation(coordinates)

		self.assertTrue(result, 'Simple cube should have positive orientation')

		pass


if __name__ == '__main__' :

	unittest.main()
