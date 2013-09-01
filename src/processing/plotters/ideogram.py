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
from traits.api import Str, List, on_trait_change, Dict, Bool
# from chaco.api import ArrayDataSource
from chaco.data_label import DataLabel
#============= standard library imports ========================
from numpy import asarray, linspace, zeros, ones, pi, exp, max, min, Inf
# from chaco.ticks import DefaultTickGenerator
import time
#============= local library imports  ==========================
from src.processing.plotters.results_tabular_adapter import IdeoResultsAdapter
from src.processing.plotters.plotter import Plotter
from src.stats.core import calculate_weighted_mean
from src.stats.peak_detection import find_peaks
from src.processing.plotters.point_move_tool import PointMoveTool
from src.processing.plotters.sparse_ticks import SparseLogTicks, SparseTicks

N = 500


class Ideogram(Plotter):
    ages = None
    errors = None

#    ideogram_of_means = Bool
#    error_calc_method = Enum('SEM, but if MSWD>1 use SEM * sqrt(MSWD)', 'SEM')
#    ideogram_of_means = Bool(False)
#    error_bar_overlay = Any
#    graph = Any
#    selected_analysis = Any
#    analyses = Any

#    nsigma = Int(1, enter_set=True, auto_set=False)
#    nsigma = Range(1, 3, enter_set=True, auto_set=False)

#    plot_label_text = Property(depends_on='plotter_options.nsigma')

#    plot/_label = Any
    graphs = List

    probability_curve_kind = Str
    mean_calculation_kind = Str
    color_map_analysis_number = Bool(False)

    _prev_selection = Dict
#    graph_panel_info = Instance(GraphPanelInfo, ())



#    def build_results(self, display):
#        width = lambda x, w = 8:'{{:<{}s}}='.format(w).format(x)
# #        floatfmt = lambda x, w = 3:'{{:0.{}f}}'.format(w).format(x)
#        floatfmt = lambda x:'{:0.3f}'.format(x)
#        attr = lambda n, v:'{}{}'.format(width(n), floatfmt(v))
#
# #        display.add_text(' ')
# #        lines = []
#
# #        for ai, ei in zip(self.ages, self.errors):
#        for ri in self.results:
#            display.add_text(attr('age', ri.age))
#            display.add_text(attr('error', ri.error))
#    def _ideogram_of_means_changed(self):
# #        self.build()
# #        self.graph.redraw()
#        self.figure.refresh()

    def _get_font_args(self, font):
        if isinstance(font, str):
            f, s = font.split(' ')
        else:
            f, s = font.name, font.size
        return f, s

    def _build_xtitle(self, g, xtitle_font, xtick_font, age_unit='Ma'):
        f, s = self._get_font_args(xtitle_font)
#         f, s = xtitle_font.split(' ')
        g.set_x_title('Age ({})'.format(age_unit), font=f, size=int(s))
        g.set_axis_traits(axis='x',
#                          tick_label_font=xtick_font
                          )

    def _build_ytitle(self, g, ytitle_font, ytick_font, aux_plots, **kw):
        f, s = self._get_font_args(ytitle_font)
#         f, s = ytitle_font.split(' ')
        g.set_y_title('Relative Probability', font=f, size=int(s))
        for k, ap in enumerate(aux_plots):
            g.set_y_title(ap['ytitle'], plotid=k + 1, font=f, size=int(s))
            g.set_axis_traits(axis='y',
                              tick_label_font=ytick_font
                              )

    def _build_hook(self, g, analyses, aux_plots=None):
        g.analyses = analyses
        g.maxprob = None
        g.minprob = None

#         group_ids = list(set([a.group_id for a in analyses]))

        if not analyses:
            return

#        def get_ages_errors(group_id):
#
#            nages, nerrors = zip(*[(a.age.nominal_value, a.age.std_dev())
#                                   for a in analyses if a.group_id == group_id])
#            return array(nages), array(nerrors)

#        if self.ideogram_of_means:
#
#            ages, errors = zip(*[calculate_weighted_mean(*get_ages_errors(gi)) for gi in group_ids])
#            xmin, xmax = self._get_limits(ages)
#            self._add_ideo(g, ages, errors, xmin, xmax, padding, 0, len(analyses))
#
#        else:


        options = self.plotter_options
        ucr = options.use_centered_range
        if ucr:
            xmin, xmax = self._get_limits(analyses, centered_range=options.centered_range)
        else:
            xmin, xmax = options.xlow, options.xhigh

        if xmax == 0 and xmin == 0:
            xmin, xmax = self._get_limits(analyses)

        start = 1
        offset = 0

        from itertools import groupby

        key = lambda x: x.group_id
        groups = groupby(sorted(analyses, key=key), key)

        for group_id, analyses in groups:
            # buffer the analyses generator
            ans = [ai for ai in analyses]
            labnumber = self.get_labnumber(ans)
            nages, nerrors = self._get_ages(ans)

#         for group_id in group_ids:
#             ans = [a for a in analyses if a.group_id == group_id]
#             labnumber = self.get_labnumber(ans)
#             nages, nerrors = self._get_ages(analyses, group_id)
            offset = self._add_ideo(g, nages, nerrors, xmin, xmax, group_id,
                           start=start,
                           labnumber=labnumber,
                           offset=offset,
                           )

            aux_namespace = dict(nages=nages,
                                 nerrors=nerrors,
                                 start=start)

            for plotid, ap in enumerate(aux_plots):
                # get aux type and plot
                try:
                    func = getattr(self, '_aux_plot_{}'.format(ap['name']))
                    func(g, ans, plotid + 1, group_id, aux_namespace,
                         value_scale=ap['scale'],
                         x_error=ap['x_error'],
                         y_error=ap['y_error']
                         )
                except AttributeError, e:
                    print e

            # add analysis number plot
            start = start + len(ans) + 1

#        g.set_x_limits(min=xmin, max=xmax)

        self._set_y_limits(g)

        self._add_plot_metadata(g)

        return g

    def _make_sorted_pairs(self, attr, analyses, group_id):
        ages = self._get_ages(analyses, group_id, unzip=False)
        attrs = [getattr(a, attr) for a in analyses
                        if a.group_id == group_id]
        age_attr_pairs = zip(ages, attrs)
        age_attr_pairs = sorted(age_attr_pairs, key=lambda x:x[0])
        return zip(*age_attr_pairs)


    def _aux_plot_moles_K39(self, g, analyses, plotid, group_id, aux_namespace, **kw):
        ages, mk39 = self._make_sorted_pairs('moles_K39', analyses, group_id)

#        mk39, mk39_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in mk39])
        ages, age_errs = self._unzip_value_error(ages)
        mk39, mk39_errs = self._unzip_value_error(mk39)
        self._add_aux_plot(g, ages, mk39, age_errs, mk39_errs, group_id, plotid, **kw)

    def _aux_plot_radiogenic_percent(self, g, analyses, plotid, group_id, aux_namespace, **kw):
#        nages = aux_namespace['nages']
        ages, rads = self._make_sorted_pairs('rad40_percent', analyses, group_id)
        ages, age_errs = self._unzip_value_error(ages)
        rads, rad_errs = self._unzip_value_error(rads)
#        rads, rad_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in rads])
        self._add_aux_plot(g, ages, rads, age_errs, rad_errs,
                           group_id,
                           plotid=plotid, **kw
                           )

    def _aux_plot_kca(self, g, analyses, plotid, group_id, aux_namespace, **kw):
#        nages = aux_namespace['nages']
#        k39s = [a.k39 for a in analyses if a.group_id == group_id]
#        n = zip(nages, k39s)
#        n = sorted(n, key=lambda x:x[0])
#        aages, k39s = zip(*n)

        ages, kcas = self._make_sorted_pairs('kca', analyses, group_id)
        ages, age_errs = self._unzip_value_error(ages)
        kcas, kca_errs = self._unzip_value_error(kcas)
#        kcas, kca_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in kcas])
        self._add_aux_plot(g, ages, kcas, age_errs, kca_errs,
                           group_id,
                           plotid=plotid,
                           **kw
#                           value_scale=value_scale,
#                           x_error=x_error,
#                           y_error=y_error
                           )

    def _aux_plot_analysis_number(self, g, analyses, plotid, group_id, aux_namespace, **kw):
        nages = aux_namespace['nages']
        nerrors = aux_namespace['nerrors']
        start = aux_namespace['start']

        n = zip(nages, nerrors, analyses)
        aages, xerrs, analyses = zip(*sorted(n))
        maa = start + len(aages)
        age_ys = linspace(start, maa, len(aages))

#         tt = [ai.timestamp for ai in self.analyses]
        ts = [ai.timestamp for ai in analyses]
#        ts = array(ts)
#        ts-=min(ts)
#        ts/=((max(ts)-min(ts))*.75)
        if self.color_map_analysis_number:
            kw.update(dict(plot_type='cmap_scatter',
                           colors=ts,
                           color_map_name='gray',
                           marker_size=4,))

        self._add_aux_plot(g, aages, age_ys, xerrs, None, group_id,
                               value_format=lambda x: '{:d}'.format(int(x)),
                               additional_info=lambda x: x.age_string,
                               plotid=plotid,
                                **kw
                               )

    def _calculate_probability_curve(self, ages, errors, xmi, xma):
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
#        maxs, mins = find_peaks(y, 1, x)

        return x, y

    def _unmix_ages(self, ages, errors, xmi, xma):
        pass

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

    def _calculate_stats(self, ages, errors, xs, ys):
        mswd, valid_mswd, n = self._get_mswd(ages, errors)
#         mswd = calculate_mswd(ages, errors)
#         valid_mswd = validate_mswd(mswd, len(ages))

        if self.mean_calculation_kind == 'kernel':
            wm , we = 0, 0
            delta = 1
            maxs, _mins = find_peaks(ys, delta, xs)
            wm = max(maxs, axis=1)[0]
        else:
            wm, we = calculate_weighted_mean(ages, errors)
            we = self._calc_error(we, mswd)

        return wm, we, mswd, valid_mswd

    def _add_ideo(self, g, ages, errors, xmi, xma,
                   group_id, start=1,
                   labnumber=None,
                   offset=0,
                   ):

        ages = asarray(ages)
        errors = asarray(errors)
        bins, probs = self._calculate_probability_curve(ages, errors, xmi, xma)
        wm, we, mswd, valid_mswd = self._calculate_stats(ages, errors, bins, probs)

        minp = min(probs)
        maxp = max(probs)

        percentH = 1 - 0.954  # 2sigma
        s, _p = g.new_series(x=bins, y=probs, plotid=0)
        _s, _p = g.new_series(x=bins, y=probs,
                              plotid=0,
                              visible=False,
                              color=s.color,
                              line_style='dash',
                              )

        ym = maxp * percentH + offset
        s, p = g.new_series([wm], [ym],
                             type='scatter',
                             marker='circle',
                             marker_size=3,
                             color=s.color,
                             plotid=0
                             )

        display_mean_indicator = self._get_plot_option(self.options, 'display_mean_indicator', default=True)
        if not display_mean_indicator:
            s.visible = False

        label = None
        display_mean = self._get_plot_option(self.options, 'display_mean_text', default=True)
        if display_mean:
            text = self._build_label_text(wm, we, mswd, valid_mswd, ages.shape[0])
            font = self._get_plot_option(self.options, 'data_label_font', default='modern 12')
            self._add_data_label(s, text, (wm, ym),
#                                 font=font
                                 )
        # add a tool to move the mean age point
        s.tools.append(PointMoveTool(component=s,
                                     label=label,
                                     constrain='y'))

        d = lambda *args: self._update_bounds(g, s, group_id)
        p.index_mapper.on_trait_change(d, 'updated')

#        print group_id, we
        # we already scaled by nsigma
        self._add_error_bars(s, [we], 'x', 1)

        if g.minprob:
            minp = min([g.minprob, minp])

        if g.maxprob:
            maxp = max([g.maxprob, maxp])

        g.minprob = minp
        g.maxprob = maxp

        g.set_axis_traits(tick_visible=False,
                          tick_label_formatter=lambda x:'',
                          axis='y', plotid=0)

        return ym

    def _calc_error(self, we, mswd):
        ec = self.plotter_options.error_calc_method
        n = self.plotter_options.nsigma
        if ec == 'SEM':
            a = 1
        elif ec == 'SEM, but if MSWD>1 use SEM * sqrt(MSWD)':
            a = 1
            if mswd > 1:
                a = mswd ** 0.5
        return we * a * n

    def _add_aux_plot(self, g, ages, ys, xerrors, yerrors, group_id,
                      plotid=1,
                      value_format=None,
                      value_scale='linear',
                      x_error=False,
                      y_error=False,
                      additional_info=None,
                      plot_type='scatter',
                      **kw
                      ):

        g.set_grid_traits(visible=False, plotid=plotid)
        g.set_grid_traits(visible=False, grid='y', plotid=plotid)

        if not 'marker_size' in kw:
            kw['marker_size'] = 2

        scatter, p = g.new_series(ages, ys,
                                   type=plot_type, marker='circle',
#                                    marker_size=2,
                                   value_scale=value_scale,
#                                   selection_marker='circle',
                                   selection_marker_size=3,
                                   plotid=plotid,
                                   **kw
                                   )

        if xerrors and x_error:
            self._add_error_bars(scatter, xerrors, 'x', 1)

        if yerrors and y_error:
            self._add_error_bars(scatter, yerrors, 'y', 1)

        self._add_scatter_inspector(g.plotcontainer, p, scatter,
                                    group_id=group_id,
                                    value_format=value_format,
                                    additional_info=additional_info
                                    )

        d = lambda obj, name, old, new: self._update_metadata(g, scatter, group_id, obj, name, old, new)
        scatter.index.on_trait_change(d, 'metadata_changed')

        p = g.plots[plotid]

        if value_scale == 'log':
            pad = 0.1
            mi = min(ys)
            ma = max(ys)
            dev = ma - mi

            ma += dev * pad
            nmi = mi - dev * pad
            while nmi < 0:
                pad /= 2.0
                nmi = mi - dev * pad

            mi = nmi
            p.value_range.low_setting = mi
            p.value_range.high_setting = ma
            p.value_axis.tick_generator = SparseLogTicks()
        else:
            p.value_axis.tick_generator = SparseTicks()


#    def update_graph_metadata(self, obj, name, old, new):
# ##        print obj, name, old, new
#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]
#            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]

    def _cmp_analyses(self, x):
        return x.age.nominal_value

    def _update_metadata(self, g, scatter, group_id, obj, name, old, new):
        sel = obj.metadata.get('selections', None)
        if sel:
            obj.was_selected = True
            self._update_graph(g, scatter, group_id)
        elif hasattr(obj, 'was_selected'):
            if obj.was_selected:
                self._update_graph(g, scatter, group_id)
            obj.was_selected = False

    _last_bounds_update = None
    def _update_bounds(self, *args, **kw):
        # limit the update graph rate when only resizing
        # update only every 0.5s
        if not self._last_bounds_update or time.time() - self._last_bounds_update > 1:
            self._update_graph(*args, **kw)
#        else:
        self._last_bounds_update = time.time()

    def _update_graph(self, graph, scatter, group_id, bounds_only=False):
#         import inspect
#         stack = inspect.stack()
#         self.debug('update graph called by {}'.format(stack[1][3]))

        xmi, xma = graph.get_x_limits()
        ideo = graph.plots[0]
        sel = scatter.index.metadata['selections']
#        if self._prev_selection.has_key(scatter):
#            if self._prev_selection[scatter] == sel:
#                if not bounds_only:
#                    self.debug('skipping graph update')
#                    return

#        self._prev_selection[scatter] = sel

        lp = ideo.plots['plot{}'.format(group_id * 3)][0]
        dp = ideo.plots['plot{}'.format(group_id * 3 + 1)][0]
        sp = ideo.plots['plot{}'.format(group_id * 3 + 2)][0]

        ages_errors = self._get_ages(graph.analyses, group_id=group_id, unzip=False)
        ages_errors = sorted(ages_errors, key=lambda x: x.nominal_value)
        ages, errors = zip(*[(ai.nominal_value, ai.std_dev) for j, ai in enumerate(ages_errors)
                             if not j in sel])

        xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
        wm, we, mswd, valid_mswd = self._calculate_stats(ages, errors, xs, ys)

        lp.value.set_data(ys)
        lp.index.set_data(xs)
        sp.index.set_data([wm])
        sp.xerror.set_data([we])

        mi = min(ys)
        ma = max(ys)
        self._set_y_limits(graph, mi, ma)

        if not bounds_only:
            # update the data label position
            for ov in sp.overlays:
                if isinstance(ov, DataLabel):
                    _, y = ov.data_point
                    ov.data_point = wm, y
                    n = len(ages)
                    ov.label_text = self._build_label_text(wm, we, mswd, valid_mswd, n)

            if sel:
                dp.visible = True
                ages, errors = zip(*[(a.nominal_value, a.std_dev) for a in ages_errors])
                xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
                dp.value.set_data(ys)
                dp.index.set_data(xs)
            else:
    #                result.oage, result.oerror, result.omswd = None, None, None
                dp.visible = False



#        graph.redraw()

    def _set_y_limits(self, graph, ymin=None, ymax=None):
#        minp = min([0, mi])
        minp = 0
        if ymax is None:
            ymax = -Inf
        maxp = max([graph.maxprob, ymax])
#        graph.maxprob = maxp

        graph.set_y_limits(min_=minp, max_=maxp * 1.05, plotid=0)
#===============================================================================
# handlers
#==============================================================================
#    def _error_calc_method_changed(self):
#        for g in self.graphs:
#            self._update_graph(g)

    @on_trait_change('graph_panel_info:[ncols,nrows, padding_+]')
    def _graph_panel_info_changed(self, obj, name, new):
        if obj.ncols * obj.nrows <= self._ngroups:
            oc = self._plotcontainer
            np, nplots = self.build(padding=obj.padding)

            pc = self.figure.graph.plotcontainer
            ind = pc.components.index(oc)
            pc.remove(oc)
            pc.insert(ind, np)
            self.figure.graph.redraw()
            self._plotcontainer = np

    def _plot_label_text_changed(self):
        self.plot_label.text = self.plot_label_text
#===============================================================================
#
#===============================================================================
    def _get_adapter(self):
        return IdeoResultsAdapter

    def _get_limits(self, analyses, centered_range=None, pad=0.02):

        ages, errors = self._get_ages(analyses)
        ma_ages = ages + errors
        mi_ages = ages - errors

        xmin = min(mi_ages)
        xmax = max(ma_ages)
        dev = xmax - xmin
        if centered_range is None:
            xmin -= dev * pad
            xmax += dev * pad
        else:
            c = xmin + dev / 2.0
            xmin = c - centered_range / 2.0
            xmax = c + centered_range / 2.0

        return xmin, xmax

    def _get_metadata_label_text(self):
        # sigmas displayed as separate chars in Illustrator
        # use the 's' instead
        ustr = u'data 1s, age {}s'.format(self.plotter_options.nsigma)
#        ustr = u'data 1\u03c3, age {}\u03c3'.format(self.plotter_options.nsigma)
#        ustr = 'data 1s, age {}s'.format(self.nsigma)
        return ustr



#===============================================================================
# views
#===============================================================================
#    def _get_content(self):
#        g = Group(layout='tabbed')
#        r = super(Ideogram, self)._get_content()
#        g.content.append(r)
#        e = Item('graph_panel_info', show_label=False, style='custom')
#        g.content.append(e)
#        return g

#    def _get_toolbar(self):
#        return HGroup(
#                      Item('nsigma', style='custom'),
#                      Item('ideogram_of_means'),
#                      Item('error_calc_method', show_label=False),
#                      spring
#                      )
#    def traits_view(self):
#        v = View(HGroup(Item('nsigma'), spring),
#                 Item('results',
#                      style='custom',
#                      show_label=False,
#                      editor=TabularEditor(adapter=IdeoResultsAdapter())
#
#
#                      )
#
#                 )
#        return v

# class MultipleIdeogram(Ideogram):
#    def _build_ideo(self, g):
#        for i in range(3):
#            anals = [a for a in self.analyses if a.group_id == i]
#            ages, errors = zip(*[a.age for a in anals])
#            self._add_ideo(g, ages, errors)



#============= EOF =============================================
# g = StackedGraph(panel_height=200,
#                         equi_stack=False
#                         )
#
#        g.new_plot()
#        g.add_minor_xticks()
#        g.add_minor_xticks(placement='opposite')
#        g.add_minor_yticks()
#        g.add_minor_yticks(placement='opposite')
#        g.add_opposite_ticks()
#
#        g.set_x_title('Age (Ma)')
#        g.set_y_title('Relative Probability')
#
# #        ages, errors = zip(*[(ai.age, ai.age_err) for ai in self.analyses])
#        ages = self.ages
#        errors = self.errors
#        pad = 1
#        mi = min(ages) - pad
#        ma = max(ages) + pad
#        n = 500
#        bins = linspace(mi, ma, n)
#        probs = zeros(n)
#        g.set_x_limits(min=mi, max=ma)
#
#        ages = asarray(ages)
#        wm, we = weighted_mean(ages, errors)
#        self.age = wm
#        self.age_err = we
# #        print ages
# #        print errors
# #        print 'waieht', wm, we
#        for ai, ei in zip(ages, errors):
#            for j, bj in enumerate(bins):
#                #calculate the gaussian prob
#                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
#                #see http://en.wikipedia.org/wiki/Normal_distribution
#                delta = math.pow(ai - bj, 2)
#                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))
#
#                #cumulate probablities
#                probs[j] += prob
#
#        minp = min(probs)
#        maxp = max(probs)
#        g.set_y_limits(min=minp, max=maxp * 1.05)
#
#        g.new_series(x=bins, y=probs)
#
#        dp = maxp - minp
#
#        s, _p = g.new_series([wm], [maxp - 0.85 * dp], type='scatter', color='black')
#        s.underlays.append(ErrorBarOverlay(component=s))
#        nsigma = 2
#        s.xerror = ArrayDataSource([nsigma * we])
#
#        g.new_plot(bounds=[50, 100])
