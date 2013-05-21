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

#============= enthought library imports=======================
from traits.api import Property, Int
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import os
from src.paths import paths
from src.constants import EXTRACTION_COLOR, MEASUREMENT_COLOR, SUCCESS_COLOR, \
    SKIP_COLOR, NOT_EXECUTABLE_COLOR
# from src.experiment.utilities.identifier import make_runid
#============= local library imports  ==========================
# def get_name(func):
#    def _get_name(obj, trait, item):
#        name = func(obj, trait, item)
#
#        if name:
#            name, _ext = os.path.splitext(name)
#
#            if '_' in name:
#                ns = name.split('_')
#                name = '_'.join(ns[1:])
#
#        return name if name else ''
#    return _get_name

class AutomatedRunSpecAdapter(TabularAdapter):

    #===========================================================================
    # widths
    #===========================================================================

    sample_width = Int(80)
    aliquot_width = Int(50)
    position_width = Int(50)
    duration_width = Int(60)
    cleanup_width = Int(60)
    overlap_width = Int(50)
    autocenter_width = Int(70)
    pattern_width = Int(125)
    extract_value_width = Int(85)
    extract_units_width = Int(50)
    extract_device_width = Int(125)
    labnumber_width = Int(90)
    extraction_script_width = Int(125)
    measurement_script_width = Int(125)
    post_measurement_script_width = Int(125)
    post_equilibration_script_width = Int(125)

    comment_width = Int(125)
    #===========================================================================
    # number values
    #===========================================================================
    extract_value_text = Property
    duration_text = Property
    cleanup_text = Property
    labnumber_text = Property
    aliquot_text = Property


    def get_bg_color(self, obj, trait, row, column):
        item = self.item
        if not item.executable:
            color = NOT_EXECUTABLE_COLOR
        if item.skip:
            color = SKIP_COLOR  # '#33CCFF'  # light blue
        elif item.state == 'success':
            color = SUCCESS_COLOR  # '#66FF33'  # light green
        elif item.state == 'extraction':
            color = EXTRACTION_COLOR  # '#FFFF66'  # light yellow
        elif item.state == 'measurement':
            color = MEASUREMENT_COLOR  # '#FF7EDF'  # magenta
        else:
            if row % 2 == 0:
                color = 'white'
            else:
                color = '#E6F2FF'  # light gray blue

        return color

    def _get_labnumber_text(self, trait, item):
        it = self.item
        ln = it.labnumber
        if it.user_defined_aliquot:
            ln = '{}-{:02n}'.format(it.labnumber, it.aliquot)
#         else:
#             if self.item.step:
#                 ln = make_runid(it.labnumber,
#                                     it.aliquot,
#                                     it.step)


        return ln
    def _get_aliquot_text(self, trait, item):
        it = self.item

        if  it.step:
            al = '{:02n}{}'.format(it.aliquot, it.step)
        else:
            al = '{:02n}'.format(it.aliquot)

        return al

    def _get_extract_value_text(self, trait, item):
        return self._get_number('extract_value')

    def _get_duration_text(self, trait, item):
        return self._get_number('duration')

    def _get_cleanup_text(self, trait, item):
        return self._get_number('cleanup')
#
#    def _get_aliquot_text(self, trait, item):
#        return self._get_number('aliquot')

    def _get_number(self, attr):
        '''
            dont display 0.0's
        '''
        v = getattr(self.item, attr)
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                v = ''
        if v:
            return v
        else:
            return ''

    def _columns_default(self):
        return self._columns_factory()

    def _columns_factory(self):
        cols = [
#                ('', 'state'),
                 ('Labnumber', 'labnumber'),
                ('Aliquot', 'aliquot'),
                 ('Sample', 'sample'),
                 ('Position', 'position'),
#                 ('Autocenter', 'autocenter'),
#                 ('Overlap', 'overlap'),
                 ('Extract', 'extract_value'),
                 ('Units', 'extract_units'),
                 ('Duration', 'duration'),
                 ('Cleanup', 'cleanup'),
                 ('Pattern', 'pattern'),
                 ('Extraction', 'extraction_script'),
                 ('Measurement', 'measurement_script'),
                 ('Post Eq.', 'post_equilibration_script'),
                 ('Post Meas.', 'post_measurement_script'),
                 ('Comment', 'comment')
                 ]

        return cols

class UVAutomatedRunSpecAdapter(AutomatedRunSpecAdapter):
    def _columns_factory(self):
        cols = super(UVAutomatedRunSpecAdapter, self)._columns_factory()
        cols.insert(7, ('Rep. Rate', 'reprate'))
        cols.insert(8, ('Mask', 'mask'))
        cols.insert(9, ('Attenuator', 'attenuator'))
        return cols

COLOR_STATES = dict(extraction='yellow', measurement='orange',
                     success='green', fail='red', truncate='blue')

# class ExecuteAutomatedRunAdapter(AutomatedRunSpecAdapter):
#    state_width = Int(20)
#    aliquot_width = Int(50)
#    irradiation_width = Int(80)
#    state_image = Property
#    def get_bg_color(self, *args, **kw):
#        item = self.item
#        if not item.executable:
#            color = 'red'
#        if item.skip:
#            color = '#33CCFF'  # light blue
#        elif item.state == 'success':
#            color = '#66FF33'  # light green
#        else:
#            color = super(ExecuteAutomatedRunAdapter, self).get_bg_color(*args, **kw)
#
#        return color
#
#    def _get_state_image(self):
#        im = 'gray'
#        if self.item:
#            if self.item.state in COLOR_STATES:
#                im = COLOR_STATES[self.item.state]
#
#        def debug_path(img):
#            root = os.path.split(__file__)[0]
#            while not root.endswith('src'):
#                root = os.path.split(root)[0]
#
#            root = os.path.split(root)[0]
#            root = os.path.join(root, 'resources', 'balls')
#            return os.path.join(root, '{}_ball.png'.format(img))
#
#        if paths.app_resources:
#            root = paths.app_resources
#            p = os.path.join(root, '{}_ball.png'.format(im))
#            if not os.path.isfile(p):
#                p = debug_path(im)
#        else:
#            p = debug_path(im)
#
#        return p
#
#    def _columns_factory(self):
#        cols = [
#                 ('', 'state'),
#                 ('Labnumber', 'labnumber'),
#                 ('Aliquot', 'aliquot'),
#                 ('Sample', 'sample'),
#                 ('Irrad.', 'irradiation'),
#                 ('Position', 'position'),
# #                 ('Autocenter', 'autocenter'),
# #                 ('Overlap', 'overlap'),
#                 ('Extract', 'extract_value'),
#                 ('Units', 'extract_units'),
#                 ('Duration', 'duration'),
#                 ('Cleanup', 'cleanup'),
#                 ('Pattern', 'pattern'),
#                 ('Extraction', 'extraction_script'),
#                 ('Measurement', 'measurement_script'),
#                 ('Post equilibration', 'post_equilibration_script'),
#                 ('Post Measurement', 'post_measurement_script'),
#                 ('Comment', 'comment')
#                 ]
#
#        return cols

# class AutomatedRunAdapter(TabularAdapter):
#    show_state = Bool(True)
#
#    state_width = Int(20)
#    aliquot_width = Int(50)
#
#    sample_width = Int(80)
#    position_width = Int(50)
#    duration_width = Int(60)
#    cleanup_width = Int(60)
#    overlap_width = Int(50)
#    autocenter_width = Int(70)
#    pattern_width = Int(125)
#    extract_value_width = Int(85)
#    extract_units_width = Int(50)
#    extract_device_width = Int(125)
#    labnumber_width = Int(70)
#
#    extraction_script_width = Int(125)
#    measurement_script_width = Int(125)
#    post_measurement_script_width = Int(125)
#    post_equilibration_script_width = Int(125)
#
#    state_image = Property
#    state_text = Property
#
#    extraction_script_text = Property
#    measurement_script_text = Property
#    post_measurement_script_text = Property
#    post_equilibration_script_text = Property
#
#    position_text = Property
#    extract_value_text = Property
#    extract_units_text = Property
#    duration_text = Property
#    cleanup_text = Property
#    autocenter_text = Property
#    overlap_text = Property
#    aliquot_text = Property
#    sample_text = Property
#
#
#
# #    def get_can_edit(self, obj, trait, row):
# #        return self.item.state == 'not run'
#
#    def get_font(self, obj, trait, row):
#        import wx
#        s = 12
#        f = wx.FONTFAMILY_DEFAULT
#        st = wx.FONTSTYLE_NORMAL
# #        w = wx.FONTWEIGHT_BOLD
#        w = wx.FONTWEIGHT_NORMAL
#
#        return wx.Font(s, f, st, w, False, u'Helvetica')
#
#    def get_bg_color(self, obj, trait, row):
#        item = getattr(obj, trait)[row]
#        color = 'white'
#        if not item.executable:
#            color = 'red'
#        if item.skip:
#            color = '#33CCFF'  # light blue
#        elif item.state == 'success':
#            color = '#66FF33'  # light green
#        return color
#
#    def _columns_default(self):
#        return self._columns_factory()
#
#    def _columns_factory(self):
#
# #        hp = ('Temp', 'extract_value')
# #        if self.kind == 'watts':
# #            hp =
#
#        cols = [('', 'state'),
#                 ('Labnumber', 'labnumber'),
#                 ('Aliquot', 'aliquot'),
#                 ('Sample', 'sample'),
#                 ('Position', 'position'),
# #                 ('Autocenter', 'autocenter'),
#                 ('Pattern', 'pattern'),
# #                 ('Overlap', 'overlap'),
#                 ('Extract', 'extract_value'),
#                 ('Units', 'extract_units'),
#                 ('Duration', 'duration'),
#                 ('Cleanup', 'cleanup'),
#                 ('Extraction', 'extraction_script'),
#                 ('Measurement', 'measurement_script'),
#                 ('Post equilibration', 'post_equilibration_script'),
#                 ('Post Measurement', 'post_measurement_script'),
#                 ]
#        if not self.show_state:
#            cols.pop(0)
#
#        return cols
#
#    def _get_sample_text(self):
#        return self.item.run_info.sample
#
#    def _get_extract_value_text(self, trait, item):
#        return self._get_number('extract_value')
#
#    def _get_extract_units_text(self):
#        if self.item.extract_units == '---':
#            return ''
#        else:
#            return self.item.extract_units
#
#    def _get_duration_text(self, trait, item):
#        return self._get_number('duration')
#
#    def _get_cleanup_text(self, trait, item):
#        return self._get_number('cleanup')
#
#    def _get_overlap_text(self, trait, item):
#        return self._get_number('overlap')
#
#    def _get_position_text(self, trait, item):
# #        print self.ite/m.position, 'ndasd'
#
# #        return 'ffff'
#        return self.item.position
# #        return self._get_number('position')
#
#    def _get_autocenter_text(self, trait, item):
#        return 'yes' if self.item.autocenter else ''
#
#    def _get_aliquot_text(self, trait, item):
#        return '{}{}'.format(self.item.aliquot, self.item.step)
#
#    def _get_state_text(self):
#        return ''
#
#    def _get_state_image(self):
#        if self.item:
#            im = 'gray'
#            if self.item.state == 'extraction':
#                im = 'yellow'
#            elif self.item.state == 'measurement':
#                im = 'orange'
#            elif self.item.state == 'success':
#                im = 'green'
#            elif self.item.state == 'fail':
#                im = 'red'
#            elif self.item.state == 'truncate':
#                im = 'blue'
#
#        def debug_path(img):
#            root = os.path.split(__file__)[0]
#            while not root.endswith('src'):
#                root = os.path.split(root)[0]
#
#            root = os.path.split(root)[0]
#            root = os.path.join(root, 'resources', 'balls')
#            return os.path.join(root, '{}_ball.png'.format(img))
#
#        if paths.app_resources:
#            root = paths.app_resources
#            p = os.path.join(root, '{}_ball.png'.format(im))
#            if not os.path.isfile(p):
#                p = debug_path(im)
#        else:
#            p = debug_path(im)
#
#        return p
#
#    def _get_extraction_script_text(self):
#        return self._get_script_name('extraction')
#
#    def _get_measurement_script_text(self):
#        return self._get_script_name('measurement')
#
#    def _get_post_measurement_script_text(self):
#        return self._get_script_name('post_measurement')
#
#    def _get_post_equilibration_script_text(self):
#        return self._get_script_name('post_equilibration')
# #
#    def _get_script_name(self, script):
#        name = ''
#        script_name = getattr(self.item.script_info, '{}_script_name'.format(script))
# #        print script_name
#        if script:
#            name, _ext = os.path.splitext(script_name)
#            name = name.replace(self.item.mass_spectrometer, '')
#        return name
#
#    def _get_number(self, attr):
#        '''
#            dont display 0.0's
#        '''
#        v = getattr(self.item, attr)
#        if isinstance(v, str):
#            try:
#                v = int(v)
#            except ValueError:
#                v = ''
#        if v:
#            return v
#        else:
#            return ''
#
# class UVAutomatedRunAdapter(AutomatedRunAdapter):
#    def _columns_factory(self):
#        cols = super(UVAutomatedRunAdapter, self)._columns_factory()
#        cols.insert(8, ('Rep. Rate', 'reprate'))
#        cols.insert(9, ('Mask', 'mask'))
#        cols.insert(10, ('Attenuator', 'attenuator'))
#        return cols
#============= EOF =============================================
#    @get_name
#    def _get_extraction_script_text(self, trait, item):
#        if self.item.extraction_script:
#            return self.item.extraction_script.name
#
#    @get_name
#    def _get_measurement_script_text(self, trait, item):
#        if self.item.measurement_script:
#            return self.item.measurement_script.name
#
#    @get_name
#    def _get_post_measurement_script_text(self, trait, item):
#        if self.item.post_measurement_script:
#            return self.item.post_measurement_script.name
#
#    @get_name
#    def _get_post_equilibration_script_text(self, trait, item):
#        if self.item.post_equilibration_script:
# #            return self.item.post_equilibration_script.name
#            return self.item.post_equilibration_script.name
#    def _set_extract_value_text(self, value):
#        self._set_float('extract_value', value)
#    def _set_extract_units_text(self, value):
#        value = value.lower()
#        if value in ['watts', 'percent', 'temp']:
#            self.item.extract_units = value
#    def _set_duration_text(self, value):
#        self._set_int('duration', value)
#    def _set_cleanup_text(self, value):
#        self._set_int('cleanup', value)
#    def _set_overlap_text(self, value):
#        self._set_int('overlap', value)
#    def _set_position_text(self, value):
#        self.item.position = values
#    def _set_float(self, attr, value):
#        try:
#            if value.strip() == '':
#                value = ''
#            setattr(self.item, attr, float(value))
#            self.item.dirty = True
#        except Exception:
#            pass
#    def _set_int(self, attr, value):
#        try:
#            if value.strip() == '':
#                value = 0
#            setattr(self.item, attr, int(value))
#            self.item.dirty = True
#        except ValueError, e:
#            print e
#    def _set_autocenter_text(self, value):
#        value = value.lower()
#        if value in ['yes', 'y', 'x']:
#            self.item.autocenter = True
#        else:
#            self.item.autocenter = False
#    def _set_aliquot_text(self, value):
#        pass
#    def _set_extraction_script_text(self, *args, **kw):
#        pass
#
#    def _set_measurement_script_text(self, *args, **kw):
#        pass
#
#    def _set_post_extraction_script_text(self, *args, **kw):
#        pass
#
#    def _set_post_equilibration_script_text(self, *args, **kw):
#        pass
