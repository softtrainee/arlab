#=============enthought library imports=======================
from traits.api import Any, Instance, Range, Button, Int
from traitsui.api import View, Item
from src.image.image_helper import draw_polygons, draw_contour_list, colorspace, \
    threshold, grayspace, crop, centroid, new_point, contour, get_polygons, \
    erode, dilate, draw_rectangle
from ctypes_opencv.cxcore import cvCircle, CV_AA
from src.image.image import Image
from src.image.image_editor import ImageEditor
from pyface.timer.do_later import do_later
from src.managers.manager import Manager
#============= standard library imports ========================
#============= local library imports  ==========================
class MachineVisionManager(Manager):

    video = Any
    image = Instance(Image, ())
    pxpermm = 64
    cropwidth = 2
    cropheight = 2
    threshold = Range(0, 255, 65)
    test = Button

    image_width = Int(640)
    image_height = Int(324)
    
    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)
        
    def calculate_positioning_error(self, threshold_val=None, open_image=True):
        #src = self.video.get_frame()
        #self.image.load(src)
        mi = 50
        ma = 100
        dx = None
        dy = None
        src = self.image.source_frame
        
        cw_px = self.cropwidth * self.pxpermm
        ch_px = self.cropheight * self.pxpermm
        
        xo = 0
        xo = 50
#        xo = 50 + 11
        yo = 50
        yo = 0
#        yo = 57

        x = int((src.width - cw_px) / 2 + xo)
        y = int((src.height - ch_px) / 2 + yo)
        
        #draw crop mask onto source
        #draw_rectangle(self.image.frames[0], x, y, cw_px, ch_px, thickness=2)
        crop(src, x, y, cw_px, ch_px)
        gsrc = grayspace(src)
        self.image.frames[0] = colorspace(gsrc)
    
#        if threshold_val:
#            steps = xrange(threshold_val, threshold_val + 1, 1)
#        else:
#            steps = xrange(mi, ma, 1)
#            
#        params1 = self._threshold_loop(gsrc, steps, 0, 0)
#        if params1 is None:          
#            params1 = self._dilate_loop(gsrc, steps, 0)
#            if params1 is None:
#                params1 = self._erode_loop(gsrc, steps)

        if threshold_val:
            steps = xrange(threshold_val, threshold_val + 1, 1)
        else:
            steps = xrange(ma, mi, -1)
        

        params2 = self._threshold_loop(gsrc, steps, 0, 0)
        if params2 is None:          
            params2 = self._dilate_loop(gsrc, steps, 0)
            if params2 is None:
                params2 = self._erode_loop(gsrc, steps)
        
#        if params1:
##            draw_contour_list(self.image.frames[0], params1[4], external_color=(100, 0, 0),
##                              hole_color=(100, 0, 100))
#            draw_polygons(self.image.frames[1], [params1[1]], color=(11, 66, 170), thickness=1)
#            self._draw_indicator(self.image.frames[1], params1[0], (11, 66, 170))
#            print 'p1', self._calculate_deviation(params1[0]), 'di', params1[2], 'ei', params1[3]
        
        true_cx = cw_px / 2.0
        true_cy = ch_px / 2.0
        self._draw_indicator(self.image.frames[1], new_point(true_cx, true_cy), (243, 253, 0), thickness=1)
        if params2:
            draw_contour_list(self.image.frames[0], params2[4],
                                external_color=(255, 255, 0))
            
            draw_polygons(self.image.frames[1], [params2[1]], color=(255, 7, 0), thickness=1)
            self._draw_indicator(self.image.frames[1], new_point(*params2[0]), (255, 7, 0))

            #calculate bounding rect and bounding square for polygon
            r = params2[5]
            draw_rectangle(self.image.frames[1], r.x, r.y, r.width, r.height)
            calc_center = new_point(r.x + r.width / 2, r.y + r.height / 2)
            self._draw_indicator(self.image.frames[1], calc_center , (25, 0, 100))

            #if % diff in w and h greater than 20% than use the centroid as the calculated center
            #otherwise use the bounding rect center            
            dwh = abs(r.width - r.height) / float(max(r.width, r.height))
            if dwh > 0.2:
                calc_center = new_point(*params2[0])           
            
            #indicate which center is chosen
            self._draw_indicator(self.image.frames[1],
                                 calc_center,
                                 color=(0, 255, 0),
                                 thickness=1
                                 )
            dx, dy = self._calculate_deviation(calc_center)
        if open_image:    
            do_later(self.edit_traits, view='image_view')
        return dx, dy
    
    def _calculate_deviation(self, c):
        cw_px = self.cropwidth * self.pxpermm
        ch_px = self.cropheight * self.pxpermm
        
        true_cx = cw_px / 2.0
        true_cy = ch_px / 2.0
        return true_cx - c.x, true_cy - c.y
        
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
                
    def _draw_indicator(self, src, center, color, thickness= -1):
        r = 4
        #x = cvRound(center.x)
        #y = cvRound(center.y)
        #cpt = new_point(x, y)
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
    
        _n, contours = contour(thresh_src)
        if contours:
            polygons, bounding_rect = get_polygons(contours, min_area, max_area, 0)
            if polygons:
                for pi, br in zip(polygons, bounding_rect):
                    if len(pi) > 4:
                        return centroid(pi), pi, dilate_val, erode_val, contours, br
    
    def _threshold_changed(self):
        self.calculate_positioning_error(self.threshold, open_image=False)
    
    def _test_fired(self):
        self.calculate_positioning_error()
        
    def traits_view(self):
        v = View('test')
        return v
        
    def image_view(self):
        v = View(
                 Item('threshold', show_label=False),
                 Item('image', show_label=False, editor=ImageEditor(),
                      width=self.image_width, height=self.image_height
                      )
                 )
        return v

#m = MachineVisionManager()
#def timeit_test():
#    m.image.load('/Users/Ross/Desktop/testtray.tiff', swap_rb=True)
#    
#    m.calculate_positioning_error()
#    #m.configure_traits()

def main():
    m = MachineVisionManager()
    m.image.load('/Users/Ross/Desktop/testtray.tiff', swap_rb=True)
#    m.calculate_positioning_error()
    m.configure_traits()
    
if __name__ == '__main__':
#    from timeit import Timer
#    t = Timer('timeit_test()', 'from __main__ import timeit_test')
#    n = 20
#    ti = t.timeit(n)
#    print n, ti, ti / n * 1000
#    
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
