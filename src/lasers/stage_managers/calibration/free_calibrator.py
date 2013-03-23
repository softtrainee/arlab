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
from traits.api import HasTraits, Float, Button, Bool, Any, String
from traitsui.api import View, Item, HGroup
from src.traits_editors.custom_label_editor import CustomLabel
from src.geometry.geometry import calculate_reference_frame_center
from src.lasers.stage_managers.calibration.calibrator import TrayCalibrator
#============= standard library imports ========================
#============= local library imports  ==========================
HELP_TAG = '''Enter the x, y for this point {:0.3f},{:0.3f}
in data space i.e mm
'''
class FreeCalibrator(TrayCalibrator):
    x = Float
    y = Float
#    accept_point = Button
#    finished = Button
#    calibrating = Bool(False)
    manager = Any
    point1 = None
    point2 = None
    help_tag = String(HELP_TAG)
    def _point_enter_view(self):
        v = View(
                 CustomLabel('help_tag',
                             top_padding=10,
                             left_padding=10,
#                             align='center',
                             color='maroon'),
                 HGroup('x', 'y'),
                 buttons=['OK', 'Cancel'],
                 kind='modal',
                 title='Reference Point'
                 )
        return v

#    def get_controls(self):
#        cg = HGroup(Item('object.calibrator.accept_point',
#                         enabled_when='object.calibrator.calibrating',
#                       show_label=False),
#                  Item('object.calibrator.finished', show_label=False))
#        return cg

    def handle(self, step, x, y, canvas):
        if step == 'Calibrate':
            canvas.new_calibration_item()
#            self.calibrating = True
            self.point1 = None
            return 'Set Point1', None, None, None
        elif step == 'Set Point1':
            self._set_point((x, y))
            return 'Set Point2', None, None, None
        elif step == 'Set Point2':
            self._set_point((x, y))

            cx, cy, rot = calculate_reference_frame_center(self.point1[0],
                                                           self.point2[0],
                                                           self.point1[1],
                                                           self.point2[1])
            return 'Calibrate', cx, cy, rot

    def _set_point(self, sp):
        self.help_tag = HELP_TAG.format(sp[0], sp[1])
        info = self.edit_traits(view='_point_enter_view')
        if info.result:
            dp = self.x, self.y
            if self.point1 is None:
                self.point1 = (dp, sp)
            else:
                self.point2 = (dp, sp)


#    def _finished(self):
#        self.manager.calibration_step = 'Calibrate'
#        self.calibrating = False
#============= EOF =============================================
