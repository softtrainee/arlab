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
from traitsui.api import View, Item, Handler, HGroup, Group
from pyface.timer.do_later import do_later, do_after
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.image.image import Image
from src.image.image_editor import ImageEditor

from src.helpers.paths import setup_dir, hidden_dir

from detectors.tray_mapper import TrayMapper
from src.machine_vision.detectors.hole_detector import HoleDetector
from src.machine_vision.detectors.zoom_calibration_detector import ZoomCalibrationDetector


class ImageHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui


class MachineVisionManager(Manager):

    video = Any
    stage_controller = Any
    laser_manager = Any
    autofocus_manager = Any
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

    hole_detector = Instance(HoleDetector)

    style = DelegatesTo('hole_detector')
    use_dilation = DelegatesTo('hole_detector')
    use_erosion = DelegatesTo('hole_detector')
    save_positioning_error = DelegatesTo('hole_detector')
    use_histogram = DelegatesTo('hole_detector')
    use_smoothing = DelegatesTo('hole_detector')

    start_threshold_search_value = DelegatesTo('hole_detector')
    threshold_search_width = DelegatesTo('hole_detector')
    crop_tries = DelegatesTo('hole_detector')
    crop_expansion_scalar = DelegatesTo('hole_detector')
    threshold_tries = DelegatesTo('hole_detector')
    threshold_expansion_scalar = DelegatesTo('hole_detector')

    calibration_detector = Any

    testing = False

    def _test_fired(self):
        from threading import Thread
        if not self.testing:
            self.testing = True
            d = ZoomCalibrationDetector(parent=self,
                                        image=self.image,
                                        pxpermm=self.pxpermm)
            t = Thread(target=d.do_zoom_calibration)
            t.start()
        else:
            self.testing = False

    def search(self, *args, **kw):
        if self.hole_detector is not None:
            return self.hole_detector.search(*args, **kw)

    def dump_hole_detector(self):

        p = os.path.join(hidden_dir, 'hole_detector')
        with open(p, 'wb') as f:
            pickle.dump(self.hole_detector, f)

    def load_hole_detector(self):
        hd = HoleDetector()
        
        p = os.path.join(hidden_dir, 'hole_detector')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    hd = pickle.load(f)
                except Exception:
                    pass
        
        hd.parent = self
        hd.image = self.image
        hd.pxpermm = self.pxpermm
        hd.name='hole_detector'
        
        return hd

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

    def configure_view(self):
        search_grp = Group(Item('start_threshold_search_value'),
                            Item('threshold_search_width'),
                            Item('threshold_expansion_scalar'),
                            Item('threshold_tries'),
                            Item('crop_tries'),
                            Item('crop_expansion_scalar'),
                            show_border=True,
                           label='Search')

        process_grp = Group(
                            Item('use_smoothing'),
                            Item('use_dilation'),
                            Item('use_erosion'),
                            Item('use_histogram'),
                            show_border=True,
                           label='Process')
        v = View(
                 search_grp,
                 process_grp,
                 Item('save_positioning_error'),
                 buttons=['OK', 'Cancel'],
                 title='Configure Hole Detector'
                )

        return v

    def image_view(self):
        v = View(
                 HGroup(
                        Item('threshold', format_str='%03i',
                             #style='readonly'
                             ),
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

    def load_source(self, path=None):
        if self._debug:
            if path is None:
                src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
                src = '/Users/ross/Desktop/tray_screen_shot3.tiff'
                src = '/Users/ross/Desktop/tray_screen_shot3.596--13.321.tiff'
                src = '/Users/ross/Desktop/snapshot006.jpg'
                src = '/Users/ross/Desktop/snapshot007-10mm.jpg'
    #            src = '/Users/ross/Desktop/snapshot007--4.jpg'
                src = '/Users/ross/Desktop/snapshot008-14.jpg'
                src = '/Users/ross/Desktop/testimage.png'
    #            src = '/Users/ross/Documents/testimage1.tiff'
    #            src = '/Users/ross/Desktop/foo1 copy.tiff'
                src = '/Users/ross/Pychrondata_beta1.2/data/snapshots/snapshot010.jpg'
            else:
                src = path

        else:
            src = self.video.get_frame()
        self.image.load(src)
        return self.image.source_frame

    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)

    def _hole_detector_default(self):
        return self.load_hole_detector()

#==============================================================================
# getter/setters
#==============================================================================
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
                    if self.current_hole else 'Positioning Error'

    def _get_threshold(self):
        return self._threshold

    def _set_threshold(self, v):
        self._threshold = v

#        self.calibration_detector.update_threshold(v)


if __name__ == '__main__':

    from src.helpers.logger_setup import setup
    setup('machine_vision')
    m = MachineVisionManager(_debug=True)
    m.configure_traits()

#    time_comp()
#============= EOF =====================================
