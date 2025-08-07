from pathlib import Path

import unittest
import numpy as np

from pyFOAM_hexBlockMesh.FaceCollection import FlatFaceCollection
from pyFOAM_hexBlockMesh.Writer import PointsWriter, FacesWriter

class TestWriter(unittest.TestCase) :

	def test_pointsWriter(self) :
		'''
		Test the write method
		'''

		test_path = Path('test_polyMesh')
		if (test_path / 'points').exists():
			for item in test_path.iterdir():
				item.unlink()
			test_path.rmdir()
		test_path.mkdir(parents=True, exist_ok=True)

		writer = PointsWriter(test_path)

		points = np.array([
			[0, 0, 0],
			[1, 0, 0],
			[0, 1, 0],
			[0, 0, 1],
			[1, 1, 0],
			[1, 0, 1],
			[0, 1, 1],
			[1, 1, 1],
		], dtype=float)

		writer.write(points)

		pass

	def test_facesWriter(self) :
		'''
		Test the write method
		'''

		test_path = Path('test_polyMesh')
		if test_path.exists():
			for item in test_path.iterdir():
				item.unlink()
			test_path.rmdir()
		test_path.mkdir(parents=True, exist_ok=True)

		writer = FacesWriter(test_path)

		faces = FlatFaceCollection(name='test_faces')

		faces.owner = np.array([0, 1, 2, 3], dtype=int)
		faces.vertices = np.array([
			[0, 1, 2, 3],
			[4, 5, 6, 7],
			[8, 9, 10, 11],
			[12, 13, 14, 15],
		], dtype=int)
		faces.neighbour = np.array([1, 2, 3, 4], dtype=int)

		writer.write([faces])

		pass

if __name__ == '__main__' :
	
	unittest.main()