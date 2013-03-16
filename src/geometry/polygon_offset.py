#===============================================================================
# Copyright 2012 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
#============= standard library imports ========================
import math
from numpy import array, cross, dot
#============= local library imports  ==========================
from src.geometry.geometry import sort_clockwise
# import euclid as eu
# import copy



def scaleadd(origin, offset, vectorx):
    """
    From a vector representing the origin,
    a scalar offset, and a vector, returns
    a Vector3 object representing a point 
    offset from the origin.

    (Multiply vectorx by offset and add to origin.)
    """
    multx = vectorx * offset
    return multx + origin

def normalize(v):
    return v / max(abs(v))

def magnitude(v):
    return (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5

def getinsetpoint(pt1, pt2, pt3, offset):
    """
    Given three points that form a corner (pt1, pt2, pt3),
    returns a point offset distance OFFSET to the right
    of the path formed by pt1-pt2-pt3.

    pt1, pt2, and pt3 are two tuples.

    Returns a Vector3 object.
    """
#    origin = eu.Vector3(pt2[0], pt2[1], 0.0)
    origin = array((pt2[0], pt2[1], 0.0))

#    v1 = eu.Vector3(pt1[0] - pt2[0],
#                    pt1[1] - pt2[1], 0.0)
    v1 = array((pt1[0] - pt2[0],
                    pt1[1] - pt2[1], 0.0))
#    v1.normalize()
    v1 = v1 / max(abs(v1))

#    v2 = eu.Vector3(pt3[0] - pt2[0],
#                    pt3[1] - pt2[1], 0.0)
    v2 = array((pt3[0] - pt2[0],
                    pt3[1] - pt2[1], 0.0))

    v2 = v2 / max(abs(v2))

    v3 = v1[:]
#    v3 = copy.copy(v1)
#    v1 = v1.cross(v2)
    v1 = cross(v1, v2)
    v3 += v2

    v3 = v3 / max(abs(v3))
    cs = dot(v3, v2)
    a1 = cs * v2
    a2 = v3 - a1
#    print a2
    if cs > 0:
        alpha = (magnitude(a2)) ** 0.5
    else:
        alpha = -(magnitude(a2)) ** 0.5

    if v1[2] < 0.0:
        retval = scaleadd(origin, -offset / alpha, v3)
    else:
        retval = scaleadd(origin, offset / alpha, v3)
    return tuple(retval)

def polygon_offset(poly, offset):
    if poly[-1][0] != poly[0][0] and poly[-1][1] != poly[0][1]:
        poly = poly + poly[:1]

    polyinset = []
    lenpolygon = len(poly)
    i = 0

    while i < lenpolygon - 2:
        polyinset.append(getinsetpoint(poly[i],
                     poly[i + 1], poly[i + 2], offset))
        i += 1
    polyinset.append(getinsetpoint(poly[-2],
                 poly[0], poly[1], offset))
    polyinset.append(getinsetpoint(poly[0],
                 poly[1], poly[2], offset))
    return polyinset

if __name__ == '__main__':
    from pylab import plot, show, array
    pts = [(2, 7), (4, 12), (8, 15), (16, 9), (11, 5), (8, 7), (5, 5)]
#    pts = sort_clockwise(pts, pts)
    ppts = array(pts + pts[:1])
    xs, ys = ppts.T

#    plot(xs, ys)
    for i in range(6):
        print  i * 0.25
        opts = polygon_offset(pts, i * 0.25)
    #    opts = offsetpolygon(pts, -0.25)
    #    print opts
        opts = array(opts)
    #    print opts
        xs, ys, zs = opts.T
        plot(xs, ys)

    show()
#============= EOF =============    ================================
