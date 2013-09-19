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
from numpy import linspace, pi, exp, zeros, ones, array, arange
from chaco.array_data_source import ArrayDataSource
#============= local library imports  ==========================

from src.processing.plotters.arar_figure import BaseArArFigure
from src.graph.error_bar_overlay import ErrorBarOverlay
N = 200


class Ideogram(BaseArArFigure):
    probability_curve_kind = 'weighted_mean'
    xmi = Float
    xma = Float
    xs = Array
    xes = Array
    index_key = 'age'
    ytitle = 'Relative Probability'

    def plot(self, graph, plots):
        '''
            plot data on plots
        '''
        self.xs, self.xes = array([[ai.nominal_value, ai.std_dev]
                         for ai in self._get_xs(key=self.index_key)]).T

        self._plot_relative_probability(graph, graph.plots[0], 0)

        for pid, (plotobj, po) in enumerate(zip(graph.plots, plots)):
            getattr(self, '_plot_{}'.format(po.name))(po, graph, plotobj, pid + 1)

    def max_x(self, attr):
        return max([ai.nominal_value for ai in self._unpack_attr(attr)])

    def min_x(self, attr):
        return min([ai.nominal_value for ai in self._unpack_attr(attr)])

#===============================================================================
# plotters
#===============================================================================
    def _plot_radiogenic_yield(self, po, graph, plot, pid):

        ys = list(self._unpack_attr('radiogenic_percent'))
        scatter = self._add_aux_plot(graph, ys, '%40Ar*', pid)

        self._add_error_bars(scatter, self.xes, 'x', 1,
                                   visible=po.x_error)

    def _plot_analysis_number(self, po, graph, plot, pid):
        xs = self.xs
        ys = arange(1, xs.shape[0] + 1)
        scatter = self._add_aux_plot(graph, ys,
                                     'Analysis #', pid)

        self._add_error_bars(scatter, self.xes, 'x', 1,
                             visible=po.x_error)

    def _plot_relative_probability(self, graph, plot, pid):

        bins, probs = self._calculate_probability_curve(self.xs, self.xes)

        s, _p = graph.new_series(x=bins, y=probs, plotid=pid)

        # add the dashed original line
        graph.new_series(x=bins, y=probs,
                              plotid=pid,
                              visible=False,
                              color=s.color,
                              line_style='dash',
                              )
#===============================================================================
# overlays
#===============================================================================
    def _add_error_bars(self, scatter, errors, axis, nsigma,
                        visible=True):
        ebo = ErrorBarOverlay(component=scatter,
                              orientation=axis,
                              nsigma=nsigma,
                              visible=visible)

        scatter.underlays.append(ebo)
        setattr(scatter, '{}error'.format(axis), ArrayDataSource(errors))
        return ebo

#===============================================================================
# utils
#===============================================================================
    def _unpack_attr(self, attr):
        return (getattr(ai, attr) for ai in self.analyses)

    def _get_xs(self, key='age'):
        xs = array([ai for ai in self._unpack_attr(key)])
        return xs

    def _add_aux_plot(self, graph, ys, title, pid, **kw):
        graph.set_y_title(title,
                          plotid=pid)
        s, p = graph.new_series(
                         x=self.xs, y=ys,
                         type='scatter',
                         marker='circle',
                         marker_size=2,
                         plotid=pid, **kw
                         )
        return s

    def _calculate_probability_curve(self, ages, errors):
        xmi, xma = self.xmi, self.xma
#        print self.probability_curve_kind
        if self.probability_curve_kind == 'kernel':
            return self._kernel_density(ages, errors, xmi, xma)

        else:
            return self._cumulative_probability(ages, errors, xmi, xma)

    def _kernel_density(self, ages, errors, xmi, xma):
        from scipy.stats.kde import gaussian_kde
        pdf = gaussian_kde(ages)
        x = linspace(xmi, xma, N)
        y = pdf(x)

        return x, y

    def _cumulative_probability(self, ages, errors, xmi, xma):
        bins = linspace(xmi, xma, N)
        probs = zeros(N)

        for ai, ei in zip(ages, errors):
            if abs(ai) < 1e-10 or abs(ei) < 1e-10:
                continue

            # calculate probability curve for ai+/-ei
            # p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
            # see http://en.wikipedia.org/wiki/Normal_distribution
            ds = (ones(N) * ai - bins) ** 2
            es = ones(N) * ei
            es2 = 2 * es * es
            gs = (es2 * pi) ** -0.5 * exp(-ds / es2)

            # cumulate probabilities
            # numpy element_wise addition
            probs += gs

        return bins, probs

#============= EOF =============================================
