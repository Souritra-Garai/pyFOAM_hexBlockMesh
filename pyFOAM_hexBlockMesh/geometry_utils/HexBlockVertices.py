from dataclasses import dataclass

import numpy as np

from pyFOAM_hexBlockMesh.geometry_utils.HexBlockMap import vertex_map, vertex_connectivity

def verticesShareFaceAlongAxis(vertices:tuple[int, int, int, int], axis:int) -> bool :
	'''
	Check if the vertices share a face along the axis
	'''
	
	flag = True

	try :

		axis_val = vertex_map[vertices[0]][axis]
		
		for v in vertices[1:] :
		
			flag = flag and (vertex_map[v][axis] == axis_val)

	except IndexError:

		raise ValueError('Invalid input')
	
	return flag

@dataclass
class Slice3D :
	'''
	Slice of a 3D array
	'''

	slices	: list[slice|int]
	axes	: list[int]

	def __init__(self) -> None :
		'''
		Initialize the surface slice
		'''

		self.slices	= [slice(None)] * 3
		self.axes	= [0, 1, 2]

		pass

	def isValid(self) -> bool :
		'''
		Check if the slice is valid
		'''

		flag = set(self.axes) == {0, 1, 2}
		flag = flag and len(self.slices) == 3 and len(self.axes) == 3
		flag = flag and all([isinstance(s, (int, slice)) for s in self.slices])

		return flag

	def getArrayView(self, points:np.ndarray) -> np.ndarray :
		'''
		Get the array view of the points array
		'''

		# Check if the input is valid
		assert isinstance(points, np.ndarray)
		assert self.isValid(), 'Invalid slice'
		assert points.ndim >= 3, 'Invalid input'

		# Get the array view of the points array
		points_view = np.moveaxis(points, self.axes, (0, 1, 2))
		points_view = points_view[tuple(self.slices)]

		return points_view
	
@dataclass
class AxisProperties :
	'''
	Dimension is the axis along which the edge is oriented.
	Orientation is the direction of the edge from v0 to v1.
	'''

	dimension	: int
	orientation	: bool

	def __init__(self, v0:int, v1:int) -> None :
		'''
		Initialize the axis properties
		'''

		# Check if the ordered pairs are in the dictionary
		# If not, swap the ordered pairs
		# to check if the swapped ordered pairs are in the dictionary
		# If not, raise an error
		if (v0, v1) in vertex_connectivity :
			
			# If the ordered pair is in the dictionary
			# The edge is along the axis
			# and the orientation is positive
			self.dimension		= vertex_connectivity[(v0, v1)]
			self.orientation	= True
		
		elif (v1, v0) in vertex_connectivity  :
			
			# If the swapped ordered pair is in the dictionary
			# The edge is along the axis
			# and the orientation is negative
			self.dimension		= vertex_connectivity[(v1, v0)]
			self.orientation	= False
		
		else :	
			
			if v0 in range(8) and v1 in range(8) :

				raise ValueError('Vertices are not connected')
			
			else :
			
				raise ValueError('Invalid input')
			
		pass
	
	def getSlice(self) -> slice :
		'''
		Get the slice according to the orientation
		'''

		match self.orientation :

			case True	: return slice(None, None, 1)
			case False	: return slice(None, None, -1)

	def getInteriorSlice(self) -> slice :
		'''
		Get the slice excluding the end points
		'''

		match self.orientation :
			
			case True	: return slice(1, -1)
			case False	: return slice(-2, 0, -1)
	
def getEdgeInteriorSlice(v0:int, v1:int) -> Slice3D :
	'''
	Get the slice of the points array for the edge.
	Excludes the end vertices.
	'''
	
	axis = AxisProperties(v0, v1)

	slice_3d = Slice3D()

	slice_3d.axes[0]	= axis.dimension
	slice_3d.slices[0]	= axis.getInteriorSlice()

	remaining_axes = list({0, 1, 2} - {axis.dimension})
	
	slice_3d.axes[1]	= remaining_axes[0]
	slice_3d.slices[1]	= vertex_map[v0][remaining_axes[0]]

	slice_3d.axes[2]	= remaining_axes[1]
	slice_3d.slices[2]	= vertex_map[v0][remaining_axes[1]]

	# Check if the slice is valid
	assert slice_3d.isValid(), 'Invalid slice'

	return slice_3d

@dataclass
class SurfaceProperties :
	'''
	Properties of a surface
	'''

	axes		: tuple[AxisProperties, AxisProperties]
	'''
	Axes of the surface
	0: Axis along the first edge
	1: Axis along the second edge
	'''
	# The third axis is the constant axis
	# The third axis is the axis along which the surface is constant

	constant_axis		: int
	constant_axis_index	: int

	def __init__(self, vertices:tuple[int, int, int, int]) -> None :
		'''
		Initialize the surface properties
		'''

		# Check if the input is valid
		assert len(vertices) == 4, f'Invalid input {vertices}'
		assert all([isinstance(v, int) for v in vertices]), \
		f'Invalid input {vertices}'

		self.axes		= (
			AxisProperties(vertices[0], vertices[1]),
			AxisProperties(vertices[1], vertices[2])
		)

		self.constant_axis = 3 - self.axes[0].dimension - self.axes[1].dimension

		assert verticesShareFaceAlongAxis(vertices, self.constant_axis),	\
		'Vertices do not share a face'
		
		self.constant_axis_index = vertex_map[vertices[0]][self.constant_axis]

		pass

def getSurfaceInteriorSlice(vertices:tuple[int, int, int, int]) -> Slice3D :
	'''
	Get the points on the surface excluding the vertices and edges
	'''
	surface		= SurfaceProperties(vertices)
	surface_slice	= Slice3D()

	surface_slice.axes[0]	= surface.axes[0].dimension
	surface_slice.slices[0]	= surface.axes[0].getInteriorSlice()
	
	surface_slice.axes[1]	= surface.axes[1].dimension
	surface_slice.slices[1]	= surface.axes[1].getInteriorSlice()

	surface_slice.axes[2]	= surface.constant_axis
	surface_slice.slices[2]	= surface.constant_axis_index

	return surface_slice

def getSurfaceCompleteSlice(vertices:tuple[int, int, int, int]) -> Slice3D :
	'''
	Get the points on the surface including the vertices and edges
	'''

	surface		= SurfaceProperties(vertices)
	surface_slice	= Slice3D()

	surface_slice.axes[0]	= surface.axes[0].dimension
	surface_slice.slices[0]	= surface.axes[0].getSlice()
	
	surface_slice.axes[1]	= surface.axes[1].dimension
	surface_slice.slices[1]	= surface.axes[1].getSlice()

	surface_slice.axes[2]	= surface.constant_axis
	surface_slice.slices[2]	= surface.constant_axis_index

	return surface_slice
