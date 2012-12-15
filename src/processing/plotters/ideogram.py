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
from traits.api import HasTraits, Instance, Any, Int, Str, Float, List, Range, Property, Bool, \
    Enum, on_trait_change
from traitsui.api import View, Item, HGroup, spring, Group, VGroup, EnumEditor
#from chaco.api import ArrayDataSource
#============= standard library imports ========================
from numpy import asarray, linspace, zeros, array, ones, pi, exp, hstack, max
from chaco.data_label import DataLabel
from chaco.tools.data_label_tool import DataLabelTool
from chaco.ticks import AbstractTickGenerator, DefaultTickGenerator
#============= local library imports  ==========================

#from src.graph.stacked_graph import StackedGraph
#from src.graph.error_bar_overlay import ErrorBarOverlay
from src.processing.plotters.results_tabular_adapter import IdeoResults, \
    IdeoResultsAdapter
from src.processing.plotters.plotter import Plotter
from src.stats.core import calculate_weighted_mean, calculate_mswd
from src.stats.peak_detection import find_peaks
#from src.processing.figure import AgeResult

#def weighted_mean(x, errs):
#    x = asarray(x)
#    errs = asarray(errs)
#
#    weights = asarray(map(lambda e: 1 / e ** 2, errs))
#
#    wtot = weights.sum()
#    wmean = (weights * x).sum() / wtot
#    werr = wtot ** -0.5
#    return wmean, werr
#class mStackedGraph(IsotopeContextMenuMixin, StackedGraph):
#    pass

N = 700

class SparseTicks(DefaultTickGenerator):
    step = Int(2)
    def get_ticks(self, *args, **kw):
        ticks = super(SparseTicks, self).get_ticks(*args, **kw)
        s = self.step
        try:
            if len(ticks) > s + 2:
                nticks = hstack((ticks[0], ticks[s:-s:s], ticks[-1]))
                return nticks
            else:
                return ticks
        except IndexError:
            return ticks


class Ideogram(Plotter):
    ages = None
    errors = None

    ideogram_of_means = Bool
    error_calc_method = Enum('SEM, but if MSWD>1 use SEM * sqrt(MSWD)', 'SEM')
#    ideogram_of_means = Bool(False)
#    error_bar_overlay = Any
#    graph = Any
#    selected_analysis = Any
#    analyses = Any

#    nsigma = Int(1, enter_set=True, auto_set=False)
    nsigma = Range(1, 3, enter_set=True, auto_set=False)

    plot_label_text = Property(depends_on='nsigma')
    plot_label = Any
    graphs = List

    probability_curve_kind = Str
    mean_calculation_kind = Str
#    graph_panel_info = Instance(GraphPanelInfo, ())



#    def build_results(self, display):
#        width = lambda x, w = 8:'{{:<{}s}}='.format(w).format(x)
##        floatfmt = lambda x, w = 3:'{{:0.{}f}}'.format(w).format(x)
#        floatfmt = lambda x:'{:0.3f}'.format(x)
#        attr = lambda n, v:'{}{}'.format(width(n), floatfmt(v))
#
##        display.add_text(' ')
##        lines = []
#
##        for ai, ei in zip(self.ages, self.errors):
#        for ri in self.results:
#            display.add_text(attr('age', ri.age))
#            display.add_text(attr('error', ri.error))
#    def _ideogram_of_means_changed(self):
##        self.build()
##        self.graph.redraw()
#        self.figure.refresh()
    def set_excluded_points(self, exclude, group_id, graph_id=0):
        if not exclude:
            return

        graph = self.graphs[graph_id]

        try:
            plot = graph.plots[1].plots['plot{}'.format(group_id)][0]
            plot.index.metadata['selections'] = exclude
        except IndexError:
            pass

    def _build_xtitle(self, g, xtitle_font, xtick_font):
        f, s = xtitle_font.split(' ')
        g.set_x_title('Age (Ma)', font=f, size=int(s))
        g.set_axis_traits(axis='x', tick_label_font=xtick_font)

    def _build_ytitle(self, g, ytitle_font, ytick_font, aux_plots):
        f, s = ytitle_font.split(' ')
        g.set_y_title('Relative Probability', font=f, size=int(s))
        for k, ap in enumerate(aux_plots):
            g.set_y_title(ap['ytitle'], plotid=k + 1, font=f, size=int(s))
            g.set_axis_traits(axis='y', tick_label_font=ytick_font)

    def _get_grouped_analyses(self):
        analyses = self.analyses
        group_ids = list(set([a.group_id for a in analyses]))

        return [[ai for ai in analyses if ai.group_id == gid]
                for gid in group_ids
                ]

    def _build_hook(self, g, analyses, padding, aux_plots=None):
        g.analyses = analyses
        g.maxprob = None
        g.minprob = None

        group_ids = list(set([a.group_id for a in analyses]))

        if not analyses:
            return

        ages, errors = self._get_ages(analyses)
        def get_ages_errors(group_id):
#            nages = [a.age[0] for a in analyses if a.group_id == group_id]
#            nerrors = [a.age[1] for a in analyses if a.group_id == group_id]

            nages, nerrors = zip(*[(a.age.nominal_value, a.age.std_dev()) for a in analyses if a.group_id == group_id])
            aa = array(nages)
            ee = array(nerrors)
            return aa, ee

        if self.ideogram_of_means:

            ages, errors = zip(*[calculate_weighted_mean(*get_ages_errors(gi)) for gi in group_ids])
            xmin, xmax = self._get_limits(ages)
            self._add_ideo(g, ages, errors, xmin, xmax, padding, 0, len(analyses))

        else:
            xmin, xmax = self._get_limits(ages)
            start = 1
            offset = 0
            for group_id in group_ids:
                ans = [a for a in analyses if a.group_id == group_id]
                labnumber = self.get_labnumber(ans)
                nages, nerrors = get_ages_errors(group_id)
                offset = self._add_ideo(g, nages, nerrors, xmin, xmax, padding, group_id,
                               start=start,
                               labnumber=labnumber,
                               offset=offset,
                               )

                aux_namespace = dict(nages=nages,
                                     nerrors=nerrors,
                                     start=start)

                for plotid, ap in enumerate(aux_plots):
                    #get aux type and plot
                    try:
                        func = getattr(self, '_aux_plot_{}'.format(ap['func']))
                        func(analyses, g, padding, plotid + 1, group_id, aux_namespace,
                             value_scale=ap['scale']
                             )
                    except AttributeError, e:
                        print e

                #add analysis number plot
                start = start + len(ans) + 1

#            maxp = g.maxprob

#            step = maxp / len(group_ids)
#            print step
#            step = 1
#            #tweak age labels
#            for i, (k, v) in enumerate(g.plots[0].plots.iteritems()):
#                print k, v[0]
#
#                kk = int(k[-1]) + 1
#                if not kk % 3:
##                if k in ['plot2', 'plot5', ]:
#                    v[0].value.set_data([(i + 1) * step])



        g.set_x_limits(min=xmin, max=xmax, pad='0.2', plotid=0)
        for i, _ in enumerate(aux_plots):
            g.set_x_limits(min=xmin, max=xmax, pad='0.2', plotid=i + 1)

        minp = 0
        maxp = g.maxprob
        g.set_y_limits(min=minp, max=maxp * 1.05, plotid=0)

        #add meta plot info
        font = self._get_plot_option(self.options, 'metadata_label_font', default='modern 10')
        self.plot_label = g.add_plot_label(self.plot_label_text, 0, 0, font=font)

        return g

    def _aux_plot_radiogenic_percent(self, analyses, g, padding, plotid, group_id, aux_namespace,
                                     value_scale='linear'
                                     ):
        nages = aux_namespace['nages']
        rads = [a.rad40_percent for a in analyses if a.group_id == group_id]

        n = zip(nages, rads)
        n = sorted(n, key=lambda x:x[0])
        aages, rads = zip(*n)
        rads, rad_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in rads])
        self._add_aux_plot(g, aages,
                           rads,
                           None,
                           rad_errs,
                           padding,
                           group_id,
                           plotid=plotid,
                           value_scale=value_scale
                           )

    def _aux_plot_kca(self, analyses, g, padding, plotid, group_id, aux_namespace,
                      value_scale='linear'):
        nages = aux_namespace['nages']
        k39s = [a.k39 for a in analyses if a.group_id == group_id]
        n = zip(nages, k39s)
        n = sorted(n, key=lambda x:x[0])
        aages, k39s = zip(*n)

        k39, k39_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in k39s])
        self._add_aux_plot(g, aages,
                           k39,
                           None,
                           k39_errs,
                           padding,
                           group_id,
                           plotid=plotid,
                           value_scale=value_scale
                           )



    def _aux_plot_analysis_number(self, analyses, g, padding, plotid, group_id, aux_namespace,
                                  value_scale='linear'):
        nages = aux_namespace['nages']
        nerrors = aux_namespace['nerrors']
        start = aux_namespace['start']

        n = zip(nages, nerrors)
        n = sorted(n, key=lambda x:x[0])
        aages, xerrs = zip(*n)
        maa = start + len(aages)
        age_ys = linspace(start, maa, len(aages))
        self._add_aux_plot(g, aages, age_ys, xerrs, None, padding, group_id,
                               value_format=lambda x: '{:d}'.format(int(x)),
                               plotid=plotid,
                               value_scale=value_scale
                               )
        g.set_axis_traits(tick_visible=False,
          tick_label_formatter=lambda x:'',
          axis='y', plotid=1)

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

    def _cumulative_probability(self, ages, errors, xmi, xma):
        bins = linspace(xmi, xma, N)
        probs = zeros(N)

        for ai, ei in zip(ages, errors):
            if abs(ai) < 1e-10 or abs(ei) < 1e-10:
                continue

            #calculate probability curve for ai+/-ei
            #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
            #see http://en.wikipedia.org/wiki/Normal_distribution
            ds = (ones(N) * ai - bins) ** 2
            es = ones(N) * ei
            es2 = 2 * es * es
            gs = (es2 * pi) ** -0.5 * exp(-ds / es2)

            #cumulate probabilities
            #numpy element_wise addition
            probs += gs

        return bins, probs

    def _calculate_stats(self, ages, errors, xs, ys):
        mswd = calculate_mswd(ages, errors)
        if self.mean_calculation_kind == 'kernel':
            wm , we = 0, 0
            delta = 1
            maxs, mins = find_peaks(ys, delta, xs)
            wm = max(maxs, axis=1)[0]
        else:
            wm, we = calculate_weighted_mean(ages, errors)
            we = self._calc_error(we, mswd)
        return wm, we, mswd

    def _add_ideo(self, g, ages, errors, xmi, xma, padding,
                   group_id, start=1,
                   labnumber=None,
                   offset=0,
                   ):

        ages = asarray(ages)
        errors = asarray(errors)
        bins, probs = self._calculate_probability_curve(ages, errors, xmi, xma)
        wm, we, mswd = self._calculate_stats(ages, errors, bins, probs)

        self.results.append(IdeoResults(
                                        labnumber=labnumber,
                                        age=wm,
                                        mswd=mswd,
                                        error=we,
                                        error_calc_method=self.error_calc_method
                                        ))
        minp = min(probs)
        maxp = max(probs)

        percentH = 1 - 0.954 #2sigma
        s, _p = g.new_series(x=bins, y=probs, plotid=0)
        _s, _p = g.new_series(x=bins, y=probs,
                              plotid=0,
                              visible=False,
                              color=s.color,
                              line_style='dash',
                              )

        ym = maxp * percentH + offset
        s, _p = g.new_series([wm], [ym],
                             type='scatter',
                             marker='circle',
                             marker_size=3,
                             color=s.color,
                             plotid=0
                             )
        display_mean_indicator = self._get_plot_option(self.options, 'display_mean_indicator', default=True)
        if not display_mean_indicator:
            s.visible = False

        display_mean = self._get_plot_option(self.options, 'display_mean_text', default=True)
        if display_mean:
            text = self._build_label_text(wm, ym, we, mswd, ages.shape[0])
            font = self._get_plot_option(self.options, 'data_label_font', default='modern 12')
            self._add_data_label(s, text, (wm, ym),
                                 font=font
                                 )

        d = lambda *args: self._update_graph(g, *args)
        s.index_mapper.on_trait_change(d, 'updated')

        self._add_error_bars(s, [we], 'x', sigma_trait='nsigma')

        if g.minprob:
            minp = min(g.minprob, minp)

        if g.maxprob:
            maxp = max(g.maxprob, maxp)

        g.minprob = minp
        g.maxprob = maxp

        g.set_axis_traits(tick_visible=False,
                          tick_label_formatter=lambda x:'',
                          axis='y', plotid=0)

#        if g.analyses:
        #set the color
#        for a in g.analyses:
#            a.color = s.color

        return ym * 2.5

#    def _add_data_label(self, s, args):
#        wm, ym, we, mswd, n = args
#        label_text = self._build_label_text(*args)
#        label = DataLabel(component=s, data_point=(wm, ym),
#                          label_position='top right',
#                          label_text=label_text,
#                          border_visible=False,
#                          bgcolor='transparent',
#                          show_label_coords=False,
#                          marker_visible=False,
#                          text_color=s.color,
#                          arrow_color=s.color,
#                          )
#        s.overlays.append(label)
#        tool = DataLabelTool(label)
#        label.tools.append(tool)


    def _build_label_text(self, x, y, we, mswd, n):
        display_n = True
        display_mswd = True
        if display_n:
            n = 'n= {}'.format(n)
        else:
            n = ''

        if display_mswd:
            mswd = 'mswd= {:0.2f}'.format(mswd)
        else:
            mswd = ''

        return u'{:0.3f} \u00b1{:0.3f} {} {}'.format(x, we, mswd, n)

    def _calc_error(self, we, mswd):
        ec = self.error_calc_method
        if ec == 'SEM':
            a = 1
        elif ec == 'SEM, but if MSWD>1 use SEM * sqrt(MSWD)':
            a = 1
            if mswd > 1:
                a = mswd ** 0.5
        return we * a

    def _add_aux_plot(self, g, ages, ys, xerrors, yerrors, padding, group_id,
                      plotid=1,
                      value_format=None,
                      value_scale='linear'
                      ):

        g.set_grid_traits(visible=False, plotid=plotid)
        g.set_grid_traits(visible=False, grid='y', plotid=plotid)

        scatter, p = g.new_series(ages, ys,
                                   type='scatter', marker='circle',
                                   marker_size=2,
                                   value_scale=value_scale,
#                                   selection_marker='circle',
                                   selection_marker_size=3,
                                   plotid=plotid)
        if xerrors:
            self._add_error_bars(scatter, xerrors, 'x')

        if yerrors:
            self._add_error_bars(scatter, yerrors, 'y')

        self._add_scatter_inspector(g.plotcontainer, p, scatter,
                                    group_id=group_id,
                                    value_format=value_format
                                    )

        d = lambda *args: self._update_graph(g, *args)
        scatter.index.on_trait_change(d, 'metadata_changed')

        #use sparse ticks
        p = g.plots[plotid]
        p.value_axis.tick_generator = SparseTicks()

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


#    def update_graph_metadata(self, obj, name, old, new):
###        print obj, name, old, new
#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]
#            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]

    def _cmp_analyses(self, x):
        return x.age.nominal_value

    def _update_graph(self, g):
        xmi, xma = g.get_x_limits()
        ideo = g.plots[0]

        sels = dict()
        for pp in g.plots[1:]:
#            si = []
            for i, p in enumerate(pp.plots.itervalues()):
                ss = p[0].index.metadata['selections']

                if i in sels:
                    sels[i] = list(set(ss + sels[i]))
                else:
                    sels[i] = ss

        ideoplots = filter(lambda a:a[0] % 3 == 0, enumerate(g.plots[0].plots.iteritems()))
        for i, p in enumerate(ideoplots):
#            if not i in sels:
#                continue
            try:
                sel = sels[i]
            except KeyError:
                sel = []

            result = self.results[i]

            lp = ideo.plots['plot{}'.format(i * 3)][0]
            dp = ideo.plots['plot{}'.format(i * 3 + 1)][0]
            sp = ideo.plots['plot{}'.format(i * 3 + 2)][0]

            try:
                ages_errors = sorted([a.age for a in g.analyses if a.group_id == i],
                                     key=lambda x: x.nominal_value)
                ages, errors = zip(*[(ai.nominal_value, ai.std_dev()) for j, ai in enumerate(ages_errors) if not j in sel])

                xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
                wm, we, mswd = self._calculate_stats(ages, errors, xs, ys)

                result.age = wm
                result.error = we
                result.mswd = mswd
                result.error_calc_method = self.error_calc_method
            except ValueError:
                wm, we = 0, 0
                ys = zeros(N)

            lp.value.set_data(ys)
            lp.index.set_data(xs)
            sp.index.set_data([wm])
            sp.xerror.set_data([we])
            #update the data label position
            for ov in sp.overlays:
                if isinstance(ov, DataLabel):
                    _, y = ov.data_point
                    ov.data_point = wm, y
                    n = len(ages)
                    ov.label_text = self._build_label_text(wm, y, we, mswd, n)

            if sel:
                dp.visible = True
                ages, errors = zip(*[(a.nominal_value, a.std_dev()) for a in ages_errors])
                wm, we = calculate_weighted_mean(ages, errors)
                mswd = calculate_mswd(ages, errors)
                we = self._calc_error(we, mswd)
                result.oage, result.oerror, result.omswd = wm, we, mswd
                xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
                dp.value.set_data(ys)
                dp.index.set_data(xs)
            else:
                result.oage, result.oerror, result.omswd = None, None, None
                dp.visible = False

        g.redraw()

#===============================================================================
# handlers
#==============================================================================
    def _error_calc_method_changed(self):
        for g in self.graphs:
            self._update_graph(g)

    @on_trait_change('graph_panel_info:[ncols,nrows, padding_+]')
    def _graph_panel_info_changed(self, obj, name, new):
        if obj.ncols * obj.nrows <= self._ngroups:
            oc = self._plotcontainer
#            op = self._plots
            np, nplots = self.build(padding=obj.padding)

            pc = self.figure.graph.plotcontainer
#            print self.figure.graph.plotcontainer.components
            ind = pc.components.index(oc)
            pc.remove(oc)
            pc.insert(ind, np)
#            for opi in op:
#                self.figure.graph.plots.remove(opi)

#            self.figure.graph.plots += op
            self.figure.graph.redraw()
            self._plotcontainer = np
#            self._plots = nplots
#            print self._plotcontainer
#            self.figure.graph.plotcontainer.remove(oc)
#            self.figure.graph.plotcontainer.
#        op, r, c = self._create_grid_container(self._ngroups)

    def _plot_label_text_changed(self):
        self.plot_label.text = self.plot_label_text
#===============================================================================
# 
#===============================================================================
    def _get_adapter(self):
        return IdeoResultsAdapter

    def _get_limits(self, ages):
        xmin = min(ages)
        xmax = max(ages)
        dev = xmax - xmin
        xmin -= dev * 0.01
        xmax += dev * 0.01
        return xmin, xmax

    def _get_plot_label_text(self):
        #sigmas displayed as separate chars in Illustrator
        #use the 's' instead
        ustr = u'data 1\u03c3, age {}\u03c3'.format(self.nsigma)
#        ustr = 'data 1s, age {}s'.format(self.nsigma)
        return ustr

    def _get_ages(self, analyses):
        ages, errors = zip(*[(a.age.nominal_value,
                              a.age.std_dev())
                               for a in analyses
                                    if a.age is not None])
        ages = asarray(ages)
        errors = asarray(errors)
        return ages, errors

#===============================================================================
# views
#===============================================================================
    def _get_content(self):
        g = Group(layout='tabbed')
        r = super(Ideogram, self)._get_content()
        g.content.append(r)
        e = Item('graph_panel_info', show_label=False, style='custom')
        g.content.append(e)
        return g

    def _get_toolbar(self):
        return HGroup(
                      Item('nsigma', style='custom'),
                      Item('ideogram_of_means'),
                      Item('error_calc_method', show_label=False),
                      spring
                      )
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

#class MultipleIdeogram(Ideogram):
#    def _build_ideo(self, g):
#        for i in range(3):
#            anals = [a for a in self.analyses if a.group_id == i]
#            ages, errors = zip(*[a.age for a in anals])
#            self._add_ideo(g, ages, errors)



#============= EOF =============================================
#g = StackedGraph(panel_height=200,
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
##        ages, errors = zip(*[(ai.age, ai.age_err) for ai in self.analyses])
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
##        print ages
##        print errors
##        print 'waieht', wm, we
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