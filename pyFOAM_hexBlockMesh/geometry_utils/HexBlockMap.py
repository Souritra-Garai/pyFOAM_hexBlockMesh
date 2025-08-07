# Refer to Figure 5.3
# https://doc.cfd.direct/openfoam/user-guide-v12/blockmesh#x28-1570005.4.4
# for the hex vertices numbering

#  0 represents start of an array
# -1 represents end of an array
# For a (n0, n1, n2, ...) points array named hex_A, 
# hexA[vertex_map[i]] represents the vertex i
vertex_map = (
	( 0, 0, 0),	# 0
	(-1, 0, 0),	# 1
	(-1,-1, 0),	# 2
	( 0,-1, 0),	# 3
	( 0, 0,-1),	# 4
	(-1, 0,-1),	# 5
	(-1,-1,-1),	# 6
	( 0,-1,-1)	# 7
)

# Dictionary tells which vertices are connected
# via an edge and along which axis
# (v0, v1) : axn
# Edge v0 -> v1 is along positive axn
vertex_connectivity = {
	(0, 1) : 0,	# 0
	(3, 2) : 0,	# 1
	(7, 6) : 0,	# 2
	(4, 5) : 0,	# 3
	(0, 3) : 1,	# 4
	(1, 2) : 1,	# 5
	(5, 6) : 1,	# 6
	(4, 7) : 1,	# 7
	(0, 4) : 2,	# 8
	(1, 5) : 2,	# 9
	(2, 6) : 2,	# 10
	(3, 7) : 2	# 11
}

# Each face is represented by a tuple of vertex indices
# The vertices are ordered such that the face normal points outwards
hex_face_vertices = (
	(0, 3, 2, 1),	# 0
	(4, 5, 6, 7),	# 1
	(0, 1, 5, 4),	# 2
	(2, 3, 7, 6),	# 3
	(0, 4, 7, 3),	# 4
	(1, 2, 6, 5)	# 5
)

# For face with normal along axis axn,
# face_axes[axn] gives the tuple of two axes which
# are parallel to the face, such that
# Cross product of face_axes[axn][0] and face_axes[axn][1] gives the face normal
face_axes = (
	(1, 2),	# 0
	(2, 0),	# 1
	(0, 1),	# 2
)

# Each tuple of slices gives the vertices to form a quadrilateral face
# from a 2D/3D grid of points
# The vertex slices are ordered in anti-clockwise direction
# to preserve the right-hand coordinate axis system
face_vertex_slices = (
	(slice(0, -1),		slice(0, -1)),		# 0
	(slice(1, None),	slice(0, -1)),		# 1
	(slice(1, None),	slice(1, None)),	# 2
	(slice(0, -1),		slice(1, None))		# 3
)
