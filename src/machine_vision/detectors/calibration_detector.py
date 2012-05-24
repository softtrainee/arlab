#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Int
#============= standard library imports ========================
from numpy import polyfit, histogram
#============= local library imports  ==========================

from src.image.cvwrapper import  draw_lines, \
    threshold, crop, colorspace, grayspace, find_lines, isolate_color, contour, \
    get_polygons, draw_contour_list, draw_polygons
from src.machine_vision.detectors.detector import Detector

class CalibrationDetector(Detector):

    zoom_start = Int(0)
    zoom_end = Int(75)
    zoom_step = Int(5)


#    def do_zoom_calibration(self, src=None):
#        if src is None:
#            src = self.parent.load_source()
#
#        self.parent.show_image()
#        self.image.frames[0] = colorspace(src)
#        '''
#            loop thru zoomss
#                1. set zoom
#                2. refocus
#                3. calc Ab/Ao
#        '''
#        laser_man = self.parent.laser_manager
#        autofocus_man = self.parent.autofocus_manager
#        fstart = 50
#        fend = 40
#        w, h = src.size()
#        for z in range(self.zoom_start, self.zoom_end, self.zoom_step):
#            if laser_man:
#                laser_man.set_zoom(z, block=True)
#
#            if autofocus_man:
#                autofocus_man._passive_focus_1step('sobel',
#                                                        fstart, fend)
#            fstart -= 5
#            fend -= 5
#
#            src = self.parent.load_source()
#
#            break
##            Ab = areas[0]
##
##            Ao = w * h - Ab
##
##            self.info('ratio {}'.format(Ab, Ao))
    def locate_calibration_object(self, src, t):
        gsrc = grayspace(src)

        tsrc = threshold(gsrc, t)
        ntsrc = colorspace(tsrc)

        cont, hi = contour(tsrc)

        draw_contour_list(ntsrc, cont)
        polygons, brs, areas = get_polygons(cont, hi, nsizes=3, min_area=2000)
        cgsrc = colorspace(gsrc)
        draw_polygons(cgsrc, polygons)
#        print len(polygons)
#        print len(areas), areas

        self.image.frames[0] = cgsrc
        if len(self.image.frames) == 2:
            self.image.frames[1] = ntsrc
        else:
            self.image.frames.append(ntsrc)


        if areas:
            return areas[0]

    def locate_calibration_object1(self):
        src = self.parent.load_source()
        self.parent.show_image()
#        src = grayspace(src)
        self.image.frames[0] = colorspace(src)
        csrc = isolate_color(src, 2)
        self.image.frames.append(csrc)

#        cs = find_circles(src, 200)
#
#        csrc = colorspace(src)
#        self.image.frames.append(csrc)
#        for ci in cs.tolist():
#            ci = map(int, ci)
#
#            draw_circle(csrc, new_point(ci[0], ci[1]), ci[2])

    def locate_calibration_object2(self):
        src = self.parent.load_source()
        w = 640
        h = 480
        x = (640 - w) / 2
        y = (480 - h) / 2

        ox = 0
        oy = 0
        x += ox
        y += oy
        self.parent.show_image()

        src = crop(src, x, y, w, h)
        src = grayspace(src)
        self.image.frames[0] = colorspace(src)

        self.intercepts = []
        for ti in range(40, 60, 1):
            dst, lines = find_lines(src, ti, minlen=200)
            if len(self.image.frames) == 2:
                self.image.frames[1] = colorspace(dst)
            else:
                self.image.frames.append(colorspace(dst))

            clines = self.filter_calibration_lines(lines)

#            time.sleep(0.1)

        bins, edges = histogram(self.intercepts)
        print self.intercepts
        print bins
        print edges
        intercepts = []
        for i, b in enumerate(bins):
            if b:
                intercepts.append(edges[i])

        cpoints = []
        for i in range(len(intercepts)):
            for j in range(len(intercepts)):
#                print i, j, intercepts[i], intercepts[j]
                d = abs(intercepts[i] - intercepts[j])
                if int(d) and not d in cpoints:
                    cpoints.append(d)
        print cpoints
        draw_lines(self.image.frames[0],
                   [[(0, ci), (100, ci) ]for ci in self.intercepts])

    def filter_calibration_lines(self, ls):
        if not ls:
            return

        for l in ls:
            if self._is_calibration_line(l, 0, tol=4.999):
#                print l
                m, b = self._get_coeffs(l)
                print m, b
                if b < 479:
                    print m, b
#                print b
#                self.intercepts.append(b)

    def _get_coeffs(self, l):
        return polyfit([l[0], l[2]],
                       [l[1], l[3]],
                       1)

    def _is_calibration_line(self, l, m, tol=0.01):
        #calculate slope of line
        dx = l[0] - l[2]
        dy = l[1] - l[3]

        if abs(dx) < tol and m == 'inf':
            return True

#        if abs(dx) > 0.0001:
        mm = abs(dy / float(dx))
#        if abs(mm - m) <= tol:
#        print 'a', mm, m, tol
        return abs(m - mm) <= tol

    def update_threshold(self, v):
        pass
#        src = self.image.frames[0]
#        self.image.frames[1] = threshold(src, v)

#============= EOF =============================================
