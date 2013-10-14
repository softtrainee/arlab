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
from traits.api import Array
from chaco.plot_label import PlotLabel
from chaco.array_data_source import ArrayDataSource
#============= standard library imports ========================
from numpy import array, linspace, delete
#============= local library imports  ==========================
from src.codetools.simple_timeit import timethis

from src.helpers.formatting import calc_percent_error
from src.processing.argon_calculations import age_equation
from src.processing.plotters.arar_figure import BaseArArFigure

from src.stats.peak_detection import find_peaks
from src.stats.core import calculate_weighted_mean
from src.graph.error_ellipse_overlay import ErrorEllipseOverlay
from src.regression.new_york_regressor import ReedYorkRegressor

N = 500


class Isochron(BaseArArFigure):
    pass


class InverseIsochron(Isochron):
#     xmi = Float
#     xma = Float

    xs = Array
    _cached_data = None
    _plot_label = None

    def plot(self, plots):
        """
            plot data on plots
        """
        graph = self.graph

        self._plot_inverse_isochron(graph.plots[0], 0)

        for pid, (plotobj, po) in enumerate(zip(graph.plots, plots)):
            getattr(self, '_plot_{}'.format(po.name))(po, plotobj, pid + 1)

        omit = self._get_omitted(self.analyses)
        if omit:
            self._rebuild_iso(omit)

    def max_x(self, attr):
        return max([ai.nominal_value for ai in self._unpack_attr(attr)])

    def min_x(self, attr):
        return min([ai.nominal_value for ai in self._unpack_attr(attr)])

    #===============================================================================
    # plotters
    #===============================================================================
    def _plot_aux(self, title, vk, ys, po, plot, pid, es=None):
        scatter = self._add_aux_plot(ys, title, vk, pid)

    #         self._add_error_bars(scatter, self.xes, 'x', 1,
    #                              visible=po.x_error)
    #         if es:
    #             self._add_error_bars(scatter, es, 'y', 1,
    #                              visible=po.y_error)

    def _add_plot(self, xs, ys, es, plotid, value_scale='linear'):
        pass

    #def _get_analyses(self):
    #    ans=self.analyses
    #
    #    for a in ans:
    #        a.Ar40
    #       #timethis(lambda :a.Ar40)
    #
    #    return ans

    def _plot_inverse_isochron(self, plot, pid):
        analyses = self.analyses
        plot.padding_left = 75

        refiso = analyses[0]

        self._ref_j = refiso.j
        self._ref_age_scalar = refiso.arar_constants.age_scalar
        self._ref_age_units = refiso.arar_constants.age_units

        ans = [(a.Ar39, a.Ar36, a.Ar40) for a in analyses]
        #ans= timethis(self._get_analyses)
        #return

        a39, a36, a40 = array(ans).T
        try:
            xx = a39 / a40
            yy = a36 / a40
        except ZeroDivisionError:
            return

        xs, xerrs = zip(*[(xi.nominal_value, xi.std_dev) for xi in xx])
        ys, yerrs = zip(*[(yi.nominal_value, yi.std_dev) for yi in yy])

        self._cached_data = (xs, ys, xerrs, yerrs)

        graph = self.graph
        graph.set_x_title('39Ar/40Ar')
        graph.set_y_title('36Ar/40Ar')

        graph.set_grid_traits(visible=False)
        graph.set_grid_traits(visible=False, grid='y')

        scatter, _p = graph.new_series(xs, ys,
                                       xerror=ArrayDataSource(data=xerrs),
                                       yerror=ArrayDataSource(data=yerrs),
                                       type='scatter',
                                       marker='circle',
                                       marker_size=1)
        self._scatter = scatter

        eo = ErrorEllipseOverlay(component=scatter)
        scatter.overlays.append(eo)

        graph.set_x_limits(min_=min(xs), max_=max(xs), pad='0.1')

        reg = ReedYorkRegressor(xs=xs, ys=ys, xserr=xerrs, yserr=yerrs)
        reg.calculate()

        mi, ma = graph.get_x_limits()

        rxs = linspace(mi, ma)
        rys = reg.predict(rxs)

        graph.new_series(rxs, rys)
        graph.set_series_label('fit')

        self._add_scatter_inspector(scatter,
                                    # add_tool,
                                    # value_format,
                                    # additional_info
        )

        self._add_info(plot, reg)

    #===============================================================================
    # overlays
    #===============================================================================
    def _add_info(self, plot, reg, label=None):
        intercept = reg.predict(0)
        err = reg.get_intercept_error()
        try:
            inv_intercept = intercept ** -1
            p = calc_percent_error(inv_intercept, err)
            v = '{:0.2f}'.format(inv_intercept)
            e = '{:0.3f}'.format(err)

        except ZeroDivisionError:
            v, e, p = 'NaN', 'NaN', 'NaN'
        ratio_line = 'Ar40/Ar36= {} +/-{} ({}%)'.format(v, e, p)

        xt = reg.x_intercept

        j = self._ref_j
        s = self._ref_age_scalar
        u = self._ref_age_units

        age = age_equation(j, xt, scalar=s)
        v = age.nominal_value
        e = age.std_dev
        p = calc_percent_error(v, e)

        age_line = 'Age= {:0.3f} +/-{:0.4f} ({}%) {}'.format(v, e, p, u)
        if label is None:
            label = PlotLabel(
                component=plot,
                overlay_position='inside bottom',
                hjustify='left')
            plot.overlays.append(label)
            self._plot_label = label

        lines = '\n'.join((ratio_line, age_line))
        label.text = '{}\n\n'.format(lines)

    def update_index_mapper(self, obj, name, old, new):
        if new is True:
            self.update_graph_metadata(None, name, old, new)

    def _rebuild_iso(self, sel):
        #print 'rebuild iso',sel
        if self._cached_data:
            self._scatter.index.metadata['selections'] = sel

            xs, ys, xerr, yerr = self._cached_data

            nxs = delete(xs, sel)
            nys = delete(ys, sel)
            nxerr = delete(xerr, sel)
            nyerr = delete(yerr, sel)

            reg = ReedYorkRegressor(xs=nxs, ys=nys,
                                    xserr=nxerr, yserr=nyerr)
            reg.calculate()

            rxs = self.graph.get_data(series=1)
            #mi, ma = self.graph.get_x_limits()
            #rxs = linspace(mi, ma)
            rys = reg.predict(rxs)

            #self.graph.set_data(nxs,series=1, axis=0)
            self.graph.set_data(rys, series=1, axis=1)

            if self._plot_label:
                self._add_info(self.graph.plots[0], reg, label=self._plot_label)

    def update_graph_metadata(self, obj, name, old, new):
        if obj:
            self._filter_metadata_changes(obj, self._rebuild_iso, self.analyses)
            #self._set_selected(self.analyses, sel)

            #

        #===============================================================================
    # utils
    #===============================================================================
    def _get_age_errors(self, ans):
        ages, errors = zip(*[(ai.age.nominal_value,
                              ai.age.std_dev)
                             for ai in self.sorted_analyses])
        return array(ages), array(errors)

    def _add_aux_plot(self, ys, title, vk, pid, **kw):
        graph = self.graph
        graph.set_y_title(title,
                          plotid=pid)

        xs, ys, es, _ = self._calculate_spectrum(value_key=vk)
        s = self._add_plot(xs, ys, es, pid, **kw)
        return s

    def _calculate_stats(self, ages, errors, xs, ys):
        mswd, valid_mswd, n = self._get_mswd(ages, errors)
        #         mswd = calculate_mswd(ages, errors)
        #         valid_mswd = validate_mswd(mswd, len(ages))
        if self.options.mean_calculation_kind == 'kernel':
            wm, we = 0, 0
            delta = 1
            maxs, _mins = find_peaks(ys, delta, xs)
            wm = max(maxs, axis=1)[0]
        else:
            wm, we = calculate_weighted_mean(ages, errors)
            we = self._calc_error(we, mswd)

        return wm, we, mswd, valid_mswd

    def _calc_error(self, we, mswd):
        ec = self.options.error_calc_method
        n = self.options.nsigma
        if ec == 'SEM':
            a = 1
        elif ec == 'SEM, but if MSWD>1 use SEM * sqrt(MSWD)':
            a = 1
            if mswd > 1:
                a = mswd ** 0.5
        return we * a * n

#===============================================================================
# labels
#===============================================================================
#     def _build_integrated_age_label(self, tga, *args):
#         age, error = tga.nominal_value, tga.std_dev
#         error *= self.options.nsigma
#         txt = self._build_label_text(age, error, *args)
#         return 'Integrated Age= {}'.format(txt)

#============= EOF =============================================
