#=============enthought library imports=======================
from traits.api import Any, Instance, Range, Button, Int, Property, Bool, Tuple
from traitsui.api import View, Item, Handler, HGroup, spring
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


from src.managers.manager import Manager
from src.image.image import Image
from src.image.image_editor import ImageEditor

from src.helpers.paths import  positioning_error_dir
from src.helpers.filetools import unique_path
from threading import Thread
import os
#import time
#from src.graph.graph import Graph
#from src.data_processing.time_series.time_series import smooth

class TargetResult(object):
    def __init__(self, cv, ps, cs, tv, dv, ev, br, *args, **kw):
        self.centroid_value = cv
        self.poly_points = ps
        self.contours = cs
        self.threshold_value = tv
        self.dilate_value = dv
        self.erode_value = ev
        self.bounding_rect = br

class ImageHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui

class MachineVisionManager(Manager):

    video = Any
    image = Instance(Image, ())
    pxpermm = 23

#    cropwidth = 6
#    cropheight = 6

    cropwidth = 4
    cropheight = 4

    croppixels = None

    crosshairs_offsetx = 0
    crosshairs_offsety = 0

    threshold = Property(Range(0, 255, 65), depends_on='_threshold')
    _threshold = Int
    test = Button

    image_width = Int(640)
    image_height = Int(324)
#    image_height = Int(324 * 2)

    start_threshold_search_value = 100
    threshold_search_width = 20
#    threshold_search_width = 10

    debug = False
#    debug = True

    style = 'co2'
    save_positioning_error = Bool(True)

    title = Property
    current_hole = None

    corrected_position = Property
    _corrected_position = Tuple(0,0)

    nominal_position = Property
    _nominal_position = Tuple(0,0)

    def _get_corrected_position(self):
        
        return '{:5f}, {:5f}'.format(*self._corrected_position)

    def _get_nominal_position(self):
        return '{:5f}, {:5f}'.format(*self._nominal_position)

    def _get_title(self):
        return 'Positioning Error Hole {}'.format(self.current_hole) \
                    if self.current_hole else 'Positioing Error'

    def load_source(self):
        if self.debug:
            src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
            src = '/Users/ross/Desktop/tray_screen_shot3.tiff'

        else:
            src = self.video.get_frame()#_frame#get_frame(flip=True, clone=True, swap_rb=False)

        self.image.load(src)
        return self.image.source_frame

    def search(self, cx, cy, holenum=None, **kw):
        self._nominal_position = (cx, cy)

        self.current_hole = holenum
        self.info('locating {} sample hole {}'.format(self.style, holenum))
        self.load_source()

        start = self.start_threshold_search_value

        end = start + self.threshold_search_width
        expand_value = 5
        found = False

        self.close_image()
        do_after(500, self.edit_traits, view='image_view')

        ntries = 3
        for i in range(ntries):
            s = start - i * expand_value
            e = end + i * expand_value
            self.info('searching... thresholding image {} - {}'.format(s, e))

            args = self._search_for_well(s, e)

            '''
                args = dev1x, dev1y, dev2x, dev2y
                dev1== bound rect dev
                dev2== centroid dev
                centroid dev empirically calculates a more accurate deviation
            '''
            if args and args[2] != []:
                self.info('POSITIONING ERROR DETECTED')
                found = True
                #if i > 0:
                #    #this is the first threshold value to successfully locate the target
                #    #so we should use this as our future starting threshold value
                #    self.start_threshold_search_value = args[4][0]-10
                break

        if not found:
            self.warning('no target found during search. threshold {} - {}'.format(s, e))
        else:
            def dev(d):
                f, v = histogram(array(d))
                i = len(f)  if argmax(f) == len(f) - 1 else argmax(f)
                return v[i]

            dx = dev(args[2])
            dy = dev(args[3])

            #calculate the data position to move to nx,ny
            dxmm = dx / self.pxpermm
            dymm = dy / self.pxpermm
            nx = cx - dxmm
            ny = cy + dymm

            self._corrected_position = (nx, ny)
            #tx, ty = self._get_true_xy()

            #self._draw_indicator(self.image.frames[0], new_point(tx - dx, ty - dy), (255, 0, 0), rect=True, size=4)
            args = cx, cy, nx, ny, dxmm, dymm, int(dx), int(dy)

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

    def _search_for_well(self, start, end):
        dev1x = []
        dev1y = []
        dev2x = []
        dev2y = []
        thresholds = []

        #make end inclusive
        for i in range(start, end + 1):
            self._threshold = i
            try:
                results = self._calculate_positioning_error(i)
            except Exception, e:
                print e
            if results:
                '''                 
                 instead of trying to figure out if the result is the left of right well
                 if only one result is found require that both wells are identified ie len(results)==2
                 then determine which is the left and right
                 
                '''
                thresholds.append(i)
                if self.style == 'co2':
                    _, _, dx, dy = self._co2_well(results)
                else:
                    _, _, dx, dy = self._diode_well(results)

#                print 'threshold', i, dx, dy
                dev2x += dx
                dev2y += dy
#                time.sleep(0.1)

        return dev1x, dev1y, dev2x, dev2y, thresholds

    def _diode_well(self, results, right_search=True):
        dev1x = []
        dev1y = []
        dev2x = []
        dev2y = []

        if len(results) >= 2:
            r1 = results[0]
            r2 = results[1]
            if right_search:
    #                   search for the rhs well
                func = min
                func2 = argmin
            else:
    #                   search for the lhs well
                func = max
                func2 = argmax

            if r2 is not None:
    #                    xargs = array([r1.dev1[0], r2.dev1[0]])
    #                    yi = func2(xargs)
    #                    dx = func(xargs) 
    #                    dy = r2.dev1[1] if yi else r1.dev1[1] 

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
        devx = []
        devy = []
#        #find the well that is closest to the center
        cx = self.croppixels[0] / 2.0
        cy = self.croppixels[1] / 2.0
#
#        tol = self.pxpermm * 1
        for r in results:
            x, y = r.centroid_value
#            if abs(x - cx) < tol and abs(y - cy) < tol:
            devx.append(cx - x)
            devy.append(cy - y)

        return [], [], devx, devy

    def _test_fired(self):

        t = Thread(target=self.search, args=(0, 0), kwargs=dict(right_search=True))
        t.start()
#        self.passive_focus(None, '2step')

    def close_image(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def traits_view(self):
        v = View('test')
        return v

    def image_view(self):
        v = View(
#                 Item('threshold', show_label=False),
                 HGroup(spring, Item('nominal_position', style='readonly'),
                        Item('corrected_position', style='readonly')),
                 Item('image', show_label=False, editor=ImageEditor(),
                      width=self.image_width, height=self.image_height
                      ),
                 title=self.title,
                 handler=ImageHandler,
                 x=35,
                 y=35
                 )
        return v

    def _calculate_positioning_error(self, threshold_val=None):
        src = self.image.source_frame

        cw_px = int(self.cropwidth * self.pxpermm)
        ch_px = int(self.cropheight * self.pxpermm)

        #for debugging calculated deviation should equal devx,devy
        xo = 0; yo = 0
        DEBUG = False
        if DEBUG:
            devx = -10;cx = 75
            devy = -30;cy = 19
            xo = cx + devx
            yo = cy + devy

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
        if not results:
            results = self._dilate_loop(gsrc, steps, 0)
            if not results:
                results = self._erode_loop(gsrc, steps)

        if results:
            #add to indicators to ensure the indicator is drawn on top
            indicators = []
            for pi in results:
                draw_contour_list(self.image.frames[1], pi.contours, external_color=(255, 255, 0))
                draw_polygons(self.image.frames[0], [pi.poly_points], color=(255, 7, 0), thickness=1)

                #draw the centroid in blue
                centroid_center = new_point(*pi.centroid_value)
                indicators.append((self.image.frames[1], centroid_center , (0, 7, 255), 'rect', 2))

                #calculate bounding rect and bounding square for polygon
                r = pi.bounding_rect
                draw_rectangle(self.image.frames[1], r.x, r.y, r.width, r.height)

                br_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
                indicators.append((self.image.frames[1],
                                   br_center,
                                   (255, 0, 0), 'rect', 2))

                #if % diff in w and h greater than 20% than use the centroid as the calculated center
                #otherwise use the bounding rect center            
                dwh = abs(r.width - r.height) / float(max(r.width, r.height))
                if dwh > 0.2:
                    calc_center = centroid_center
                else:
                    calc_center = br_center

                #indicate which center is chosen                
                indicators.append((self.image.frames[0], calc_center, (255, 255, 0), 'rect', 2))
                indicators.append((self.image.frames[1], calc_center, (255, 255, 0), 'crosshairs', 1))

                dx1, dy1 = self._calculate_deviation(calc_center)
                dx2, dy2 = self._calculate_deviation(new_point(*pi.centroid_value))
                pi.dev1 = (dx1, dy1)
                pi.dev2 = (dx2, dy2)

            #draw the center of the image
            true_cx, true_cy = self._get_true_xy()
            self._draw_indicator(self.image.frames[0], new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')
            self._draw_indicator(self.image.frames[1], new_point(true_cx, true_cy), (255, 255, 0), 'crosshairs')

            for i in indicators:
                self._draw_indicator(*i)

        return results

    def _calc_sample_hole_position(self, gsrc, ti, dilate_val, erode_val):
        min_area = 1000
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
                        tr = TargetResult((cx, cy), pi, contours, ti, dilate_val, erode_val, br)
#                        print self.style, self._near_center(cx, cy)
                        if self.style == 'co2':
                            if self._near_center(cx, cy):
                                found.append(tr)
                        else:
                            found.append(tr)
        return found

    def _calculate_deviation(self, c):
        true_cx, true_cy = self._get_true_xy()
        return cvRound(true_cx - c.x), cvRound(true_cy - c.y)

    def _threshold_loop(self, gsrc, steps, *args):
        for td in steps:
            params = self._calc_sample_hole_position(gsrc, td, *args)
            if params:
                return params

    def _dilate_loop(self, gsrc, steps, ei):
        for di in range(1, 4):
            center = self._threshold_loop(gsrc, steps, di, ei)
            if center:
                return center

    def _erode_loop(self, gsrc, steps):
        for ei in range(1, 4):
            center = self._dilate_loop(gsrc, steps, ei)
            if center:
                return center

    def _near_center(self, x, y, tol=1):
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

    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)

    def _get_threshold(self):
        return self._threshold

    def _set_threshold(self, v):
        self._threshold = v
#        args = self._calculate_positioning_error(v)
#        if args:
#            for a in args:
#                print a.dev1, a.dev2, 'asdfasd'

    def _draw_indicator(self, src, center, color, shape='circle', size=3, thickness= -1):
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
m = MachineVisionManager()
m.debug = True
def timeit_func():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    m.search(0, 0)

def timeit_func2():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    m.search(0, 0, right_search=False)

#def timeit_focus_roberts():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    m._focus_sweep(None, 0, 50, 1, 'roberts')
#    
#def timeit_focus_csobel():
##    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
#    m._focus_sweep(None, 0, 10, 1, 'csobel')

def timeit_focus_sobel():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    #
    m._focus_sweep(None, 0, 10, 1, 'sobel')

def timeit_focus_var():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    m._focus_sweep(None, 0, 10, 1, 'var')

#def timeit_smd():
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
#    s = m.image.source_frame
#    print m._calculate_smd(s, (0, 0, 80, 80))
#    m.calculate_positioning_error()
#    #m.configure_traits()
def time_me():
    from timeit import Timer
    t = Timer('timeit_func()', 'from __main__ import timeit_func')
    n = 5
    ti = t.timeit(n)
    print 'right search time', n, ti, ti / n * 1000

    t = Timer('timeit_func2()', 'from __main__ import timeit_func2')
    n = 5
    ti = t.timeit(n)
    print 'left search time', n, ti, ti / n * 1000

def time_focus():
    from timeit import Timer
#    t = Timer('timeit_focus_roberts()', 'from __main__ import timeit_focus_roberts')
#    n = 5
#    ti = t.timeit(n)
#    print 'focus time roberts', n, ti, ti / n * 1000

    t = Timer('timeit_focus_sobel()', 'from __main__ import timeit_focus_sobel')
    n = 5
    ti = t.timeit(n)
    print 'focus time sobel', n, ti, ti / n * 1000

#    t = Timer('timeit_focus_csobel()', 'from __main__ import timeit_focus_csobel')
#    n = 5
#    ti = t.timeit(n)
#    print 'focus time csobel', n, ti, ti / n * 1000
#    

    t = Timer('timeit_focus_var()', 'from __main__ import timeit_focus_var')
    n = 5
    ti = t.timeit(n)
    print 'focus time var', n, ti, ti / n * 1000

def time_smd():

    from timeit import Timer
    t = Timer('timeit_smd', 'from __main__ import timeit_smd')
    n = 50
    ti = t.timeit(n)
    print 'search time', n, ti, ti / n * 1000
def timeit_comp():
    pass

def time_comp():

    from timeit import Timer
    t = Timer('timeit_comp', 'from __main__ import timeit_comp')
    n = 50
    ti = t.timeit(n)
    print 'comp time', n, ti, ti / n * 1e9

def main():
    from src.helpers.logger_setup import setup
    setup('machine_vision')
    m = MachineVisionManager(debug=True)
#    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff')
    m._test_fired()
    m.configure_traits(view='image_view')

if __name__ == '__main__':
    #setup('machine_vision')
#    timeit_smd()
#    time_smd()
#    time_me()
    main()

#    time_comp()
#============= EOF =====================================
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
