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
from traits.api import HasTraits, Instance, Int, Property, List, on_trait_change, Dict
from traitsui.api import View, Item, TableEditor, Group, HGroup
from src.loggable import Loggable
from src.graph.graph import Graph
from src.graph.stacked_graph import StackedGraph
from src.viewable import ViewableHandler, Viewable
from src.displays.rich_text_display import RichTextDisplay
from src.graph.regression_graph import StackedRegressionGraph
from uncertainties import ufloat
#============= standard library imports ========================
from numpy import Inf
#============= local library imports  ==========================
class PlotPanelHandler(ViewableHandler):
    pass
class PlotPanel(Viewable):
    graph = Instance(Graph)
    window_x = 0
    window_y = 0
    window_title = ''

    ncounts = Property(Int(enter_set=True, auto_set=False), depends_on='_ncounts')
    _ncounts = Int

    detector = None
    detectors = List
    isotopes = Property(depends_on='detectors')

    stack_order = 'bottom_to_top'
    series_cnt = 0
    ratio_display = Instance(RichTextDisplay)
    signal_display = Instance(RichTextDisplay)
    fits = List

    signals = Dict

    ratios = ['Ar40:Ar36', 'Ar40:Ar39', ]
    @on_trait_change('graph:regression_results')
    def _update_display(self, new):
        if new:
            display = self.signal_display
            display.clear()
            for iso, reg in zip(self.isotopes, new):
                v = '{:0.5f}'.format(reg.coefficients[-1])
                e = '{:0.5f}'.format(reg.coefficient_errors[-1])
                v = v + u'\00b1 ' + e
                display.add_text('{}={:>10s}'.format(iso, v))

            display = self.ratio_display
            display.clear()
            for ra in self.ratios:
                u, l = ra.split(':')

                try:
                    ru = new[self.isotopes.index(u)]
                    rl = new[self.isotopes.index(l)]
                    ruf = self._get_fit(ru)
                    rlf = self._get_fit(rl)

                    if rl.coefficient_errors[-1] == Inf or ru.coefficient_errors[-1] == Inf:
                        return

                    rr = ufloat((ru.coefficients[-1], ru.coefficient_errors[-1])) / ufloat((rl.coefficients[-1], rl.coefficient_errors[-1]))
                    res = '{}/{}= {:>12s} '.format(u, l, '{:0.5f}'.format(rr.nominal_value)) + \
                          u'\u00b1' + '{:>10s}'.format('{:0.5f}'.format(rr.std_dev())) + \
                            ' {}/{}'.format(ruf, rlf)
                    display.add_text(res)
                except  IndexError:
                    pass

    def _get_fit(self, reg):
        deg = reg.degree
        if deg in [1, 2, 3]:
            return ['l', 'p', 'c'][deg - 1]

    def _fits_changed(self):
        self.graph.set_fits(self.fits)

    def close(self, isok):
        self.parent.cancel()
        return isok

    def _get_ncounts(self):
        return self._ncounts

    def _set_ncounts(self, v):
        self.info('{} set to terminate after {} counts'.format(self.window_title, v))
        self._ncounts = v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        return StackedRegressionGraph(container_dict=dict(padding=5, bgcolor='gray',
                                                stack_order=self.stack_order
                                             ))
    def traits_view(self):
        v = View(
                 Item('graph', show_label=False, style='custom'),
                 Group(
                     Group(
                           HGroup(
                               Item('signal_display', width=0.4, show_label=False, style='custom'),
                               Item('ratio_display', width=0.6, show_label=False, style='custom'),
                           ),
                           label='Results'
                           ),
                     Group(
                           Item('ncounts'),
                           label='Controls',
                           ),
                       layout='tabbed'
                       ),
                 width=500,
                 height=725,
                 x=self.window_x,
                 y=self.window_y,
                 title=self.window_title,
                 handler=PlotPanelHandler
                 )
        return v

    def _get_isotopes(self):
        return [d.isotope for d in self.detectors]
#===============================================================================
# defaults
#===============================================================================
    def _signal_display_default(self):
        return RichTextDisplay(height=100,
                               default_color='black',
                               default_size=12,
#                               width=0.25
                               )
    def _ratio_display_default(self):
        return RichTextDisplay(height=100,
                               default_color='black',
                               default_size=12,
#                               width=0.75
                               )
#============= EOF =============================================
