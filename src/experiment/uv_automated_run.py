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
from traits.api import HasTraits, Int, Str, Enum , Property, List, cached_property
from traitsui.api import View, Item, VGroup, EnumEditor
from src.experiment.automated_run import AutomatedRun
from src.constants import NULL_STR
import os
from src.paths import paths
#============= standard library imports ========================
#============= local library imports  ==========================

class UVAutomatedRun(AutomatedRun):
    reprate = Int
    mask = Str
    masks = Property
    attenuator = Str
    extract_units_names = List([NULL_STR, 'burst', 'continuous'])
    _default_extract_units = 'burst'

    @cached_property
    def _get_masks(self):
        p = os.path.join(paths.device_dir, 'uv', 'masks.txt')
        masks = []
        with open(p, 'r') as fp:
            for lin in fp:
                lin = lin.strip()
                if not lin or lin.startswith('#'):
                    continue
                masks.append(lin)

        return masks

    def _get_supplemental_extract_group(self):
        g = VGroup(Item('reprate'),
                   Item('mask', editor=EnumEditor(name='masks')),
                   Item('attenuator'),
                   label='UV'
                   )
        return g

    def _extraction_script_factory(self, ec, key):
        obj = super(UVAutomatedRun, self)._extraction_script_factory(ec, key)
        obj.setup_context(reprate=self.reprate,
                          mask=self.mask,
                          attenuator=self.attenuator
                          )
        return obj


#    @cached_property
#    def _get_post_measurement_script(self):
#        self._post_measurement_script = self._load_script('post_measurement')
#        return self._post_measurement_script
#
#    @cached_property
#    def _get_post_equilibration_script(self):
#        self._post_equilibration_script = self._load_script('post_equilibration')
#        return self._post_equilibration_script
#
#    @cached_property
#    def _get_measurement_script(self):
#        self._measurement_script = self._load_script('measurement')
#        return self._measurement_script
#
#    @cached_property
#    def _get_extraction_script(self):
#        self._extraction_script = self._load_script('extraction')
#        return self._extraction_script

#============= EOF =============================================
