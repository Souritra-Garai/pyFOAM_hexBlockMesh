from pathlib import Path

import numpy as np

import pyFOAM_hexBlockMesh.FaceCollection as FaceCollection
import pyFOAM_hexBlockMesh.writer_utils.PolyMeshFile as PolyMeshFile

class PointsWriter :

	def __init__(self, polyMesh_path: Path) :

		assert polyMesh_path.exists() and polyMesh_path.is_dir(), \
		f'PolyMesh_path {polyMesh_path} does not exist or is not a directory'

		self.path = polyMesh_path / 'points'

		assert not self.path.exists(), \
		f'Points file {self.path} already exists.'

		pass

	def write(self, points: np.ndarray) -> None :
		'''
		Write points to the points file.
		'''

		assert points.ndim == 2 and points.shape[1] == 3, \
		f'Points must be a 2D array with shape (N, 3), got {points.shape}'

		assert points.dtype == float, \
		f'Points must be of type float, got {points.dtype}'

		header = PolyMeshFile.getPolyMeshHeader(
			class_name='vectorField',
			object_name='points',
			format='ascii',
			foam_version='13',
		)

		header += f'{points.shape[0]}\n'
		header += '(\n'

		footer = ')\n\n' + PolyMeshFile.file_EOF + '\n'

		np.savetxt(
			self.path,
			points, fmt='\t(%.16e\t\t%.16e\t\t%.16e)',
			header=header, footer=footer, comments='',
		)

		assert self.path.exists(), \
		f'Points file {self.path} was not created.'

		pass

class FacesWriter :

	def __init__(self, polyMesh_path: Path) :

		assert polyMesh_path.exists() and polyMesh_path.is_dir(), \
		f'PolyMesh_path {polyMesh_path} does not exist or is not a directory'

		self.path_faces = polyMesh_path / 'faces'
		self.path_owner = polyMesh_path / 'owner'
		self.path_neighbour = polyMesh_path / 'neighbour'

		self.path_boundary = polyMesh_path / 'boundary'

		assert not self.path_faces.exists(), \
		f'Faces file {self.path_faces} already exists.'

		assert not self.path_owner.exists(), \
		f'Owner file {self.path_owner} already exists.'

		assert not self.path_neighbour.exists(), \
		f'Neighbour file {self.path_neighbour} already exists.'

		assert not self.path_boundary.exists(), \
		f'Boundary file {self.path_boundary} already exists.'

		pass

	def __writeFaces(self, faces: np.ndarray) -> None :
		'''
		Write faces to the faces file.
		'''

		assert faces.ndim == 2 and faces.shape[1] == 4, \
		f'Faces must be a 2D array with shape (N, 4), got {faces.shape}'

		assert faces.dtype == int, \
		f'Faces must be of type int, got {faces.dtype}'

		header = PolyMeshFile.getPolyMeshHeader(
			class_name='faceList',
			object_name='faces',
			format='ascii',
			foam_version='13',
		)

		header += f'{faces.shape[0]}\n'
		header += '(\n'

		footer = ')\n\n' + PolyMeshFile.file_EOF + '\n'

		np.savetxt(
			self.path_faces,
			faces, fmt='\t4(%d\t\t%d\t\t%d\t\t%d)',
			header=header, footer=footer, comments='',
		)

		assert self.path_faces.exists(), \
		f'Faces file {self.path_faces} was not created.'

		pass

	def __writeOwner(self, owner: np.ndarray) -> None :
		'''
		Write owner to the owner file.
		'''

		assert owner.ndim == 1, \
		f'Owner must be a 1D array, got {owner.shape}'

		assert owner.dtype == int, \
		f'Owner must be of type int, got {owner.dtype}'

		header = PolyMeshFile.getPolyMeshHeader(
			class_name='labelList',
			object_name='owner',
			format='ascii',
			foam_version='13',
		)

		header += f'{owner.shape[0]}\n'
		header += '(\n'

		footer = ')\n\n' + PolyMeshFile.file_EOF + '\n'

		np.savetxt(
			self.path_owner,
			owner, fmt='\t%d',
			header=header, footer=footer, comments='',
		)

		assert self.path_owner.exists(), \
		f'Owner file {self.path_owner} was not created.'

		pass

	def __writeNeighbour(self, neighbour: np.ndarray) -> None :
		'''
		Write neighbour to the neighbour file.
		'''

		assert neighbour.ndim == 1, \
		f'Neighbour must be a 1D array, got {neighbour.shape}'

		assert neighbour.dtype == int, \
		f'Neighbour must be of type int, got {neighbour.dtype}'

		header = PolyMeshFile.getPolyMeshHeader(
			class_name='labelList',
			object_name='neighbour',
			format='ascii',
			foam_version='13',
		)

		header += f'{neighbour.shape[0]}\n'
		header += '(\n'

		footer = ')\n\n' + PolyMeshFile.file_EOF + '\n'

		np.savetxt(
			self.path_neighbour,
			neighbour, fmt='\t%d',
			header=header, footer=footer, comments='',
		)

		assert self.path_neighbour.exists(), \
		f'Neighbour file {self.path_neighbour} was not created.'

		pass

	def __writeBoundary(self, boundary: dict) -> None :
		'''
		Write boundary to the boundary file.
		'''

		assert isinstance(boundary, dict), \
		f'Boundary must be a dictionary, got {type(boundary)}'

		header = PolyMeshFile.getHeader('13')
		header += 'FoamFile\n{\n'
		header += PolyMeshFile.getDictionaryString({
			'format'	: 'ascii',
			'class'		: 'polyBoundaryMesh',
			'location'	: '"constant/polyMesh"',
			'object'	: 'boundary',
		}, 1)
		header += '}\n'
		header += PolyMeshFile.file_separator + '\n\n\n'

		boundary_string = f'{len(boundary)}\n(\n'

		boundary_string += PolyMeshFile.getDictionaryString(boundary, 1)

		boundary_string += ')\n\n'

		with open(self.path_boundary, 'w') as f:
			
			f.write(header + boundary_string + PolyMeshFile.file_EOF + '\n')

		assert self.path_boundary.exists(), \
		f'Boundary file {self.path_boundary} was not created.'

		pass

	def __organizeFaces(self, face_list: list[FaceCollection.FlatFaceCollection]) \
	-> tuple[FaceCollection.FlatFaceCollection, dict] :
		'''
		Organize faces into a FaceCollection.
		'''

		assert isinstance(face_list, list), \
		f'Face list must be a list, got {type(face_list)}'

		assert \
		all(isinstance(face, FaceCollection.FlatFaceCollection) for face in face_list), \
		f'All elements in face_list must be FlatFaceCollection instances'

		# Sort all faces such that boundary face collections are at the end
		face_list.sort(key=lambda x: x.isBoundary())

		# Create a new FaceCollection to hold all faces
		all_faces = FaceCollection.mergeFaceCollections(face_list)

		boundary_dict = {}
		num_faces = 0

		for face_collection in face_list :

			if not face_collection.isBoundary() :

				num_faces += face_collection.getSize()
				continue

			# If the face collection is a boundary, add it to the boundary dictionary
			assert boundary_dict.get(face_collection.name) is None, \
			f'Boundary {face_collection.name} is already defined'

			boundary_dict[face_collection.name] = {
				'type'		: 'patch',
				'nFaces'	: face_collection.getSize(),
				'startFace'	: num_faces,
			}

			num_faces += face_collection.getSize()

		assert num_faces == all_faces.getSize(), \
		f'Total number of faces {num_faces} does not match ' \
		f'the size of all faces {all_faces.getSize()}'

		# Return the organized face collections
		return all_faces, boundary_dict

	def write(self, face_list: list[FaceCollection.FlatFaceCollection]) -> None :
		'''
		Write faces to the faces, owner, neighbour, and boundary files.
		'''

		assert isinstance(face_list, list), \
		f'Face list must be a list, got {type(face_list)}'

		assert \
		all(isinstance(face, FaceCollection.FlatFaceCollection) for face in face_list), \
		f'All elements in face_list must be FlatFaceCollection instances'

		all_faces, boundary_dict = self.__organizeFaces(face_list)

		self.__writeFaces(all_faces.vertices)
		self.__writeOwner(all_faces.owner)
		self.__writeNeighbour(all_faces.neighbour)

		self.__writeBoundary(boundary_dict)

		pass
	