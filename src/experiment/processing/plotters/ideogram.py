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
from numpy import asarray, linspace, zeros, array, ma, ones, pi, exp
#============= local library imports  ==========================

from src.graph.stacked_graph import StackedGraph
#from src.graph.error_bar_overlay import ErrorBarOverlay
from src.experiment.processing.plotters.results_tabular_adapter import IdeoResults, \
    IdeoResultsAdapter
from src.experiment.processing.plotters.plotter import Plotter, mStackedGraph
from src.stats.core import calculate_weighted_mean, calculate_mswd
from src.graph.context_menu_mixin import IsotopeContextMenuMixin
from src.graph.graph import Graph
from chaco.plot_containers import GridPlotContainer
from chaco.tools.traits_tool import TraitsTool
from chaco.data_label import DataLabel
from chaco.tools.data_label_tool import DataLabelTool
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



EInt = lambda x: Int(x, enter_set=True, auto_set=False)
class GraphPanelInfo(HasTraits):
    nrows = EInt(1)#Int(1, enter_set=True, auto_set=False)
    ncols = EInt(2)#Int(2, enter_set=True, auto_set=False)
    fixed = Str('cols')
    padding_left = EInt(40)
    padding_right = EInt(5)
    padding_top = EInt(40)
    padding_bottom = EInt(40)

    padding = Property
    def _get_padding(self):
        return [self.padding_left, self.padding_right, self.padding_top, self.padding_bottom]

    def traits_view(self):
        v = View(HGroup(
                        VGroup(
                               Item('ncols'),
                               Item('nrows'),
                               ),
                        Item('fixed',
                             show_label=False,
                             style='custom',
                             editor=EnumEditor(values=['cols', 'rows'],
                                               cols=1,
                                               )
                             ),
                        VGroup(
                               Item('padding_left', label='Left'),
                               Item('padding_right', label='Right'),
                               Item('padding_top', label='Top'),
                               Item('padding_bottom', label='Bottom'),
                               )
                        )
                 )
        return v

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

    graph_panel_info = Instance(GraphPanelInfo, ())

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

    def build(self, analyses=None, padding=None):

        if analyses is None:
            analyses = self.analyses

        self.analyses = analyses
#        g = self._build(analyses=analyses, padding=padding)
#        return g.plotcontainer

#        analyses = [[analyses, analyses, analyses],
#                  [analyses, analyses, analyses],
#                  [analyses, analyses, analyses]
#                  ]
        #parse analyses into graph groups

#        graphs = []
#        gs = []
        graph_ids = sorted(list(set([a.graph_id for a in analyses])))
        def get_analyses(gii):
            return [a for a in analyses if a.graph_id == gii]

        graph_groups = [get_analyses(gi)
                            for gi in graph_ids]
        self._ngroups = n = len(graph_groups)

        op, r, c = self._create_grid_container(n)
        self._plotcontainer = op

        aux_plot_height = 100 / r
        self.graphs = []
        self.results = []
        plots = []
        font = 'modern {}'.format(10)
        tfont = 'modern {}'.format(10)
        for i in range(r):
            for j in range(c):

                k = i * c + j
#                print k, i, j
                try:
                    ans = graph_groups[k]
                except IndexError:
                    break
                lns = map(str, list(set([ai.labnumber for ai in ans])))
                g = self._build(
                                ans,
                                #analyses[i][j],
                                padding,
                                aux_plot_height,
#                                labnumber=ans[0].labnumber,
                                title=', '.join(lns)
                                )
                if i == r - 1:
                    g.set_x_title('Age (Ma)')

                if j == 0:
                    g.set_y_title('Relative Probability')
                    g.set_y_title('Analysis #', plotid=1)
                    g.set_y_title('%40*', plotid=2)
#                    g.set_y_title('k39', plotid=3)


#                p1 = g.plots[0]
#                p2 = g.plots[1]
#                p1.y_axis.tick_label_font = font
#                p1.y_axis.title_font = tfont
#                p1.x_axis.tick_label_font = font
#                p1.x_axis.title_font = tfont
#                p2.y_axis.tick_label_font = font
#                p2.y_axis.title_font = tfont

                for pi in g.plots:
                    pi.y_axis.tick_in = False

                op.add(g.plotcontainer)
                self.graphs.append(g)
                for pi in g.plots:
                    plots.append(pi)

        self._plots = plots
        return op, plots

    def _create_grid_container(self, ngroups):
        gpi = self.graph_panel_info
        r = gpi.nrows
        c = gpi.ncols

        while ngroups > r * c:
            if gpi.fixed == 'cols':
                r += 1
            else:
                c += 1

        if ngroups == 1:
            r = c = 1

        op = GridPlotContainer(shape=(r, c),
                               bgcolor='white',
                               fill_padding=True,
                               padding_top=10
                               )
        return op, r, c

    def _build(self, analyses, padding=None, aux_plot_height=100, title=''):
        if padding is None:
            padding = [50, 5 , 35, 35]

        g = mStackedGraph(panel_height=200,
                            equi_stack=False,
                            container_dict=dict(padding=0),
                            plotter=self
                            )
        g.clear()
#        g.plotcontainer.tools.append(TraitsTool(g.plotcontainer))
        g._has_title = True
        p = g.new_plot(
#                   contextmenu=False,
                   padding=padding)

        p.value_range.tight_bounds = False
        p = g.new_plot(
#                   contextmenu=False,
                   padding=padding, #[padding_left, padding_right, 1, 0],
                   bounds=[50, aux_plot_height],
                   )
        p.value_range.tight_bounds = False
        p = g.new_plot(
#                   contextmenu=False,
                   padding=padding, #[padding_left, padding_right, 1, 0],
                   bounds=[50, aux_plot_height],
                   title=title
                   )
        p.value_range.tight_bounds = False
#        p = g.new_plot(
#                   contextmenu=False,
#                   padding=padding, #[padding_left, padding_right, 1, 0],
#                   bounds=[50, aux_plot_height],
#                   title=title
#                   )
#        p.value_range.tight_bounds = False

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

#        g.labnumber = labnumber
        g.analyses = analyses
        g.maxprob = None
        g.minprob = None

        group_ids = list(set([a.group_id for a in analyses]))

        if not analyses:
            return

        ages, errors = self._get_ages(analyses)
        def get_ages_errors(group_id):
            nages = [a.age[0] for a in analyses if a.group_id == group_id]
            nerrors = [a.age[1] for a in analyses if a.group_id == group_id]
            aa = array(nages)
            ee = array(nerrors)
            return aa, ee

        def get_rads(group_id):
            rads = [a.rad40 for a in analyses if a.group_id == group_id]
            return rads

        def get_k39s(group_id):
            rads = [a.k39 for a in analyses if a.group_id == group_id]
            return rads

        if self.ideogram_of_means:

            ages, errors = zip(*[calculate_weighted_mean(*get_ages_errors(gi)) for gi in group_ids])
            xmin, xmax = self._get_limits(ages)
            self._add_ideo(g, ages, errors, xmin, xmax, padding, 0, len(analyses),
#                           labnumber=labnumber
                           )

        else:
            xmin, xmax = self._get_limits(ages)
            start = 1
            offset = 0
            for group_id in group_ids:
                ans = [a for a in analyses if a.group_id == group_id and a.age[0] in ages]
                labnumber = ', '.join(sorted(list(set([str(a.labnumber) for a in ans]))))
                nages, nerrors = get_ages_errors(group_id)
                offset = self._add_ideo(g, nages, nerrors, xmin, xmax, padding, group_id,
                               start=start,
                               labnumber=labnumber,
                               offset=offset
                               )

                #add analysis number plot
                n = zip(nages, nerrors)
                n = sorted(n, key=lambda x:x[0])
                aages, xerrs = zip(*n)
                maa = start + len(ages)
                age_ys = linspace(start, maa, len(aages))
                self._add_aux_plot(g, aages, age_ys, xerrs, None, padding, group_id,
                                       plotid=1)
                g.set_axis_traits(tick_visible=False,
                  tick_label_formatter=lambda x:'',
                  axis='y', plotid=1)

                start = start + len(ans) + 1

                #add rad plot
                rads = get_rads(group_id)
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
                                       plotid=2)

                g.set_axis_traits(axis='y', plotid=2)

#                #add k39 plot
#                k39s = get_k39s(group_id)
#                n = zip(nages, k39s)
#                n = sorted(n, key=lambda x:x[0])
#                aages, k39s = zip(*n)
#                k39, k39_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in k39s])
#                self._add_aux_plot(g, aages,
#                                   k39,
#                                   None,
#                                   k39_errs,
#                                   padding,
#                                   group_id,
#                                   plotid=3)


            maxp = g.maxprob

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
#        g.set_x_limits(min=xmin, max=xmax, pad='0.2', plotid=1)

        minp = 0
        maxp = g.maxprob
        g.set_y_limits(min=minp, max=maxp * 1.05, plotid=0)

        #add meta plot info
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

    def _add_ideo(self, g, ages, errors, xmi, xma, padding,
                   group_id, start=1,
                   labnumber=None,
                   offset=0
#                   analyses=None
                   ):
        ages = asarray(ages)
        errors = asarray(errors)
#        ages, errors = self._get_ages(analyses)

        wm, we = calculate_weighted_mean(ages, errors)
        mswd = calculate_mswd(ages, errors)
        we = self._calc_error(we, mswd)
        self.results.append(IdeoResults(
                                        labnumber=labnumber,
                                        age=wm,
                                        mswd=mswd,
                                        error=we,
                                        error_calc_method=self.error_calc_method
                                        ))
#        print ages
        bins, probs = self._calculate_probability_curve(ages, errors, xmi, xma)
        minp = min(probs)
        maxp = max(probs)
#        dp = maxp - minp
#        print dp
#        if abs(dp) < 1e-6:
#        dp = maxp

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
#                             marker='plus',
                             marker='circle',
                             marker_size=3,
                             color=s.color,
                             plotid=0
                             )

        self._add_data_label(s, (wm, ym, we, mswd, ages.shape[0]))
        d = lambda *args: self._update_graph(g, *args)
#        s.index_mapper.on_trait_change(self._update_graph, 'updated')
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
        for a in g.analyses:
            a.color = s.color
        return ym * 2.5

    def _add_data_label(self, s, args):
        wm, ym, we, mswd, n = args
        label_text = self._build_label_text(*args)
        label = DataLabel(component=s, data_point=(wm, ym),
                          label_position='top right',
                          label_text=label_text,
                          border_visible=False,
                          bgcolor='transparent',
                          show_label_coords=False,
                          marker_visible=False,
                          text_color=s.color,
                          arrow_color=s.color,
                          )
        s.overlays.append(label)
        tool = DataLabelTool(label,
#                             auto_arrow_root=False
                             )
        label.tools.append(tool)


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

    def _add_aux_plot(self, g, ages, ys, xerrors, yerrors, padding, group_id, plotid=1):

        g.set_grid_traits(visible=False, plotid=plotid)
        g.set_grid_traits(visible=False, grid='y', plotid=plotid)

        scatter, p = g.new_series(ages, ys,
                                   type='scatter', marker='circle',
                                   marker_size=2,
#                                   selection_marker='circle',
                                   selection_marker_size=3,
                                   plotid=plotid)
        if xerrors:
            self._add_error_bars(scatter, xerrors, 'x')
        if yerrors:
            self._add_error_bars(scatter, yerrors, 'y')

#        print 'aaa', group_id, id(scatter)
        self._add_scatter_inspector(g.plotcontainer, p, scatter, group_id=group_id)

#        p.value_range.tight_bounds = False
#        scatter.value_range.tight_bounds = False
#        p.value_range.margin = 0.5
#        print p.value_range.low, p.value_range.high, p.value_range.tight_bounds
#        g.set_y_limits(*limits, plotid=plotid)
#        if plotid == 1:
        d = lambda *args: self._update_graph(g, *args)
        scatter.index.on_trait_change(d, 'metadata_changed')

#    def update_graph_metadata(self, obj, name, old, new):
###        print obj, name, old, new
#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]
#            self.selected_analysis = sorted([a for a in self.analyses], key=lambda x:x.age)[hoverid]
    def _cmp_analyses(self, x):
        return x.age[0]

    def _update_graph(self, g):
        xmi, xma = g.get_x_limits()
        ideo = g.plots[0]

        sels = dict()
#        sel = []
        has_sel = False
        for pp in g.plots[1:]:
#            si = []
            for i, p in enumerate(pp.plots.itervalues()):
                ss = p[0].index.metadata['selections']

                if i in sels:
                    sels[i] = list(set(ss + sels[i]))
                else:
                    sels[i] = ss
#
#                if ss:
#                    has_sel = True
#                    break
#            if has_sel:
#                break

#        for ppp in g.plots[1:]:
#            if ppp == pp:
#                continue
#
#            for i, p in enumerate(ppp.plots.itervalues()):
#                if i in sels:
#                    p[0].index.metadata['selections'] = sels[i]

#                si += ss

#            sels[p[0]] = si
#        print 'a', sels
#
#        for pp in g.plots[1:]:
#            for i, p in enumerate(pp.plots.itervalues()):
#                meta = p[0].index.metadata
#                print meta
#                p[0].index.metadata['selections'] = sel
#                n = dict(selections=sel)
#                n = dict()
#                n.update(meta, selections=sel)
#                p[0].index.trait_set(metadata=n, trait_change_notify=False)

        for i, p in enumerate(g.plots[1].plots.itervalues()):
            result = self.results[i]
#            print sels[p[0]]
#            p[0].index.metadata['selections'] = sel
#            sel = p[0].index.metadata['selections']
#            print 'b', sel
            try:
                sel = sels[i]
            except KeyError:
                continue
#            print sel, i
            dp = ideo.plots['plot{}'.format(i * 3 + 1)][0]
            ages_errors = sorted([a.age for a in g.analyses if a.group_id == i], key=lambda x: x[0])
            if sel:
                dp.visible = True
                ages, errors = zip(*ages_errors)
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

            lp = ideo.plots['plot{}'.format(i * 3)][0]
            sp = ideo.plots['plot{}'.format(i * 3 + 2)][0]
            try:
                ages, errors = zip(*[ai for j, ai in enumerate(ages_errors) if not j in sel])
                wm, we = calculate_weighted_mean(ages, errors)
                mswd = calculate_mswd(ages, errors)
                we = self._calc_error(we, mswd)

                result.age = wm
                result.error = we
                result.mswd = mswd
                result.error_calc_method = self.error_calc_method
                xs, ys = self._calculate_probability_curve(ages, errors, xmi, xma)
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
