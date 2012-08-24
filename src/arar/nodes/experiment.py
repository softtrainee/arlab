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
from traits.api import Str, List, Any, Float, Set
from traitsui.api import View, Item, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import struct
#============= local library imports  ==========================
from core import CoreNode
from analysis import AnalysisNode


class AnalysesAdapter(TabularAdapter):
    columns = [('RunID', 'rid'), ('Age', 'age'), ('Error', 'age_err')]


class ExperimentNode(CoreNode):
    name = Str('Exp1')
    analyses = List(CoreNode)
    experiments = List(CoreNode)
    selected_analysis = Any
    age = Float
    age_err = Float
#    analyses_table = Property(depends_on='analyses')
#    def _get_analyses_table(self):
#        plus_minus = unicode('\xb1')
#        return ['{:0.3f}{}{:0.3f}'.format(a.age,
#                                plus_minus, a.age_err) for a in self.analyses]
#    dclicked = Event
#    selected = Any
#    def _dclicked_fired(self):
#        if self.selected:
#            info = self.selected.edit_traits()
#            info.control.Raise()

    def traits_view(self):
        def readonly(name, **kw):
            return Item(name, style='readonly', **kw)
#        readonly = lambda x, kw:Item(x, style='readonly', **kw)
        v = View(
                 readonly('name', show_label=False),
                 readonly('age', format_str='%0.3f'),
                 readonly('age_err', label='Error', format_str='%0.3f'),
#                 Item('name', show_label=False, style='readonly'),
#                 Item('age', style='readonly'),
#                 Item('age_err', style='readonly'),
                 Item('analyses',
#                      style='readonly',
                      show_label=False,
                      height=300,
                      editor=TabularEditor(adapter=AnalysesAdapter(),
#                                           right_clicked='dclicked',
                                           selected='object.selected_analysis',
                                           editable=False, operations=[]))
                 )
        return v

    def load_database_reference(self, ref, rid, kwargs):
        if not next((a for a in self.analyses if a.rid == rid), None):
            anode = AnalysisNode(rid=rid, **kwargs)

            #save peak regressions
            for iso in ref.isotopes:
                ps = iso.peak_time_series
                xs, ys = self.parse_timeblob(ps.PeakTimeBlob)
                anode.add_iso_series(iso.Label, xs, ys)
            self.analyses.append(anode)

    @classmethod
    def parse_timeblob(cls, blob):
        v, t = zip(*[struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)])
        return t, v

#============= EOF =============================================
