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
from traits.api import HasTraits, Any, Dict
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
#from src.graph.graph import Graph
#from src.graph.time_series_graph import TimeSeriesGraph
from src.graph.regression_graph import StackedRegressionTimeSeriesGraph
from src.processing.plotters.plotter import Plotter
def colorname_gen():
    r = ['black', 'red', 'green', 'blue', 'yellow']
    i = 0
    while 1:
        yield r[i]
        i += 1


class Series(Plotter):
    fits = None
    pxma = None
    pxmi = None
    regressors = Dict
    def axis_formatter(self, x):
        if 1000 > abs(x) > 0.01:
            return '{:0.2f}'.format(x)
        elif 1e5 > abs(x) > 1000:
            return '{:0.1f}'.format(x)
        elif abs(x) < 1e-15:
            return '{:0.2f}'.format(0)
        else:
            return '{:0.2e}'.format(x)

    def build(self, analyses, keys, basekeys, gids, padding,
              graph=None,
              new_plot=True,
              regress=True):
        self.analyses = analyses
        self.colorgen = colorname_gen()
        if isinstance(keys, str):
            keys = [keys]

        if graph is None:
            klass = StackedRegressionTimeSeriesGraph
            graph = klass(container_dict=dict(
                                          bgcolor='lightgray',
    #                                      padding=2,
                                          padding_top=0,
                                          padding_bottom=5,
                                          padding_left=0,
                                          padding_right=0,
                                          stack_order='top_to_bottom'
                                          ),
                      equi_stack=True
                      )
        self.graph = graph

        self.fits = dict()
        cnt = 0
#        pxma = None
#        pxmi = None
        for i, (k, f) in enumerate(keys + basekeys):
            if new_plot:
                graph.new_plot(padding_left=padding[0],
                       padding_right=padding[1],
                       padding_top=padding[2],
                       padding_bottom=padding[3],
                       pan=False,
                       zoom=False,
                       ytitle='{} (fA)'.format(k))

                p = graph.plots[-1]

                p.value_range.tight_bounds = False
                p.value_range.margin = 0.1

            self.fits[k] = f

            for gid in gids:
                xs, ys, es = zip(*[(a.timestamp,
                                self._get_series_value(a, k, i, gid),
                                self._get_series_error(a, k, i, gid),
                                ) for a in analyses if a.timestamp > 0 and a.gid == gid])

                self._add_series(graph, k, xs, ys, es, f, padding,
                                 regress, gid, plotid=cnt)
                xma = max(xs)
                xmi = min(xs)

                if self.pxma:
                    xma = max(self.pxma, xma)
                    xmi = min(self.pxmi, xmi)

                self.pxma = xma
                self.pxmi = xmi
            cnt += 1

        if self.pxma and self.pxmi:
            graph.set_x_limits(self.pxmi, self.pxma, plotid=0, pad='0.1')

        return graph

    def _get_series_value(self, a, k, i, gid):
        return a.signals[k].value

    def _get_series_error(self, a, k, i, gid):
        return a.signals[k].error


    def _add_series(self, g, iso, xs, ys, es, fi, padding, regress, gid, plotid=0):
        color = self.colorgen.next()
        marker_size = 2
        if not regress:
            fi = None
            color = 'blue'
            marker_size = 5

        args = g.new_series(xs, ys,
                     plotid=plotid,
                     fit=fi,
#                     regress=regress,
                     type='scatter',
                     marker='circle',
                     color=color,
                     marker_size=marker_size
                     #color=self.colorgen.next(),
                     #marker_size=2
                     )

#        g.set_x_limits(min(xs), max(xs), pad='0.25', plotid=plotid)

        g.set_axis_traits(tick_label_formatter=self.axis_formatter, plotid=plotid, axis='y')

        if regress:
#            print 'ffff', g.regressors
            scatter = args[1]
            self._add_error_bars(scatter, es, 'y')
            self._add_scatter_inspector(scatter, gid)
        else:
#            print args
#            print plotid, g.plots[plotid].plots.keys()
            scatter = g.plots[plotid].plots['plot{}'.format(args[0][-1])][0]

#        g.regress_plots()


#============= EOF =============================================
