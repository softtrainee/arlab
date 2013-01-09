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
from traits.api import HasTraits, Instance, Str
#     on_trait_change
from traitsui.api import View, Item, VGroup, HGroup
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from src.database.isotope_analysis.history_summary import HistorySummary
from src.graph.graph import Graph

#from src.graph.graph import Graph
#from src.graph.stacked_graph import StackedGraph


class DetGraph(HasTraits):
    graph = Instance(Graph)
    value = Str

    def traits_view(self):
        v = View(
                 VGroup(
                        HGroup(
                               Item('value',
                                    label='IC Factor',
                                    style='readonly',
                                    ),
                               ),
                      Item('graph',
                           show_label=False, style='custom',
                           height=0.95,
#                           width=700,
                      ),
                    ),
#                 width=700,
                 )

        return v

class DetectorIntercalibrationSummary(HistorySummary):
    history_name = 'detector_intercalibration'
    graph = Instance(DetGraph)
    apply_name = 'selected_detector_intercalibration'
    def _graph_default(self):
        g = super(DetectorIntercalibrationSummary, self)._graph_default()
        return DetGraph(graph=g)

    def _build_graph(self, history):

        dbr = self.record
#        g = Graph(container_dict=dict(padding=5, bgcolor='lightgray'),
#                  width=510
#                  )
        g = self.graph.graph
        g.clear()
        g.new_plot(padding=[50, 0, 0, 50])
#        self.graph = DetGraph(graph=g)

#        bi = getattr(history, self.history_name)
        bi = history.detector_intercalibration
        if not bi:
            return
#        print bi.fit

        det = next((iso.detector for iso in dbr.dbrecord.isotopes
                      if iso.molecular_weight.name == 'Ar36'), None)
        bi = next((item for item in bi if item.detector == det), None)


        if bi.fit:
            xs = [dbr.make_timestamp(str(bs.analysis.rundate),
                                     str(bs.analysis.runtime)) for bs in bi.sets]

            xs = np.array(xs)
            if xs.shape[0]:
                xs = xs - np.min(xs)
                ys = np.random.random(xs.shape[0])
                g.new_series(xs, ys)
#                xma = max(xma, max(xs))
#                xmi = min(xmi, min(xs))

        else:
            uv = bi.user_value
            ue = bi.user_error

            s, _p = g.new_series([0], [uv], type='scatter')

            kw = dict(plotid=0, color=(0, 0, 0))
            g.add_horizontal_rule(uv, line_style='solid',
                                  **kw)
            g.add_horizontal_rule(uv + ue, **kw)
            g.add_horizontal_rule(uv - ue, **kw)

#            s.value_range.trait_set(tight_bounds=False,
#                                    margin=0.01
#                                    )
#            g.set_x_limits(-10, 10)
            s.index_range.trait_set(tight_bounds=False,
                                    margin=0.1
                                    )

            mi = max(0, uv - ue * 1.1)
            ma = (uv + ue * 1.1)
            g.set_y_limits(min=mi,
                           max=ma, plotid=0)
        g.redraw()
        v = '{:0.5f} '.format(uv) + PLUSMINUS + ' {:0.5f}'.format(ue)
        self.graph.value = v
#        g.redraw()

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
