from pathlib import Path

file_separator	= '// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //'
file_EOF	= '// ************************************************************************* //'

def getHeader(version: str) -> str:
	'''
	Return the OpenFOAM file header.
	'''

	file_header = \
f'''/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  {version}
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
'''
	return file_header

def getDictionaryString(input_dict: dict, indent: int = 0) -> str:
	'''
	Write a dictionary to the specified file path with proper indentation.
	'''

	if len(input_dict) == 0 : return ''

	max_key_length = max(len(str(key)) for key in input_dict.keys())

	n = len(input_dict)

	return_string = ''

	for key, value in input_dict.items() :

		if isinstance(value, dict):

			return_string += '\t' * indent + f'{key:<{max_key_length}}\n'
			return_string += '\t' * indent + '{\n'

			return_string += getDictionaryString(value, indent + 1)

			return_string += '\t' * indent + '}\n'

			if n > 1 : return_string += '\n'

		else:
			return_string += '\t' * indent + f'{key:<{max_key_length}}\t{value};\n'

		n -= 1

	return return_string

def getPolyMeshHeader(
	class_name: str,
	object_name: str,
	format: str = 'ascii',
	foam_version: str = '13',
	file_version: str| None = None,
) -> str :
	'''
	Return the OpenFOAM PolyMesh header.
	'''

	file_dict = {
		'format'	: format,
		'class'		: class_name,
		'location'	: '"constant/polyMesh"',
		'object'	: object_name,
	}

	if file_version is not None :
		
		file_dict['version'] = file_version

	header = getHeader(foam_version)
	header += 'FoamFile\n{\n'
	header += getDictionaryString(file_dict, 1)
	header += '}\n'
	header += file_separator + '\n\n\n'

	return header
