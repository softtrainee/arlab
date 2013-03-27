#===============================================================================
# Copyright 2012 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
from traits.api import HasTraits, Float, Event, String, Bool, Any, Enum, Property, cached_property
from traitsui.api import View, Item, VGroup, HGroup, spring, Group
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.traits_editors.custom_label_editor import CustomLabel
from src.lasers.stage_managers.calibration.free_calibrator import FreeCalibrator
from src.lasers.stage_managers.calibration.calibrator import TrayCalibrator
import os
from src.paths import paths

TRAY_HELP = '''1. Locate center hole
2. Locate right hole
'''
FREE_HELP = '''1. Move to Point, Enter Reference Position. Repeat at least 2X
2. Hit End Calibrate to finish and compute parameters
'''
from src.regex import XY_REGEX


class TrayCalibrationManager(Manager):
    x = Float
    y = Float
    rotation = Float
    scale = Float
    calibrate = Event
    calibration_step = String('Calibrate')
    calibration_help = String(TRAY_HELP)
    style = Enum('Tray', 'Free')
    canvas = Any
    calibrator = Property(depends_on='style')

    position_entry = String(enter_set=True, auto_set=False)

    def isCalibrating(self):
        return self.calibration_step != 'Calibrate'
#===============================================================================
# handlers
#===============================================================================
    def _style_changed(self):
        if self.style == 'Free':
            self.calibration_help = FREE_HELP
        else:
            self.calibration_help = TRAY_HELP

    def _position_entry_changed(self, en):
        '''
            go to a calibrated position
        '''
        if XY_REGEX.match(en):
            x, y = map(float, en.split(','))
            self.parent.linear_move(x, y, use_calibration=True, block=False)
        else:
            try:
                h = int(en)
                self.parent.move_to_hole(h)
            except ValueError:
                pass

    def get_current_position(self):
        x = self.parent.stage_controller.x
        y = self.parent.stage_controller.y
        return x, y

    def _calibrate_fired(self):
        '''
        '''
        x, y = self.get_current_position()
        self.rotation = 0

        args = self.calibrator.handle(self.calibration_step,
                                      x, y, self.canvas)
        if args:
            cstep, cx, cy, rot, scale = args
            if cstep is not None:
                self.calibration_step = cstep
            if cx is not None and cy is not None:
                self.x, self.y = cx, cy
            if scale is not None:
                self.scale = scale
            if rot is not None:
                self.rotation = rot
                self.save_calibration()

    def load_calibration(self, stage_map=None):
        if stage_map is None:
            stage_map = self.parent.stage_map

        calobj = TrayCalibrator.load(stage_map)
        if calobj is not None:
            self.canvas.calibration_item = calobj
            self.x, self.y = calobj.cx, calobj.cy
            self.rotation = calobj.rotation
            self.scale = calobj.scale
            self.style = calobj.style
            # force style change update
            self._style_changed()

    def save_calibration(self):
        PICKLE_PATH = p = os.path.join(paths.hidden_dir, '{}_stage_calibration')
        # delete the corrections file
        stage_map_name = self.parent.stage_map
        ca = self.canvas.calibration_item
        if  ca is not None:
            self.parent._stage_map.clear_correction_file()
            ca.style = self.style
            p = PICKLE_PATH.format(stage_map_name)
            self.info('saving calibration {}'.format(p))
            with open(p, 'wb') as f:
                pickle.dump(ca, f)

    def get_additional_controls(self):
        return self.calibrator.get_controls()

    def traits_view(self):
        cg = VGroup(
                    Item('style', show_label=False, enabled_when='not object.isCalibrating()'),
                    self._button_factory('calibrate', 'calibration_step'),
                    HGroup(Item('x', format_str='%0.3f', style='readonly'),
                           Item('y', format_str='%0.3f', style='readonly')),
                    Item('rotation', format_str='%0.3f', style='readonly'),
                    Item('scale', format_str='%0.3f', style='readonly'),
                    )
        ad = self.get_additional_controls()
        if ad is not None:
            cg.content.append(ad)

        v = View(cg,
                    CustomLabel('calibration_help',
                                color='green',
                                height=75, width=300),
                    Group(Item('position_entry',
                               show_label=False,
                               tooltip='Enter a positon e.g 1 for a hole, or 3,4 for X,Y'
                               ), label='Position',
                          show_border=True)
                )
        return v
#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_calibrator(self):
        kw = dict(name=self.parent.stage_map,
                manager=self)
        if self.style == 'Free':
            klass = FreeCalibrator
        else:
            klass = TrayCalibrator

        return klass(**kw)
#============= EOF =============================================
