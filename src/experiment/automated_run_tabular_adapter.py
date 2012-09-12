#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Property
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import os
#============= local library imports  ==========================

class AutomatedRunAdapter(TabularAdapter):

    state_image = Property
    state_text = Property
    extraction_script_text = Property
    measurement_script_text = Property
    post_measurement_script_text = Property
    post_equilibration_script_text = Property
    position_text = Property
    heat_value_text = Property
    duration_text = Property
    autocenter_text = Property
    overlap_text = Property

    can_edit = False
#    def get_can_edit(self, obj, trait, row):
#        if self.item:
#            if self.item.state == 'not run':
#                return True

    def _columns_default(self):
#        hp = ('Temp', 'heat_value')
#        if self.kind == 'watts':
#            hp =

        return  [('', 'state'), ('RunID', 'identifier'), ('Aliquot', 'aliquot'),

                 ('Sample', 'sample'),
                 ('Position', 'position'),
                 ('Autocenter', 'autocenter'),
                 ('HeatDevice', 'heat_device'),
                 ('Overlap', 'overlap'),
                 ('Heat', 'heat_value'),
                 ('Duration', 'duration'),
                 ('Extraction', 'extraction_script'),
                 ('Measurement', 'measurement_script'),
                 ('Post Measurement', 'post_measurement_script'),
                 ('Post equilibration', 'post_equilibration_script'),
                 ]

    def _get_heat_value_text(self, trait, item):
        _, u = self.item.heat_value
        if u:
            return '{:0.2f},{}'.format(*self.item.heat_value)
        else:
            return ''

    def _get_duration_text(self, trait, item):
        return self._get_number('duration')

    def _get_overlap_text(self, trait, item):
        return self._get_number('overlap')

    def _get_position_text(self, trait, item):
        return self._get_number('position')

    def _get_number(self, attr):
        v = getattr(self.item, attr)
        if v:
            return v
        else:
            return ''

    def _get_autocenter_text(self, trait, item):
        return 'yes' if self.item.autocenter else ''

    def _get_extraction_script_text(self, trait, item):
        if self.item.extraction_script:
            return self.item.extraction_script.name

    def _get_measurement_script_text(self, trait, item):
        if self.item.measurement_script:
            return self.item.measurement_script.name

    def _get_post_measurement_script_text(self, trait, item):
        if self.item.post_measurement_script:
            return self.item.post_measurement_script.name

    def _get_post_equilibration_script_text(self, trait, item):
        if self.item.post_equilibration_script:
            return self.item.post_equilibration_script.name

    def _get_state_text(self):
        return ''

    def _get_state_image(self):
        if self.item:
            im = 'gray'
            if self.item.state == 'extraction':
                im = 'yellow'
            elif self.item.state == 'measurement':
                im = 'orange'
            elif self.item.state == 'success':
                im = 'green'
            elif self.item.state == 'fail':
                im = 'red'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]
            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')
            return os.path.join(root, '{}_ball.png'.format(im))

#============= EOF =============================================
