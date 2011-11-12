#=============enthought library imports=======================
from traits.api import Any, Instance, Range, Button, Int, Property, Bool
from traitsui.api import View, Item, Handler
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#from pylab import histogram, argmax, array, argmin
from numpy import histogram, argmax, argmin, array, linspace
from ctypes_opencv.cxcore import cvCircle, CV_AA, cvRound
from threading import Thread
#============= local library imports  ==========================
from src.image.image_helper import draw_polygons, draw_contour_list, colorspace, \
    threshold, grayspace, crop, centroid, new_point, contour, get_polygons, \
    erode, dilate, draw_rectangle, subsample, rotate
from src.managers.manager import Manager
from src.image.image import Image
from src.image.image_editor import ImageEditor
from src.helpers.logger_setup import setup
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
    pxpermm = 64
    cropwidth = 3
    cropheight = 3
    crosshairs_offsetx = 0
    crosshairs_offsety = 0
    
    threshold = Property(Range(0, 255, 65), depends_on='_threshold')
    _threshold = Int
    test = Button

    image_width = Int(640)
    image_height = Int(324)
    
    start_threshold_search_value = 125
    threshold_search_width = 25

    def close_image(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        
        self.ui = None
        
    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)
        
#    def calculate_positioning_error(self, threshold_val=None, open_image=True):
    def _calculate_positioning_error(self, threshold_val=None):
        src = self.image.source_frame
        
        cw_px = int(self.cropwidth * self.pxpermm)
        ch_px = int(self.cropheight * self.pxpermm)
        
        #for debugging calculated deviation should equal devx,devy
        xo = 0; yo = 0
        DEBUG = True
        if DEBUG:
            devx = -10;cx = 75
            devy = -30;cy = 19
            xo = cx + devx
            yo = cy + devy 

        x = int((src.width - cw_px) / 2 + xo)
        y = int((src.height - ch_px) / 2 + yo)
        
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
        
        true_cx, true_cy = self.get_true_xy()
        if results:
            #add to indicators to ensure the indicator is drawn on top
            indicators = []
            for pi in results:
                draw_contour_list(self.image.frames[0], pi.contours, external_color=(255, 255, 0))
                draw_polygons(self.image.frames[1], [pi.poly_points], color=(255, 7, 0), thickness=1)
                
                indicators.append((self.image.frames[1], new_point(*pi.centroid_value), (255, 7, 0)))
    
                #calculate bounding rect and bounding square for polygon
                r = pi.bounding_rect
                draw_rectangle(self.image.frames[1], r.x, r.y, r.width, r.height)

                calc_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
                indicators.append((self.image.frames[1], calc_center , (25, 0, 100)))
    
                #if % diff in w and h greater than 20% than use the centroid as the calculated center
                #otherwise use the bounding rect center            
                dwh = abs(r.width - r.height) / float(max(r.width, r.height))
                if dwh > 0.2:
                    calc_center = new_point(*pi.centroid_value)           

                #indicate which center is chosen                
                indicators.append((self.image.frames[0], calc_center, (0, 255, 0)))
            
                dx1, dy1 = self._calculate_deviation(calc_center)
                dx2, dy2 = self._calculate_deviation(new_point(*pi.centroid_value))
                
                pi.dev1 = (dx1, dy1)
                pi.dev2 = (dx2, dy2)
            #draw the center of the image
            self._draw_indicator(self.image.frames[0], new_point(true_cx, true_cy), (243, 253, 0))
            self._draw_indicator(self.image.frames[1], new_point(true_cx, true_cy), (243, 253, 0))
            
            for i in indicators:
                self._draw_indicator(*i) 
                
#        if open_image:    
#            do_later(self.edit_traits, view='image_view')
            
        return results
    
    def _calculate_deviation(self, c):
        true_cx, true_cy = self.get_true_xy()
        return cvRound(true_cx - c.x), cvRound(true_cy - c.y)
    
    def get_true_xy(self):
        cw_px = self.cropwidth * self.pxpermm
        ch_px = self.cropheight * self.pxpermm
        
        true_cx = cw_px / 2.0 + self.crosshairs_offsetx
        true_cy = ch_px / 2.0 + self.crosshairs_offsety
        
        return true_cx, true_cy
    
    def _dilate_loop(self, gsrc, steps, ei):
        for di in range(1, 4):
            center = self._threshold_loop(gsrc, steps, di, ei)
            if center:    
                return center
    
    def _threshold_loop(self, gsrc, steps, *args):
        for td in steps:
            params = self._calc_sample_hole_position(gsrc, td, *args)
            if params:
                return params
    
    def _erode_loop(self, gsrc, steps):
        for ei in range(1, 4):
            center = self._dilate_loop(gsrc, steps, ei)
            if center:
                return center
                
    def _draw_indicator(self, src, center, color, rect=False, size=3, thickness= -1):
        r = size
        if rect:
            draw_rectangle(src, center.x - r / 2, center.y - r / 2, r, r, thickness=thickness)                
        else:
            cvCircle(src, center, r, color, thickness=thickness, line_type=CV_AA)
          
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
                        found.append(TargetResult(centroid(pi), pi, contours, ti, dilate_val, erode_val, br))
        return found 
    
    def _get_threshold(self):
        return self._threshold
    
    def _set_threshold(self, v):
        self._threshold = v
#        args = self._calculate_positioning_error(v, open_image=False)
        args = self._calculate_positioning_error(v)
        if args:
            for a in args:
                print a.dev1, a.dev2
                
    def load_source(self, debug=False):
        if debug:
            src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
        else:
            src = self.video.get_frame(flip=True, clone=True)
            
        self.image.load(src, swap_rb=True)
        
        return self.image.source_frame
            
    def search(self, cx, cy, debug=False, **kw):
        self.load_source(debug=debug)
        
        start = self.start_threshold_search_value
        end = start + self.threshold_search_width
        expand_value = 5
        found = False
        
        
        self.close_image()
        #if open_image:    
        do_later(self.edit_traits, view='image_view')
        
        
        d = rotate(self.image.source_frame, 45)
        self.image.source_frame = d
        for i in range(3):
            s = start - i * expand_value
            e = end + i * expand_value
            self.info('searching... thresholding {} - {}'.format(s, e))
#            args = self._search(s, e, open_image=i == 0, **kw)
            args = self._search(s, e, **kw)
            '''
                args = dev1x, dev1y, dev2x, dev2y
                dev1== bound rect dev
                dev2== centroid dev
                centroid dev empirically calculates a more accurate deviation
            '''
            if args[2] != []:
                found = True
                if i > 0:
                    #this is the first threshold value to successfully locate the target
                    #so we should use this as our future starting threshold value
                    self.start_threshold_search_value = args[4][0]
                
                break
            
        if not found:
            self.warning('no target found during search. threshold {} - {}'.format(s, e))
            
        else:
            f, v = histogram(array(args[2]))
            n = len(f)
            i = n  if argmax(f) == len(f) - 1 else argmax(f)
            dx = v[i]
#    
            f, v = histogram(array(args[3]))
            i = n  if argmax(f) == len(f) - 1 else argmax(f)
            dy = v[i]
    
            #calculate the data position to move to nx,ny
            dxmm = dx / self.pxpermm
            dymm = dy / self.pxpermm
            nx = cx - dxmm 
            ny = cy + dymm
            
            tx, ty = self.get_true_xy()
            self._draw_indicator(self.image.frames[0], new_point(tx - dx, ty - dy), (255, 0, 0), rect=True, size=4)
            args = cx, cy, nx, ny, dxmm, dymm, int(dx), int(dy)
            self.info('current pos: {:0.3f},{:0.3f} calculated pos: {:0.3f}, {:0.3f} dev: {:0.3f},{:0.3f} ({:n},{:n})'.format(*args))
            return nx, ny
    
#    def _search(self, start, end, open_image=True, right_search=True):
    def _search(self, start, end, right_search=True):
        
        dev1x = []
        dev1y = []
        dev2x = []
        dev2y = []
        thresholds = []
        #make end inclusive
        for i in range(start, end + 1):
            self._threshold = i
#            results = self.calculate_positioning_error(i, open_image=i == start and open_image)
            results = self._calculate_positioning_error(i)
            if results:
                '''                 
                 instead of trying to figure out if the result is the left of right well
                 if only one result is found require that both wells be identified ie len(results)==2
                 then determine which is the left and right
                 
                '''
                if len(results) < 2:
                    continue
                
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
                thresholds.append(i)
                #dev1x.append(dx)
                dev2x.append(dx2)
                #dev1y.append(dy)
                dev2y.append(dy2)
            
#        self.hist_dev1x = array(dev1x)
#        self.hist_dev2x = array(dev2x)
#        
#        self.hist_dev1y = array(dev1y)
#        self.hist_dev2y = array(dev2y)
        
        return dev1x, dev1y, dev2x, dev2y, thresholds
        
    def _test_fired(self):
        t = Thread(target=self.search, args=(0, 0), kwargs=dict(right_search=True, debug=True))
        t.start()
      
    def traits_view(self):
        v = View('test')
        return v
        
    def image_view(self):
        v = View(
                 Item('threshold', show_label=False),
                 Item('image', show_label=False, editor=ImageEditor(),
                      width=self.image_width, height=self.image_height
                      ),
                 title='Positioning Error',
                 handler=ImageHandler
                 )
        return v
    
    def passive_focus(self, manager):
        
        self.info('passive focus. objective func: SMD')
        
        self._passive_focus_thread = Thread(target=self._passive_focus, args=(manager,))
        self._passive_focus_thread.start()
        
    def _passive_focus_2step(self, manager):
        '''
            see
            IMPLEMENTATION OF A PASSIVE AUTOMATIC FOCUSING ALGORITHM
            FOR DIGITAL STILL CAMERA
            DOI 10.1109/30.468047  
            
            and
            
            http://cybertron.cg.tu-berlin.de/pdci10/frankencam/#autofocus
            
        '''
        nominal_focus = self._passive_focus(manager, grad_operator='var', set_z=False)
        
        window = 2
        self._passive_focus(manager, grad_operator='sobel',
                             fstart=nominal_focus - window,
                             fend=nominal_focus + window,
                             step_scalar=5
                             )
        
    def _passive_focus(self, manager, grad_operator='roberts', fstart=25, fend=30, step_scalar=1, set_z=True):
        '''
            see
            IMPLEMENTATION OF A PASSIVE AUTOMATIC FOCUSING ALGORITHM
            FOR DIGITAL STILL CAMERA
            DOI 10.1109/30.468047  
            
            and
            
            http://cybertron.cg.tu-berlin.de/pdci10/frankencam/#autofocus
            
        '''
        controller = manager.stage_manager.stage_controller

        steps = step_scalar * (fend - fstart) + 1
        
        prev_zoom = manager.zoom
        zoom = 50
        self.info('setting zoom: {}'.format(zoom))
        manager.set_zoom(zoom, block=True)
        mi, ma, fmi, fma = self._focus_sweep(controller, fstart, fend, steps, grad_operator)         
        
        #print mii, focussteps[mii] , max(smds)
        
        self.info('passive focus results:Operator={} ImageGradmin={} (z={}), ImageGradmax={}, (z={})'.format(grad_operator, mi, fmi, ma, fma))
        self.info('passive focus. focus z= {}'.format(fma))    
        
        if set_z: 
            controller._set_z(fma)
        
            self.info('returning to previous zoom: {}'.format(prev_zoom))
            manager.set_zoom(prev_zoom, block=True)
            
        return fma
    
    def _focus_sweep(self, controller, start, end, steps, operator):
        grads = []

        focussteps = linspace(start, end, steps)
        for fi in focussteps:
            #move to focal distance
            controller._set_z(fi)
            controller._block_()

            self.load_source(debug=True)
            grads.append(self._calculate_focus_measure(operator, (0, 0, int(40), int(40))))
        mi = min(grads)
        ma = max(grads)
        fmi = focussteps[argmin(grads)]
        fma = focussteps[argmax(grads)]
        
        return mi, fmi, ma, fma
    
    def _calculate_focus_measure(self, operator, roi, src=None):
        def _fm_(v, oper=None, x=True):
            ni, nj = v.shape
            if x:
                if oper == 'sobel':
                    genx = xrange(1, ni - 1)
                    geny = xrange(1, nj - 1)
                    func = lambda g, i, j: (g[i + 1, j - 1] + g[i + 1, j + 1] - 
                                         g[i - 1, j - 1] - g[i - 1, j + 1] + 
                                         2 * g[i + 1, j] - 2 * g[i - 1, j])
                    
                else:
                    genx = xrange(ni - 1)
                    geny = xrange(nj)
                    func = lambda g, i, j:(g[i, j] / 255. - g[i + 1, j] / 255.) ** 2
            else:
                if oper == 'sobel':
                    genx = xrange(1, ni - 1)
                    geny = xrange(1, nj - 1)
                    func = lambda g, i, j: (g[i - 1, j + 1] + g[i + 1, j + 1] - 
                                            g[i - 1, j - 1] - g[i + 1, j - 1] + 
                                            2 * g[i, j + 1] - 2 * g[i, j - 1])
                else:
                    genx = xrange(ni)
                    geny = xrange(nj - 1)
                    func = lambda g, i, j:(g[i, j] / 255. - g[i, j + 1] / 255.) ** 2


            return sum([func(v, i, j) for i in genx for j in geny])      
        
        if src is None:
            src = self.image.source_frame
        
        gsrc = grayspace(src)
        v = subsample(gsrc, *roi).as_numpy_array()
        
        if operator == 'var':
            
            ni, nj = v.shape
            genx = xrange(ni)
            geny = xrange(nj)
            
            mu = 1 / (ni * nj) * sum([v[i, j] for i in genx for j in geny])
            func = lambda g, i, j:abs(g[i, j] - mu) ** 2
            fm = 1 / (ni * nj) * sum([func(v, i, j) for i in genx for j in geny])
            
        else:
            fmx = _fm_(v, oper=operator)
            fmy = _fm_(v, x=False, oper=operator)
            fm = fmx + fmy
            
        return fm
        

m = MachineVisionManager()
def timeit_func():
    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    m.search(0, 0)
    
def timeit_func2():
    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    m.search(0, 0, right_search=False)

def timeit_smd():
    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
    s = m.image.source_frame
    print m._calculate_smd(s, (0, 0, 80, 80))
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
    
def time_smd():
    
    from timeit import Timer
    t = Timer('timeit_smd', 'from __main__ import timeit_smd')
    n = 50
    ti = t.timeit(n)
    print 'search time', n, ti, ti / n * 1000
    
    
    
def main():
    m = MachineVisionManager()
#    m.image.load('/Users/Ross/Desktop/testtray.tiff', swap_rb=True)
    m.image.load('/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff', swap_rb=True)
   # m.passive_focus()
    
#    m.calculate_positioning_error()
    
#    print d.as_numpy_array()
    
#    print s.as_numpy_array().shape
        
    m.configure_traits()
    
if __name__ == '__main__':
#    setup('machine_vision')
#    timeit_smd()
#    time_smd()
#    time_me()
    main()
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
