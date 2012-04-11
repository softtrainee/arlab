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
from traitsui.api import View, Item, Handler, HGroup, Group, spring
from pyface.timer.do_later import do_later, do_after
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.image.image import Image
from src.image.image_editor import ImageEditor

from src.helpers.paths import setup_dir, hidden_dir

#from detectors.tray_mapper import TrayMapper
from src.machine_vision.detectors.co2_detector import CO2HoleDetector
from src.machine_vision.detectors.tray_mapper import TrayMapper
import copy
import math
#from src.machine_vision.detectors.zoom_calibration_detector import ZoomCalibrationDetector


class ImageHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui


class MachineVisionManager(Manager):

    video = Any
    stage_controller = Any
    laser_manager = Any
    autofocus_manager = Any
    image = Instance(Image, ())
    working_image = Instance(Image, ())
    pxpermm = 23

    croppixels = None

#    crosshairs_offsetx = 0
#    crosshairs_offsety = 0

    threshold = Property(Range(0, 255, 65), depends_on='_threshold')
    _threshold = Int
    test = Button

    image_width = Int(int(640))
    image_height = Int(480)

    _debug = False

    title = Property
    current_hole = None

    corrected_position = Property(depends_on='_corrected_position')
    _corrected_position = Tuple(0, 0)

    nominal_position = Property(depends_on='_nominal_position')
    _nominal_position = Tuple(0, 0)

    hole_detector = Instance(CO2HoleDetector)

#    style = DelegatesTo('hole_detector')
    use_dilation = DelegatesTo('hole_detector')
    use_erosion = DelegatesTo('hole_detector')
    save_positioning_error = DelegatesTo('hole_detector')
    use_histogram = DelegatesTo('hole_detector')
    use_smoothing = DelegatesTo('hole_detector')
    use_contrast_equalization = DelegatesTo('hole_detector')

    segmentation_style = DelegatesTo('hole_detector')

    start_threshold_search_value = DelegatesTo('hole_detector')
    threshold_search_width = DelegatesTo('hole_detector')
    crop_tries = DelegatesTo('hole_detector')
    crop_expansion_scalar = DelegatesTo('hole_detector')
    threshold_tries = DelegatesTo('hole_detector')
    threshold_expansion_scalar = DelegatesTo('hole_detector')

    calibration_detector = Any

    testing = False
    _debug = True

#    def _zoom_calibration(self):
#        d = ZoomCalibrationDetector(parent=self,
#                                    image=self.image,
#                                    pxpermm=self.pxpermm)
#        self._spawn_thread(d.do_zoom_calibration())

    def _spawn_thread(self, func, *args, **kw):

        from threading import Thread
        t = Thread(target=func, args=args, kwargs=kw)
        t.start()

    def _test_fired(self):
        if not self.testing:
            self.testing = True
#            self.show_image()
            self._spawn_thread(self.map_holes)
#            self._zoom_calibration()
#            self._spawn_thread(self.hole_detector.locate_sample_well,
#                               0, 0
#                               )

        else:
            self.testing = False

    def search(self, *args, **kw):
        if self.hole_detector is not None:
            return self.hole_detector.locate_sample_well(*args, **kw)

    def dump_hole_detector(self):

        p = os.path.join(hidden_dir, 'hole_detector')
        with open(p, 'wb') as f:
            pickle.dump(self.hole_detector, f)

    def load_hole_detector(self):
        hd = CO2HoleDetector()

        p = os.path.join(hidden_dir, 'hole_detector')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    hd = pickle.load(f)
                except Exception, e:
                    print e

        hd.parent = self
        hd.image = self.image
        hd.working_image = self.working_image
        hd.pxpermm = self.pxpermm
        hd.name = 'hole_detector'
        hd._debug = self._debug

        return hd

    def cancel_calibration(self):
        self._cancel_calibration = True

    def do_auto_calibration(self, calibration_item):
        self._cancel_calibration = False
        cx, cy, rx, ry = self._calculate_calibration()

        if cx and cy and rx and ry:
            calibration_item.set_center(cx, cy)
            calibration_item.set_right(rx, ry)

        #now move thru all the holes mapping each one
        sm = self.parent._stage_map
        for h in  sm.sample_holes:
            if self._cancel_calibration:
                break
            self.parent._move_to_hole(h.id)

        #interpolate correct positions for holes that could not be 
        #identified
        sm.interpolate_noncorrected()

    def _calculate_calibration(self):
        cx = None
        cy = None
        rx = None
        ry = None
        sm = self.parent._stage_map
#        for ch in ['3', '119', '219', '103', '111']:
        #move to a set of calibration holes
        #n,e,s,w,c
        if sm.calibration_holes is None:
            self.warning('no calibration holes')
            return

        for ch in sm.calibration_holes:
            if self._cancel_calibration:
                self.info('moving to calibration hole {}'.format(ch))
                self.parent._move_to_hole(ch)
                return

        print sm.calibration_holes
        #calculate the center pos
        npos = [[], []]
        for a, b, i in [(0, 2, 1), (1, 3, 0)]:
            a = sm.calibration_holes[a]
            b = sm.calibration_holes[b]
            cpos1 = sm.get_corrected_hole_pos(a)
            cpos2 = sm.get_corrected_hole_pos(b)
            if cpos1 and cpos2:
                d = abs(cpos1[i] - cpos2[i]) / 2.0
                npos[i].append(min(cpos1[i], cpos2[i]) + d)

        ccpos = sm.get_corrected_hole_pos(sm.calibration_holes[4])
        if ccpos:
            npos[0].append(ccpos[0])
            npos[1].append(ccpos[1])

        if npos[0] and npos[1]:
            print 'npos', npos
            cx = sum(npos[0]) / len(npos[0])
            cy = sum(npos[1]) / len(npos[1])

            rots = []
            #calculate the rotations between c and n,s, c and e,w
            for i, offset in [(0, -90), (2, -90), (1, 0), (3, 0)]:
                npos = sm.get_corrected_hole_pos(sm.calibration_holes[i])
                if npos is not None:
                    rot = math.atan2((cx - npos[0]), (cy - npos[1]))\
                            + math.radians(offset)
                    rots.append(rot)

            rightx, righty = sm.get_hole_pos(sm.calibration_holes[1])
            centerx, centery = sm.get_hole_pos(sm.calibration_holes[4])

            L = ((centerx - rightx) ** 2 + (centery - righty) ** 2) ** 0.5

            print 'calculated rotations', rots
            if rots:
                rot = sum(rots) / len(rots)
                rx = cx + L * math.cos(rot)
                ry = cy + L * math.sin(rot)

        return cx, cy, rx, ry

#        #use map holes to move to multiple regions and 
#        #determine corrected position
#        self.map_holes()
#
#        sm = self.parent._stage_map
#        #now stage map has corrected positions
#
#        #use stage map to get corrected center and corrected right
#        cx, cy = sm.get_corrected_center()
#        rx, ry = sm.get_corrected_right()

#        return cx, cy, rx, ry

    def map_holes(self):
        self.load_source()
#        self.image.panel_size = 450
        if self.parent is None:
            from src.managers.stage_managers.stage_map import StageMap
            p = os.path.join(setup_dir, 'tray_maps', '221-hole.txt')
            sm = StageMap(file_path=p)
            center_mx, center_my = 3.596, -13.321
            cpos = -2.066, -0.695
            rot = 358.099

        else:
            sm = self.parent._stage_map
            ca = self.parent.canvas.calibration_item
            if ca is not None:
                rot = ca.get_rotation()
                cpos = ca.get_center_position()

        tm = TrayMapper(image=self.image,
                        working_image=self.working_image,
                        stage_map=sm,
#                        center_mx=center_mx,
#                        center_my=center_my,
                        calibrated_center=cpos,
                        calibrated_rotation=rot,
                        pxpermm=self.pxpermm,
                        _debug=self._debug,
                        parent=self
                        )

        self.hole_detector = tm
        if self.parent is not None:
            center_mx = self.parent.stage_controller.x
            center_my = self.parent.stage_controller.y

        regions = [(0, 0)]
        for r in regions:
            #move to a new region
            if self.parent is not None:
                self.parent.stage_controller.linear_move(*r, block=True)

            tm.center_my = center_my
            tm.center_mx = center_mx
            tm.map_holes()

        sm.interpolate_noncorrected()

        for s in sm.sample_holes:
            if s.interpolated:
                cx, cy = s.x_cor, s.y_cor
    #            if abs(cx) > 1e-6 or abs(cy) > 1e-6:

                cx, cy = sm.map_to_uncalibration((cx, cy), cpos, rot)
                cx, cy = tm.map_screen(cx, cy)

    #                print 'draw ind for {} {},{}'.format(s.id, cx, cy)
    #                cy = 250
                tm._draw_indicator(self.image.frames[0], (cx, cy), color=(255, 0, 0))

#        center_mx = 3.596
#        center_my = -13.321
#        cpos = -2.066, -0.695
#        rot = 358.099
    def close_image(self):
        if self.ui is not None:
            do_later(self.ui.dispose)
        self.ui = None

    def show_image(self, reopen_image=False):
        self.info('show image')
        if reopen_image:
            if self.ui is not None:
                self.close_image()
            do_after(50, self.edit_traits, view='image_view')
        elif self.ui is None:
            do_after(50, self.edit_traits, view='image_view')
#        else:
#            self.ui.control.Raise()



#        if self._debug:
#            do_after(50, self.edit_traits, view='working_image_view')


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
                           label='Search',
                           )

        process_grp = Group(
                            Item('use_smoothing'),
                            Item('use_dilation'),
                            Item('use_erosion'),
                            Item('use_histogram'),
                            Item('use_contrast_equalization'),
                            show_border=True,
                           label='Process')
        v = View(Item('segmentation_style'),

                 search_grp,
                 process_grp,
                 Item('save_positioning_error'),
                 buttons=['OK', 'Cancel'],
                 title='Configure Hole Detector'
                )

        return v

    def working_image_view(self):
        imgrp = Item('working_image', show_label=False, editor=ImageEditor(),
                      width=self.image_width,
                      height=self.image_height
                      )
        v = View(imgrp,
                 handler=ImageHandler,
                 x=0.6,
                 y=35,
                 width=680,
                 height=self.image_height + 100,)
        return v

    def image_view(self):
        v = View(
                 HGroup(
                        Item('segmentation_style', show_label=False),
#                        Item('threshold', format_str='%03i',
                             #style='readonly'
#                             ),
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
                 height=self.image_height + 100,
                 resizable=True
                 )
        return v

    def load_source(self, path=None):
        if self._debug:
            if path is None:
                src = '/Users/Ross/Downloads/Archive/puck_screen_shot3.tiff'
                src = '/Users/ross/Desktop/tray_screen_shot3.tiff'
                src = '/Users/ross/Sandbox/tray_screen_shot3.596--13.321.tiff'
#                src = '/Users/ross/Sandbox/snapshot001.jpg'
#                src = '/Users/ross/Desktop/watershed_test.tif'
#                src = '/Users/ross/Desktop/snapshot006.jpg'
#                src = '/Users/ross/Desktop/snapshot007-10mm.jpg'
    #            src = '/Users/ross/Desktop/snapshot007--4.jpg'
#                src = '/Users/ross/Desktop/snapshot008-14.jpg'
#                src = '/Users/ross/Desktop/testimage.png'
    #            src = '/Users/ross/Documents/testimage1.tiff'
    #            src = '/Users/ross/Desktop/foo1 copy.tiff'
#                src = '/Users/ross/Pychrondata_beta1.2/data/snapshots/snapshot010.jpg'

            else:
                src = path

        else:
            src = self.video.get_frame()

        self.image.load(src)

        return self.image.source_frame

    def _image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)

    def _working_image_default(self):
        return Image(width=self.image_width,
                     height=self.image_height)

    def _hole_detector_default(self):
        return self.load_hole_detector()

#==============================================================================
# getter/setters
#==============================================================================
    def _get_corrected_position(self):
        try:
            return '{:3f}, {:3f}'.format(*self._corrected_position)
        except IndexError:
            pass

    def _get_nominal_position(self):
        try:
            return '{:3f}, {:3f}'.format(*self._nominal_position)
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
    from src.helpers.logger_setup import logging_setup
    logging_setup('machine_vision')
    m = MachineVisionManager(_debug=True)

    m.configure_traits()

#    time_comp()
#============= EOF =====================================
