import numpy as np

def isValid(
	owner:np.ndarray,
	vertices:np.ndarray,
	neighbour:np.ndarray|None=None
) -> bool :
	'''
	Check if the face collection is valid
	'''

	flag = vertices.dtype == int
	flag = flag and owner.dtype == int

	face_shape = owner.shape
	flag = flag and vertices.shape == face_shape + (4,)

	if neighbour is not None :

		flag = flag and neighbour.dtype == int
		flag = flag and neighbour.shape == face_shape

	return flag

class NDFaceCollection :
	'''
	Collection of quadrilateral faces
	'''
	
	def __init__(
		self,
		owner:np.ndarray,
		vertices:np.ndarray,
		neighbour:np.ndarray|None=None
	) -> None :
		'''
		Initialize the face
		'''

		assert isinstance(owner, np.ndarray)
		assert isinstance(vertices, np.ndarray)
		assert isinstance(neighbour, np.ndarray) or neighbour is None

		assert isValid(owner, vertices, neighbour), 'Invalid input'

		self.owner = owner
		self.vertices = vertices
		self.neighbour = neighbour

		pass

	def isValid(self) -> bool :
		'''
		Check if the face collection is valid
		'''

		flag = isValid(self.owner, self.vertices, self.neighbour)

		return flag

	def getShape(self) -> tuple[int, ...] :
		'''
		Get the shape of the face collection
		'''

		face_shape = self.owner.shape

		return face_shape
	
	def assignNeighbour(self, neighbour:np.ndarray) -> None :
		'''
		Assign the neighbour
		'''

		assert isinstance(neighbour, np.ndarray)
		assert neighbour.dtype == int
		assert neighbour.shape == self.getShape()

		self.neighbour = neighbour

		pass

	def flatten(self) -> 'NDFaceCollection' :
		'''
		Flatten the face collection
		'''
		
		# Create the indices that map the face collection to a 1D array
		# Flatten order 'F' => 
		# indices are parsed fastest along axis 0, then axis 1, then axis 2
		indices = [index.flatten(order='F') for index in np.indices(self.getShape())]
		indices = tuple(indices)
		
		owner		= self.owner[indices]
		# Using the same indices ensures that
		# the vertices are also flattened in the same order
		vertices	= self.vertices[indices]
		
		if self.neighbour is None : neighbour = None
		else :	neighbour = self.neighbour[indices]

		return NDFaceCollection(owner, vertices, neighbour)

			
class FlatFaceCollection :
	'''
	1D Collection of quadrilateral faces
	'''
	
	def __init__(self, name:str='Wall') -> None :
		'''
		Initialize the face
		'''

		self.owner	= np.zeros(0, dtype=int)
		self.neighbour	= np.zeros(0, dtype=int)
		self.vertices	= np.zeros((0, 4), dtype=int)

		self.name = name

		pass

	def isValid(self) -> bool :
		'''
		Check if the face collection is valid
		'''

		flag = self.vertices.dtype == int
		flag = flag and self.owner.dtype == int
		flag = flag and self.neighbour.dtype == int

		flag = flag and self.owner.ndim == 1
		flag = flag and self.neighbour.ndim == 1
		flag = flag and self.vertices.ndim == 2

		flag = flag and self.vertices.shape == self.owner.shape + (4,)
		# Boundary faces have no neighbour
		# Merged internal and boundary faces will have smaller number of neighbours
		flag = flag and self.neighbour.size <= self.owner.size

		return flag

	def getSize(self) -> int :
		'''
		Get the number of faces
		'''

		# assert self.isValid(), 'Corrupted data'

		size = self.owner.shape[0]

		return size
	
	def isBoundary(self) -> bool :
		'''
		Check if the face collection is a boundary
		Returns False even if the face collection is empty
		'''

		assert self.isValid(), 'Corrupted data'

		flag = self.getSize() > 0 and self.neighbour.size == 0

		return flag
	
	def appendNDFaceCollection(self, faces:NDFaceCollection) -> None :
		'''
		Append a face collection
		'''

		assert isinstance(faces, NDFaceCollection)
		assert faces.isValid(), 'Invalid input'
		assert self.isValid(), 'Corrupted data'

		faces_flattened = faces.flatten()

		flag_self_is_boundary = self.isBoundary()

		# Append the face collection
		self.owner	= np.append(self.owner, faces_flattened.owner)
		self.vertices	= np.append(self.vertices, faces_flattened.vertices, axis=0)

		if faces_flattened.neighbour is not None :

			if flag_self_is_boundary :

				raise ValueError('Cannot append internal faces to boundary')
			
			self.neighbour = np.append(self.neighbour, faces_flattened.neighbour)

		pass

	def appendFlatFaceCollection(self, faces:'FlatFaceCollection') -> None :
		'''
		Append a flat face collection
		'''

		assert isinstance(faces, FlatFaceCollection)
		assert faces.isValid(), 'Invalid input'
		assert self.isValid(), 'Corrupted data'

		if not faces.isBoundary() :

			if self.isBoundary() :

				raise ValueError('Cannot append internal faces to boundary')

			self.neighbour = np.append(self.neighbour, faces.neighbour)

		# Append the face collection
		self.owner = np.append(self.owner, faces.owner)
		self.vertices = np.append(self.vertices, faces.vertices, axis=0)

		pass
	
def mergeFaceCollections(face_collections:list[FlatFaceCollection]) -> FlatFaceCollection :
	'''
	Merge multiple face collections into one
	'''

	assert isinstance(face_collections, list), 'Invalid input'
	assert len(face_collections) > 0, 'Empty face collections'

	# Create a new face collection
	merged_faces = FlatFaceCollection()

	for face_collection in face_collections :

		assert isinstance(face_collection, FlatFaceCollection), 'Invalid face collection'
		assert face_collection.isValid(), 'Invalid face collection'

		merged_faces.appendFlatFaceCollection(face_collection)

	return merged_faces

def checkInteriorFaces(
	face_collection:FlatFaceCollection,
	points:np.ndarray,
	cell_centers:np.ndarray,
) -> bool :
	'''
	Check if the face collection is interior
	'''

	assert isinstance(face_collection, FlatFaceCollection), 'Invalid face collection'
	assert face_collection.isValid(), 'Invalid face collection'
	assert isinstance(points, np.ndarray), 'Invalid points'
	assert isinstance(cell_centers, np.ndarray), 'Invalid cell centers'

	owner_coordinates	= cell_centers[face_collection.owner]
	neighbour_coordinates	= cell_centers[face_collection.neighbour]

	face_coordinates	= points[face_collection.vertices]

	face_normals = np.cross(
		face_coordinates[:, 1] - face_coordinates[:, 0],
		face_coordinates[:, 2] - face_coordinates[:, 1],
		axis=-1
	)

	flag = np.all(
		np.sum(
			face_normals * (neighbour_coordinates - owner_coordinates),
			axis=-1
		) > 0
	)

	return bool(flag)

def checkBoundaryFaces(
	face_collection:FlatFaceCollection,
	points:np.ndarray,
	cell_centers:np.ndarray,
) -> bool :
	'''
	Check if the face collection is boundary
	'''

	assert isinstance(face_collection, FlatFaceCollection), 'Invalid face collection'
	assert face_collection.isValid(), 'Invalid face collection'
	assert isinstance(points, np.ndarray), 'Invalid points'
	assert isinstance(cell_centers, np.ndarray), 'Invalid cell centers'

	owner_coordinates	= cell_centers[face_collection.owner]
	face_coordinates	= points[face_collection.vertices]

	face_normals = np.cross(
		face_coordinates[:, 1] - face_coordinates[:, 0],
		face_coordinates[:, 2] - face_coordinates[:, 1],
		axis=-1
	)

	face_centers = face_coordinates.mean(axis=1)

	flag = np.all(
		np.sum(
			face_normals * (face_centers - owner_coordinates),
			axis=-1
		) > 0
	)

	return bool(flag)
