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
from traits.api import Any, Instance, Range, Button, Int, Property, Tuple, \
    DelegatesTo
from traitsui.api import View, Item, Handler, HGroup
from pyface.timer.do_later import do_later, do_after
#============= standard library imports ========================
from numpy import histogram, argmax, argmin, array, linspace, asarray, mean
#from scipy.ndimage.filters import sobel, generic_gradient_magnitude
#from scipy.ndimage import sum as ndsum
#from scipy.ndimage.measurements import variance

#from ctypes_opencv.cxcore import cvCircle, CV_AA, cvRound, \
#    cvPutText, cvScalar, cvFont, cvPoint

#============= local library imports  ==========================
#from src.image.image_helper import draw_polygons, draw_contour_list, \
from src.image.cvwrapper import draw_polygons, draw_contour_list, \
    threshold, grayspace, new_point, \
    erode, dilate, draw_rectangle, \
    draw_lines, colorspace, draw_circle

from src.managers.manager import Manager
from src.image.image import Image
from src.image.image_editor import ImageEditor

from src.helpers.paths import  positioning_error_dir, setup_dir
from src.helpers.filetools import unique_path
from threading import Thread
import os
#from src.graph.graph import Graph
#from src.data_processing.time_series.time_series import smooth
#import random

from hole_detector import HoleDetector
from tray_mapper import TrayMapper
#DEVX = random.randint(-10, 10)
#DEVY = random.randint(-10, 10)
#DEVX = 0
#DEVY = -2
#CX = 39
#CY = -41


#class TargetResult(object):
#
#    def __init__(self, origin, cv, ps, cs, tv, dv, ev, br, *args, **kw):
#        self.origin = origin
#        self.centroid_value = cv
#        self.poly_points = ps
#        self.contours = cs
#        self.threshold_value = tv
#        self.dilate_value = dv
#        self.erode_value = ev
#        self.bounding_rect = br
#
#    @property
#    def dev_centroid(self):
#        return (cvRound(self.origin[0] - self.centroid_value[0]),
#                cvRound(self.origin[1] - self.centroid_value[1]))
#
#    @property
#    def dev_br(self):
#        return (cvRound(self.origin[0] - self.bounding_rect[0]),
#                cvRound(self.origin[1] - self.bounding_rect[1]))
#
#
class ImageHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui


class MachineVisionManager(Manager):

    video = Any
    image = Instance(Image, ())
    pxpermm = 23

    croppixels = None

#    crosshairs_offsetx = 0
#    crosshairs_offsety = 0

    threshold = Property(Range(0, 255, 65), depends_on='_threshold')
    _threshold = Int
    test = Button

#    image_width = Int(int(640 * 1.5))
#    image_height = Int(int(324 * 1.5))
    image_width = Int(int(640))
    image_height = Int(324)
#    image_height = Int(int(324))
#    image_height = Int(324 * 2)

    start_threshold_search_value = 80
    threshold_search_width = 3
    crop_tries = 2
    threshold_tries = 3
#    threshold_search_width = 10

    _debug = False
#    _debug = True

#    style = 'co2'

    title = Property
    current_hole = None

    corrected_position = Property(depends_on='_corrected_position')
    _corrected_position = Tuple

    nominal_position = Property(depends_on='_nominal_position')
    _nominal_position = Tuple

    hole_detector = Instance(HoleDetector, ())
    use_dilation = DelegatesTo('hole_detector')
    use_erosion = DelegatesTo('hole_detector')
    save_positioning_error = DelegatesTo('hole_detector')
    use_histogram = DelegatesTo('hole_detector')

    cropwidth = DelegatesTo('hole_detector')
    cropheight = DelegatesTo('hole_detector')
    cropscalar = DelegatesTo('hole_detector')

    style = DelegatesTo('hole_detector')

    def _test_fired(self):

        t = Thread(target=self.search, args=(0, 0),
                   kwargs=dict(right_search=True))
        t.start()
#        t = Thread(target=self.map_holes)
#        t.start()

    def map_holes(self):
        self._load_source()
#        self.image.panel_size = 450

        from src.managers.stage_managers.stage_map import StageMap
        p = os.path.join(setup_dir, 'tray_maps', '221-hole.txt')
        sm = StageMap(file_path=p)

        center_mx = self.parent.stage_controller.x
        center_my = self.parent.stage_controller.y
        ca = self.parent.canvas.calibration_item
        if ca is not None:
            rot = ca.get_rotation()
            cpos = ca.get_center_position()

#        center_mx = 3.596
#        center_my = -13.321
#        cpos = -2.066, -0.695
#        rot = 358.099

        tm = TrayMapper(image=self.image,
                        stage_map=sm,
                        center_mx=center_mx,
                        center_my=center_my,
                        calibrated_center=cpos,
                        calibrated_rotation=rot
                        )

        tm.pxpermm = self.pxpermm
        self.show_image()
        tm.map_holes()

    def search(self, cx, cy, holenum=None, close_image=True, **kw):
#        self.cropwidth = 4
#        self.cropheight = 4
        self._nominal_position = (cx, cy)

        self.current_hole = holenum
        self.info('locating {} sample hole {}'.format(self.style,
                                                holenum if holenum else ''))

        start = self.start_threshold_search_value

        end = start + self.threshold_search_width
        expand_value = 5
        found = False

        self.hole_detector.pxpermm = self.pxpermm
        self.hole_detector._debug = self._debug
        self.hole_detector.image = self.image

        for ci in range(self.crop_tries):
            if close_image:
                self.close_image()

            self.show_image()

            src = self._load_source()

            cw = (1 + ci * self.cropscalar) * self.cropwidth
            ch = (1 + ci * self.cropscalar) * self.cropheight

#            self.cropwidth = cw
#            self.cropheight = ch
            self.info('cropping image to {}mm x {}mm'.format(cw, ch))
            for i in range(self.threshold_tries):
                s = start - i * expand_value
                e = end + i * expand_value
                self.info('searching... thresholding image {} - {}'.format(s,
                                                                           e))

                args = self.hole_detector._search_for_well(src, s, e, cw, ch)
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
            self.hole_detector.draw_center_indicator(self.image.frames[0])
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
            self._threshold = ts
            src = threshold(grayspace(self.image.frames[0]), ts)
            if ds:
                src = dilate(src, ds)
            if es:
                src = erode(src, es)

            self.image.frames[1] = colorspace(src)

            self.hole_detector._draw_markup(args[0], dev=(dx, dy))

            #calculate the data position to move to nx,ny
            dxmm = dx / float(self.pxpermm)
            dymm = dy / float(self.pxpermm)
            nx = cx - dxmm
            ny = cy + dymm
            self._corrected_position = (dxmm, dymm)

            args = cx, cy, nx, ny, dxmm, dymm, round(dx), round(dy)#int(dx), int(dy)

            self.info('current pos: {:0.3f},{:0.3f} calculated pos: {:0.3f}, {:0.3f} dev: {:0.3f},{:0.3f} ({:n},{:n})'.format(*args))

            if self.save_positioning_error:
                if holenum:
                    path, _ = unique_path(positioning_error_dir, 'positioning_error{:03n}_'.format(int(holenum)), filetype='jpg')
                    self.image.save(path)
                    #save an associated text file with some metadata
                    head, _ = os.path.splitext(path)
                    with open(head + '.txt', 'w') as f:
                        f.write('hole={}\n'.format(holenum))
                        f.write('nominal pos=   {:5f}, {:5f}\n'.format(cx, cy))
                        f.write('corrected pos= {:5f}, {:5f}\n'.format(nx, ny))
                        f.write('deviation=     {:5f}, {:5f}'.format(dxmm, dymm))

            return nx, ny

#    def _search_for_well(self, start, end, cw, ch):
#        dev1x = []
#        dev1y = []
#        dev2x = []
#        dev2y = []
#        ts = []
#        ds = []
#        es = []
#
#        rresults = None
#        #make end inclusive
#        for i in range(start, end + 1):
#            self._threshold = i
#            try:
#                results = self._calculate_positioning_error(cw, ch, threshold_val=i)
#            except Exception, e:
#                print e
#
#            if results:
#                '''                 
#                 instead of trying to figure out if the result is the left of right well
#                 if only one result is found require that both wells are identified ie len(results)==2
#                 then determine which is the left and right
#                 
#                '''
#                if self.style == 'co2':
#                    _, _, dx, dy, ti, di, ei = self._co2_well(results)
#                else:
#                    _, _, dx, dy = self._diode_well(results)
#
#                dev2x += dx
#                dev2y += dy
#
#                ts.append(ti)
#                ds.append(di)
#                es.append(ei)
#                rresults = results
#
#        avg = lambda s: sum(s) / max(1, len(s))
#        return rresults, dev1x, dev1y, dev2x, dev2y, avg(ts), avg(ds), avg(es)

#    def _diode_well(self, results, right_search=True):
#        dev1x = []
#        dev1y = []
#        dev2x = []
#        dev2y = []
#
#        if len(results) >= 2:
#            r1 = results[0]
#            r2 = results[1]
#            if right_search:
#    #                   search for the rhs well
#                func = min
#                func2 = argmin
#            else:
#    #                   search for the lhs well
#                func = max
#                func2 = argmax
#
#            if r2 is not None:
#    #                    xargs = array([r1.dev1[0], r2.dev1[0]])
#    #                    yi = func2(xargs)
#    #                    dx = func(xargs) 
#    #                    dy = r2.dev1[1] if yi else r1.dev1[1] 
#
#                xargs = array([r1.dev2[0], r2.dev2[0]])
#                yi = func2(xargs)
#                dx2 = func(r1.dev2[0], r2.dev2[0])
#                dy2 = r2.dev2[1] if yi else r1.dev2[1]
#
#            #dev1x.append(dx)
#            dev2x.append(dx2)
#            #dev1y.append(dy)
#            dev2y.append(dy2)
#
#        return dev1x, dev1y, dev2x, dev2y

#    def _co2_well(self, results):
#        devx, devy = zip(*[r.dev_centroid for r in results])
#        ts = results[0].threshold_value
#        es = results[0].erode_value
#        ds = results[0].dilate_value
#
#        return [], [], devx, devy, ts, ds, es

    def close_image(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def show_image(self):
        do_after(500, self.edit_traits, view='image_view')

    def traits_view(self):
        v = View('test')
        return v

    def image_view(self):
        v = View(
                 HGroup(
                        Item('threshold', format_str='%03i', style='readonly'),
                        #spring,
                        Item('nominal_position', label='Nom. Pos.', style='readonly'),
                        Item('corrected_position', label='Cor. Pos.', style='readonly')
                        ),
                 Item('image', show_label=False, editor=ImageEditor(),
                      width=self.image_width,
                      height=self.image_height
                      ),
                 title=self.title,
                 handler=ImageHandler,
                 x=35,
                 y=35,
                 width=680,
                 height=self.image_height + 50,
                 resizable=True
                 )
        return v

    def _load_source(self):
        if self._debug:
            src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
            src = '/Users/ross/Desktop/tray_screen_shot3.tiff'
            src = '/Users/ross/Desktop/tray_screen_shot3.596--13.321.tiff'
#            src = '/Users/ross/Documents/testimage1.tiff'
            src = '/Users/ross/Desktop/snapshot003.jpg'

        else:
            src = self.video.get_frame()#_frame#get_frame(flip=True, clone=True, swap_rb=False)

        self.image.load(src)
        return self.image.source_frame

#    def _draw_markup(self, results, dev=None):
#        #add to indicators to ensure the indicator is drawn on top
#        indicators = []
#        for pi in results:
#
#            f1 = self.image.frames[1]
#            f0 = self.image.frames[0]
#            draw_polygons(f0, [pi.poly_points2], color=(0, 255, 0), thickness=2)
#            draw_polygons(f0, [pi.poly_points], color=(255, 7, 0), thickness=1)
#
#            draw_contour_list(f1, pi.contours, hierarchy=pi.hierarchy, external_color=(255, 255, 0))
#
#            #draw the centroid in blue
#            centroid_center = new_point(*pi.centroid_value)
#            indicators.append((f1, centroid_center , (0, 255, 0), 'rect', 2))
#
#            centroid_center2 = new_point(*pi.centroid_value2)
#
#            indicators.append((f0, centroid_center2 , (0, 255, 0), 'rect', 2))
#
#            #calculate bounding rect and bounding square for polygon
#            r = pi.bounding_rect
#            draw_rectangle(f1, r.x, r.y, r.width, r.height)
#
#            br_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
#            indicators.append((f1,
#                               br_center,
#                               (255, 0, 0), 'rect', 2))
#
##                #if % diff in w and h greater than 20% than use the centroid as the calculated center
##                #otherwise use the bounding rect center            
##                dwh = abs(r.width - r.height) / float(max(r.width, r.height))
##                if dwh > 0.2:
##                    calc_center = centroid_center
##                else:
##                    calc_center = br_center
#
#            calc_center = centroid_center
#            #indicate which center is chosen                
#            indicators.append((f0, calc_center, (0, 255, 255), 'crosshairs', 1))
#            indicators.append((f1, calc_center, (0, 255, 255), 'crosshairs', 1))
#
#            pi.center = calc_center
#
#        #draw the center of the image
#        true_cx, true_cy = self.hole_detector._get_true_xy()
#        self._draw_indicator(f0, new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')
#        self._draw_indicator(f1, new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')
#
#        for i in indicators:
#            self._draw_indicator(*i)
#
#        #draw the calculated center
#        if dev:
#
#            self._draw_indicator(f0, new_point(true_cx - dev[0],
#                                               true_cy - dev[1]), (255, 0, 255), 'crosshairs')
#
#    def _draw_indicator(self, src, center, color=(255, 0, 0), shape='circle', size=3, thickness= -1):
#        r = size
#        if shape == 'rect':
#            draw_rectangle(src, center.x - r / 2, center.y - r / 2, r, r,
#                           color=color,
#                           thickness=thickness)
#        elif shape == 'crosshairs':
#            draw_lines(src,
#                   [[(center.x - size, center.y),
#                    (center.x + size, center.y)],
#                    [(center.x, center.y - size),
#                     (center.x, center.y + size)]],
#                       color=color,
#                       thickness=1
#                   )
#        else:
##            cvCircle(src, center, r, color, thickness=thickness, line_type=CV_AA)
#            draw_circle(src, center, r, color, thickness=thickness)

    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)

#===============================================================================
# getter/setters
#===============================================================================
    def _get_corrected_position(self):
        try:
            return '{:5f}, {:5f}'.format(*self._corrected_position)
        except IndexError:
            pass

    def _get_nominal_position(self):
        try:
            return '{:5f}, {:5f}'.format(*self._nominal_position)
        except IndexError:
            pass

    def _get_title(self):
        return 'Positioning Error Hole {}'.format(self.current_hole) \
                    if self.current_hole else 'Positioing Error'
    def _get_threshold(self):
        return self._threshold

    def _set_threshold(self, v):
        self._threshold = v


def main():
    from src.helpers.logger_setup import setup
    setup('machine_vision')
    m = MachineVisionManager(_debug=True)
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
#    m._load_source()
    #m._test_fired()
    m.configure_traits()#view='image_view')

if __name__ == '__main__':
    #setup('machine_vision')
#    timeit_smd()
#    time_smd()
#    time_me()
    main()

#    time_comp()
#============= EOF =====================================
#m = MachineVisionManager()
#m._debug = True
#def timeit_func():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    m.search(0, 0)
#
#def timeit_func2():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    m.search(0, 0, right_search=False)
#
##def timeit_focus_roberts():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
##    m._focus_sweep(None, 0, 50, 1, 'roberts')
##    
##def timeit_focus_csobel():
###    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
##    m._focus_sweep(None, 0, 10, 1, 'csobel')
#
#def timeit_focus_sobel():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    #
#    m._focus_sweep(None, 0, 10, 1, 'sobel')
#
#def timeit_focus_var():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    m._focus_sweep(None, 0, 10, 1, 'var')
#
##def timeit_smd():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
##    s = m.image.source_frame
##    print m._calculate_smd(s, (0, 0, 80, 80))
##    m.calculate_positioning_error()
##    #m.configure_traits()
#def time_me():
#    from timeit import Timer
#    t = Timer('timeit_func()', 'from __main__ import timeit_func')
#    n = 5
#    ti = t.timeit(n)
#    print 'right search time', n, ti, ti / n * 1000
#
#    t = Timer('timeit_func2()', 'from __main__ import timeit_func2')
#    n = 5
#    ti = t.timeit(n)
#    print 'left search time', n, ti, ti / n * 1000
#
#def time_focus():
#    from timeit import Timer
##    t = Timer('timeit_focus_roberts()', 'from __main__ import timeit_focus_roberts')
##    n = 5
##    ti = t.timeit(n)
##    print 'focus time roberts', n, ti, ti / n * 1000
#
#    t = Timer('timeit_focus_sobel()', 'from __main__ import timeit_focus_sobel')
#    n = 5
#    ti = t.timeit(n)
#    print 'focus time sobel', n, ti, ti / n * 1000
#
##    t = Timer('timeit_focus_csobel()', 'from __main__ import timeit_focus_csobel')
##    n = 5
##    ti = t.timeit(n)
##    print 'focus time csobel', n, ti, ti / n * 1000
##    
#
#    t = Timer('timeit_focus_var()', 'from __main__ import timeit_focus_var')
#    n = 5
#    ti = t.timeit(n)
#    print 'focus time var', n, ti, ti / n * 1000
#
#def time_smd():
#
#    from timeit import Timer
#    t = Timer('timeit_smd', 'from __main__ import timeit_smd')
#    n = 50
#    ti = t.timeit(n)
#    print 'search time', n, ti, ti / n * 1000
#def timeit_comp():
#    pass
#
#def time_comp():
#
#    from timeit import Timer
#    t = Timer('timeit_comp', 'from __main__ import timeit_comp')
#    n = 50
#    ti = t.timeit(n)
#    print 'comp time', n, ti, ti / n * 1e9

#    def polygonate(self, t, frame_id=0, skip=None, line_width=1, min_area=1000,
#                    max_area=1e10, convextest=0):
#        gsrc = self.threshold(t)
#        
#        #esrc = erode(gsrc, 2)
#        #self.frames.append(colorspace(esrc))
#        
#        _nc, contours = contour(gsrc)
##        print skip
#        if contours:
#            polygons = get_polygons(contours, min_area, max_area, convextest)
#            print 'polygos', len(polygons)
##            polygons = polygons[:3]
#            f = self.frames[frame_id]
#            if skip is not None:
#                polygons = [p for i, p in enumerate(polygons) if i not in skip ]
##            polygons = polygons[:9]
#            
#            newsrc = new_dst(colorspace(gsrc), zero=True)
#            draw_contour_list(f, contours)
##            draw_polygons(f, polygons, line_width)
#            draw_polygons(newsrc, polygons, line_width)
#            self.frames.append(newsrc)
#            return polygons


#ORDER OF MAGNITUDE SLOWER THAN USING SCIPY. CYTHON NOT ANY BETTER
#        def _fm_(v, oper=None, x=True):
#            ni, nj = v.shape
#            if x:
#                if oper == 'sobel':
#                    genx = xrange(1, ni - 1)
#                    geny = xrange(1, nj - 1)
#                    func = lambda g, i, j: (g[i + 1, j - 1] + g[i + 1, j + 1] - 
#                                         g[i - 1, j - 1] - g[i - 1, j + 1] + 
#                                         2 * g[i + 1, j] - 2 * g[i - 1, j])
#                    
#                else:
#                    genx = xrange(ni - 1)
#                    geny = xrange(nj)
#                    func = lambda g, i, j:(g[i, j] - g[i + 1, j] ) ** 2
#            else:
#                if oper == 'sobel':
#                    genx = xrange(1, ni - 1)
#                    geny = xrange(1, nj - 1)
#                    func = lambda g, i, j: (g[i - 1, j + 1] + g[i + 1, j + 1] - 
#                                            g[i - 1, j - 1] - g[i + 1, j - 1] + 
#                                            2 * g[i, j + 1] - 2 * g[i, j - 1])
#                else:
#                    genx = xrange(ni)
#                    geny = xrange(nj - 1)
#                    func = lambda g, i, j:(g[i, j] - g[i, j + 1]) ** 2
#
#
#            return sum([func(v, i, j) for i in genx for j in geny])

#    def _calculate_positioning_error(self, cw, ch, threshold_val=None):
#        src = self.image.source_frame
#
#        cw_px = int(cw * self.pxpermm)
#        ch_px = int(ch * self.pxpermm)
#
#        #for debugging calculated deviation should equal devx,devy
#        xo = 0; yo = 0
#
#        if self._debug:
#            xo = CX + DEVX
#            yo = CY + DEVY
#
#        x = int((src.width - cw_px) / 2 + xo)
#        y = int((src.height - ch_px) / 2 + yo)
#
##        smooth(src)        
#        self.croppixels = (cw_px, ch_px)
#        crop(src, x, y, cw_px, ch_px)
#        gsrc = grayspace(src)
#        self.image.frames[0] = colorspace(gsrc)
#
#        if threshold_val is None:
#            threshold_val = self.start_threshold_search_value
#
#        steps = xrange(threshold_val, threshold_val + 1, 1)
#
#        results = self._threshold_loop(gsrc, steps, 0, 0)
#        if results:
#            if not results and self.use_dilation:
#                results = self._dilate_loop(gsrc, steps, 0)
#
#        if not results and self.use_erosion:
#            results = self._erode_loop(gsrc, steps, dilate=self.use_dilation)
#
#        return results
#
#    def _dilate_loop(self, gsrc, steps, ei):
#        for di in range(1, 4):
#            center = self._threshold_loop(gsrc, steps, di, ei)
#            if center:
#                return center
#
#    def _erode_loop(self, gsrc, steps, dilate=True):
#        for ei in range(1, 4):
#            if dilate:
#                center = self._dilate_loop(gsrc, steps, ei)
#            else:
#                center = self._threshold_loop(gsrc, steps, 0, ei)
#            if center:
#                return center
#
#    def _threshold_loop(self, gsrc, steps, *args):
#        for td in steps:
#            params = self._calc_sample_hole_position(gsrc, td, *args)
#            if params:
#                return params
##            time.sleep(0.5)
#
#    def _calc_sample_hole_position(self, gsrc, ti, dilate_val, erode_val):
#
##        if self._debug:
##            time.sleep(0.1)
#
#        min_area = 1000
#        max_area = gsrc.width * gsrc.height
#        thresh_src = threshold(gsrc, ti)
#
#        if dilate_val:
#            thresh_src = dilate(thresh_src, dilate_val)
#        if erode_val:
#            thresh_src = erode(thresh_src, erode_val)
#
#        if len(self.image.frames) == 2:
#            self.image.frames[1] = colorspace(thresh_src)
#        else:
#            self.image.frames.append(colorspace(thresh_src))
#
#        found = []
#        _n, contours = contour(thresh_src)
#        if contours:
#            polygons, bounding_rect = get_polygons(contours, min_area, max_area, 0)
#            if polygons:
#                for pi, br in zip(polygons, bounding_rect):
#                    if len(pi) > 4:
#                        cx, cy = centroid(pi)
#                        tr = TargetResult(self._get_true_xy(),
#                                          (cx, cy), pi, contours, ti, dilate_val, erode_val, br)
#
#                        if self._debug:
#                            self.debug('threshold={}, dilate={}, erode={}'.format(ti, dilate_val, erode_val))
#                            self._draw_result(self.image.frames[1], tr, pi)
#                            time.sleep(0.5)
#
#                        if self.style == 'co2':
#                            if self._near_center(cx, cy):
#                                found.append(tr)
#                        else:
#                            found.append(tr)
#
#        return found
#
#    def _draw_result(self, src, result, pi):
#        self._draw_indicator(src, new_point(*result.centroid_value), shape='crosshairs')
#        draw_polygons(src, [pi])

#    def _near_center(self, x, y, tol=1.5):
#        cx = self.croppixels[0] / 2.0
#        cy = self.croppixels[1] / 2.0
#
#        tol *= self.pxpermm
#
#        return abs(x - cx) < tol and abs(y - cy) < tol
