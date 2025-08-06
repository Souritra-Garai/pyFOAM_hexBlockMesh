from setuptools import setup, find_packages

setup(
	name='pyFOAM_hexBlockMesh',
	version='0.1.0',
	packages=find_packages(),
	install_requires=[
		'numpy'
	],
	entry_points={
		'console_scripts': [
			# Add command line scripts here
		],
	},

	author='Souritra Garai',
	# author_email='',
	# license='MIT',
	description='A Python package for creating hex block meshes for OpenFOAM',
	long_description=open('README.md').read(),
	long_description_content_type='text/markdown',
	classifiers=[
		'Programming Language :: Python :: 3',
		# 'License :: OSI Approved :: MIT License',
		'Operating System :: Linux',
	],
	python_requires='>=3.6',
)