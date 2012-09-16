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
from src.graph.graph import Graph
from src.graph.time_series_graph import TimeSeriesGraph
from src.graph.regression_graph import RegressionGraph, \
    RegressionTimeSeriesGraph, StackedRegressionTimeSeriesGraph

#============= enthought library imports =======================
#from traits.api import HasTraits
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class Series(object):
    def axis_formatter(self, x):
        if x > 0.01:
            return '{:0.2f}'.format(x)
        elif abs(x) < 1e-7:
            return '{:n}'.format(x)
        else:
            return '{:0.2e}'.format(x)

    def build(self, analyses, keys, basekeys, padding):
        if isinstance(keys, str):
            keys = [keys]

#        isos = zip(*[[getattr(a, isoname.lower()) for isoname in a.isotope_names] for a in self.analyses])
#        n = len(a.isotope_names)
#        c = 3
#        r = n / c
#        if n % c:
#            r += 1

#        r = 1
#        c = 1
#        shape = r, c
        klass = StackedRegressionTimeSeriesGraph
#        klass = RegressionTimeSeriesGraph
#        klass = TimeSeriesGraph
        g = klass(container_dict=dict(
                                      bgcolor='lightgray',
#                                      padding=2,
                                      padding_top=0,
                                      padding_bottom=5,
                                      padding_left=0,
                                      padding_right=0,
#                                      spacing=0,
#                                      padding_left=20,
#                                      padding_right=0,
                                      stack_order='top_to_bottom'
#                                      kind='g',
#                                      shape=shape,
                                      ),
                  equi_stack=True
                  )
        cnt = 0
        for _, (key, fi) in enumerate(keys):
#        g = self._graph_factory((r, c))
#        for i, (ti, iso) in enumerate(zip(a.isotope_names, isos)):
            xs, ys = zip(*[(a.timestamp, a.signals[key].value) for a in analyses if a.timestamp > 0])

#        import random
#        xs = range(100)
#        ys = [random.random() for i in xs]

            self._add_series(g, key, xs, ys, fi, padding, plotid=cnt)
            cnt += 1


        for _, (key, fi) in enumerate(basekeys):
            try:
                xs, ys = zip(*[(a.timestamp, a.signals[key].value) for a in analyses if a.timestamp > 0])
                self._add_series(g, key, xs, ys, fi, padding, plotid=cnt)
                cnt += 1
            except KeyError, e:
                print e
        return g

    def _add_series(self, g, ti, xs, ys, fi, padding, plotid=0):

#        ti.replace('-baseline', 'bs')
#        print padding
        g.new_plot(padding_left=padding[0],
                   padding_right=padding[1],
                   padding_top=padding[2],
                   padding_bottom=padding[3],

#                   title=ti,
#                   padding_right=5,
#                   padding_top=20,
#                   padding_left=75,
#                   padding_bottom=50,
#                   xtitle='Time',
                   ytitle='{} (fA)'.format(ti))

#        n = len(iso)
#        x = range(n)
        g.new_series(xs, ys,
                     plotid=plotid,
                     fit_type=fi,
                     type='scatter', marker='circle', marker_size=1.25)

        g.set_y_limits(min(ys), max(ys), pad='0.1', plotid=plotid)
        g.set_x_limits(min(xs), max(xs), pad=1, plotid=plotid)

        g.set_axis_traits(tick_label_formatter=self.axis_formatter, plotid=plotid, axis='y')

#============= EOF =============================================
