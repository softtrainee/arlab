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
from traits.api import HasTraits, Float, Any, Instance, Range, Button, Int, Property, Bool, Tuple
from traitsui.api import View, Item, Handler, HGroup, spring, Spring
from pyface.timer.do_later import do_later, do_after
#============= standard library imports ========================
from numpy import histogram, argmax, argmin, array, linspace, asarray, mean
#from scipy.ndimage.filters import sobel, generic_gradient_magnitude
#from scipy.ndimage import sum as ndsum
#from scipy.ndimage.measurements import variance

from ctypes_opencv.cxcore import cvCircle, CV_AA, cvRound, cvPutText, cvScalar, \
    cvFont, cvPoint

#============= local library imports  ==========================
from src.image.image_helper import draw_polygons, draw_contour_list, colorspace, \
    threshold, grayspace, crop, centroid, new_point, contour, get_polygons, \
    erode, dilate, draw_rectangle, subsample, rotate, smooth, clone, \
    convert_color, draw_lines
#    erode, dilate, draw_rectangle, clone

#from src.managers.manager import Manager
from src.image.image import Image
#from src.image.image_editor import ImageEditor
#
#from src.helpers.paths import  positioning_error_dir
#from src.helpers.filetools import unique_path
#from threading import Thread
#import os
#import time
#from src.graph.graph import Graph
#from src.data_processing.time_series.time_series import smooth
import random
import time
from src.loggable import Loggable
DEVX = random.randint(-10, 10)
DEVY = random.randint(-10, 10)
DEVX = 0
DEVY = -2
CX = 39
CY = -41
class TargetResult(object):
    def __init__(self, origin, cv, ps, cs, tv, dv, ev, br, *args, **kw):
        self.origin = origin
        self.centroid_value = cv
        self.poly_points = ps
        self.contours = cs
        self.threshold_value = tv
        self.dilate_value = dv
        self.erode_value = ev
        self.bounding_rect = br

    @property
    def dev_centroid(self):
        return (cvRound(self.origin[0] - self.centroid_value[0]),
                cvRound(self.origin[1] - self.centroid_value[1]))

    @property
    def dev_br(self):
        return (cvRound(self.origin[0] - self.bounding_rect[0]),
                cvRound(self.origin[1] - self.bounding_rect[1]))
    @property
    def aspect_ratio(self):
        return self.bounding_rect.width / float(self.bounding_rect.height)
    @property
    def area(self):
        return self.bounding_rect.width * self.bounding_rect.height
class HoleDetector(Loggable):
    pxpermm = Float
    _debug = False
#    video = Any
    image = Instance(Image)

    cropwidth = 4
    cropheight = 4
    cropscalar = 0.5

    crosshairs_offsetx = 0
    crosshairs_offsety = 0

    style = 'co2'

    use_dilation = Bool(False)
    use_erosion = Bool(True)
    save_positioning_error = Bool(False)
    use_histogram = Bool(False)

    def _search_for_well(self, src, start, end, cw, ch):
        dev1x = []
        dev1y = []
        dev2x = []
        dev2y = []
        ts = []
        ds = []
        es = []

        rresults = None
        #make end inclusive
        for i in range(start, end + 1):
            self._threshold = i
            try:
                results = self._calculate_positioning_error(src, cw, ch, threshold_val=i)
            except Exception, e:
                print e

            if results:
                '''                 
                 instead of trying to figure out if the result is the left of right well
                 if only one result is found require that both wells are identified ie len(results)==2
                 then determine which is the left and right
                 
                '''
                if self.style == 'co2':
                    _, _, dx, dy, ti, di, ei = self._co2_well(results)
                else:
                    _, _, dx, dy = self._diode_well(results)

                dev2x += dx
                dev2y += dy

                ts.append(ti)
                ds.append(di)
                es.append(ei)
                rresults = results

        avg = lambda s: sum(s) / max(1, len(s))
        return rresults, dev1x, dev1y, dev2x, dev2y, avg(ts), avg(ds), avg(es)

    def _diode_well(self, results, right_search=True):
        dev1x = []
        dev1y = []
        dev2x = []
        dev2y = []

        if len(results) >= 2:
            r1 = results[0]
            r2 = results[1]
            if right_search:
#               search for the rhs well
                func = min
                func2 = argmin
            else:
#               search for the lhs well
                func = max
                func2 = argmax

            if r2 is not None:
#                xargs = array([r1.dev1[0], r2.dev1[0]])
#                yi = func2(xargs)
#                dx = func(xargs) 
#                dy = r2.dev1[1] if yi else r1.dev1[1] 

                xargs = array([r1.dev2[0], r2.dev2[0]])
                yi = func2(xargs)
                dx2 = func(r1.dev2[0], r2.dev2[0])
                dy2 = r2.dev2[1] if yi else r1.dev2[1]

            #dev1x.append(dx)
            dev2x.append(dx2)
            #dev1y.append(dy)
            dev2y.append(dy2)

        return dev1x, dev1y, dev2x, dev2y

    def _co2_well(self, results):
        devx, devy = zip(*[r.dev_centroid for r in results])
        ts = results[0].threshold_value
        es = results[0].erode_value
        ds = results[0].dilate_value

        return [], [], devx, devy, ts, ds, es

    def _calculate_positioning_error(self, src, cw, ch, threshold_val=None):
#        src = self.image.source_frame

        cw_px = int(cw * self.pxpermm)
        ch_px = int(ch * self.pxpermm)

        #for debugging calculated deviation should equal devx,devy
        xo = 0; yo = 0

        if self._debug:
            xo = CX + DEVX
            yo = CY + DEVY

        x = int((src.width - cw_px) / 2 + xo)
        y = int((src.height - ch_px) / 2 + yo)

#        smooth(src)        
        self.croppixels = (cw_px, ch_px)
        crop(src, x, y, cw_px, ch_px)
        gsrc = grayspace(src)
        self.image.frames[0] = colorspace(gsrc)

        if threshold_val is None:
            threshold_val = self.start_threshold_search_value

        steps = xrange(threshold_val, threshold_val + 1, 1)

        results = self._threshold_loop(gsrc, steps, 0, 0)
        if results:
            if not results and self.use_dilation:
                results = self._dilate_loop(gsrc, steps, 0)

        if not results and self.use_erosion:
            results = self._erode_loop(gsrc, steps, dilate=self.use_dilation)

        return results

    def _dilate_loop(self, gsrc, steps, ei):
        for di in range(1, 4):
            center = self._threshold_loop(gsrc, steps, di, ei)
            if center:
                return center

    def _erode_loop(self, gsrc, steps, dilate=True):
        for ei in range(1, 4):
            if dilate:
                center = self._dilate_loop(gsrc, steps, ei)
            else:
                center = self._threshold_loop(gsrc, steps, 0, ei)
            if center:
                return center

    def _threshold_loop(self, gsrc, steps, *args):
        for td in steps:
            params = self._calc_sample_hole_position(gsrc, td, *args)
            if params:
                return params
#            time.sleep(0.5)

    def _calc_sample_hole_position(self, gsrc, ti, dilate_val, erode_val, min_area=1000, max_area=None):

#        if self._debug:
#            time.sleep(0.1)

#        min_area = 1000
        if max_area is None:
            max_area = gsrc.width * gsrc.height


        thresh_src = threshold(gsrc, ti)

        if dilate_val:
            thresh_src = dilate(thresh_src, dilate_val)
        if erode_val:
            thresh_src = erode(thresh_src, erode_val)

        if len(self.image.frames) == 2:
            self.image.frames[1] = colorspace(thresh_src)
        else:
            self.image.frames.append(colorspace(thresh_src))

        found = []
        _n, contours = contour(thresh_src)
        if contours:
            polygons, bounding_rect = get_polygons(contours, min_area, max_area, 0)
            if polygons:
                for pi, br in zip(polygons, bounding_rect):
                    if len(pi) > 4:
                        cx, cy = centroid(pi)
                        tr = TargetResult(self._get_true_xy(),
                                          (cx, cy), pi, contours, ti, dilate_val, erode_val, br)

                        if self._debug:
#                            self.debug('threshold={}, dilate={}, erode={}'.format(ti, dilate_val, erode_val))
                            self._draw_result(self.image.frames[1], tr)
                            time.sleep(0.5)

                        if self.style == 'co2':
                            if self._near_center(cx, cy):
                                found.append(tr)
                        else:
                            found.append(tr)

        return found

    def _draw_result(self, src, result, with_br=False, thickness=1, color=(255, 0, 0)):
        self._draw_indicator(src, new_point(*result.centroid_value), shape='crosshairs')
        draw_polygons(src, [result.poly_points])
        if with_br:
            draw_rectangle(src, result.bounding_rect.x,
                                result.bounding_rect.y,
                                result.bounding_rect.width,
                                result.bounding_rect.height,
                                thickness=thickness,
                                color=color
                                )

    def _near_center(self, x, y, tol=1.5):
        cx = self.croppixels[0] / 2.0
        cy = self.croppixels[1] / 2.0

        tol *= self.pxpermm

        return abs(x - cx) < tol and abs(y - cy) < tol

    def _get_true_xy(self):
        cw_px = self.cropwidth * self.pxpermm
        ch_px = self.cropheight * self.pxpermm

        true_cx = cw_px / 2.0 + self.crosshairs_offsetx
        true_cy = ch_px / 2.0 + self.crosshairs_offsety

        return true_cx, true_cy

    def _draw_markup(self, results, dev=None):
        #add to indicators to ensure the indicator is drawn on top
        indicators = []
        for pi in results:

            f1 = self.image.frames[1]
            f0 = self.image.frames[0]
            draw_polygons(f0, [pi.poly_points], color=(255, 7, 0), thickness=1)
            draw_contour_list(f1, pi.contours, external_color=(255, 255, 0))

            #draw the centroid in blue
            centroid_center = new_point(*pi.centroid_value)
            indicators.append((f1, centroid_center , (0, 255, 0), 'rect', 2))

            #calculate bounding rect and bounding square for polygon
            r = pi.bounding_rect
            draw_rectangle(f1, r.x, r.y, r.width, r.height)

            br_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
            indicators.append((f1,
                               br_center,
                               (255, 0, 0), 'rect', 2))

#                #if % diff in w and h greater than 20% than use the centroid as the calculated center
#                #otherwise use the bounding rect center            
#                dwh = abs(r.width - r.height) / float(max(r.width, r.height))
#                if dwh > 0.2:
#                    calc_center = centroid_center
#                else:
#                    calc_center = br_center

            calc_center = centroid_center
            #indicate which center is chosen                
            indicators.append((f0, calc_center, (0, 255, 255), 'crosshairs', 1))
            indicators.append((f1, calc_center, (0, 255, 255), 'crosshairs', 1))

            pi.center = calc_center

        #draw the center of the image
        true_cx, true_cy = self._get_true_xy()
        self._draw_indicator(f0, new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')
        self._draw_indicator(f1, new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')

        for i in indicators:
            self._draw_indicator(*i)

        #draw the calculated center
        if dev:
            self._draw_indicator(f0, new_point(true_cx - dev[0],
                                               true_cy - dev[1]), (255, 0, 255), 'crosshairs')

    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=3, thickness= -1):
        r = size
        if shape == 'rect':
            draw_rectangle(src, center.x - r / 2, center.y - r / 2, r, r,
                           color=color,
                           thickness=thickness)
        elif shape == 'crosshairs':
            draw_lines(src,
                   [[(center.x - size, center.y),
                    (center.x + size, center.y)],
                    [(center.x, center.y - size),
                     (center.x, center.y + size)]],
                       color=color,
                       thickness=1
                   )
        else:
            cvCircle(src, center, r, color, thickness=thickness, line_type=CV_AA)

#============= EOF =====================================
