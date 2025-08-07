import unittest
import numpy as np

from pyFOAM_hexBlockMesh.ConnectedHexCollection import ConnectedHexCollection, HexBlock

class TestConnectedHexCollection(unittest.TestCase) :

	def test_addHexBlock(self) :
		'''
		Test the addHexBlock method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block = HexBlock(2, 2, 2)

		index = collection.addHexBlock(hex_block)

		pass

	def test_connectHexBlocks(self) :
		'''
		Test the connectHexBlocks method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1, index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)	

		pass

	def test_assignCellIDs(self) :
		'''
		Test the assignCellIDs method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1,
			index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)

		num_cells = collection.assignCellIDs()

		self.assertEqual(num_cells, 16)
		
		pass

	def test_assignHexVertexPointIDs(self) :
		'''
		Test the assignHexVertexPointIDs method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1,
			index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)

		num_points = collection.assignPointIDs()

		self.assertEqual(num_points, 45)

		pass

	def test_getFaces(self) :
		'''
		Test the getFaces method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1,
			index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)

		collection.assignPointIDs()
		collection.assignCellIDs()

		faces = collection.getFaces()

		self.assertEqual(len(faces), 11)

		pass

	def test_getPoints(self) :
		'''
		Test the getPoints method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1,
			index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)

		collection.assignPointIDs()
		collection.assignCellIDs()

		points = collection.getPoints()

		self.assertEqual(len(points), 45)

		pass

	def test_getCellCenters(self) :
		'''
		Test the getCellCenters method
		'''
		
		collection = ConnectedHexCollection()
		
		hex_block1 = HexBlock(2, 2, 2)
		hex_block2 = HexBlock(2, 2, 2)

		x0 = np.array([0, 0.5, 1])
		x1 = np.array([1, 1.5, 2])
		y  = np.array([0, 0.5, 1])
		z  = np.array([0, 0.5, 1])

		volume_x, volume_y, volume_z = np.meshgrid(x0, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block1.setPointCoordinates(volume)

		volume_x, volume_y, volume_z = np.meshgrid(x1, y, z, indexing='ij')
		volume = np.stack((volume_x, volume_y, volume_z), axis=-1)
		hex_block2.setPointCoordinates(volume)

		index1 = collection.addHexBlock(hex_block1)
		index2 = collection.addHexBlock(hex_block2)

		collection.connectHexBlocks(
			index1,
			index2,
			(1, 2, 6, 5),
			(0, 3, 7, 4)
		)

		collection.assignPointIDs()
		collection.assignCellIDs()

		cell_centers = collection.getCellCenters()

		self.assertEqual(len(cell_centers), 16)

		pass

if __name__ == '__main__' :
	
	unittest.main()
		