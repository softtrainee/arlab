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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.mv.machine_vision_manager import MachineVisionManager
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#============= local library imports  ==========================

class AutoCenterManager(MachineVisionManager):
    def locate_center(self, cx, cy, holenum, dim=1.5):
        frame = self.new_image_frame()
        im = self.new_image(frame)

        self.view_image(im)

        loc = self.new_co2_locator()
        cw = ch = dim * 3
        frame = self._crop_image(self.target_image.source_frame, cw, ch)
#        loc.croppixels=(cw,ch)
        dx, dy = loc.find(self.target_image, frame, dim=dim * self.pxpermm)
        if dx and dy:
            mdx = dx / self.pxpermm
            mdy = dy / self.pxpermm
            self.info('calculated deviation px={:n},{:n}, mm={:0.3f},{:0.3f}'.format(round(dx), round(dy),
                                                                                     mdx, mdy))

            return  cx + mdx, cy - mdy

#============= EOF =============================================
