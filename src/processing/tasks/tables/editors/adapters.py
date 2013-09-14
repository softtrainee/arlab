#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Int, Str, Property, Any
from traitsui.api import View, Item
from traitsui.tabular_adapter import TabularAdapter
from src.helpers.formatting import floatfmt
#============= standard library imports ========================
#============= local library imports  ==========================
class TableBlank(HasTraits):
    analysis = Any
    def __getattr__(self, attr):
        return getattr(self.analysis, attr)

def swidth(v=60):
    return Int(v)
def ewidth(v=50):
    return Int(v)

PM = u'\u00b1 1\u03c3'
class BaseAdapter(TabularAdapter):
    blank_column_text = Str('')
    def _get_value(self, attr):
        if isinstance(self.item, TableBlank):
            v = ''
            if self.item.isotopes.has_key(attr):
                v = self.item.isotopes.get(attr).blank.value
                v = floatfmt(v)
            return v
        else:
            v = getattr(self.item, attr).nominal_value
            return floatfmt(v)

    def _get_error(self, attr):
        if isinstance(self.item, TableBlank):
            v = ''
            if self.item.isotopes.has_key(attr):
                v = self.item.isotopes.get(attr).blank.error
                v = floatfmt(v)
            return v
        else:
            v = getattr(self.item, attr).std_dev


            return floatfmt(v)

class LaserTableAdapter(BaseAdapter):
    columns = [
               ('N', 'aliquot_step_str'),
               ('Power', 'extract_value'),
               ('Mol. Ar40', 'moles_Ar40'),
               ('Ar40', 'ar40'),
               (PM, 'ar40_err'),

               ('Ar39', 'ar39'),
               (PM, 'ar39_err'),

               ('Ar38', 'ar38'),
               (PM, 'ar38_err'),

               ('Ar37', 'ar37'),
               (PM, 'ar37_err'),

               ('Ar36', 'ar36'),
               (PM, 'ar36_err'),
               ('%40Ar*', 'rad40_percent'),

               ('40Ar*/39ArK', 'R'),
               ('Age', 'age'),
               (PM, 'age_error'),
               ('K/Ca', 'kca'),
               (PM, 'kca_error'),
               ('', 'blank_column')
               ]

    aliquot_step_str_text = Property
    extract_value_text = Property
    moles_Ar40_text = Property

    ar40_text = Property
    ar39_text = Property
    ar38_text = Property
    ar37_text = Property
    ar36_text = Property

    ar40_err_text = Property
    ar39_err_text = Property
    ar38_err_text = Property
    ar37_err_text = Property
    ar36_err_text = Property
    rad40_percent_text = Property
    R_text = Property
    age_text = Property
    age_error_text = Property
    kca_text = Property
    kca_error_text = Property



    aliquot_step_str_width = Int(30)
    extract_value_width = Int(40)
    moles_Ar40_width = Int(50)

    ar40_width = swidth()
    ar39_width = swidth()
    ar38_width = swidth()
    ar37_width = swidth()
    ar36_width = swidth()

    ar40_err_width = ewidth()
    ar39_err_width = ewidth()
    ar38_err_width = ewidth()
    ar37_err_width = ewidth()
    ar36_err_width = ewidth(65)

    rad40_percent_width = Int(60)
    age_width = swidth()
    age_error_width = ewidth()
    R_width = Int(70)
    R_width = Int(70)

    font = 'Arial 9'

    def get_bg_color(self, obj, trait, row, column):
        c = 'white'
        if row % 2 == 0:
            c = 'lightgray'
        if self.item.temp_status != 0 or self.item.status != 0:
            c = '#FF9999'

        return c

    def _get_aliquot_step_str_text(self):
        item = self.item
        r = ''
        if not isinstance(item, TableBlank):
            r = '{:02n}{}'.format(item.aliquot, item.step)
        return r

    def _get_extract_value_text(self):
        return self._get_text_value('extract_value')

    def _get_moles_Ar40_text(self):
        return self._get_text_value('moles_Ar40')

    def _get_text_value(self, attr):
        v = ''
        if not isinstance(self.item, TableBlank):
            v = getattr(self.item, attr)
        return v

    def _get_ar40_text(self):
        return self._get_value('Ar40')
    def _get_ar39_text(self):
        return self._get_value('Ar39')
    def _get_ar38_text(self):
        return self._get_value('Ar38')
    def _get_ar37_text(self):
        return self._get_value('Ar37')
    def _get_ar36_text(self):
        return self._get_value('Ar36')

    def _get_ar40_err_text(self):
        return self._get_error('Ar40')
    def _get_ar39_err_text(self):
        return self._get_error('Ar39')
    def _get_ar38_err_text(self):
        return self._get_error('Ar38')
    def _get_ar37_err_text(self):
        return self._get_error('Ar37')
    def _get_ar36_err_text(self):
        return self._get_error('Ar36')


    def _get_rad40_percent_text(self):
        return self._get_value('rad40_percent')
    def _get_R_text(self):
        return self._get_value('R')
    def _get_age_text(self):
        return self._get_value('age')

    def _get_age_error_text(self):
        v = self._get_text_value('age_error')
        if v is not None:
            v = floatfmt(v)
        else:
            v = ''
        return v

    def _get_kca_text(self):
        return self._get_value('kca')

    def _get_kca_error_text(self):
        return self._get_error('kca')


class LaserTableMeanAdapter(BaseAdapter):

    columns = [
               ('N', 'nanalyses'),
               ('Wtd. Age', 'weighted_age'),
               ('S.E', 'age_se'),
               ('Arith. Age', 'arith_age'),
               ('S.D', 'age_sd'),
               ('', 'blank_column')
               ]

    nanalyses_width = Int(40)

    weighted_age_text = Property
    arith_age_text = Property
    age_se_text = Property
    age_sd_text = Property
    font = 'Arial 9'

    def _get_weighted_age_text(self):
        return self._get_value('weighted_age')

    def _get_arith_age_text(self):
        return self._get_value('arith_age')

    def _get_age_se_text(self):
        return self._get_error('weighted_age')

    def _get_age_sd_text(self):
        return self._get_error('arith_age')
#============= EOF =============================================
# class LaserTableBlankAdapter(LaserTableAdapter):
#     columns = [
#                ('N', 'aliquot_step_str'),
#                ('', 'blank_column'),
#                ('Ar40', 'ar40'),
#                (PM, 'ar40_err'),
#
#                ('Ar39', 'ar39'),
#                (PM, 'ar39_err'),
#
#                ('Ar38', 'ar38'),
#                (PM, 'ar38_err'),
#
#                ('Ar37', 'ar37'),
#                (PM, 'ar37_err'),
#
#                ('Ar36', 'ar36'),
#                (PM, 'ar36_err'),
#                ('', 'blank_column') ]
# #     aliquot_step_str_width = Int(120)
#     blank_column_width = Int(100)
#     def _get_ar40_text(self):
#         return self._get_value('Ar40')
#     def _get_ar39_text(self):
#         return self._get_value('Ar39')
#     def _get_ar38_text(self):
#         return self._get_value('Ar38')
#     def _get_ar37_text(self):
#         return self._get_value('Ar37')
#     def _get_ar36_text(self):
#         return self._get_value('Ar36')
#
#     def _get_ar40_err_text(self):
#         return self._get_error('Ar40')
#     def _get_ar39_err_text(self):
#         return self._get_error('Ar39')
#     def _get_ar38_err_text(self):
#         return self._get_error('Ar38')
#     def _get_ar37_err_text(self):
#         return self._get_error('Ar37')
#     def _get_ar36_err_text(self):
#         return self._get_error('Ar36')
#
#     def _get_value(self, attr):
#         v = self.item.isotopes[attr].blank.value
#         return floatfmt(v)
#
#     def _get_error(self, attr):
#         v = self.item.isotopes[attr].blank.error
#         return floatfmt(v)
