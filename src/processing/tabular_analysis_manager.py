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
from traits.api import List, Int, Property, Event, Any, cached_property, Str
from traitsui.api import Item, TabularEditor, Group, VGroup
from traitsui.tabular_adapter import TabularAdapter
from src.viewable import Viewable, ViewableHandler
import math
from src.processing.analysis_means import AnalysisRatioMean, \
    AnalysisIntensityMean
from src.database.core.database_selector import ColumnSorterMixin

#============= standard library imports ========================
#============= local library imports  ==========================
class AnalysisAdapter(TabularAdapter):
    columns = [('Status', 'status'),
               ('ID', 'record_id'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error')
#               (unicode('03c3', encoding='symbol'), 'error')
               ]

    status_text = Property
    status_width = Int(40)
    age_text = Property
    age_error_text = Property
#    age_error_format = Str('%0.4f')
#    age_width = Int(80)
#    age_error_width = Int(80)
    def _get_status_text(self):
        status = ''
        if self.item.status != 0 or self.item.temp_status != 0:
            status = 'X'
        return status

    def _get_age_text(self):
        return self._get_value('age')

    def _get_age_error_text(self):
        return self._get_error('age')

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w)

    def get_bg_color(self, obj, trait, row):
        bgcolor = 'white'
        if self.item.status != 0 or self.item.temp_status != 0:
            bgcolor = '#FF7373'

        elif row % 2 == 0:
            bgcolor = '#F0F8FF'

        return bgcolor

    def _floatfmt(self, f, n=5):
        if abs(f) < math.pow(10, -(n - 1)) or abs(f) > math.pow(10, n):
            fmt = '{:0.3e}'
        else:
            fmt = '{{:0.{}f}}'.format(n)

        return fmt.format(f)

    def _get_value(self, k):
        return self._floatfmt(getattr(self.item, k).nominal_value)

    def _get_error(self, k):
        return self._floatfmt(getattr(self.item, k).std_dev(), n=6)


class AnalysisIntensityAdapter(AnalysisAdapter):
    columns = [
               ('Status', 'status'),
               ('ID', 'record_id'),
               ('Ar40', 'Ar40'),
               (u'\u00b11s', 'Ar40_error'),
               ('Ar39', 'Ar39'),
               (u'\u00b11s', 'Ar39_error'),
               ('Ar38', 'Ar38'),
               (u'\u00b11s', 'Ar38_error'),
               ('Ar37', 'Ar37'),
               (u'\u00b11s', 'Ar37_error'),
               ('Ar36', 'Ar36'),
               (u'\u00b11s', 'Ar36_error'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error'),
               ]

    Ar40_text = Property
    Ar40_error_text = Property
    Ar39_text = Property
    Ar39_error_text = Property
    Ar38_text = Property
    Ar38_error_text = Property
    Ar37_text = Property
    Ar37_error_text = Property
    Ar36_text = Property
    Ar36_error_text = Property


    def _get_Ar40_text(self):
        return self._get_value('Ar40')

    def _get_Ar40_error_text(self):
        return self._get_error('Ar40')

    def _get_Ar39_text(self):
        return self._get_value('Ar39')

    def _get_Ar39_error_text(self):
        return self._get_error('Ar39')

    def _get_Ar38_text(self):
        return self._get_value('Ar38')

    def _get_Ar38_error_text(self):
        return self._get_error('Ar38')

    def _get_Ar37_text(self):
        return self._get_value('Ar37')

    def _get_Ar37_error_text(self):
        return self._get_error('Ar37')

    def _get_Ar36_text(self):
        return self._get_value('Ar36')

    def _get_Ar36_error_text(self):
        return self._get_error('Ar36')


class AnalysisRatioAdapter(AnalysisAdapter):
    columns = [
               ('Status', 'status'),
               ('ID', 'record_id'),
               ('40*/K39', 'Ar40_39'),
               (u'\u00b11s', 'Ar40_39_error'),
               ('Ar37/Ar39', 'Ar37_39'),
               (u'\u00b11s', 'Ar37_39_error'),
               ('Ar36/Ar39', 'Ar36_39'),
               (u'\u00b11s', 'Ar36_39_error'),
               ('K/Ca', 'kca'),
               (u'\u00b11s', 'kca_error'),
               ('K/Cl', 'kcl'),
               (u'\u00b11s', 'kcl_error'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error'),
               ]

    Ar40_39_text = Property
    Ar40_39_error_text = Property
    Ar37_39_text = Property
    Ar37_39_error_text = Property
    Ar36_39_text = Property
    Ar36_39_error_text = Property
    kca_text = Property
    kca_error_text = Property
    kcl_text = Property
    kcl_error_text = Property

    def _get_Ar40_39_text(self):
        return self._get_value('Ar40_39')

    def _get_Ar40_39_error_text(self):
        return self._get_error('Ar40_39')

    def _get_Ar37_39_text(self):
        return self._get_value('Ar37_39')

    def _get_Ar37_39_error_text(self):
        return self._get_error('Ar37_39')

    def _get_Ar36_39_text(self):
        return self._get_value('Ar36_39')

    def _get_Ar36_39_error_text(self):
        return self._get_error('Ar36_39')

    def _get_kca_text(self):
        return self._get_value('kca')

    def _get_kca_error_text(self):
        return self._get_error('kca')

    def _get_kcl_text(self):
        return self._get_value('kcl')

    def _get_kcl_error_text(self):
        return self._get_error('kcl')


class MeanAdapter(AnalysisAdapter):
    nanalyses_width = Int(40)
    def get_bg_color(self, obj, trait, row):
        bgcolor = 'white'
        if row % 2 == 0:
            bgcolor = '#F0F8FF'

        return bgcolor


class AnalysisRatioMeanAdapter(MeanAdapter, AnalysisRatioAdapter):
    columns = [('N', 'nanalyses'),
               ('ID', 'identifier'),
               ('40*/K39', 'Ar40_39'),
               (u'\u00b11s', 'Ar40_39_error'),
               ('Ar37/Ar39', 'Ar37_39'),
               (u'\u00b11s', 'Ar37_39_error'),
               ('Ar36/Ar39', 'Ar36_39'),
               (u'\u00b11s', 'Ar36_39_error'),
               ('K/Ca', 'kca'),
               (u'\u00b11s', 'kca_error'),
               ('K/Cl', 'kcl'),
               (u'\u00b11s', 'kcl_error'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error'),
               ]


class AnalysisIntensityMeanAdapter(MeanAdapter, AnalysisIntensityAdapter):
    columns = [('N', 'nanalyses'),
               ('ID', 'identifier'),
               ('Ar40', 'Ar40'),
               (u'\u00b11s', 'Ar40_error'),
               ('Ar39', 'Ar39'),
               (u'\u00b11s', 'Ar39_error'),
               ('Ar38', 'Ar38'),
               (u'\u00b11s', 'Ar38_error'),
               ('Ar37', 'Ar37'),
               (u'\u00b11s', 'Ar37_error'),
               ('Ar36', 'Ar36'),
               (u'\u00b11s', 'Ar36_error'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error'),
               ]


class TabularAnalysisHandler(ViewableHandler):
    def object_title_changed(self, info):
        if info.initialized:
            info.ui.title = info.object.title


class TabularAnalysisManager(Viewable, ColumnSorterMixin):
    analyses = List
    ratio_means = Property(depends_on='analyses.[temp_status,status]')
    intensity_means = Property(depends_on='analyses.[temp_status,status]')

    update_selected_analysis = Event
    selected_analysis = Any
    db = Any
    window_x = 50
    window_y = 200
    window_width = 0.85
    window_height = 500
    title = Str('Analysis Table')
    handler_klass = TabularAnalysisHandler

    def set_title(self, title):
        self.title = 'Table {}'.format(title)

    @cached_property
    def _get_ratio_means(self):
        means = [AnalysisRatioMean(analyses=self.analyses)]
        return means

    @cached_property
    def _get_intensity_means(self):
        means = [AnalysisIntensityMean(analyses=self.analyses)]
        return means

    def traits_view(self):
        intensity = VGroup(Item('analyses',
                              height=300,
                              show_label=False,
                              editor=TabularEditor(adapter=AnalysisIntensityAdapter(),
                                   dclicked='update_selected_analysis',
                                   selected='selected_analysis',
                                   column_clicked='column_clicked',
                                   editable=False,
                                   auto_update=True
                                   )),
                           Item('intensity_means',
                              height=100,
                              show_label=False,
                              editor=TabularEditor(adapter=AnalysisIntensityMeanAdapter(),
                                                   editable=False,
                                                   auto_update=True,
                                                   column_clicked='column_clicked',
                                                   )
                                )

                           )
        ratio = VGroup(
                       Item('analyses',
                          height=300,
                          show_label=False,
                          editor=TabularEditor(adapter=AnalysisRatioAdapter(),
                               dclicked='update_selected_analysis',
                               selected='selected_analysis',
                               column_clicked='column_clicked',
                               editable=False,
                               auto_update=True
                               )
                            ),
                       Item('ratio_means',
                          height=100,
                          show_label=False,
                          editor=TabularEditor(adapter=AnalysisRatioMeanAdapter(),
                                               editable=False,
                                               auto_update=True,
                                               column_clicked='column_clicked',
                                               )
                            )

                       )

        return self.view_factory(Group(
                                       Group(intensity, label='Intensities'),
                                       Group(ratio, label='Ratios'),
                                       layout='tabbed'
                                       ),
                                 )

    def _update_selected_analysis_fired(self):
        sa = self.selected_analysis
        if sa is not None:
            dbr = sa.isotope_record
            if self.db:
                self.db.selector.open_record(dbr)
#            dbr.load_graph()
#            dbr.edit_traits()
#============= EOF =============================================
#    def _set_Ar40_text(self, v):
#        pass
#
#    def _set_Ar40_error_text(self, v):
#        pass
#
#    def _set_Ar39_text(self, v):
#        pass
#
#    def _set_Ar39_error_text(self, v):
#        pass
#
#    def _set_Ar38_text(self, v):
#        pass
#
#    def _set_Ar38_error_text(self, v):
#        pass
#
#    def _set_Ar37_text(self, v):
#        pass
#
#    def _set_Ar37_error_text(self, v):
#        pass
#
#    def _set_Ar36_text(self, v):
#        pass
#
#    def _set_Ar36_error_text(self, v):
#        pass
#
#    def _set_age_text(self, v):
#        pass
#
#    def _set_age_error_text(self, v):
#        pass
