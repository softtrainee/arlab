'''
see http://paulbourke.net/geometry/polyarea/


'''
import numpy as np
cimport numpy as np
def area(np.ndarray[np.float64_t, ndim=2] data):
	cdef int n = data.shape[0]
	cdef int j = n - 1
	cdef float x = 0
	cdef float y = 0
	cdef float a = 0
	for i in range(n):
		p1 = data[i]
		p2 = data[j]
		a += (p1[0] * p2[1])
		a -= (p1[1] * p2[0])
		j = i
	return a / 2

def centroid(np.ndarray[np.float64_t, ndim=2] data):
	cdef int n = data.shape[0]
	cdef int j = n - 1
	cdef float x = 0
	cdef float y = 0
	for i in range(n):
		p1 = data[i]
		p2 = data[j]
		f = p1[0] * p2[1] - p2[0] * p1[1]
		x += (p1[0] + p2[0]) * f
		y += (p1[1] + p2[1]) * f
		j = i

	cdef float a = area(data)
	return x / (6 * a), y / (6 * a)