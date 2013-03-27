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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import array
import math
#============= local library imports  ==========================
def sort_clockwise(pts, xy, reverse=False):
    '''
        pts = list of points
        xy = list of corresponding x,y tuples
    '''
    xy = array(xy)
    # sort points clockwise
    try:
        xs, ys = xy.T
    except ValueError:
        xs, ys, _ = xy.T
    cx = xs.mean()
    cy = ys.mean()

    angles = [(math.atan2(y - cy, x - cx), pi) for pi, x, y in zip(pts, xs, ys)]
    angles = sorted(angles, key=lambda x: x[0], reverse=reverse)
    _, pts = zip(*angles)

    return list(pts)
#    self.points = list(pts)

def calc_point_along_line(x1, y1, x2, y2, L):
    '''
        calculate pt (x,y) that is L units from x1, y1

        if calculated pt is past endpoint use endpoint


                    * x2,y2
                  /
                /
          L--- * x,y
          |  /
          *
        x1,y1

        L**2=(x-x1)**2+(y-y1)**2
        y=m*x+b

        0=(x-x1)**2+(m*x+b-y1)**2-L**2

        solve for x
    '''
    run = (x2 - x1)

    if run:
        from scipy.optimize import fsolve
        m = (y2 - y1) / float(run)
        b = y2 - m * x2
        f = lambda x: (x - x1) ** 2 + (m * x + b - y1) ** 2 - L ** 2

        # initial guess x 1/2 between x1 and x2
        x = fsolve(f, x1 + (x2 - x1) / 2.)[0]
        y = m * x + b

    else:
        x = x1
        if y2 > y1:
            y = y1 + L
        else:
            y = y1 - L

    lx, hx = min(x1, x2), max(x1, x2)
    ly, hy = min(y1, y2), max(y1, y2)
    if  not lx <= x <= hx or not ly <= y <= hy:
        x, y = x2, y2

    return x, y

def calculate_reference_frame_center(r1, r2, R1, R2):
    '''
        r1=x,y p1 in frame 1 (data space)
        r2=x,y p2 in frame 1
        R1=x,y p1 in frame 2 (screen space)
        R2=x,y p2 in frame 2

        given r1, r2, R1, R2 calculate center of frame 1 in frame 2 space
    '''
    # calculate delta rotation for r1 in R2
    a1 = calc_angle(R1, R2)
    a2 = calc_angle(r1, r2)
    print a1, a2
    rot = 0
#     rot = a1 - a2

    # rotate r1 to convert to frame 2
    r1Rx, r1Ry = rotate_pt(r1, rot)

    # calculate scaling i.e px/mm
    rL = calc_length(r1, r2)
    RL = calc_length(R1, R2)
    rperR = abs(RL / rL)

    print 'rrrr', rL, RL
    print r1, r2, R1, R2
    # calculate center
    cx = R1[0] - r1Rx * rperR
    cy = R1[1] - r1Ry * rperR

    return cx, cy, 180 - rot


def rotate_pt(pt, theta):
    pt = array([[pt[0]], [pt[1]]])

    co = math.cos(math.radians(theta))
    si = math.sin(math.radians(theta))
    R = array([[co, -si], [si, co]])
    npt = R.dot(pt)
    return npt[0, 0], npt[1, 0]

def calc_length(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def calc_angle(p1, p2):
    dx = float(p1[0] - p2[0])
    dy = float(p1[1] - p2[1])
    return math.degrees(math.atan2(dy, dx))

#============= EOF =============================================
