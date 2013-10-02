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
from chaco.plot_label import PlotLabel
from traits.api import Float, Array
from chaco.array_data_source import ArrayDataSource
from chaco.tools.broadcaster import BroadcasterTool
#============= standard library imports ========================
from numpy import linspace, pi, exp, zeros, ones, array, arange, \
    Inf
#============= local library imports  ==========================

from src.processing.plotters.arar_figure import BaseArArFigure
from src.graph.error_bar_overlay import ErrorBarOverlay

from src.graph.tools.rect_selection_tool import RectSelectionOverlay, \
    RectSelectionTool
from src.graph.tools.analysis_inspector import AnalysisPointInspector
from src.graph.tools.point_inspector import PointInspectorOverlay
from src.stats.peak_detection import find_peaks
from src.stats.core import calculate_weighted_mean
from src.processing.plotters.point_move_tool import PointMoveTool
from chaco.data_label import DataLabel

N = 500


class Ideogram(BaseArArFigure):
    xmi = Float
    xma = Float
    xs = Array
    xes = Array
    index_key = 'age'
    ytitle = 'Relative Probability'
    #     _reverse_sorted_analyses = True
    _analysis_number_cnt = 0

    x_grid_visible = False
    y_grid_visible = False

    def plot(self, plots):
        '''
            plot data on plots
        '''
        graph = self.graph
        self._analysis_number_cnt = 0

        self.xs, self.xes = array([[ai.nominal_value, ai.std_dev]
                                   for ai in self._get_xs(key=self.index_key)]).T

        self._plot_relative_probability(graph.plots[0], 0)

        omit = [i for i, ai in enumerate(self.sorted_analyses)
                if ai.temp_status]

        for pid, (plotobj, po) in enumerate(zip(graph.plots, plots)):
            scatter = getattr(self, '_plot_{}'.format(po.name))(po, plotobj, pid + 1,
            )
            if omit:
                scatter.index.metadata['selections'] = omit

        graph.set_x_limits(min_=self.xmi, max_=self.xma,
                           pad='0.1')

        ref = self.analyses[0]
        age_units = ref.arar_constants.age_units
        graph.set_x_title('Age ({})'.format(age_units))

        #turn off ticks for prob plot by default
        plot = graph.plots[0]
        plot.value_axis.tick_label_formatter = lambda x: ''
        plot.value_axis.tick_visible = False

        if omit:
            self._rebuild_ideo(omit)


    def max_x(self, attr):
        return max([ai.nominal_value for ai in self._unpack_attr(attr)])

    def min_x(self, attr):
        return min([ai.nominal_value for ai in self._unpack_attr(attr)])

    #===============================================================================
    # plotters
    #===============================================================================

    def _plot_aux(self, title, vk, ys, po, plot, pid, es=None):
        scatter = self._add_aux_plot(ys,
                                     title, pid)

        self._add_error_bars(scatter, self.xes, 'x', 1,
                             visible=po.x_error)
        if es:
            self._add_error_bars(scatter, es, 'y', 1,
                                 visible=po.y_error)

        self._add_scatter_inspector(scatter)
        return scatter

    def _plot_analysis_number(self, po, plot, pid):
        xs = self.xs
        n = xs.shape[0]

        startidx = 1
        for p in self.graph.plots:
            if p.y_axis.title == 'Analysis #':
                startidx += p.default_index.get_size()
            #                 print 'asdfasfsa', p.index.data.get_size()

        ys = arange(startidx, startidx + n)

        scatter = self._add_aux_plot(ys,
                                     'Analysis #', pid)

        self._add_error_bars(scatter, self.xes, 'x', 1,
                             visible=po.x_error)

        self._add_scatter_inspector(scatter,
                                    value_format=lambda x: '{:d}'.format(int(x)),
                                    additional_info=lambda x: u'Age= {}'.format(x.age_string),
        )

        #         self._analysis_number_cnt += n
        self.graph.set_y_limits(min_=0,
                                max_=max(ys) + 1,
                                plotid=pid)
        return scatter

    def _plot_relative_probability(self, plot, pid):
        graph = self.graph
        bins, probs = self._calculate_probability_curve(self.xs, self.xes)

        gid = self.group_id
        scatter, _p = graph.new_series(x=bins, y=probs, plotid=pid)
        graph.set_series_label('Current-{:03n}'.format(gid), series=0, plotid=pid)

        # add the dashed original line
        graph.new_series(x=bins, y=probs,
                         plotid=pid,
                         visible=False,
                         color=scatter.color,
                         line_style='dash',
        )
        graph.set_series_label('Original-{:03n}'.format(gid), series=1, plotid=pid)

        self._add_info(graph, plot)
        self._add_mean_indicator(graph, scatter, bins, probs, pid)
        mi, ma = min(probs), max(probs)
        self._set_y_limits(mi, ma, min_=0)

        d = lambda a, b, c, d: self.update_index_mapper(a, b, c, d)
        plot.index_mapper.on_trait_change(d, 'updated')

    #===============================================================================
    # overlays
    #===============================================================================
    def _add_info(self, g, plot):
        m = self.options.mean_calculation_kind
        e = self.options.error_calc_method
        pl = PlotLabel(text='Mean: {}\nError: {}'.format(m, e),
                       overlay_position='inside top',
                       hjustify='left',
                       component=plot,
        )
        plot.overlays.append(pl)

    def _add_mean_indicator(self, g, scatter, bins, probs, pid):
        offset = 0
        percentH = 1 - 0.954  # 2sigma

        maxp = max(probs)
        wm, we, mswd, valid_mswd = self._calculate_stats(self.xs, self.xes,
                                                         bins, probs)
        ym = maxp * percentH + offset

        s, p = g.new_series([wm], [ym],
                            type='scatter',
                            marker='circle',
                            marker_size=3,
                            color=scatter.color,
                            plotid=0
        )
        gid = self.group_id
        g.set_series_label('Mean-{:03n}'.format(gid), series=2, plotid=pid)

        self._add_error_bars(s, [we], 'x', self.options.nsigma)
        #         display_mean_indicator = self._get_plot_option(self.options, 'display_mean_indicator', default=True)
        if not self.options.display_mean_indicator:
            s.visible = False

        label = None
        #         display_mean = self._get_plot_option(self.options, 'display_mean_text', default=True)
        if self.options.display_mean:
            text = self._build_label_text(wm, we, mswd, valid_mswd, len(self.xs))
            #             font = self._get_plot_option(self.options, 'data_label_font', default='modern 12')
            self._add_data_label(s, text, (wm, ym),
                                 #                                 font=font
            )
            # add a tool to move the mean age point
        s.tools.append(PointMoveTool(component=s,
                                     label=label,
                                     constrain='y'))

    def update_index_mapper(self, obj, name, old, new):
        if new:
            self.update_graph_metadata(None, name, old, new)

    def update_graph_metadata(self, obj, name, old, new):
        sorted_ans = self.sorted_analyses
        if obj:
            hover = obj.metadata.get('hover')
            if hover:
                hoverid = hover[0]
                try:
                    self.selected_analysis = sorted_ans[hoverid]

                except IndexError, e:
                    print 'asaaaaa', e
                    return
            else:
                self.selected_analysis = None

            sel = obj.metadata.get('selections', [])

            if sel:
                obj.was_selected = True
                self._rebuild_ideo(sel)
            elif hasattr(obj, 'was_selected'):
                if obj.was_selected:
                    self._rebuild_ideo(sel)

                obj.was_selected = False

            # set the temp_status for all the analyses
            for i, a in enumerate(sorted_ans):
                a.temp_status = 1 if i in sel else 0
        else:
            sel = [i for i, a in enumerate(sorted_ans)
                   if a.temp_status]

            self._rebuild_ideo(sel)

    def _rebuild_ideo(self, sel):
        graph = self.graph
        plot = graph.plots[0]

        gid = self.group_id
        lp = plot.plots['Current-{:03n}'.format(gid)][0]
        dp = plot.plots['Original-{:03n}'.format(gid)][0]
        sp = plot.plots['Mean-{:03n}'.format(gid)][0]

        def f(a):
            i, _ = a
            return i not in sel

        d = zip(self.xs, self.xes)
        oxs, oxes = zip(*d)

        d = filter(f, enumerate(d))
        fxs, fxes = zip(*[(a, b) for _, (a, b) in d])

        xs, ys = self._calculate_probability_curve(fxs, fxes)
        wm, we, mswd, valid_mswd = self._calculate_stats(fxs, fxes, xs, ys)

        lp.value.set_data(ys)
        lp.index.set_data(xs)

        sp.index.set_data([wm])
        sp.xerror.set_data([we])

        mi = min(ys)
        ma = max(ys)
        self._set_y_limits(mi, ma, min_=0)

        # update the data label position
        for ov in sp.overlays:
            if isinstance(ov, DataLabel):
                _, y = ov.data_point
                ov.data_point = wm, y
                n = len(fxs)
                ov.label_text = self._build_label_text(wm, we, mswd, valid_mswd, n)

        if sel:
            dp.visible = True
            xs, ys = self._calculate_probability_curve(oxs, oxes)
            dp.value.set_data(ys)
            dp.index.set_data(xs)
        else:
            dp.visible = False

        #===============================================================================
        # utils
        #===============================================================================

    def _get_xs(self, key='age'):
        xs = array([ai for ai in self._unpack_attr(key)])
        return xs

    def _add_aux_plot(self, ys, title, pid, **kw):
        graph = self.graph
        graph.set_y_title(title,
                          plotid=pid)
        s, p = graph.new_series(
            x=self.xs, y=ys,
            type='scatter',
            marker='circle',
            marker_size=2,
            plotid=pid, **kw
        )

        graph.set_y_limits()

        return s

    def _calculate_probability_curve(self, ages, errors):

        xmi, xma = self.graph.get_x_limits()
        if xmi == -Inf or xma == Inf:
            xmi, xma = self.xmi, self.xma

        #        print self.probability_curve_kind
        if self.options.probability_curve_kind == 'kernel':
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

    def _cmp_analyses(self, x):
        return x.age

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


#============= EOF =============================================
