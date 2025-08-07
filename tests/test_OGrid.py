from pathlib import Path

import unittest
import numpy as np

from pyFOAM_hexBlockMesh.ConnectedHexCollection import \
ConnectedHexCollection, HexBlock
from pyFOAM_hexBlockMesh.FaceCollection import checkInteriorFaces, checkBoundaryFaces
from pyFOAM_hexBlockMesh.Writer import PointsWriter, FacesWriter

def setUpOGrid() -> ConnectedHexCollection :

	center_block = HexBlock(2, 2, 2)
	pos_x_block = HexBlock(2, 2, 2)	
	pos_y_block = HexBlock(2, 2, 2)
	neg_x_block = HexBlock(2, 2, 2)
	neg_y_block = HexBlock(2, 2, 2)

	# Center block
	x = np.array([-1, 0, 1], dtype=float)
	y = np.array([-1, 0, 1], dtype=float)
	z = np.array([-1, 0, 1], dtype=float)

	volume_x, volume_y, volume_z = np.meshgrid(x, y, z, indexing='ij')
	volume_coordinates = np.stack((volume_x, volume_y, volume_z), axis=-1)
	center_block.setPointCoordinates(volume_coordinates)

	# Positive x block
	neg_x_face = center_block.getSurfacePointCoordinates((1, 2, 6, 5))

	y = np.array([-2, 0, 2], dtype=float)
	z = np.array([-1, 0, 1], dtype=float)

	pos_x_face_x = np.tile(2, (3, 3))
	pos_x_face_y, pos_x_face_z = np.meshgrid(y, z, indexing='ij')
	pos_x_face = np.stack((pos_x_face_x, pos_x_face_y, pos_x_face_z), axis=-1)

	volume_coordinates = np.linspace(neg_x_face, pos_x_face, 3)
	pos_x_block.setPointCoordinates(volume_coordinates)

	# Positive y block
	neg_y_face = center_block.getSurfacePointCoordinates((3, 2, 6, 7))

	x = np.array([-2, 0, 2], dtype=float)
	z = np.array([-1, 0, 1], dtype=float)

	pos_y_face_y = np.tile(2, (3, 3))
	pos_y_face_x, pos_y_face_z = np.meshgrid(x, z, indexing='ij')
	pos_y_face = np.stack((pos_y_face_x, pos_y_face_y, pos_y_face_z), axis=-1)

	volume_coordinates = np.linspace(neg_y_face, pos_y_face, 3, axis=1)
	pos_y_block.setPointCoordinates(volume_coordinates)

	# Negative x block
	volume_coordinates = pos_x_block.point_coordinates.copy()
	volume_coordinates[..., 0] = -volume_coordinates[..., 0]
	volume_coordinates = volume_coordinates[::-1, ...]

	neg_x_block.setPointCoordinates(volume_coordinates)

	# Negative y block
	volume_coordinates = pos_y_block.point_coordinates.copy()
	volume_coordinates[..., 1] = -volume_coordinates[..., 1]
	# volume_coordinates = volume_coordinates[:, ::-1, :]
	volume_coordinates = volume_coordinates[::-1, :, :]

	neg_y_block.setPointCoordinates(volume_coordinates)

	# Create the connected hex collection
	hex_collection = ConnectedHexCollection()

	ID_center_block = hex_collection.addHexBlock(center_block)
	ID_pos_x_block  = hex_collection.addHexBlock(pos_x_block)
	ID_pos_y_block  = hex_collection.addHexBlock(pos_y_block)
	ID_neg_x_block  = hex_collection.addHexBlock(neg_x_block)
	ID_neg_y_block  = hex_collection.addHexBlock(neg_y_block)

	# Add the connections
	hex_collection.connectHexBlocks(
		ID_center_block, ID_pos_x_block,
		(1, 2, 6, 5), (0, 3, 7, 4)
	)

	hex_collection.connectHexBlocks(
		ID_center_block, ID_pos_y_block,
		(3, 2, 6, 7), (0, 1, 5, 4)
	)
	hex_collection.connectHexBlocks(
		ID_pos_x_block, ID_pos_y_block,
		(3, 2, 6, 7), (1, 2, 6, 5)
	)

	hex_collection.connectHexBlocks(
		ID_center_block, ID_neg_x_block,
		(0, 3, 7, 4), (1, 2, 6, 5)
	)
	hex_collection.connectHexBlocks(
		ID_pos_y_block, ID_neg_x_block,
		(0, 3, 7, 4), (2, 3, 7, 6)
	)

	hex_collection.connectHexBlocks(
		ID_center_block, ID_neg_y_block,
		# (0, 1, 5, 4), (3, 2, 6, 7)
		(0, 1, 5, 4), (1, 0, 4, 5)
	)
	hex_collection.connectHexBlocks(
		ID_neg_x_block, ID_neg_y_block,
		# (0, 1, 5, 4), (0, 3, 7, 4)
		(0, 1, 5, 4), (2, 1, 5, 6)
	)
	hex_collection.connectHexBlocks(
		ID_pos_x_block, ID_neg_y_block,
		# (0, 1, 5, 4), (2, 1, 5, 6)
		(0, 1, 5, 4), (0, 3, 7, 4)
	)

	hex_collection.assignCellIDs()
	hex_collection.assignPointIDs()

	return hex_collection


class TestOGrid(unittest.TestCase) :

	def test_setup(self) -> None :

		setUpOGrid()

		pass

	def test_faces(self) -> None :
		'''
		Test the faces of the O-grid
		'''

		hex_collection = setUpOGrid()

		points = hex_collection.getPoints()
		cell_centers = hex_collection.getCellCenters()

		faces = hex_collection.getFaces()

		for face_collection in faces :
			
			if face_collection.isBoundary() :

				self.assertTrue(checkBoundaryFaces(
					face_collection, points, cell_centers
				))

			else :

				self.assertTrue(checkInteriorFaces(
					face_collection, points, cell_centers
				))

		test_path = Path('test_polyMesh_OGrid')
		if test_path.exists():
			for item in test_path.iterdir():
				item.unlink()
			test_path.rmdir()
		test_path.mkdir(parents=True, exist_ok=True)

		points_writer = PointsWriter(test_path)
		points_writer.write(points)

		faces_writer = FacesWriter(test_path)
		faces_writer.write(faces)

		pass

	
if __name__ == '__main__' :
		
	unittest.main()
	