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
from traits.api import HasTraits, Instance
from traitsui.api import View, Item, Group, HGroup, HSplit, InstanceEditor
#============= standard library imports ========================
import numpy as np

#============= local library imports  ==========================
from src.viewable import Viewable
from src.database.selectors.isotope_selector import IsotopeAnalysisSelector
from src.graph.stacked_graph import StackedGraph
from chaco.tools.scatter_inspector import ScatterInspector
from chaco.abstract_overlay import AbstractOverlay


class RecallOverlay(AbstractOverlay):
    def overlay(self, component, gc, *args, **kw):

        gc.save_state()
        x = component.x
        y = component.y
        x2 = component.x2
        y2 = component.y2
        gc.set_fill_color((1, 1, 1))
        w = 100
        h = 110

        gc.rect(x + 5, y2 - 5 - h, w, h)
        gc.draw_path()

        machines = ['jan', 'obama', 'map']
        colors = [(0.5, 0, 1), (0, 0, 1), (1, 0, 0)]
        xo = x + 5
        yo = y2 - 10
        texth = 12
        for i, (mi, color) in enumerate(zip(machines, colors)):
            gc.set_fill_color(color)
            yi = yo - (texth) * (i + 1)
            gc.set_text_position(xo + 20, yi)
            gc.show_text(mi)

#        markers = ['circle', 'square', 'diamond', 'triangle']
        ats = ['blank', 'air', 'cocktail', 'unknown', 'background']
        gc.set_fill_color((0, 0, 0))
        for i, si in enumerate(ats):
            yy = yi - (texth) * (i + 1)
            plot = component.plots['jan {}'.format(si)][0]
            pcolor, plot.color = plot.color, 'black'
            mpcolor, plot.outline_color = plot.outline_color, 'black'
            plot._render_icon(gc, xo + 5, yy, 5, 5)
            plot.color = pcolor
            plot.outline_color = mpcolor
            gc.set_text_position(xo + 20, yy)
            gc.show_text(si)


        gc.restore_state()

class SelectionView(Viewable):
    table = Instance(IsotopeAnalysisSelector)
    graph = Instance(StackedGraph)
    def _graph_default(self):
        g = StackedGraph(container_dict=dict(padding=5))
        g.new_plot(
#                   show_legend='ul',
                   padding=5)

        ll = RecallOverlay(g.plots[0])
#        g.plotcontainer.overlays.append(ll)
        g.plots[0].overlays.append(ll)
        g.set_axis_traits(axis='y', visible=False)
        g.set_axis_traits(axis='x', visible=False)
        g.set_grid_traits(grid='x', visible=False)
        g.set_grid_traits(grid='y', visible=False)
        return g

    def build_graph(self):

        skw = dict(type='scatter', marker_size=3)
#            skw = dict(type='bar')
        g = self.graph
        xs = []
        ys = []
        ats = ['blank', 'air', 'cocktail', 'unknown', 'background']
        machines = ['jan', 'obama', 'map']
        for mach in machines:
            for i, at in enumerate(ats):
                xi = np.array([ri.timestamp for ri in self.table.results
                                if ri.analysis_type == at
                                    and ri.mass_spectrometer == mach])
                n = len(xi)
                xs.append(xi)
                ys.append(np.array(range(n)) + 1 + 5 * i)

        mm = [min(xj) for xj in xs if len(xj)]
        xmi = min(mm)
        mm = [max(yj) for yj in ys if len(yj)]
        yma = max(mm)

        xs = np.array([xk - xmi for xk in xs])
        ys = np.array(ys)
        mm = [max(xj) for xj in xs if len(xj)]
        xma = max(mm)

        colors = ['purple', 'blue', 'green']
        markers = ['circle', 'square', 'diamond', 'triangle', 'cross']

        def ffunc(s):
            def func(new):
                if new:
                    self._update_graph(s, xmi)
            return func

        for i, (name, color) in enumerate(zip(machines, colors)):
            xxj = xs[i * 5:i * 5 + 5]
            yyj = ys[i * 5:i * 5 + 5]
            for at, xx, yy, marker in zip(ats, xxj, yyj, markers):
                s, _ = g.new_series(xx, yy, marker=marker, color=color, **skw)
                g.set_series_label('{} {}'.format(name, at))
#                self.add_trait('scatter_{}_{}'.format(at, name), s)

                tool = ScatterInspector(s, selection_mode='single')
                s.tools.append(tool)

                s.index.on_trait_change(ffunc(s), 'metadata_changed')

#                s.index.on_trait_change(getattr(self, '_update_{}'.format(at)), 'metadata_changed')

        g.set_x_limits(min=0, max=xma, pad='0.1')
        g.set_y_limits(min=0, max=yma * 1.1)

    def _update_graph(self, scatter, xmi):
#        sel = scatter.index.metadata.get('selections')
        hover = scatter.index.metadata.get('hover')
        if hover:
            xs = scatter.index.get_data()

            ts = xs[hover] + xmi
            result = next((ri for ri in self.table.results
                           if abs(ri.timestamp - ts) < 1), None)

            self.table.selected = [result]

    def traits_view(self):
        tgrp = Item('table', show_label=False,
                    style='custom', width=0.3,
                    editor=InstanceEditor(view='panel_view')
                    )
        ggrp = Item('graph', show_label=False, style='custom', width=0.7)
        v = View(HSplit(tgrp,
                        ggrp),
                 width=1000,
                 height=500,
                 title='Recent Analyses',
                 resizable=True)
        return v
#============= EOF =============================================
