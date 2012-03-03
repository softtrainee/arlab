'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
from traits.api import Int
from pyface.timer.api import do_later
#============= standard library imports ========================
import time
from numpy import array, hstack
#============= local library imports  ==========================
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.image.cvwrapper import draw_circle, new_point, find_circles, draw_lines, \
    threshold, crop, colorspace, grayspace, contour, \
    get_polygons, draw_contour_list, draw_polygons
from detector import Detector
from src.graph.regression_graph import RegressionGraph


class ZoomCalibrationDetector(Detector):

    zoom_start = Int(0)
    zoom_end = Int(75)
    zoom_step = Int(5)

    def do_zoom_calibration(self):
        dm = CSVDataManager()
#        self.calibration_detector = CalibrationDetector(parent=self,
#                                image=self.image,
#                                pxpermm=self.pxpermm,
#                                )

        self.parent.show_image()
#        zoomin_areas = array([])
#        zoomout_areas = array([])
#        zoomin_zooms = array([])
#        zoomout_zooms = array([])
        for i in range(1):
            dm.new_frame()
            if not self.parent.testing:
                break

            self.info('zoom calibration trial {}'.format(i + 1))
            zoom_start = 0
            zoom_end = 50
            zoom_step = 5
            xsin = range(zoom_start, zoom_end, zoom_step)

            fstart = 10
            fend = 2
            fstep = 0

            if not self.parent.testing:
                break
            self.info('zoom in sweep')
            zia = array(self.zoom_calibration_sweep(zoom_start, zoom_end,
                                        zoom_step, fstart,
                                        fend, fstep, dm))
            if i == 0:
                zoomin_areas = zia
                zoomin_zooms = array(xsin)
            else:
                zoomin_areas = hstack((zoomin_areas, zia))
                zoomin_zooms = hstack((zoomin_zooms, xsin))

            zoom_start = zoom_end - zoom_step
            zoom_end = -1
            zoom_step = -5
#            fstart = 10
#            fend = 2
#            fstep = 0
            xsout = xsin[:]
#            xsout.reverse()

            if not self.parent.testing:
                break

            self.info('zoom out sweep')
            zoa = array(self.zoom_calibration_sweep(zoom_start, zoom_end,
                                        zoom_step, fstart,
                                        fend, fstep, dm))
#            zoa = zia
            zoa = array(zoa[::-1])
            if i == 0:
                zoomout_areas = zoa
                zoomout_zooms = xsout
            else:
                zoomout_areas = hstack((zoomout_areas, zoa))
                zoomout_zooms = hstack((zoomout_zooms, xsout))

        g = RegressionGraph(show_regression_editor=False)
        g.new_plot()
#        g.new_plot()

        wh = 640 * 480.

        def cal_pxpermm(zs):
            return [self.pxpermm * (1 + (ai - zs[0]) / (wh)) for ai in zs]

        ys_in = cal_pxpermm(zoomin_areas)

        ys_out = cal_pxpermm(zoomout_areas)

#        g.new_series(x=xsin, y=ys_in, fit_type='parabolic')
#        g.new_series(x=xsout, y=ys_out, fit_type='parabolic')
        g.new_series(x=hstack((zoomin_zooms, zoomout_zooms)),
                      y=hstack((ys_in, ys_out)), fit_type='parabolic')
#        xa = linspace(0, 50, 50)
#        g.new_series(x=xa, y=polyval(polyfit(xs, ys, 2), xa), regress=False)

        do_later(g.edit_traits)

    def zoom_calibration_sweep(self, zs, ze, step, fstart, fend, fstep, dm):
        areas = []
        for zi in range(zs, ze, step):
            #set zoom
            if not self.parent.testing:
                break

            if self.parent.laser_manager is not None:
                self.parent.laser_manager.set_zoom(zi, block=True)
                time.sleep(1)

                refocus = True
                if self.parent.autofocus_manager is not None and refocus:
                    self.parent.autofocus_manager._passive_focus_1step(fstart=fstart,
                                                          fend=fend,
                                                          operator='laplace',
                                                          velocity_scalar=0.25)
                    fstart += fstep
                    fend += fstep
                    time.sleep(2)

#            accumulated = new_dst(mode='float32')
            src = self.parent.load_source()
#            for i in range(5):
#                if not self.testing:
#                    break
#                self.info('accumulating image {}'.format(i + 1))
#                src = self.load_source()
#                if i == 0:
#                    size = src.size()
#                    w = size[0]
#                    h = size[1]
#                    accumulated = new_dst(width=w, height=h, mode='float32')
##                print src.size(), accumulated.size()
#                running_average(src, accumulated)
#                time.sleep(0.1)
#
#            src = convert(accumulated, new_dst())

            if not self.parent.testing:
                break

            for ti in range(150, 200):
                area = self.calculate_calibration_area(src, ti)
#                time.sleep(1)
                if area:
                    self.info('calculated area for {}= {}'.format(
                                                        zi, area))
                    areas.append(area)
                    dm.write_to_frame((zi, area))
                    break

        return areas

    def calculate_calibration_area(self, src, t):
        gsrc = grayspace(src)

        tsrc = threshold(gsrc, t)
        ntsrc = colorspace(tsrc)

        cont, hi = contour(tsrc)

        draw_contour_list(ntsrc, cont)
        polygons, _brs, areas = get_polygons(cont, hi, nsizes=3, min_area=2000)
        cgsrc = colorspace(gsrc)
        draw_polygons(cgsrc, polygons)

        self.image.frames[0] = cgsrc
        if len(self.image.frames) == 2:
            self.image.frames[1] = ntsrc
        else:
            self.image.frames.append(ntsrc)

        if areas:
            return areas[0]

#    def locate_calibration_object1(self):
#        src = self.parent.load_source()
#        self.parent.show_image()
##        src = grayspace(src)
#        self.image.frames[0] = colorspace(src)
#        csrc = isolate_color(src, 2)
#        self.image.frames.append(csrc)

#        cs = find_circles(src, 200)
#
#        csrc = colorspace(src)
#        self.image.frames.append(csrc)
#        for ci in cs.tolist():
#            ci = map(int, ci)
#
#            draw_circle(csrc, new_point(ci[0], ci[1]), ci[2])

#    def locate_calibration_object2(self):
#        src = self.parent.load_source()
#        w = 640
#        h = 480
#        x = (640 - w) / 2
#        y = (480 - h) / 2
#
#        ox = 0
#        oy = 0
#        x += ox
#        y += oy
#        self.parent.show_image()
#
#        src = crop(src, x, y, w, h)
#        src = grayspace(src)
#        self.image.frames[0] = colorspace(src)
#
#        self.intercepts = []
#        for ti in range(40, 60, 1):
#            dst, lines = find_lines(src, ti, minlen=200)
#            if len(self.image.frames) == 2:
#                self.image.frames[1] = colorspace(dst)
#            else:
#                self.image.frames.append(colorspace(dst))
#
#            clines = self.filter_calibration_lines(lines)
#
##            time.sleep(0.1)
#
#        bins, edges = histogram(self.intercepts)
#        print self.intercepts
#        print bins
#        print edges
#        intercepts = []
#        for i, b in enumerate(bins):
#            if b:
#                intercepts.append(edges[i])
#
#        cpoints = []
#        for i in range(len(intercepts)):
#            for j in range(len(intercepts)):
##                print i, j, intercepts[i], intercepts[j]
#                d = abs(intercepts[i] - intercepts[j])
#                if int(d) and not d in cpoints:
#                    cpoints.append(d)
#        print cpoints
#        draw_lines(self.image.frames[0],
#                   [[(0, ci), (100, ci) ]for ci in self.intercepts])
#
#    def filter_calibration_lines(self, ls):
#        if not ls:
#            return
#
#        for l in ls:
#            if self._is_calibration_line(l, 0, tol=4.999):
##                print l
#                m, b = self._get_coeffs(l)
#                print m, b
#                if b < 479:
#                    print m, b
##                print b
##                self.intercepts.append(b)
#
#    def _get_coeffs(self, l):
#        return polyfit([l[0], l[2]],
#                       [l[1], l[3]],
#                       1)
#
#    def _is_calibration_line(self, l, m, tol=0.01):
#        #calculate slope of line
#        dx = l[0] - l[2]
#        dy = l[1] - l[3]
#
#        if abs(dx) < tol and m == 'inf':
#            return True
#
##        if abs(dx) > 0.0001:
#        mm = abs(dy / float(dx))
##        if abs(mm - m) <= tol:
##        print 'a', mm, m, tol
#        return abs(m - mm) <= tol

    def update_threshold(self, v):
        pass
#        src = self.image.frames[0]
#        self.image.frames[1] = threshold(src, v)

#======== EOF ================================
