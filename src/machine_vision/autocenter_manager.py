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
from traits.api import HasTraits, Instance
from traitsui.api import View, Item, TableEditor
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from os import path
#============= local library imports  ==========================
from src.machine_vision.machine_vision_manager import MachineVisionManager
from src.machine_vision.detectors.co2_detector import CO2HoleDetector
from src.paths import paths

class AutocenterManager(MachineVisionManager):

    def locate_target(self, cx, cy, holenum, *args, **kw):
        try:
            if self.parent:
                sm = self.parent._stage_map
                holedim = sm.g_dimension / 2.
            else:
                holedim = 1.5

            params = self.detector.locate_sample_well(cx, cy, holenum, holedim, **kw)
            msg = 'Target found at {:0.3n}, {:0.3n}'.format(*params) if params else 'No target found'
            self.info(msg)
            return params

        except TypeError:
            import traceback
            traceback.print_exc()

    def _pxpermm_changed(self):
        self.detector.pxpermm = self.pxpermm

#===============================================================================
# persistence
#===============================================================================
    def dump_detector(self):
        p = path.join(paths.hidden_dir, 'co2_detector')
        with open(p, 'wb') as f:
            pickle.dump(self.detector, f)

    def load_detector(self):
        return self._load_detector('co2_detector', CO2HoleDetector)

#============= EOF =============================================
