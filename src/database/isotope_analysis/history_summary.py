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
from traits.api import Property, List, Str, Instance, on_trait_change
from traitsui.api import View, Item, HGroup, ListStrEditor
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from src.database.isotope_analysis.summary import Summary
from src.graph.stacked_graph import StackedGraph

class HistorySummary(Summary):
    history_names = Property(depends_on='histories')
    histories = List
    selected_history = Str
    graph = Instance(StackedGraph)

    history_name = ''

    @on_trait_change('selected_history')
    def _build_summary(self):
        hn = self.history_name
        dbr = self.result
        self.histories = getattr(dbr, '{}_histories'.format(hn))

        g = StackedGraph()
        if self.histories:
            hi = next((hh for hh in self.histories
                       if '{:<12s} {}'.format(hh.user, hh.create_date) == self.selected_history),
                      self.histories[-1])

            isokeys = sorted([bi.isotope for bi in getattr(hi, hn)
#                              if bi.use_set
                              ],
                           key=lambda x:int(x[2:4]),
                           reverse=True)
            xma = -np.Inf
            xmi = np.Inf

            for i, iso in enumerate(isokeys):
                bi = next((bii for bii in getattr(hi, hn)
                           if bii.isotope == iso), None)

                g.new_plot()
                if bi.use_set:
                    xs = [dbr.make_timestamp(str(bs.analysis.rundate),
                                         str(bs.analysis.runtime)) for bs in bi.sets]

                    xs = np.array(xs)
                    if xs.shape[0]:
                        xs = xs - np.min(xs)
                        ys = np.random.random(xs.shape[0])
                        g.new_series(xs, ys)
                        xma = max(xma, max(xs))
                        xmi = min(xmi, min(xs))
                else:
                    uv = bi.user_value
                    ue = bi.user_error
                    kw = dict(plotid=i, color=(0, 0, 0))
                    g.add_horizontal_rule(uv, line_style='solid',
                                          **kw)
                    g.add_horizontal_rule(uv + ue, **kw)
                    g.add_horizontal_rule(uv - ue, **kw)
                    g.set_y_limits(min=uv - ue,
                                   max=uv + ue, pad='0.1', plotid=i)
        self.graph = g

    def _get_history_names(self):
        return ['{:<12s} {}'.format(dbi.user, dbi.create_date)
                          for dbi in self.histories]

    def traits_view(self):
        v = View(HGroup(
                        Item('history_names', show_label=False,
                             editor=ListStrEditor(
                                         editable=False,
                                         operations=[],
                                         horizontal_lines=True,
                                         selected='object.selected_history'),
                            width=200
                            ),
                        Item('graph', show_label=False, style='custom')
                        )
                 )

        return v
#============= EOF =============================================
