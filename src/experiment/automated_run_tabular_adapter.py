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
from traits.api import Property, Int
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import os
#============= local library imports  ==========================
def get_name(func):
    def _get_name(obj, trait, item):
        name = func(obj, trait, item)

        if name:
            name, _ext = os.path.splitext(name)

            if '_' in name:
                ns = name.split('_')
                name = '_'.join(ns[1:])

        return name if name else ''
    return _get_name

class AutomatedRunAdapter(TabularAdapter):
    state_width = Int(20)
    aliquot_width = Int(50)

    sample_width = Int(80)
    position_width = Int(50)
    duration_width = Int(60)
    overlap_width = Int(50)
    autocenter_width = Int(70)
    heat_value_width = Int(85)
    heat_device_width = Int(125)
    labnumber_width = Int(60)

    extraction_script_width = Int(125)
    measurement_script_width = Int(125)
    post_measurement_script_width = Int(125)
    post_equilibration_script_width = Int(125)

    state_image = Property
    state_text = Property
    extraction_script_text = Property
    measurement_script_text = Property
    post_measurement_script_text = Property
    post_equilibration_script_text = Property
    position_text = Property
    heat_value_text = Property
    heat_units_text = Property
    duration_text = Property
    autocenter_text = Property
    overlap_text = Property

    can_edit = False
#    def get_can_edit(self, obj, trait, row):
#        if self.item:
#            if self.item.state == 'not run':
#                return True
    def get_font(self, obj, trait, row):
        import wx
        s = 12
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
#        w = wx.FONTWEIGHT_BOLD
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w, False, u'Helvetica')

    def get_bg_color(self, obj, trait, row):
        item = getattr(obj, trait)[row]
        if not item.executable:
            return 'red'

    def _columns_default(self):
#        hp = ('Temp', 'heat_value')
#        if self.kind == 'watts':
#            hp =

        return  [('', 'state'),
                 ('Labnumber', 'labnumber'), ('Aliquot', 'aliquot'),

                 ('Sample', 'sample'),
                 ('Position', 'position'),
                 ('Autocenter', 'autocenter'),
                 ('Overlap', 'overlap'),
                 #('Heat Device', 'heat_device'),
                 ('Heat', 'heat_value'),
                 ('Heat Units', 'heat_units'),
                 ('Duration', 'duration'),
                 ('Extraction', 'extraction_script'),
                 ('Measurement', 'measurement_script'),
                 ('Post Measurement', 'post_measurement_script'),
                 ('Post equilibration', 'post_equilibration_script'),
                 ]

    def _get_heat_value_text(self, trait, item):
        return self._get_number('heat_value')

    def _get_heat_units_text(self):
        if self.item.heat_units == '---':
            return ''
        else:
            return self.item.heat_units
#        v, u = self.item.heat_value
#        if u and v:
#            return '{:0.2f},{}'.format(*self.item.heat_value)
#        else:
#            return ''

    def _get_duration_text(self, trait, item):
        return self._get_number('duration')

    def _get_overlap_text(self, trait, item):
        return self._get_number('overlap')

    def _get_position_text(self, trait, item):
        return self._get_number('position')

    def _get_number(self, attr):
        '''
            dont display 0.0's
        '''
        v = getattr(self.item, attr)
        if v:
            return v
        else:
            return ''

    def _get_autocenter_text(self, trait, item):
        return 'yes' if self.item.autocenter else ''

    @get_name
    def _get_extraction_script_text(self, trait, item):
        if self.item.extraction_script:
            return self.item.extraction_script.name

    @get_name
    def _get_measurement_script_text(self, trait, item):
        if self.item.measurement_script:
            return self.item.measurement_script.name

    @get_name
    def _get_post_measurement_script_text(self, trait, item):
        if self.item.post_measurement_script:
            return self.item.post_measurement_script.name

    @get_name
    def _get_post_equilibration_script_text(self, trait, item):
        if self.item.post_equilibration_script:
#            return self.item.post_equilibration_script.name
            return self.item.post_equilibration_script.name

#    def _get_script_name(self, name):
#        return name is name is not None else ''
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
            elif self.item.state == 'truncate':
                im = 'blue'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]

            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')
            return os.path.join(root, '{}_ball.png'.format(im))
#            return os.path.join(root, 'bullet_{}.png'.format(im))

#============= EOF =============================================
