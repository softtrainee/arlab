#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Any, Instance, on_trait_change, Button, Float
from traitsui.api import View, UItem
# from src.envisage.tasks.base_editor import BaseTraitsEditor
# from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
from src.graph.graph import Graph
from src.regression.least_squares_regressor import LeastSquaresRegressor
#============= standard library imports ========================
import math
from numpy import average, asarray, cos, linspace, pi, array, max, min
import struct
from collections import namedtuple
from src.processing.tasks.analysis_edit.interpolation_editor import InterpolationEditor
from src.graph.error_bar_overlay import ErrorBarOverlay
from src.processing.argon_calculations import calculate_flux

#============= local library imports  ==========================
class FluxTool(HasTraits):
    calculate_button = Button('Calculate')
    monitor_age = Float
    def traits_view(self):
        v = View(
                 UItem('calculate_button')
                 )
        return v


Position = namedtuple('Positon', 'position x y')

class FluxEditor(InterpolationEditor):
    level = Any
    tool = Instance(FluxTool, ())

    def _rebuild_graph(self):
        g = self.graph
        if self._references:
            p = g.new_plot(xtitle='Hole Position (radians)',
                       ytitle='Flux',
                       padding=[70, 10, 10, 60]
                       )
            p.index_range.tight_bounds = False
            reg2D = self._model_flux()

            xs = reg2D.xs
            skw = dict(type='scatter', marker='circle', marker_size=2)
            scatter, _ = g.new_series(xs, reg2D.ys, yerror=reg2D.yserr,
                                 **skw)
            ebo = ErrorBarOverlay(component=scatter, orientation='y')
            scatter.overlays.append(ebo)
            self._add_inspector(scatter)

            # plot fit
            xs = linspace(min(xs), max(xs))

            ys = reg2D.predict(xs)
            g.new_series(xs, ys, color='black')

            es = reg2D.predict_error(xs, ys)

            g.new_series(xs, ys + es, color='red')
            g.new_series(xs, ys - es, color='red')

#            # plot predicted unknowns
            uxs = self._get_xs(self._unknowns)
            ys = reg2D.predict(uxs)
            es = reg2D.predict_error(uxs, ys)

            scatter, _ = g.new_series(uxs, ys, yerror=es, **skw)
            ebo = ErrorBarOverlay(component=scatter, orientation='y')
            scatter.overlays.append(ebo)
            self._add_inspector(scatter)

    def _add_inspector(self, scatter):
        from src.graph.tools.point_inspector import PointInspector
        from src.graph.tools.point_inspector import PointInspectorOverlay
        point_inspector = PointInspector(scatter)
        pinspector_overlay = PointInspectorOverlay(component=scatter,
                                                   tool=point_inspector
                                                   )
#
        scatter.overlays.append(pinspector_overlay)
        scatter.tools.append(point_inspector)

    def _model_flux(self):
        fitfunc = lambda p, x : p[0] * cos(p[1] * x + p[2]) + p[3] * x + p[4]

        x = self._get_xs(self._references)
#        x, y, e = zip(*[(ri.position, ri.labnumber.selected_flux_history.flux.j,
#                      ri.labnumber.selected_flux_history.flux.j_err)
#                      for ri in self._references])
        y, e = self._get_flux(self._references)
        reg2D = LeastSquaresRegressor(
                                    initial_guess=[1, 1, 1, 1, 1],
                                    fitfunc=fitfunc,
                                    xs=x, ys=y, yserr=e
                                    )
        reg2D.calculate()
        return reg2D

    def _get_flux(self, ans):
        y, e = zip(*[(ri.labnumber.selected_flux_history.flux.j,
                         ri.labnumber.selected_flux_history.flux.j_err)
                         for ri in ans])
        return y, e

    def _get_xs(self, ans):
        xy = self._get_xy(ans)
        return [math.atan2(x, y) for x, y in xy ]

    def _get_xy(self, ans):
        xx = []
        if self.level:
            geom = self.level.holder.geometry

            positions = [
                       Position(i, x, y)
                       for i, (x, y) in enumerate([struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)])
                       ]
            for ri in ans:
                pos = next((pi for pi in positions if pi.position + 1 == ri.position), None)
                if pos:
#                    print ri.position, pos.x, pos.y, math.atan2(pos.x, pos.y)
                    xx.append((pos.x, pos.y))
        return xx

    @on_trait_change('unknowns[]')
    def _update_unknowns(self):


        '''
            TODO: find reference analyses using the current _unknowns
        '''
        self._make_unknowns()
        self.rebuild_graph()

    def _make_unknowns(self):
        self._unknowns = self.unknowns

    def make_references(self):
        self._references = self.references

    def _graph_default(self):
        g = Graph()
        return g


#============= EOF =============================================
