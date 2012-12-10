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
from traits.api import HasTraits, List, Int, Property, Str, Event, Any
from traitsui.api import View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter

#============= standard library imports ========================
#============= local library imports  ==========================
class AnalysisAdapter(TabularAdapter):
    columns = [('Status', 'status_string'), ('ID', 'record_id'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error')
#               (unicode('03c3', encoding='symbol'), 'error')
               ]
    status_string_width = Int(40)
    age_text = Property
    age_error_format = Str('%0.4f')
    age_width = Int(80)
    age_error_width = Int(80)

    def _get_age_text(self, trait, item):
        return '{:0.4f}'.format(self.item.age[0])

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w)

    def get_bg_color(self, obj, trait, row):
        bgcolor = 'white'
        if self.item.status != 0:
            bgcolor = '#FF7373'
        return bgcolor

class TabularAnalysisManager(HasTraits):
    analyses = List
    update_selected_analysis = Event
    selected_analysis = Any
    def traits_view(self):
        v = View(Item('analyses',
                      show_label=False,
                      editor=TabularEditor(adapter=AnalysisAdapter(),
                                           dclicked='update_selected_analysis',
                                           selected='selected_analysis',
                                           editable=False
                                           )),
                 x=50,
                 y=30,
                 width=500,
                 height=600,
                 resizable=True
                 )
        return v

    def _update_selected_analysis_fired(self):
        sa = self.selected_analysis
        if sa is not None:
            dbr = sa.dbrecord
            dbr.load_graph()
            dbr.edit_traits()
#============= EOF =============================================
