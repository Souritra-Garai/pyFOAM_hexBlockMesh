from dataclasses import dataclass

import numpy as np

import pyFOAM_hexBlockMesh.geometry_utils.HexBlockVertices as HexBlockVertices

from pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap import face_axes, face_vertex_slices

@dataclass
class FaceSlices :
	'''
	Slices to obtain the owner, neighbor and vertices of faces
	of a hex block.
	vertices :	HexBlockVertices.Slice3D will obtain the point IDs
			in a nD array. Then face_vertex_slices will be used
			to obtain the (..., 4) vertices of the face.
	'''

	owner		: HexBlockVertices.Slice3D
	neighbor	: HexBlockVertices.Slice3D
	vertices	: HexBlockVertices.Slice3D

	def __init__(self) :
		'''
		Initialize the slices
		'''

		self.owner	= HexBlockVertices.Slice3D()
		self.neighbor	= HexBlockVertices.Slice3D()
		self.vertices	= HexBlockVertices.Slice3D()

		pass

	def getVertices(self, point_IDs:np.ndarray) -> np.ndarray :
		'''
		Get the (..., 4) vertices of the face
		'''

		assert point_IDs.ndim == 3, \
		f'Invalid number of dimensions. Expected 3D array. Got {point_IDs.ndim}D'

		# The point IDs are ordered according to 2 axes values 
		# and their orientations (Covering all 8 ways to order the points)
		points_view = self.vertices.getArrayView(point_IDs)

		vertices = np.stack((
			points_view[face_vertex_slices[0]],
			points_view[face_vertex_slices[1]],
			points_view[face_vertex_slices[2]],
			points_view[face_vertex_slices[3]]
		), axis=-1)

		return vertices
	
	def getOwner(self, cell_IDs:np.ndarray) -> np.ndarray :
		'''
		Get the owner of the face
		'''

		assert cell_IDs.ndim == 3, 'Invalid input'

		owner = self.owner.getArrayView(cell_IDs)

		return owner
	
	def getNeighbor(self, cell_IDs:np.ndarray) -> np.ndarray :
		'''
		Get the neighbor of the face
		'''

		assert cell_IDs.ndim == 3, 'Invalid input'

		neighbor = self.neighbor.getArrayView(cell_IDs)

		return neighbor

def getSurfaceFaces(vertices:tuple[int, int, int, int]) -> FaceSlices :
	'''
	Get the slices to obtain owners cells and points for the faces
	formed by the 4 vertices.
	'''

	surface = HexBlockVertices.SurfaceProperties(vertices)

	faces = FaceSlices()

	faces.owner.axes[0]		= surface.axes[0].dimension
	faces.owner.slices[0]		= surface.axes[0].getSlice()

	faces.owner.axes[1]		= surface.axes[1].dimension
	faces.owner.slices[1]		= surface.axes[1].getSlice()

	faces.owner.axes[2]		= surface.constant_axis
	faces.owner.slices[2]		= surface.constant_axis_index

	faces.vertices.axes[0]		= surface.axes[0].dimension
	faces.vertices.slices[0]	= surface.axes[0].getSlice()

	faces.vertices.axes[1]		= surface.axes[1].dimension
	faces.vertices.slices[1]	= surface.axes[1].getSlice()

	faces.vertices.axes[2]		= surface.constant_axis
	faces.vertices.slices[2]	= surface.constant_axis_index

	return faces

def getInteriorFaces(axis:int) -> FaceSlices :
	'''
	Get the slices to obtain owners cells and points for the faces
	inside the block.
	Axis is the normal axis of the face.
	'''

	slices = FaceSlices()

	slices.owner.axes[0]		= face_axes[axis][0]
	slices.owner.slices[0]		= slice(None)

	slices.owner.axes[1]		= face_axes[axis][1]
	slices.owner.slices[1]		= slice(None)

	slices.owner.axes[2]		= axis
	slices.owner.slices[2]		= slice(0, -1)

	slices.neighbor.axes[0]		= face_axes[axis][0]
	slices.neighbor.slices[0]	= slice(None)

	slices.neighbor.axes[1]		= face_axes[axis][1]
	slices.neighbor.slices[1]	= slice(None)

	slices.neighbor.axes[2]		= axis
	slices.neighbor.slices[2]	= slice(1, None)

	slices.vertices.axes[0]		= face_axes[axis][0]
	slices.vertices.slices[0]	= slice(None)

	slices.vertices.axes[1]		= face_axes[axis][1]
	slices.vertices.slices[1]	= slice(None)

	slices.vertices.axes[2]		= axis
	slices.vertices.slices[2]	= slice(1, -1)

	return slices
	
