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
#============= local library imports  ==========================
import numpy as np
from src.lasers.geometry import sort_clockwise
from pyface.timer.do_later import do_later
from src.machine_vision.convex_hull import convex_hull
# from pylab import plot, show, text

def slope(p1, p2):
    dx = float((p2[0] - p1[0]))
    dy = float((p2[1] - p1[1]))
    if dx and dy:
        return  dx / dy  # 1/m
    else:
        return 0

def make_ET(points):
    '''
        points should be (x0,y0),(x1,y1), (x1,y1), (x2,y2),...., (xn,yn),(x0,y0)
    '''
    ET = []
    for i in range(0, len(points) - 1, 2):
        p1, p2 = points[i], points[i + 1]
        m = slope(p1, p2)
        eymin = min(p1[1], p2[1])
        eymax = max(p1[1], p2[1])
        exmin = p1[0] if p1[1] < p2[1] else p2[0]
        ET.append((m, eymin, exmin, eymax, i / 2))
    return ET

def split_vertices(points, dy):
    '''
        return new edge table pairs
    '''
    mpts = points[-1:] + points + points[:1]
    npts = []
    for i in range(1, len(mpts) - 1):
        pv = mpts[i - 1]
        cv = mpts[i]
        nv = mpts[i + 1]
        y = cv[1] - dy
        if pv[1] < cv[1] < nv[1]:
            cm = slope(pv, cv)
            x = pv[0] + cm * dy
            cv_prime = (x, y)
            npts.append(cv_prime)
            npts.append(cv)
        elif pv[1] > cv[1] > nv[1]:
            cm = slope(cv, nv)
            x = nv[0] + cm * dy
            cv_prime = (x, y)
            npts.append(cv)
            npts.append(cv_prime)
        else:
            npts.append(cv)
            npts.append(cv)

    npts = npts[1:] + npts[:1]
    return npts

def get_yminmax(points):
    pts = np.asarray(points)
    _, ys = pts[:, 0], pts[:, 1]
    ymin = np.min(ys)
    ymax = np.max(ys)
#    return ymin, ymax
    return map(int, (ymin, ymax))

def make_scan_lines(points, step=1):
    '''
        returns a line of scan lines
        a scan line = y, xi,...xn n will always be a multiple of 2
        x,y should be integers
        
        google "scan line polygon fill algorithm example"
        www.kau.edu.sa/Files/0053697/.../Polygon%20Filling.ppt
    '''

    # sort clockwise
#    xy = [pi for pi in points]

#    # sort points clockwise
#        xs, ys = xy.T
#        cx = xs.mean()
#        cy = ys.mean()
#
#
#        angles = [(math.atan2(y - cy, x - cx), pi) for pi, x, y in zip(self.points, xs, ys)]
#        angles = sorted(angles, key=lambda x: x[0])
#        _, pts = zip(*angles)
#        self.points = list(pts)

    npts = points[:1]
    for pi in points[1:]:
        npts.append(pi)
        npts.append(pi)

    npts.append(points[0])

    ymin, ymax = get_yminmax(points)

    n = ymax - ymin
    scanlines = np.linspace(ymin, ymax, n * 1 / float(step) + 1)

    # make Basic ET
    ET = np.array(make_ET(npts))

    # make modified ET
    dy = scanlines[1] - scanlines[0]
    nvs = split_vertices(points, dy)

    # make ET using split vertices
    MET = np.array(make_ET(nvs))

    # copy column 0 of ET into MET
    MET[:, 0] = ET[:, 0]

    # copy last column of ET into MET
    MET[:, -1] = ET[:, -1]

#    MET = sorted(MET, key=lambda x: x[0])
#    MET = sorted(MET, key=lambda x: x[2])
#    MET = sorted(MET, key=lambda x: x[1])

    xintersections = []
    for _ in range(len(scanlines)):
        xs = []
        for _ in range(len(MET)):
            xs.append(None)
        xintersections.append(xs)

    for m, eymin, exmin, eymax, ei in MET:
        cnt = 0
#        print '-----------'
        for xint, si in zip(xintersections, scanlines):
#            print eymin, si, eymax, eymin <= si <= eymax
            if eymin <= si <= eymax:
                v = exmin + step * m * cnt
#                print si, v
                xint[int(ei)] = v
                cnt += 1

    xs = [sorted([ii for ii in xi if ii is not None]) for xi in xintersections]
    return zip(scanlines, xs)

def raster_polygon(points, step=1, skip=1,
                   move_callback=None,
                   start_callback=None,
                   end_callback=None,
                   use_convex_hull=None,
                   use_plot=False,
                   verbose=False):

    if use_convex_hull:
        points = convex_hull(points)

    points = sort_clockwise(points, points)

#    print points
    lines = make_scan_lines(points, step)
    points = points + points[:1]

    if use_plot:
        from pylab import plot, text, show
        # plot outline
        xs, ys = zip(*points)
        plot(xs, ys)

    # initialize variables
    cnt = 0
    direction = 1
    lasing = False

    if verbose:
        print 'start raster'

    # loop thru each scan line
    for yi, xs in lines[::skip]:
        if direction == -1:
            xs = list(reversed(xs))

        # convert odd numbers lists to even
        n = len(xs)
        if n % 2 != 0:
            xs = sorted(list(set(xs)))

        # traverse each x-intersection pair
        n = len(xs)
        for i in range(0, n, 2):
            yy = (yi, yi)
            if len(xs) <= 1:
                continue

            xx = (xs[i], xs[i + 1])
            if abs(xs[i] - xs[i + 1]) > 1e-10:
                if not lasing:
                    if verbose:
                        print 'fast to {} {},{}'.format(cnt, xx[0], yy[0])
                        print '===================== laser on'
                    if move_callback is not None:
                        move_callback(xx[0], yy[0], 'fast')
                    if start_callback is not None:
                        start_callback()

                    lasing = True
                else:
                    if verbose:
                        print 'slow to {} {},{}'.format(cnt, xx[0], yy[0])
                    if move_callback is not None:
                        move_callback(xx[0], yy[0], 'slow')

                if verbose:
                    print 'move to {}a {},{}'.format(cnt, xx[1], yy[1])
                    print 'wait for move complete'

                if move_callback is not None:
                    move_callback(xx[1], yy[1], 'slow')

#                if n > 2 and not i * 2 >= n:
                if i + 2 < n and not xs[i + 1] == xs[i + 2]:
                    if verbose:
                        print '===================== laser off'
                    if end_callback is not None:
                        end_callback()

                    lasing = False
                if use_plot:
                    plot(xx, yy, 'r', linewidth=skip / 4.)
                    text(xx[0], yy[0], '{}'.format(cnt))

                cnt += 1
                flip = True
            else:
                flip = False

        if flip:
            direction *= -1

    if verbose:
        print '===================== laser off'
        print 'end raster'

    if end_callback is not None:
        end_callback()
        
    if use_plot:
        do_later(show)
#        show()


if __name__ == '__main__':
#    pts = [(2, 7), (4, 12), (8, 15), (16, 9), (11, 5), (8, 7), (5, 5)]
    pts = [(2, 7), (4, 12), (8, 15), (16, 9), (11, 5), (8, 0), (5, 5)]
    pts = np.array(pts)
    pts *= 100
    pts = list(pts)
#    pts = [(8, 15), (2, 7), (4, 12), (16, 9), (11, 5), (5, 5), (8, 7)]
#    pts = [(1, 1), (2, 5), (5, 4), (8, 7), (10, 4), (10, 2)]

#    pts = [(0, 0), (10, 0), (10, 10), (0, 10)]
    raster_polygon(pts, 1, 50, use_plot=True, verbose=True)

#============= EOF =============================================
#    # sort et on ymin
#    ET = sorted(ET, key=lambda x: x[1])
#    buckets = []
#    cymin = ET[0][1]
#    bucket = ET[:1]
#    for m, eymin, exmin, eymax, ei in ET[1:]:
#        if eymin == cymin:
#            bucket.append((m, eymin, exmin, eymax, ei))
#        else:
#            bucket = sorted(bucket, key=lambda x:x[0], reverse=True)
#            bucket = sorted(bucket, key=lambda x:x[2], reverse=True)
#
#            buckets.append(bucket)
#            bucket = [(m, eymin, exmin, eymax, ei)]
#
#        cymin = eymin
# #        print bucket
# #        print eymin, cymin, '   ', m, eymin, exmin, eymax
#
#    buckets.append(bucket)
#    AT = []
#    for si in scanlines:
#        for bi in buckets:
#            if bi[0][1] == si:
#                AT.append(bi)
#                break
#        else:
#            AT.append(None)
