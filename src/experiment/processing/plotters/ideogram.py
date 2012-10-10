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
    Enum
from traitsui.api import View, Item, HGroup, spring
#from chaco.api import ArrayDataSource
#============= standard library imports ========================
from numpy import asarray, linspace, zeros, array, ma
import math
#============= local library imports  ==========================

from src.graph.stacked_graph import StackedGraph
#from src.graph.error_bar_overlay import ErrorBarOverlay
from src.experiment.processing.plotters.results_tabular_adapter import IdeoResults, \
    IdeoResultsAdapter
from src.experiment.processing.plotters.plotter import Plotter
from src.stats.core import calculate_weighted_mean, calculate_mswd
from src.graph.context_menu_mixin import IsotopeContextMenuMixin
#from src.experiment.processing.figure import AgeResult

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

N = 500
class mStackedGraph(StackedGraph, IsotopeContextMenuMixin):
    def set_status(self):
        self.hoverid


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

    def _get_adapter(self):
        return IdeoResultsAdapter

    def _plot_label_text_changed(self):
        self.plot_label.text = self.plot_label_text

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
    def _get_limits(self, ages):
        xmin = min(ages)
        xmax = max(ages)
        dev = xmax - xmin
        xmin -= dev * 0.01
        xmax += dev * 0.01
        return xmin, xmax

    def build(self, analyses=None, padding=None, excludes=None):

        self.results = []

        if analyses is None:
            analyses = self.analyses
        if padding is None:
            padding = self.padding

        self.analyses = analyses
        self.padding = padding
        if self.graph is None:
            g = mStackedGraph(panel_height=200,
                                equi_stack=False,
                                container_dict=dict(padding=5,
                                                    bgcolor='lightgray')
                                )

            self.graph = g
        else:
            g = self.graph

        g.clear()
        g.new_plot(
                   padding=padding)
        g.new_plot(
                   padding=padding, #[padding_left, padding_right, 1, 0],
                   bounds=[50, 100]
                   )

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

        g.set_x_title('Age (Ma)')

        g.set_x_title('Age (Ma)')
        g.set_y_title('Relative Probability')

        self.minprob = None
        self.maxprob = None

        gids = list(set([a.gid for a in analyses]))

        if not analyses:
            return

        ages, errors = self._get_ages(analyses)

        def get_ages_errors(gid):
            nages = [a.age[0] for a in analyses if a.gid == gid and a.age[0] in ages]
            nerrors = [a.age[1] for a in analyses if a.gid == gid and a.age[1] in errors]
            aa = array(nages)
            ee = array(nerrors)
            return aa, ee


#            exl = []
#            if excludes:
#                exl = excludes[gid]
#            print exl, 'exx'
#            aa = array(nages)
#            ee = array(nerrors)

#            ex = [ii in exl for ii in range(len(aa))]
#            return ma.masked_array(aa, mask=ex), ma.masked_array(ee, mask=ex)

        if self.ideogram_of_means:
#                return asarray(nages), asarray(nerrors)

            ages, errors = zip(*[calculate_weighted_mean(*get_ages_errors(gi)) for gi in gids])
#            xmin = min(ages)
#            xmax = max(ages)
            xmin, xmax = self._get_limits(ages)
            self._add_ideo(g, ages, errors, xmin, xmax, padding, 0, len(analyses))

        else:
            xmin, xmax = self._get_limits(ages)
            start = 1
            for gid in gids:
                ans = [a for a in analyses if a.gid == gid and a.age[0] in ages]
                nages, nerrors = get_ages_errors(gid)
                self._add_ideo(g, nages, nerrors, xmin, xmax, padding, gid, start=start, analyses=ans)
                start = start + len(ans) + 1

        g.set_x_limits(min=xmin, max=xmax, plotid=0)
        g.set_x_limits(min=xmin, max=xmax, plotid=1)

        minp = self.minprob
        maxp = self.maxprob
        g.set_y_limits(min=minp, max=maxp * 1.05, plotid=0)

        #add meta plot info
#        sigma = '03c3'
        self.plot_label = g.add_plot_label(self.plot_label_text, 0, 0)

        return g

    def _get_plot_label_text(self):
        ustr = u'data 1\u03c3, age ' + str(self.nsigma) + u'\u03c3'
        return ustr


    def _get_ages(self, analyses):
        ages, errors = zip(*[a.age for a in analyses if a.age[0] is not None])
        ages = asarray(ages)
        errors = asarray(errors)
        return ages, errors

    def _calculate_probability_curve(self, ages, errors, xmi, xma):

        bins = linspace(xmi, xma, N)
        probs = zeros(N)

#        print ages
#        print errors
        for ai, ei in zip(ages, errors):
            if abs(ai) < 1e-10 or abs(ei) < 1e-10:
                continue

            for j, bj in enumerate(bins):
                #calculate the gaussian prob
                #p=1/(2*p*sigma2) *exp (-(x-u)**2)/(2*sigma2)
                #see http://en.wikipedia.org/wiki/Normal_distribution
                delta = math.pow(ai - bj, 2)
                prob = math.exp(-delta / (2 * ei * ei)) / (math.sqrt(2 * math.pi * ei * ei))

                #cumulate probablities
                probs[j] += prob
#            print ai, ei

        return bins, probs

    def _add_ideo(self, g, ages, errors, xmi, xma, padding, gid, start=1, analyses=None):
        ages = asarray(ages)
        errors = asarray(errors)
#        ages, errors = self._get_ages(analyses)

        wm, we = calculate_weighted_mean(ages, errors)
        mswd = calculate_mswd(ages, errors)
        we = self._calc_error(we, mswd)
        self.results.append(IdeoResults(
                                        age=wm,
                                        mswd=mswd,
                                        error=we,
                                        error_calc_method=self.error_calc_method
                                        ))
#        print ages
        bins, probs = self._calculate_probability_curve(ages, errors, xmi, xma)
        minp = min(probs)
        maxp = max(probs)
        dp = maxp - minp

        nsigma = 0.954 #2sigma
        s, _p = g.new_series(x=bins, y=probs, plotid=0)
        _s, _p = g.new_series(x=bins, y=probs,
                              plotid=0,
                              visible=False,
                              color=s.color,
                              line_style='dash',
                              )

        s, _p = g.new_series([wm], [maxp - nsigma * dp],
                             type='scatter',
#                             marker='plus',
                             marker='circle',
                             marker_size=3,
                             color=s.color,
                             plotid=0
                             )

        self._add_error_bars(s, [we], 'x', sigma_trait='nsigma')

        if self.minprob:
            minp = min(self.minprob, minp)

        if self.maxprob:
            maxp = max(self.maxprob, maxp)

        self.minprob = minp
        self.maxprob = maxp

        self._add_aux_plot(g, ages, errors, padding, gid, start)

        if analyses:
            #set the color
            for a in analyses:
                a.color = s.color

    def _calc_error(self, we, mswd):
        ec = self.error_calc_method
        if ec == 'SEM':
            a = 1
        elif ec == 'SEM, but if MSWD>1 use SEM * sqrt(MSWD)':
            a = 1
            if mswd > 1:
                a = mswd ** 0.5
        return we * a

    def _add_aux_plot(self, g, ages, errors, padding, gid, start, plotid=1):

        g.set_grid_traits(visible=False, plotid=plotid)
        g.set_grid_traits(visible=False, grid='y', plotid=plotid)

        g.set_axis_traits(tick_visible=False,
                          tick_label_formatter=lambda x:'',
                          axis='y', plotid=plotid)
        g.set_y_title('Analysis #', plotid=plotid)
#        g.set_axis_traits(orientation='right', plotid=1, axis='y')

        n = zip(ages, errors)
        n = sorted(n, key=lambda x:x[0])
        ages, errors = zip(*n)
#        ys = range(1, len(ages) + 1)
#        ma = 10 * (gid + 1)
#        ys = linspace(1, 10 * (gid + 1), len(ages))

#        gg = gid + 1
#        print gg, ns, len(ages)
#        ys = linspace(gg, ns + gid, len(ages))
#        print ys
        ma = start + len(ages)
        ys = linspace(start, ma, len(ages))
        scatter, _p = g.new_series(ages, ys,
                                   type='scatter', marker='circle',
                                   marker_size=2,
#                                   selection_marker='circle',
                                   selection_marker_size=3,
                                   plotid=plotid)
        self._add_error_bars(scatter, errors, 'x')
        self._add_scatter_inspector(scatter, gid=gid)
        scatter.index.on_trait_change(self._update_graph, 'metadata_changed')

        g.set_y_limits(min=0, max=ma + 1, plotid=1)

#
#    def update_graph_metadata(self, obj, name, old, new):
###        print obj, name, old, new
#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]
#            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]
    def _cmp_analyses(self, x):
        return x.age[0]

    def _update_graph(self, new):
        g = self.graph

        xmi, xma = g.get_x_limits()
        for i, p in enumerate(g.plots[1].plots.itervalues()):
            result = self.results[i]

            sel = p[0].index.metadata['selections']
#            if not sel:
#                try:
#                    hov = p[0].index.metadata['hover']
#                    if hov:
#                        return
#                except KeyError:
#                    pass

            plot = g.plots[0]
            dp = plot.plots['plot{}'.format(i * 3 + 1)][0]
            ages_errors = sorted([a.age for a in self.analyses if a.gid == i], key=lambda x: x[0])
            if sel:
                dp.visible = True
                ages, errors = zip(*ages_errors)
                wm, we = calculate_weighted_mean(ages, errors)
                mswd = calculate_mswd(ages, errors)
                we = self._calc_error(we, mswd)
                result.oage, result.oerror, result.omswd = wm, we, mswd
                _xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
                dp.value.set_data(ys)
            else:
                result.oage, result.oerror, result.omswd = None, None, None
                dp.visible = False

            lp = plot.plots['plot{}'.format(i * 3)][0]
            sp = plot.plots['plot{}'.format(i * 3 + 2)][0]
            try:
                ages, errors = zip(*[ai for j, ai in enumerate(ages_errors) if not j in sel])
                wm, we = calculate_weighted_mean(ages, errors)
                mswd = calculate_mswd(ages, errors)
                we = self._calc_error(we, mswd)

                result.age = wm
                result.error = we
                result.mswd = mswd
                result.error_calc_method = self.error_calc_method
                _xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
            except ValueError:
                wm, we = 0, 0
                ys = zeros(N)

            lp.value.set_data(ys)

            sp.index.set_data([wm])
            sp.xerror.set_data([we])

        g.redraw()

#===============================================================================
# handlers
#==============================================================================
    def _error_calc_method_changed(self):
        self._update_graph(True)

#===============================================================================
# views
#===============================================================================
    def _get_content(self):
        return HGroup(Item('nsigma', style='custom'),
                      Item('ideogram_of_means'),
                      Item('error_calc_method', show_label=False),
                      spring)
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
#            anals = [a for a in self.analyses if a.gid == i]
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
