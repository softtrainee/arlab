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
from traits.api import HasTraits, Float, Any, Instance, Range, Button, Int, \
    Property, Bool, Tuple
#from traitsui.api import View, Item, Handler, HGroup, spring, Spring
#from pyface.timer.do_later import do_later, do_after
#============= standard library imports ========================
from numpy import histogram, argmax, argmin, array, linspace, asarray, mean
#from numpy.ma import masked_array
#from scipy.ndimage.filters import sobel, generic_gradient_magnitude
#from scipy.ndimage import sum as ndsum
#from scipy.ndimage.measurements import variance

#from ctypes_opencv.cxcore import cvCircle, CV_AA, cvRound

#============= local library imports  ==========================
from src.image.cvwrapper import draw_polygons, draw_contour_list, \
    threshold, grayspace, crop, centroid, new_point, contour, get_polygons, \
    draw_rectangle, draw_lines, colorspace, draw_circle, get_size, \
    dilate, erode, denoise, smooth, find_circles#, add_images
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
#import time
#from src.loggable import Loggable
from src.helpers.paths import positioning_error_dir
from src.helpers.filetools import unique_path
import os
from detector import Detector
DEVX = random.randint(-10, 10)
DEVY = random.randint(-10, 10)
DEVX = 0
DEVY = 0
CX = 2
CY = -2


class TargetResult(object):
    def __init__(self, origin, cv, cv2, ps, ps2,
                 cs, hier, tv, dv, ev, br, *args, **kw):
        self.origin = origin
        self.centroid_value = cv
        self.centroid_value2 = cv2
        self.poly_points = ps
        self.poly_points2 = ps2
        self.contours = cs
        self.hierarchy = hier
        self.threshold_value = tv
        self.dilate_value = dv
        self.erode_value = ev
        self.bounding_rect = br

    @property
    def dev_centroid(self):
        return ((self.origin[0] - self.centroid_value[0]),
                (self.origin[1] - self.centroid_value[1]))

    @property
    def dev_br(self):
        return ((self.origin[0] - self.bounding_rect[0]),
                (self.origin[1] - self.bounding_rect[1]))

    @property
    def aspect_ratio(self):
        return self.bounding_rect.width / float(self.bounding_rect.height)

    @property
    def area(self):
        return self.bounding_rect.width * self.bounding_rect.height


class HoleDetector(Detector):
#    parent=Any(transient=True)

    radius_mm = Float(1.5)
    _debug = False
#    video = Any
#    image = Instance(Image, transient=True)

    cropwidth = Float(5)
    cropheight = Float(5)
    crop_expansion_scalar = Float(0.5)

    crosshairs_offsetx = 0
    crosshairs_offsety = 0

    style = 'co2'

    use_dilation = Bool(True)
    use_erosion = Bool(True)
    save_positioning_error = Bool(False)
    use_histogram = Bool(True)
    use_smoothing = Bool(True)

    start_threshold_search_value = Int(80)
    threshold_search_width = Int(20)
    crop_tries = Range(0, 102, 1)  # > 101 makes it a spinner
    threshold_tries = Range(0, 102, 2)
    threshold_expansion_scalar = Int(5)

    def search(self, cx, cy, holenum=None, close_image=True, **kw):
#        self.cropwidth = 4
#        self.cropheight = 4
        self._nominal_position = (cx, cy)
        self.current_hole = holenum
        self.info('locating {} sample hole {}'.format(self.style,
                                                holenum if holenum else ''))

        start = self.start_threshold_search_value

        end = start + self.threshold_search_width
        expand_value = self.threshold_expansion_scalar
        found = False

#        self.pxpermm = self.pxpermm
#        self.hole_detector._debug = self._debug
#        self.hole_detector.image = self.image

        for ci in range(self.crop_tries):
            if close_image:
                self.parent.close_image()

            self.parent.show_image()

            src = self.parent.load_source().clone()
#            src = self.image.source_frame

            cw = (1 + ci * self.crop_expansion_scalar) * self.cropwidth
            ch = (1 + ci * self.crop_expansion_scalar) * self.cropheight

            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            for i in range(self.threshold_tries):
                s = start - i * expand_value
                e = end + i * expand_value
                self.info('searching... thresholding image {} - {}'.format(s,
                                                                           e))

                args = self._search_for_well(src, s, e, cw, ch)
                '''
                    args = results, dev1x, dev1y, dev2x, dev2y
                    dev1== bound rect dev
                    dev2== centroid dev
                    centroid dev empirically calculates a
                    more accurate deviation
                '''
                if args and args[3] != []:
                    self.info('POSITIONING ERROR DETECTED')
                    found = True
                    '''
                    if i > 0:
                        this is the first threshold value to successfully
                        locate the target
                        so we should use this as our future starting threshold
                        value
                        self.start_threshold_search_value = args[4][0]-10
                    '''
                    break
            if found:
                break

        if not found:
            self.warning('no target found during search. threshold {} - {}'.
                         format(s, e))
            self.draw_center_indicator(self.image.frames[0])
        else:

            def hist(d):
                f, v = histogram(array(d))
                i = len(f)  if argmax(f) == len(f) - 1 else argmax(f)
                return v[i]

            if self.use_histogram:
                dx = hist(args[3])
                dy = hist(args[4])
            else:
                avg = lambda s: sum(s) / len(s)
                dx = avg(args[3])
                dy = avg(args[4])

            ts = args[5]
            ds = args[6]
            es = args[7]
#            print ts, ds, es
            self.parent._threshold = ts
            gsrc = grayspace(self.image.frames[0])

            if self.use_smoothing:
                gsrc = smooth(gsrc)

            src = threshold(gsrc, ts)
            if ds:
                src = dilate(src, ds)
            if es:
                src = erode(src, es)

            self.image.frames[1] = colorspace(src)

            self._draw_markup(args[0], dev=(dx, dy))

            #calculate the data position to move to nx,ny
            dxmm = (dx) / float(self.pxpermm)
                
            dymm = (dy + 1) / float(self.pxpermm)
            nx = cx - dxmm
            ny = cy + dymm

            self.parent._nominal_position = cx, cy
            self.parent._corrected_position = nx, ny

            args = cx, cy, nx, ny, dxmm, dymm, round(dx), round(dy)#int(dx), int(dy)

            self.info('current pos: {:0.3f},{:0.3f} calculated pos: {:0.3f}, {:0.3f} dev: {:0.3f},{:0.3f} ({:n},{:n})'.format(*args))

            if self.save_positioning_error:
                if holenum:
                    path, _ = unique_path(positioning_error_dir,
                                          'positioning_error{:03n}_'.format(int(holenum)), filetype='jpg')
                    self.image.save(path)
                    #save an associated text file with some metadata
                    head, _ = os.path.splitext(path)
                    with open(head + '.txt', 'w') as f:
                        f.write('hole={}\n'.format(holenum))
                        f.write('nominal pos=   {:5f}, {:5f}\n'.format(cx, cy))
                        f.write('corrected pos= {:5f}, {:5f}\n'.format(nx, ny))
                        f.write('deviation=     {:5f}, {:5f}'.format(dxmm, dymm))

            return nx, ny

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
                results = self._calculate_positioning_error(src, cw, ch,
                                                            threshold_val=i)
            except Exception, e:
                import traceback

                tb = traceback.format_exc()
                print tb
                print e

            if results:
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

#        avg = lambda s: sum(s) / max(1, len(s))
        avg = lambda s: s[-1] if s else 0
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

        ind = max(0, len(results) / 2)
#        ind = 0
        ts = results[ind].threshold_value
        es = results[ind].erode_value
        ds = results[ind].dilate_value
#        print ts, es, ds
        return [], [], devx, devy, ts, ds, es

    def _calculate_positioning_error(self, src, cw, ch, threshold_val=None):

        cw_px = int(cw * self.pxpermm)
        ch_px = int(ch * self.pxpermm)

        #for debugging calculated deviation should equal devx,devy
        xo = 0; yo = 0

        if self._debug:
            xo = CX + DEVX
            yo = CY + DEVY

        w, h = get_size(src)
        x = int((w - cw_px) / 2 + xo)
        y = int((h - ch_px) / 2 + yo)

#        smooth(src) 
        self.croppixels = (cw_px, ch_px)
        src = crop(src, x, y, cw_px, ch_px)

        gsrc = grayspace(src)

        self.image.frames[0] = colorspace(gsrc)

#        denoise(gsrc)
        if self.use_smoothing:
            gsrc = smooth(gsrc)

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
        radius = 1.5 * self.pxpermm

#        w, h = get_size(self.image.source_frame)
        ma = 3.1415926535 * radius ** 2 * (4 * self.croppixels[0] / 640.)
#        mi = 0.25 * ma
        mi = ma*0.25

        for td in steps:
            params = self._calc_sample_hole_position(gsrc, td, min_area=mi, max_area=ma, *args)

            if params:
#                print params
#                for p in params:
#                    self._draw_result(self.image.frames[1], p)
#                    time.sleep(0.1)
                return params
#            time.sleep(0.1)

    def _calc_sample_hole_position(self, gsrc, ti, dilate_val, erode_val, min_area=1000, max_area=None):
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
        contours, hierarchy = contour(thresh_src)

        #f=self.image.frames[1]
        #draw_contour_list(f, contours)
#        time.sleep(0.1)
        if contours:
            polygons, bounding_rect, _areas = get_polygons(contours, hierarchy, min_area, max_area)
            if polygons:
                for pi, br in zip(polygons, bounding_rect):
                    if len(pi) > 4:
                        # 1. calculate the centroid
                        cx, cy = centroid(pi)
                        use_radius_filter = False
                        if use_radius_filter:
                            # 2. calculate distances
                            tol = 1.3 * self.pxpermm * self.radius_mm
                            disp = lambda p:((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5
                            disps = map(disp, pi)

                            #filter by tol
                            fpi = filter(lambda p:p[1] < tol, zip(pi, disps))
                            if fpi:
                                pii, disps = zip(*fpi)
                            else:
                                pii = pi
                            # 3. recalc centroid
                            cx2, cy2 = centroid(pii)
                        else:
                            pii = pi
                            cx2, cy2 = cx, cy

                        tr = TargetResult(self._get_true_xy(gsrc),
                                          (cx, cy), (cx2, cy2), pi, pii, contours, hierarchy,
                                           ti, dilate_val, erode_val, br)
                        if self._debug:
#                            self.debug('threshold={}, dilate={}, erode={}'.format(ti, dilate_val, erode_val))
                            self._draw_result(self.image.frames[1], tr)
#                            time.sleep(0.2)

                        if self.style == 'co2' and not self._debug:
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

    def _near_center(self, x, y, tol=1):
        cx = self.croppixels[0] / 2.0
        cy = self.croppixels[1] / 2.0

        tol *= self.pxpermm

        return abs(x - cx) < tol and abs(y - cy) < tol

    def _get_true_xy(self, src):
#        cw_px = self.cropwidth * self.pxpermm
#        ch_px = self.cropheight * self.pxpermm
#
#        true_cx = cw_px / 2.0 + self.crosshairs_offsetx
#        true_cy = ch_px / 2.0 + self.crosshairs_offsety
        w, h = get_size(src)
        x = float(w / 2)
        y = float(h / 2)

        return x, y

    def _draw_markup(self, results, dev=None):
        #add to indicators to ensure the indicator is drawn on top
        indicators = []
        for pi in results:

            f1 = self.image.frames[1]
            f0 = self.image.frames[0]
            draw_polygons(f0, [pi.poly_points], color=(255, 255, 0), thickness=1)
            draw_contour_list(f1, pi.contours, hierarchy=pi.hierarchy)


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
            #indicators.append((f0, calc_center, (0, 255, 255), 'crosshairs', 4))
#            indicators.append((f1, calc_center, (0, 255, 255), 'crosshairs', 1))

            pi.center = calc_center

        #draw the center of the image
        true_cx, true_cy = self._get_true_xy(f0)

        l = 1.5 * self.pxpermm / 2.0
        #self._draw_indicator(f0, new_point(true_cx, true_cy), (0, 0, 255), 'crosshairs', l)
        #self._draw_indicator(f1, new_point(true_cx, true_cy), (0, 0, 255), 'crosshairs', l)
        self.draw_center_indicator(f0)
        self.draw_center_indicator(f1)

        for i in indicators:
            self._draw_indicator(*i)

#        #draw the calculated center
        if dev:
            self._draw_indicator(f0, new_point(true_cx - dev[0],
                                               true_cy - dev[1]), (255, 255, 0), 'crosshairs')

    def draw_center_indicator(self, src, color=(0, 0, 255), size=10):

#        w, h = get_size(src)
#        x = float(w / 2)
#        y = float(h / 2)
#        self._draw_indicator(src, new_point(x, y), shape='crosshairs', color=color, size=size)
        self._draw_indicator(src, new_point(*self._get_true_xy(src)),
                             shape='crosshairs',
                             color=(0, 0, 255),
                             size=10)

    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=4, thickness= -1):
        r = size
        if shape == 'rect':
            draw_rectangle(src, center.x - r / 2., center.y - r / 2., r, r,
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
            draw_circle(src, center, r, color=color, thickness=thickness)


#============= EOF =====================================
