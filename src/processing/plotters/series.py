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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================
from src.processing.plotters.plotter import Plotter
from src.graph.regression_graph import AnnotatedRegresssionTimeSeriesGraph

class Series(Plotter):
    def build(self, analyses, options):
        an = AnnotatedRegresssionTimeSeriesGraph(
                                               graph_dict=dict(container_dict=dict(padding=5),
                                                               use_inspector_tool=False
                                                               ),
                                               window_title=options.name,
                                               )

        g = an.graph
        p = g.new_plot(padding=[50, 5, 5, 35],
                       ytitle=options.name,
                       xtitle='Time')
        p.value_range.tight_bounds = False

        key = options.key
        x, ys = zip(*[(ai.timestamp, self.get_value(ai, key)) for ai in analyses])
        y, es = zip(*ys)
        '''
            multiple by a constant. normally 1 but can use 1/295.5 if plotting ICFactor
        '''
        y = array(y)
        y *= (1 / options.scalar)

        plot, scatter, _l = g.new_series(x, y,
                     type='scatter', marker_size=1.5,
                     fit=options.fit
                     )

        self._add_scatter_inspector(g.plotcontainer, plot,
                                    scatter,
                                    0,
                                    )
        self._add_error_bars(scatter, es, 'y')

        sel = [i for i, ai in enumerate(analyses) if ai.status != 0]
        scatter.index.metadata['selections'] = sel

        g.set_x_limits(min(x), max(x), pad='0.1')
        g.refresh()

        return an

    def get_value(self, analysis, k):
        def get_value(ai, ki):
            try:
#                nv = ai.arar_result[ki.replace('Ar', 's')]
                #if ki is like s40 or s39
                nv = ai.arar_result[ki]
            except KeyError:

                #ki is like Ar40 or Ar39bs
                nv = ai.signals[ki].uvalue# - ai.signals['{}bs'.format(ki)]
            return nv

        if '/' in k:
            n, d = k.split('/')
            nv = get_value(analysis, n)
            dv = get_value(analysis, d)
            v = (nv / dv)

        else:
            v = get_value(analysis, k)

        return v.nominal_value, v.std_dev()
#============= EOF =============================================

##===============================================================================
## Copyright 2012 Jake Ross
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##   http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##===============================================================================
#
##============= enthought library imports =======================
#from traits.api import HasTraits, Any, Dict
##from traitsui.api import View, Item, TableEditor
##============= standard library imports ========================
##============= local library imports  ==========================
##from src.graph.graph import Graph
##from src.graph.time_series_graph import TimeSeriesGraph
#from src.graph.regression_graph import StackedRegressionTimeSeriesGraph
#from src.processing.plotters.plotter import Plotter
#from uncertainties import ufloat
#def colorname_gen():
#    r = ['black', 'red', 'green', 'blue', 'yellow']
#    i = 0
#    while 1:
#        yield r[i]
#        i += 1
#
#
#class Series(Plotter):
#    fits = None
#    pxma = None
#    pxmi = None
#    regressors = Dict
#    def axis_formatter(self, x):
#        if 1000 > abs(x) > 0.01:
#            return '{:0.2f}'.format(x)
#        elif 1e5 > abs(x) > 1000:
#            return '{:0.1f}'.format(x)
#        elif abs(x) < 1e-15:
#            return '{:0.2f}'.format(0)
#        else:
#            return '{:0.2e}'.format(x)
#
#
#    def get_excluded_points(self, keys, group_ids):
#        exclude = dict()
#        if self.graph:
#            graph = self.graph
#
#            for i, (k, f) in enumerate(keys):
#                for group_id in group_ids:
#                    try:
#                        plot = graph.plots[i].plots['data{}'.format(group_id)][0]
#                        exclude['{}{}'.format(k, group_id)] = plot.index.metadata['selections']
#                    except IndexError:
#                        pass
#        else:
#            for i, (k, f) in enumerate(keys):
#                for group_id in group_ids:
#                    try:
##                        plot = graph.plots[i].plots['data{}'.format(group_id)][0]
##                        sel = plot.index.metadata['selections']
#                        ff = [i for i, si in enumerate(self.sorted_analyses)
#                                    if si.status == -1 and si.group_id == group_id]
#                        exclude['{}{}'.format(k, group_id)] = ff
#                    except IndexError:
#                        pass
#
#
#        return exclude
#
#    def set_excluded_points(self, exclude, keys, group_ids):
#        if not exclude:
#            return
#
#        graph = self.graph
##        ks = keys + basekeys + ratiokeys
#        graph.suppress_regression = True
#        for i, (k, f) in enumerate(keys):
#            for group_id in group_ids:
#                plot = graph.plots[i].plots['data{}'.format(group_id)][0]
#                try:
#                    plot.index.metadata['selections'] = exclude['{}{}'.format(k, group_id)]
#                except KeyError:
#                    pass
#
#        graph.suppress_regression = False
#        graph._update_graph()
#
#
#    def build(self, keys, basekeys, ratiokeys, group_ids,
#              padding,
#              graph=None,
#              new_plot=True,
#              regress=True,
#              ):
#        analyses = self.analyses
#        self.colorgen = colorname_gen()
#        if isinstance(keys, str):
#            keys = [keys]
#
#        if graph is None:
#            klass = StackedRegressionTimeSeriesGraph
#            graph = klass(container_dict=dict(
##                                          bgcolor='lightgray',
#    #                                      padding=2,
#                                          padding_top=0,
#                                          padding_bottom=5,
#                                          padding_left=0,
#                                          padding_right=0,
#                                          stack_order='top_to_bottom'
#                                          ),
#                      equi_stack=True
#                      )
#        self.graph = graph
#
#        self.fits = dict()
#        cnt = 0
##        pxma = None
##        pxmi = None
#        for i, (k, f) in enumerate(keys + basekeys):
#            if new_plot:
#                graph.new_plot(
#                        padding=padding,
#                       pan=False,
#                       zoom=False,
#                       ytitle='{} (fA)'.format(k))
#
#                p = graph.plots[-1]
#
#                p.value_range.tight_bounds = False
#                p.value_range.margin = 0.1
#                p.index_range.tight_bounds = False
#                p.index_range.margin = 0.1
#
#            self.fits[k] = f
#
#            for group_id in group_ids:
#                data = [(a.timestamp,
#                                    self._get_series_value(a, k, i, group_id),
#                                    self._get_series_error(a, k, i, group_id),
#                                    ) for a in analyses if a.timestamp > 0 and a.group_id == group_id]
#
#                data = [di for di in data if di[1] is not None]
#                xs, ys, es = zip(*data)
#
#                self._add_series(graph, k, xs, ys, es, f, padding,
#                                 regress, group_id, plotid=cnt)
#                xma = max(xs)
#                xmi = min(xs)
#
#                if self.pxma:
#                    xma = max(self.pxma, xma)
#                    xmi = min(self.pxmi, xmi)
#
#                self.pxma = xma
#                self.pxmi = xmi
#            cnt += 1
#
#        for ri, f in ratiokeys:
##            ni,di=ri.split('/')
#            if new_plot:
#                graph.new_plot(
#                        padding=padding,
#                       pan=False,
#                       zoom=False,
#                       ytitle='{} (fA)'.format(ri))
#
#                p = graph.plots[-1]
#
#                p.value_range.tight_bounds = False
#                p.value_range.margin = 0.1
#                p.index_range.tight_bounds = False
#                p.index_range.margin = 0.1
#
#            self.fits[ri] = f
#
#            def get_ratio(rs, a):
#                n, d = rs.split('/')
#                signals = a.dbrecord.signals
#                un = ufloat((signals[n].value, signals[n].error))
#                ud = ufloat((signals[d].value, signals[d].error))
#                uv = un / ud
#                return a.timestamp, uv.nominal_value, uv.std_dev()
#
#
#            for group_id in group_ids:
#                data = [get_ratio(ri, a) for a in analyses if a.timestamp > 0 and a.group_id == group_id]
#
##                data = [(a.timestamp,
##                                    self._get_series_value(a, ni, i, group_id),
##                                    self._get_series_error(a, ni, i, group_id),
##                                    ) for a in analyses if a.timestamp > 0 and a.group_id == group_id]
#
#                data = [di for di in data if di[1] is not None]
#                xs, ys, es = zip(*data)
#
#                self._add_series(graph, ri, xs, ys, es, f, padding,
#                                 regress, group_id, plotid=cnt)
#                xma = max(xs)
#                xmi = min(xs)
#
#                if self.pxma:
#                    xma = max(self.pxma, xma)
#                    xmi = min(self.pxmi, xmi)
#
#                self.pxma = xma
#                self.pxmi = xmi
#            cnt += 1
#
#        if self.pxma and self.pxmi:
#            for pi in range(cnt):
##                print self.pxma, self.pxmi
#                graph.set_x_limits(min=self.pxmi, max=self.pxma, plotid=pi, pad='0.1')
##            print self.pxma, self.pxmi
##            graph.set_x_limits(min=self.pxmi, max=self.pxma, plotid=0, pad='0.1')
#
#        return graph
#
#    def _get_series_value(self, a, k, i, group_id):
#        return a.dbrecord.signals[k].value
#
#    def _get_series_error(self, a, k, i, group_id):
#        return a.dbrecord.signals[k].error
#
#    def _add_series(self, g, iso, xs, ys, es, fi, padding, regress, group_id, plotid=0):
#        color = self.colorgen.next()
#        marker_size = 2
#        if not regress:
#            fi = None
#            color = 'blue'
#            marker_size = 5
#
#        args = g.new_series(xs, ys,
#                     plotid=plotid,
#                     fit=fi,
#                     filter_outliers=False,
##                     regress=regress,
#                     type='scatter',
#                     marker='circle',
#                     color=color,
#                     marker_size=marker_size
#                     #color=self.colorgen.next(),
#                     #marker_size=2
#                     )
#
#        g.set_x_limits(min(xs), max(xs), pad='0.25', plotid=plotid)
#
#        g.set_axis_traits(tick_label_formatter=self.axis_formatter, plotid=plotid, axis='y')
#        plot = g.plots[plotid]
#        if regress:
#            scatter = args[1]
#        else:
#            scatter = plot.plots['plot{}'.format(args[0][-1])][0]
#
#        self._add_scatter_inspector(g.plotcontainer, plot, scatter, group_id, add_tool=False)
#        self._add_error_bars(scatter, es, 'y')
#
##        g.regress_plots()
#
#
##============= EOF =============================================
