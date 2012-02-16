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
#from src.image.cvwrapper import draw_polygons, draw_contour_list, \
#    threshold, grayspace, new_point, \
#    erode, dilate, draw_rectangle, \
#    draw_lines, colorspace, draw_circle
from src.image.cvwrapper import threshold, grayspace, colorspace, erode, dilate
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

    image_width = Int(int(640))
    image_height = Int(324)

    _debug = False

    title = Property
    current_hole = None

    corrected_position = Property(depends_on='_corrected_position')
    _corrected_position = Tuple

    nominal_position = Property(depends_on='_nominal_position')
    _nominal_position = Tuple

    hole_detector = Instance(HoleDetector, ())

    style = DelegatesTo('hole_detector')

    def _test_fired(self):

        self.hole_detector.parent = self
        self.hole_detector.pxpermm = self.pxpermm
        self.hole_detector._debug = self._debug
        self.hole_detector.image = self.image

        t = Thread(target=self.hole_detector.search, args=(0, 0),
                   kwargs=dict(right_search=True))
        t.start()
#        t = Thread(target=self.map_holes)
#        t.start()

    def map_holes(self):
        self.load_source()
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
                        Item('nominal_position', label='Nom. Pos.',
                             style='readonly'),
                        Item('corrected_position', label='Cor. Pos.',
                             style='readonly')
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

    def load_source(self):
        if self._debug:
            src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
            src = '/Users/ross/Desktop/tray_screen_shot3.tiff'
            src = '/Users/ross/Desktop/tray_screen_shot3.596--13.321.tiff'
#            src = '/Users/ross/Documents/testimage1.tiff'
            src = '/Users/ross/Desktop/snapshot003.jpg'

        else:
            src = self.video.get_frame()

        self.image.load(src)
        return self.image.source_frame

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


if __name__ == '__main__':

    from src.helpers.logger_setup import setup
    setup('machine_vision')
    m = MachineVisionManager(_debug=True)
    m.configure_traits()

#    time_comp()
#============= EOF =====================================
