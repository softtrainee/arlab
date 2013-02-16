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
from traitsui.api import View, Group
#============= standard library imports ========================
import numpy as np
import math
#============= local library imports  ==========================

from src.helpers.traitsui_shortcuts import instance_item
from src.graph.graph import Graph
from src.graph.error_bar_overlay import ErrorBarOverlay
from chaco.array_data_source import ArrayDataSource
from matplotlib.figure import Figure
from src.graph.mpl_editor import MPLFigureEditor
from matplotlib.cm import coolwarm


class FluxView(HasTraits):
    flux_2D = Instance(Graph)
    flux_3D = Instance(Figure, ())
    def replot(self, monitors, unknowns, regressor2D, regressor3D):

        self.replot2D(monitors, unknowns, regressor2D)
        self.replot3D(monitors, unknowns, regressor3D)

    def replot3D(self, monitors, unknowns, regressor):
        from mpl_toolkits.mplot3d import Axes3D

        fig = self.flux_3D
        ax = fig.gca(projection='3d')

        mx, my, mys, mye = zip(*[(pi.x, pi.y, pi.pred_j, pi.pred_j_err)
                                  for pi in monitors])
        x, y, ys, ye = zip(*[(pi.x, pi.y, pi.pred_j, pi.pred_j_err)
                             for pi in unknowns])

        x = np.array(x)
        y = np.array(y)

        ys = np.array(ys)
        mys = np.array(mys)

        w = max(x) - min(x)
        w = w * 1.25
        c = len(x)
        r = len(y)
        n = r * 2 - 1

        xx, yy = np.mgrid[0:n + 1, 0:n + 1]
        xx = xx / float(n) * w - w / 2.
        yy = yy / float(n) * w - w / 2.

        z = np.zeros((r * 2, c * 2))

        for i in range(r * 2):
            for j in range(c * 2):
                pt = (xx[i, j],
                      yy[i, j])
                v, _ = regressor.predict([pt])[0]
                z[i, j] = v

        ax.plot_surface(xx, yy, z, alpha=0.3,
                        rstride=1, cstride=1,
                        cmap=coolwarm,
                        linewidths=0
                        )

        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (%change)')
        self.flux_3D.canvas.draw()

    def replot2D(self, monitors, unknowns, regressor):
        g = self.flux_2D
        g.clear()
        g.new_plot()
        self._plot(g, monitors, use_predicted_value=False)

        self._plot(g, unknowns)
        if regressor:
            low, high = g.get_x_limits()
            fx = np.linspace(low, high, 200)
            fy = regressor.predict(fx)
            g.new_series(fx, fy, color='black')

            ly, uy = regressor.calculate_ci(fx)
            g.new_series(fx, ly, color='red', line_style='dash')
            g.new_series(fx, uy, color='red', line_style='dash')

    def _plot(self, graph, positions, use_predicted_value=True):
        xs = []
        ys = []
        es = []
        for pi in positions:
            if pi.pred_j:
#                #convert pi.x,pi.y to radians
                r = math.atan2(pi.x, pi.y)
                xs.append(r)
                if use_predicted_value:
                    ys.append(pi.pred_j)
                    es.append(pi.pred_j_err)
                else:
                    ys.append(pi.j)
                    es.append(pi.j_err)

        s, _ = graph.new_series(xs, ys, yerror=ArrayDataSource(data=es),
                                type='scatter', marker='circle', marker_size=2)
        ebo = ErrorBarOverlay(component=s, orientation='y')
        s.overlays.append(ebo)

        s.index_range.tight_bounds = False
        s.value_range.tight_bounds = False

    def traits_view(self):
        v = View(Group(
                       Group(instance_item('flux_2D'),
                             label='2D'
                             ),
                       Group(instance_item('flux_3D', editor=MPLFigureEditor()),
                             label='3D'
                             ),
                       layout='tabbed'
                       )

                 )
        return v

    def _flux_2D_default(self):
#        g = RegressionGraph(container_dict=dict(padding=5))
        g = Graph(container_dict=dict(padding=5))
        return g
#============= EOF =============================================
