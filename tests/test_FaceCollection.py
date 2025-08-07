import unittest
import numpy as np

from pyFOAM_hexBlockMesh.FaceCollection import (
	NDFaceCollection, 
	FlatFaceCollection, 
	checkInteriorFaces, 
	checkBoundaryFaces
)

class TestFaceCollection(unittest.TestCase) :

	def test_flatten(self) :
		'''
		Test the flatten method
		'''

		owner = np.array([
			[1, 2],
			[3, 4]
		])

		vertices = np.array([
		[
			[1, 1, 1, 1],
			[2, 2, 2, 2]
		],
		[
			[3, 3, 3, 3],
			[4, 4, 4, 4]
		]
		])

		faces = NDFaceCollection(owner, vertices)
		flat_faces = faces.flatten()

		flat_owner = np.array([1, 3, 2, 4])
		flat_vertices = np.array([
			[1, 1, 1, 1],
			[3, 3, 3, 3],
			[2, 2, 2, 2],
			[4, 4, 4, 4]
		])

		np.testing.assert_array_equal(flat_faces.owner, flat_owner)
		np.testing.assert_array_equal(flat_faces.vertices, flat_vertices)

		pass

	def test_appendNDFaceCollection(self) :
		'''
		Test the append method
		'''

		owner1 = np.array([1, 2])
		vertices1 = np.array([
			[1, 1, 1, 1],
			[2, 2, 2, 2]
		])

		faces1 = NDFaceCollection(owner1, vertices1)

		owner2 = np.array([3, 4])
		vertices2 = np.array([
			[3, 3, 3, 3],
			[4, 4, 4, 4]
		])

		faces2 = NDFaceCollection(owner2, vertices2)

		faces_combined = FlatFaceCollection()
		faces_combined.appendNDFaceCollection(faces1)
		faces_combined.appendNDFaceCollection(faces2)

		expected_owner = np.array([1, 2, 3, 4])
		expected_vertices = np.array([
			[1, 1, 1, 1],
			[2, 2, 2, 2],
			[3, 3, 3, 3],
			[4, 4, 4, 4]
		])

		self.assertTrue(np.array_equal(faces_combined.owner, expected_owner))
		self.assertTrue(np.array_equal(faces_combined.vertices, expected_vertices))

	def test_appendFlatFaceCollection(self) :
		'''
		Test the append method for FlatFaceCollection
		'''

		faces1 = FlatFaceCollection(name='Faces1')
		faces1.appendNDFaceCollection(NDFaceCollection(
			np.array([1, 2]),
			np.array([
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			])
		))

		faces2 = FlatFaceCollection(name='Faces2')
		faces2.appendNDFaceCollection(NDFaceCollection(
			np.array([3, 4]),
			np.array([
				[3, 3, 3, 3],
				[4, 4, 4, 4]
			])
		))

		faces_combined = FlatFaceCollection()
		faces_combined.appendFlatFaceCollection(faces1)
		faces_combined.appendFlatFaceCollection(faces2)

		expected_owner = np.array([1, 2, 3, 4])
		expected_vertices = np.array([
			[1, 1, 1, 1],
			[2, 2, 2, 2],
			[3, 3, 3, 3],
			[4, 4, 4, 4]
		])

		self.assertTrue(np.array_equal(faces_combined.owner, expected_owner))
		self.assertTrue(np.array_equal(faces_combined.vertices, expected_vertices))

	def test_checkInteriorFaces(self) :
		'''
		Test the checkInteriorFaces method
		'''

		points = np.array([
			[0, 0, 0], # 0
			[1, 0, 0], # 1
			[1, 1, 0], # 2
			[0, 1, 0], # 3
			[0, 0, 1], # 4
			[1, 0, 1], # 5
			[1, 1, 1], # 6
			[0, 1, 1], # 7
			[0, 0, 2], # 8
			[1, 0, 2], # 9
			[1, 1, 2], # 10
			[0, 1, 2]  # 11
		], dtype=float)

		cell_centers = np.array([
			[0.5, 0.5, 0.5],
			[0.5, 0.5, 1.5],
		], dtype=float)

		faces = FlatFaceCollection(name='TestFaces')
		faces.vertices = np.array([
			[4, 5, 6, 7], # Face 1
			# [0, 3, 2, 1], # Face 0
			# [0, 1, 5, 4], # Face 2
			# [2, 3, 7, 6], # Face 3
			# [0, 4, 7, 3], # Face 4
			# [1, 2, 6, 5], # Face 5
			# [8, 9, 10, 11], # Face 6
			# [4, 5, 9, 8], # Face 7
			# [6, 7, 11, 10], # Face 8
			# [4, 8, 11, 7], # Face 9
			# [5, 6, 10, 9]  # Face 10
		], dtype=int)
		faces.owner = np.array([0], dtype=int)
		faces.neighbour = np.array([1], dtype=int)

		is_interior = checkInteriorFaces(faces, points, cell_centers)
		
		self.assertTrue(is_interior)

	def test_checkBoundaryFaces(self) :
		'''
		Test the checkBoundaryFaces method
		'''
		points = np.array([
			[0, 0, 0], # 0
			[1, 0, 0], # 1
			[1, 1, 0], # 2
			[0, 1, 0], # 3
			[0, 0, 1], # 4
			[1, 0, 1], # 5
			[1, 1, 1], # 6
			[0, 1, 1], # 7
			[0, 0, 2], # 8
			[1, 0, 2], # 9
			[1, 1, 2], # 10
			[0, 1, 2]  # 11
		], dtype=float)

		cell_centers = np.array([
			[0.5, 0.5, 0.5],
			[0.5, 0.5, 1.5],
		], dtype=float)

		faces = FlatFaceCollection(name='TestFaces')
		faces.vertices = np.array([
			# [4, 5, 6, 7], # Face 1
			[0, 3, 2, 1], # Face 0
			[0, 1, 5, 4], # Face 2
			[2, 3, 7, 6], # Face 3
			[0, 4, 7, 3], # Face 4
			[1, 2, 6, 5], # Face 5
			[8, 9, 10, 11], # Face 6
			[4, 5, 9, 8], # Face 7
			[6, 7, 11, 10], # Face 8
			[4, 8, 11, 7], # Face 9
			[5, 6, 10, 9]  # Face 10
		], dtype=int)
		faces.owner = np.array([
			0, 0, 0, 0, 0, 1, 1, 1, 1, 1
		], dtype=int)
		# faces.neighbour = np.array([1], dtype=int)

		is_interior = checkBoundaryFaces(faces, points, cell_centers)
		
		self.assertTrue(is_interior)


if __name__ == '__main__' :
	
	unittest.main()