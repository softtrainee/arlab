#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================
from traits.api import HasTraits, Instance, Any
from traitsui.api import View, Item
from src.graph.graph import Graph
from src.graph.error_bar_overlay import ErrorBarOverlay
#============= standard library imports ========================
from numpy import linspace, zeros, asarray
import math
from chaco.array_data_source import ArrayDataSource
from src.graph.stacked_graph import StackedGraph
from chaco.plot_factory import add_default_axes
from chaco.axis import PlotAxis

#============= local library imports  ==========================


class Demo(HasTraits):
    graph = Instance(Graph)

    def _weighted_mean(self, x, errs):
        x = asarray(x)
        errs = asarray(errs)

        weights = asarray(map(lambda e: 1 / e ** 2, errs))

        wtot = weights.sum()
        wmean = (weights * x).sum() / wtot
        werr = wtot ** -0.5

        return wmean, werr

    def _calc_mswd(self, x, errs):
        x = asarray(x)
        errs = asarray(errs)

        xmean_u = x.mean()
        xmean_w, _err = self._weighted_mean(x, errs)

        ssw = (x - xmean_w) ** 2 / errs ** 2
        ssu = (x - xmean_u) ** 2 / errs ** 2

        d = 1.0 / (len(x) - 1)
        mswd_w = d * ssw.sum()
        mswd_u = d * ssu.sum()

        return  mswd_u, mswd_w


    def _graph_default(self):
        g = StackedGraph(panel_height=200)


        ages = [10.11859, 9.93740, 10.00851]
        errors = [0.09866, 0.06795, 0.12444]

        ages = [27.95003, 28.08516, 28.11774, 28.00548]
        errors = [0.07020, 0.08275, 0.07922, 0.03871]

        g.new_plot()
        g.add_minor_xticks()
        g.add_minor_xticks(placement='opposite')
        g.add_minor_yticks()
        g.add_minor_yticks(placement='opposite')
        g.add_opposite_ticks()

        g.set_x_title('Age (Ma)')
        g.set_y_title('Relative Probability')


        mi = 9.7333
        ma = 10.4
        mi = 27.74096
        ma = 28.35406
        g.set_x_limits(min=mi, max=ma)

        n = 100
        bins = linspace(mi, ma, n)
        probs = zeros(n)

        ages = asarray(ages)
        wm, we = self._weighted_mean(ages, errors)
        for ai, ei in zip(ages, errors):
            for j, bj in enumerate(bins):
                #calculate the gaussian prob
                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
                #see http://en.wikipedia.org/wiki/Normal_distribution
                delta = math.pow(ai - bj, 2)
                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))

                #cumulate probablities
                probs[j] += prob

        g.set_y_limits(min=min(probs), max=max(probs) * 1.05)

        g.new_series(x=bins, y=probs)

        s, _p = g.new_series([wm], [1], type='scatter', color='black')
        s.underlays.append(ErrorBarOverlay(component=s))
        nsigma = 2
        s.xerror = ArrayDataSource([nsigma * we])

        g.new_plot(bounds=[50, 100])
        g.add_minor_xticks(plotid=1, placement='opposite')

        g.add_minor_yticks(plotid=1)
        g.add_minor_yticks(plotid=1, placement='opposite')

        g.add_opposite_ticks(plotid=1)

        g.set_y_title('Analysis #', plotid=1)
        g.set_axis_traits(orientation='right', plotid=1, axis='y')
        ages.sort()

        g.new_series(ages, range(1, len(ages) + 1, 1), type='scatter', marker='circle', plotid=1)
        g.set_y_limits(min=0, max=len(ages) + 1, plotid=1)

        return g



    def traits_view(self):
        v = View(Item('graph', show_label=False, style='custom',
                      width=665,
                      height=425),
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    Demo().configure_traits()

#============= EOF =====================================

