import numpy as np

def checkCoordinatesOrientation(
	coordinates:np.ndarray
	) -> bool :
	'''
	Check if the coordinates are oriented correctly.
	Coordinates are considered to have a right handed orientation
	if the volume is positive.
	'''

	assert isinstance(coordinates, np.ndarray), 'Invalid input'
	assert np.issubdtype(coordinates.dtype, np.floating), 'Invalid input'
	assert coordinates.ndim == 4, 'Invalid input'
	assert coordinates.shape[3] == 3, 'Invalid input'

	increments_x = coordinates[1:, :-1, :-1] - coordinates[:-1, :-1, :-1]
	increments_y = coordinates[:-1, 1:, :-1] - coordinates[:-1, :-1, :-1]
	increments_z = coordinates[:-1, :-1, 1:] - coordinates[:-1, :-1, :-1]

	volume_determinant = np.linalg.det(
		np.stack((
			increments_x,
			increments_y,
			increments_z
		), axis=-1)
	)

	return bool(np.all(volume_determinant > 0))
