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
#from traits.api import HasTraits, List, Str, Instance, Property, \
#     on_trait_change
#from traitsui.api import View, Item, ListStrEditor, HGroup
#============= standard library imports ========================
#import numpy as np
#============= local library imports  ==========================
#from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.history_summary import HistorySummary
#from src.graph.graph import Graph
#from src.graph.stacked_graph import StackedGraph

class BlanksSummary(HistorySummary):
    history_name = 'blanks'
#    history_names = Property(depends_on='histories')
#    histories = List
#    selected_history = Str
#    graph = Instance(Graph)
#
#    @on_trait_change('selected_history')
#    def _build_summary(self):
#        dbr = self.result
#        self.histories = dbr.blanks_histories
#
#        g = StackedGraph()
#        if self.histories:
#
#            hi = self.histories[0]
#            isokeys = sorted([bi.isotope for bi in hi.blanks if bi.use_set],
#                           key=lambda x:int(x[2:4]),
#                           reverse=True)
#            for iso in isokeys:
#
#                bset = next((bi.sets for bi in hi.blanks if bi.isotope == iso), None)
#
#                g.new_plot()
#
#                xs = [dbr.make_timestamp(str(bs.analysis.rundate),
#                                     str(bs.analysis.runtime)) for bs in bset]
#
#                xs = np.array(xs)
#                xs = xs - np.min(xs)
#                ys = np.random.random(xs.shape[0])
#                g.new_series(xs, ys)
#        self.graph = g
#
#
#    def _get_history_names(self):
#        return ['{}-{}'.format(dbi.user, dbi.create_date)
#                          for dbi in self.histories]
#
#    def traits_view(self):
#        v = View(HGroup(
#                        Item('history_names', show_label=False,
#                             editor=ListStrEditor(editable=False,
#                                         operations=[],
#                                         horizontal_lines=True,
#                                         selected='selected_history'),
#                            width=200
#                            ),
#                        Item('graph', show_label=False, style='custom')
#                        )
#                 )
#
#        return v

#============= EOF =============================================
