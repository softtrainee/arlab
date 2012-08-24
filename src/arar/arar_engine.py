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
from traits.api import Instance, Any, Enum
from traitsui.api import View, Item, TreeEditor, TreeNode
from chaco.api import ArrayDataSource
#============= standard library imports ========================
import numpy as np
import math
import os
#============= local library imports  ==========================
from src.graph.graph import Graph
from src.graph.stacked_graph import StackedGraph
from src.paths import paths
from src.loggable import Loggable
from src.arar.workspace import Workspace
from src.arar.nodes import AnalysisNode, ExperimentNode
from src.graph.error_bar_overlay import ErrorBarOverlay

def weighted_mean(x, errs):
    x = np.asarray(x)
    errs = np.asarray(errs)

    weights = np.asarray(map(lambda e: 1 / e ** 2, errs))

    wtot = weights.sum()
    wmean = (weights * x).sum() / wtot
    werr = wtot ** -0.5
    return wmean, werr


class ArArEngine(Loggable):
    name = 'ArAr Engine'

    workspace = Instance(Workspace)
    graph = Instance(Graph)

    selected = Any
    cnt = 0

    experiment_kind = Enum('spectrum', 'ideo')
    def new_workspace(self, name=None):
        self.workspace = ws = Workspace()
        if name is not None:
            ws.name = name

        ws.root = os.path.join(paths.arar_dir, ws.name)
        ws.init()
        return ws


    def _replot_experiment(self, experiment):
        if self.experiment_kind == 'spectrum':
            self._replot_spectrum(experiment)
        else:
            self._replot_ideogram(experiment)

    def _replot_ideogram(self, exp):
        g = StackedGraph(panel_height=200,
                         equi_stack=False
                         )
        self.graph = g

        g.new_plot()
        g.add_minor_xticks()
        g.add_minor_xticks(placement='opposite')
        g.add_minor_yticks()
        g.add_minor_yticks(placement='opposite')
        g.add_opposite_ticks()

        g.set_x_title('Age (Ma)')
        g.set_y_title('Relative Probability')


        ages = [1.6, 2, 3, 1.4, 1, 2.8]
        errors = [1, 1, 1, 1, 1, 1]
        pad = 1
        mi = min(ages) - pad
        ma = max(ages) + pad
        n = 500
        bins = np.linspace(mi, ma, n)
        probs = np.zeros(n)
        g.set_x_limits(min=mi, max=ma)

        ages = np.asarray(ages)
        wm, we = weighted_mean(ages, errors)
#        print ages
#        print errors
#        print 'waieht', wm, we
        for ai, ei in zip(ages, errors):
            for j, bj in enumerate(bins):
                #calculate the gaussian prob
                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
                #see http://en.wikipedia.org/wiki/Normal_distribution
                delta = math.pow(ai - bj, 2)
                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))

                #cumulate probablities
                probs[j] += prob

        minp = min(probs)
        maxp = max(probs)
        g.set_y_limits(min=minp, max=maxp * 1.05)

        g.new_series(x=bins, y=probs)

        dp = maxp - minp

        s, _p = g.new_series([wm], [maxp - 0.85 * dp], type='scatter', color='black')
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

        n = zip(ages, errors)
#        ages.sort()
        n = sorted(n, key=lambda x:x[0])
        ages, errors = zip(*n)
#        print ages, errors
#        for ni in n:
#            print ni
        s, _p = g.new_series(ages, range(1, len(ages) + 1, 1), type='scatter', marker='circle', plotid=1)
        s.underlays.append(ErrorBarOverlay(component=s))
        s.xerror = ArrayDataSource(errors)

        g.set_y_limits(min=0, max=len(ages) + 1, plotid=1)


    def _replot_spectrum(self, exp):
        self.graph = g = StackedGraph(panel_height=200,
                         equi_stack=False
                         )

        g.new_plot()

        ar39s = [0, 0.1, 0.5, 1]
        ages = [10, 10.4, 20, 30]
        errors = [1, 1, 3, 2]

        xs = []
        ys = []
        es = []
        sar = sum(ar39s)
        prev = 0

        for ai, ei, ar in zip(ages, errors, ar39s):
#            print ai, ei
            xs.append(prev)
            ys.append(ai)
            es.append(ei)

            s = 100 * ar / sar

            xs.append(s)
            ys.append(ai)
            es.append(ei)
            prev = s

        ys.append(ai)
        es.append(ei)
        xs.append(100)

        #main age line
#        g.new_series(xs, ys)
        #error box
        ox = xs[:]
        xs.reverse()
        xp = ox + xs

        yu = [yi + ei for (yi, ei) in zip(ys, es)]

        yl = [yi - ei for (yi, ei) in zip(ys, es)]
        yl.reverse()

        yp = yu + yl
        g.new_series(x=xp, y=yp, type='polygon')
        g.set_y_limits(min=min(ys) * 0.95, max=max(ys) * 1.05)

    def _replot_analysis(self, analysis):
        n = len(analysis.isotope_names)
        r = 1
        c = 3
        if n % c:
            r = 2
        self.graph = self._graph_factory((r, c))
        g = self.graph

        def axis_formatter(x):
            if x > 0.01:
                return '{:0.2f}'.format(x)
            else:
                return '{:0.2e}'.format(x)

        for i, iso in enumerate(analysis.isotope_names):
            g.new_plot(title=iso,
                       padding_right=5,
                       padding_top=20,
                       padding_left=75,
                       padding_bottom=50,
                       xtitle='Time (s)',
                       ytitle='Signal (fA)'
#                       fill_padding=True,
#                       bgcolor='yellow'
                       )

            g.set_axis_traits(tick_label_formatter=axis_formatter, plotid=i, axis='y')
#            g.set_axis_traits(plotid=i, axis='y')
            x, y = analysis.iso_series[iso]
#            x = range(10)
#            y = [i * i for i in x]
            g.new_series(x, y, type='scatter', marker='circle', marker_size=0.75)

#===============================================================================
# handlers
#===============================================================================
    def _selected_changed(self):
        if isinstance(self.selected, AnalysisNode):
            self._replot_analysis(self.selected)
        elif isinstance(self.selected, ExperimentNode):
            self._replot_experiment(self.selected)


#===============================================================================
# factories
#===============================================================================
    def _graph_factory(self, shape):
        g = Graph(container_dict=dict(type='g',
                                      shape=shape,
                                      bgcolor='gray',
                                      padding=10
                                      ),
                  )
        return g
#===============================================================================
# defaults
#===============================================================================
    def _workspace_default(self):
        return Workspace()

    def _graph_default(self):
        return self._graph_factory((1, 1))
#===============================================================================
# views
#===============================================================================
    def configure_view(self):
        v = View(Item('experiment_kind', show_label=False))
        return v

    def graph_view(self):
        v = View(Item('graph',
                      show_label=False,
                      style='custom'))
        return v
    def traits_view(self):
        nodes = [
               TreeNode(
                        node_for=[Workspace],
                        label='name',
                        ),
               TreeNode(
                        node_for=[Workspace],
                        children='experiments',
                        label='=experiments',
                        auto_open=True,
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        label='name',
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        children='analyses',
                        label='=analyses',
                        auto_open=True,
                        ),
               TreeNode(
                        node_for=[ExperimentNode],
                        children='experiments',
                        label='=experiments',
                        auto_open=True,
                        ),
                TreeNode(node_for=[AnalysisNode],
                         label='rid',
                         )
               ]

        tree_editor = TreeEditor(nodes=nodes,
                                 editable=False,
                                 selected='selected',
                                 hide_root=True,
                                 lines_mode='on'
                                 )
        v = View(Item('workspace',
                      show_label=False,
                      height= -1.0,
                      editor=tree_editor
                      ),
                 width=500,
                 height=500,
                 resizable=True
                 )
        return v
if __name__ == '__main__':
    m = ArArEngine()
    m.workspace = Workspace()
    m.configure_traits()
#============= EOF =============================================
