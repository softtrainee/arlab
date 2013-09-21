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
from traits.api import Float, Array
#============= standard library imports ========================
from numpy import hstack, array
# from chaco.array_data_source import ArrayDataSource
#============= local library imports  ==========================

from src.processing.plotters.arar_figure import BaseArArFigure
from chaco.data_label import DataLabel

# from numpy.core.numeric import Inf
# from src.processing.plotters.point_move_tool import PointMoveTool
from src.helpers.formatting import floatfmt
from chaco.tools.data_label_tool import DataLabelTool

# from src.processing.plotters.plotter import mDataLabelTool
# from chaco.scatterplot import render_markers
N = 500




class Series(BaseArArFigure):
#     xmi = Float
#     xma = Float

    xs = Array


#     index_key = 'age'
#     ytitle = 'Relative Probability'
    def build(self, plots):
        graph = self.graph

        for po in plots:
            if po.use:
                p = graph.new_plot(padding=self.padding,
                                   ytitle=po.name
                                   )
                p.padding_left = 75
#                 p.value_range.tight_bounds = False
#             if po.use:
#                 p = graph.new_plot(padding=self.padding,
#                                    ytitle=po.name
#                                    )
#                 p.value_range.tight_bounds = False

    def plot(self, plots):
        '''
            plot data on plots
        '''
        graph = self.graph
        self.xs = array([ai.timestamp for ai in self.sorted_analyses]) / 3600.
        self.xs -= self.xs[0]

        plots = (po for po in plots if po.use)
        for i, po in enumerate(plots):
            self._plot_series(po, i)

#         self._plot_age_spectrum(graph.plots[0], 0)
#
#         for pid, (plotobj, po) in enumerate(zip(graph.plots, plots)):
#             getattr(self, '_plot_{}'.format(po.name))(po, plotobj, pid + 1)

    def _plot_series(self, po, pid):
        graph = self.graph
        ys = [ai.nominal_value for ai in self._unpack_attr(po.name)]

        graph.new_series(x=self.xs,
                         y=ys,
                         fit=po.fit,
                         plotid=pid,
                         type='scatter'
                        )
#         p.visible = fi.use

    def max_x(self, attr):
        return max([ai.nominal_value for ai in self._unpack_attr(attr)])

    def min_x(self, attr):
        return min([ai.nominal_value for ai in self._unpack_attr(attr)])

#===============================================================================
# plotters
#===============================================================================

#===============================================================================
# overlays
#===============================================================================

#===============================================================================
# utils
#===============================================================================

#===============================================================================
# labels
#===============================================================================

#============= EOF =============================================
