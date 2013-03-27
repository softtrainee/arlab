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
from src.geometry.geometry import calculate_reference_frame_center, calc_length
from src.lasers.stage_managers.calibration.calibrator import TrayCalibrator
from src.geometry.reference_point import ReferencePoint
#============= standard library imports ========================
#============= local library imports  ==========================


class FreeCalibrator(TrayCalibrator):
#    accept_point = Button
#    finished = Button
#    calibrating = Bool(False)
    manager = Any
    point1 = None
    point2 = None


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
#             canvas.calibration_item.cx = x
#             canvas.calibration_item.cy = y
            return 'Set Point2', None, None, None
        elif step == 'Set Point2':
#             canvas.calibration_item.ry = y
#             canvas.calibration_item.rx = x
            self._set_point((x, y))
            r1 = self.point1[0]
            r2 = self.point2[0]
            R1 = self.point1[1]
            R2 = self.point2[1]
            cx, cy, rot = calculate_reference_frame_center(r1, r2, R1, R2)

            rd = calc_length(r1, r2)
            Rd = calc_length(R1, R2)

            scale = rd / Rd
            print scale
            ca = canvas.calibration_item
            ca.cx, ca.cy = cx, cy
            ca.rotation = rot
            ca.scale = scale
            return 'Calibrate', cx, cy, rot

    def _set_point(self, sp):
        rp = ReferencePoint(sp)
        info = rp.edit_traits()
        if info.result:
            dp = rp.x, rp.y
            if self.point1 is None:
                self.point1 = (dp, sp)

            else:
                self.point2 = (dp, sp)


#    def _finished(self):
#        self.manager.calibration_step = 'Calibrate'
#        self.calibrating = False
#============= EOF =============================================