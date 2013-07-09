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
from traits.api import Any, Int, List, Array, Float
from enable.base_tool import BaseTool
from chaco.abstract_overlay import AbstractOverlay
from enable.colors import color_table
from chaco.data_label import DataLabel
from chaco.base_xy_plot import BaseXYPlot
from enable.tools.drag_tool import DragTool
from chaco.plot_label import PlotLabel
#============= standard library imports ========================
from numpy import array, Inf, where, average, hstack
from uncertainties import ufloat
#============= local library imports  ==========================
# from src.graph.stacked_graph import StackedGraph
from src.processing.plotters.results_tabular_adapter import SpectrumResults, \
    SpectrumResultsAdapter
from src.processing.plotters.plotter import Plotter
from src.stats.core import calculate_mswd, validate_mswd
# from enable.enable_traits import Pointer
from src.processing.argon_calculations import age_equation, find_plateaus
from src.processing.analysis import IntegratedAnalysis
# from src.constants import PLUSMINUS
# from src.helpers.formatting import floatfmt
from src.processing.plotters.sparse_ticks import SparseLogTicks, SparseTicks
# from src.processing.plotters.point_move_tool import PointMoveTool
# from chaco.plot_label import PlotLabel
# from enable.font_metrics_provider import font_metrics_provider
# from chaco.data_label import DataLabel

class BasePlateauOverlay(AbstractOverlay):
    cumulative39s = Array
    def _get_section(self, pt):
        d = self.component.map_data(pt)
        cs = self.cumulative39s
        t = where(cs < d)[0]
        if len(t):
            tt = t[-1] + 1
        else:
            tt = 0
        return tt

class SpectrumTool(BaseTool, BasePlateauOverlay):
    nsigma = Int(2)
    def hittest(self, screen_pt, threshold=20):
        comp = self.component

        ndx = self._get_section(screen_pt)
        ys = comp.value.get_data()[::2]
        if ndx < len(ys):
            yd = ys[ndx]
            e = comp.errors[ndx] * self.nsigma
            yl, yu = comp.y_mapper.map_screen(array([yd - e, yd + e]))

            if yl < screen_pt[1] < yu:
                return ndx

    def normal_left_down(self, event):
        if event.handled:
            return

        pt = event.x, event.y
        ndx = self.hittest(pt)
        if ndx is not None:
            sels = self.component.index.metadata['selections']
            self.component.index.metadata['selections'] = list(set(sels) ^ set([ndx]))
            self.component.request_redraw()

        event.handled = True

    def normal_mouse_move(self, event):
        pt = event.x, event.y
        if self.hittest(pt) is not None and not event.handled:
            event.window.set_pointer('cross')
            hover = self._get_section(pt)
            self.component.index.metadata['hover'] = [hover]

        else:
            event.window.set_pointer('arrow')
            self.component.index.metadata['hover'] = None

class SpectrumErrorOverlay(AbstractOverlay):
    nsigma = Int(1)
    def overlay(self, component, gc, *args, **kw):
        comp = self.component
        with gc:
            gc.clip_to_rect(comp.x, comp.y, comp.width, comp.height)

            xs = comp.index.get_data()
            ys = comp.value.get_data()
            es = comp.errors
            sels = comp.index.metadata['selections']

            n = len(xs)
            xs = xs.reshape(n / 2, 2)
            ys = ys.reshape(n / 2, 2)
            es = es.reshape(n / 2, 2)
            for i, ((xa, xb), (ya, yb), (ea, eb)) in enumerate(zip(xs, ys, es)):
                ea *= self.nsigma
                eb *= self.nsigma
                p1 = xa, ya - ea
                p2 = xa, ya + ea
                p3 = xb, ya - ea
                p4 = xb, ya + ea
                p1, p2, p3, p4 = comp.map_screen([p1, p2, p3, p4])
                x = p1[0]
                y = p1[1]
                w = p3[0] - p1[0]
                h = p2[1] - p1[1]
                if i in sels:
                    gc.set_fill_color((0.75, 0, 0))
                else:
                    c = comp.color
                    if isinstance(c, str):
                        c = color_table[c]

                    gc.set_fill_color(c)
                gc.rect(x, y, w + 1, h)
                gc.fill_path()


class PlateauTool(DragTool):
    def normal_mouse_move(self, event):
        if self.is_draggable(event.x, event.y):
            event.handled = True

    def normal_left_down(self, event):
        if self.is_draggable(event.x, event.y):
            event.handled = True

    def is_draggable(self, x, y):
        return self.component.hittest((x, y))

    def drag_start(self, event):
        data_pt = self.component.component.map_data((event.x, event.y), all_values=True)
        self._prev_pt = data_pt
        event.handled = True

    def dragging(self, event):
        plot = self.component.component
        cur_pt = plot.map_data((event.x, event.y), all_values=True)
        dy = cur_pt[1] - self._prev_pt[1]
        self.component.y += dy
        self.component.dragged = True
        self._prev_pt = cur_pt
        event.handled = True
        plot.request_redraw()


class PlateauOverlay(BasePlateauOverlay):
    plateau_bounds = Array
    y = Float
    dragged = False

    def hittest(self, pt, threshold=7):
        x, y = pt
        pts = self._get_line()
        if pts is not None:
            pt1, pt2 = pts
            if pt1[0] <= x <= pt2[0]:
                if abs(y - pt1[1]) <= threshold:
                    return True

    def _get_line(self):
        cs = self.cumulative39s
        ps = self.plateau_bounds
        if ps[0] == ps[1]:
            return
        cstart = cs[ps[0]]
        cend = cs[ps[1] + 1]
        y = self.y
        pt1, pt2 = self.component.map_screen([(cstart, y), (cend, y)])
        return pt1, pt2

    def overlay(self, component, gc, *args, **kw):

        line_width = 4
        points = self._get_line()
        if points:
            pt1, pt2 = points
            with gc:
                comp = self.component
                gc.clip_to_rect(comp.x, comp.y, comp.width, comp.height)
                gc.set_stroke_color((1, 0, 0))
                gc.set_line_width(line_width)

                y = pt1[1]
                x1 = pt1[0] + 1
                x2 = pt2[0] - 1
                gc.lines([(x1, y), (x2, y)])

                # add end caps
                gc.lines([(x1, y - 10), (x1, y + 10)])
                gc.lines([(x2, y - 10), (x2, y + 10)])
                gc.draw_path()

class Spectrum(Plotter):
    padding = List([80, 10, 5, 40])
#     def _get_adapter(self):
#         return SpectrumResultsAdapter

    def _build_xtitle(self, g, xtitle_font, xtick_font, **kw):
        f, s = xtitle_font.split(' ')
        g.set_x_title('cumulative 39ArK', font=f, size=int(s))
        g.set_axis_traits(axis='x', tick_label_font=xtick_font)

    def _build_ytitle(self, g, ytitle_font, ytick_font, aux_plots, age_unit='Ma', **kw):
        f, s = ytitle_font.split(' ')
        g.set_y_title('Age ({})'.format(age_unit), font=f, size=int(s))
        for k, ap in enumerate(aux_plots):
            g.set_y_title(ap['ytitle'], plotid=k + 1, font=f, size=int(s))
            g.set_axis_traits(axis='y', tick_label_font=ytick_font)

    def _build_hook(self, g, analyses, aux_plots=None):
        group_ids = list(set([a.group_id for a in analyses]))
        ma, mi = -Inf, Inf
        self.cumulative39s = []
        labels = []
        for group_id in group_ids:
            anals = [a for a in analyses if a.group_id == group_id]
            miage, maage, label = self._add_age_spectrum(g, anals, group_id)

            ma = max(ma, maage)
            mi = min(mi, miage)
            labels.append(label)

            # add aux plots
            for plotid, ap in enumerate(aux_plots):
                # get aux type and plot
                name = ap['name']
                if name != 'analysis_number':
                    func = getattr(self, '_aux_plot_{}'.format(name))
                    func(g, analyses,
                         plotid + 1,
                         group_id,
                         value_scale=ap['scale']
                         )

        self._add_plot_metadata(g)

        g.set_y_limits(min=mi, max=ma, pad='0.1')
        g.analyses = analyses
        return g

    def _calculate_total_gas_rad40(self, analyses):
        r, e = zip(*[(a.rad40_percent.nominal_value,
                a.rad40_percent.std_dev)
                for a in analyses])

        r = array(r)
        e = array(e)
        wts = 1 / e ** 2

        m, ee = average(r, weights=wts, returned=True)
        ee = ee ** -0.5
        return ufloat(m, ee)

    def _calculate_total_gas_age(self, analyses):
        '''
            sum the corrected rad40 and k39 values
             
            not necessarily the same as isotopic recombination
            
        '''

        rad40, k39 = zip(*[(a.rad40, a.k39) for a in analyses])
        rad40 = sum(rad40)
        k39 = sum(k39)

        j = a.j
        return age_equation(rad40 / k39, j, scalar=1e6)

    def _calculate_spectrum(self, analyses,
                            excludes=None,
                            group_id=0,
                            index_key='k39',
                            value_key='age'
                            ):

        if excludes is None:
            excludes = []

        values = [getattr(a, value_key) for a in analyses]
        ar39s = [getattr(a, index_key).nominal_value for a in analyses]
        xs = []
        ys = []
        es = []
        sar = sum(ar39s)
        prev = 0
        c39s = []
#        steps = []
        for i, (aa, ar) in enumerate(zip(values, ar39s)):
            if isinstance(aa, tuple):
                ai, ei = aa
            else:
                ai, ei = aa.nominal_value, aa.std_dev

            xs.append(prev)

            if i in excludes:
                ei = 0
                ai = ys[-1]

            ys.append(ai)
            es.append(ei)

            s = 100 * ar / sar + prev
            c39s.append(s)
            xs.append(s)
            ys.append(ai)
            es.append(ei)
            prev = s

        return array(xs), array(ys), array(es), array(c39s)  # , array(ar39s), array(values)

    def _add_plot(self, g, xs, ys, es, cum39s=None, group_id=0, plotid=0, value_scale='linear', **kw):
        xs, ys, es = map(array, (xs, ys, es))
        ds, p = g.new_series(xs, ys, plotid=plotid)

        u = lambda a, b, c, d: self.update_graph_metadata(ds, group_id, a, b, c, d)
        ds.index.on_trait_change(u, 'metadata_changed')

        ds.index.sort_order = 'ascending'

        ds.index.on_trait_change(self._update_graph, 'metadata_changed')

#        sp = SpectrumTool(ds, spectrum=self, group_id=group_id)
        sp = SpectrumTool(ds, cumulative39s=cum39s)
        ds.tools.append(sp)

        # provide 1s errors use nsigma to control display
        ds.errors = es

        ns = self.plotter_options.step_nsigma
        sp = SpectrumErrorOverlay(component=ds, spectrum=self, group_id=group_id, nsigma=ns)
        ds.overlays.append(sp)

        if value_scale == 'log':
            p.value_axis.tick_generator = SparseLogTicks()
        else:
            p.value_axis.tick_generator = SparseTicks()
        return ds

    def _get_plateau(self, analyses, exclude=None):
        if exclude is None:
            exclude = []
        ages = self._get_ages(analyses, unzip=False)
        k39s = [a.k39.nominal_value for a in analyses]
        ages, errors = self._unzip_value_error(ages)

        # provide 1s errors
        platbounds = find_plateaus(ages, errors, k39s, overlap_sigma=2, exclude=exclude)
        n = platbounds[1] - platbounds[0] + 1
        if n > 1:
            ans = []

            for j, ai in enumerate(analyses):
                if j not in exclude and platbounds[0] <= j <= platbounds[1]:
                    ans.append(ai)
#            ans=[ai for (j,ai) in analyses if]
#            ans = analyses[platbounds[0]:platbounds[1]]
            ages, errors = self._get_ages(ans)
            mswd, valid, n = self._get_mswd(ages, errors)
            plateau_age = self._calculate_total_gas_age(ans)
            return plateau_age, platbounds, mswd, valid, len(ages)
        else:
            return 0, array([0, 0]), 0, 0, 0

#     def _get_mswd(self, ages, errors):
#         mswd = calculate_mswd(ages, errors)
#         n = len(ages)
#         valid_mswd = validate_mswd(mswd, n)
#         return mswd, valid_mswd, n

    def _add_age_spectrum(self, g, analyses, group_id):
        xs, ys, es, c39s = self._calculate_spectrum(analyses, group_id=group_id)

        ys, es = array(ys), array(es)
        ns = self.plotter_options.step_nsigma
        yl = (ys - es * ns)[::-1]
        yu = ys + es * ns
        miages = min(yl)
        maages = max(yu)

        spec = self._add_plot(g, xs, ys, es, group_id=group_id, cum39s=c39s)

        tga = self._calculate_total_gas_age(analyses)
        all_ages, all_errors = self._get_ages(analyses, group_id)
#        ages, errors = zip(*[(a.age[0], a.age[1]) for a in analyses])
#        ages = array(ages)
#        ages, errors = self._get_ages(analyses)
#        mean_age = ages.mean()
#        mean_error = ages.std()

#        weights = array(errors) ** -2

#        weighted_mean_age, ss = average(ages, weights=weights, returned=True)
#        weighted_mean_error = ss ** -0.5

#        weighted_mean_error
        # print 'tga', tga.nominal_value, tga.std_dev()
        # print 'mean', mean_age, mean_error
        # print 'wmean', weighted_mean_age, weighted_mean_error
#        print '----------'
#        rad40_percent = self._calculate_total_gas_rad40(analyses)
#        age = mean_age
#        error = mean_error

        text = self._build_integrated_age_label(tga, *self._get_mswd(all_ages, all_errors))
        dl = self._add_data_label(spec, text,
                                  (25, miages),
                                  font='modern 10',
                                  label_position='bottom right',
                                  append=False
                                  )

#        plateau_age, platbounds, nplateau_steps = self._get_plateau(ages, k39s, analyses)
        plateau_age, platbounds, mswd, valid, nplateau_steps = self._get_plateau(analyses)
        if isinstance(plateau_age, int):
            pa = 0
        else:
            pa = plateau_age.nominal_value
        point = (50, pa)
        ptext = self._build_plateau_age_label(plateau_age, mswd, valid, nplateau_steps)
        pdl = self._add_data_label(spec,
                                   ptext,
                                   point,
                                   bgcolor='white'
#                                   color='red'
                                   )
        if nplateau_steps == 0:
            pdl.visible = False

        self._add_plateau_overlay(spec, platbounds, c39s, pa)
#        self.results.append(SpectrumResults(
#                                           labnumber=self.get_labnumber(analyses),
#                                           mean_age=mean_age,
#                                           mean_error=mean_error,
#                                           weighted_mean_age=weighted_mean_age,
#                                           weighted_mean_error=weighted_mean_error,
#                                           tga=tga.nominal_value,
#                                           tga_error=tga.std_dev(),
#                                           rad40_percent=rad40_percent,
#                                           mswd=mswd
#                                           ))

        return miages, maages, dl

    def _build_plateau_age_label(self, plat_age, *args):
        if isinstance(plat_age, int):
            age, error = 1, 1
        else:

            age, error = plat_age.nominal_value, plat_age.std_dev

        error *= self.plotter_options.nsigma
        txt = self._build_label_text(age, error, *args)
        return 'Age= {}'.format(txt)

    def _build_integrated_age_label(self, tga, *args):
        age, error = tga.nominal_value, tga.std_dev
        error *= self.plotter_options.nsigma
        txt = self._build_label_text(age, error, *args)
        return 'Integrated Age= {}'.format(txt)

    def _update_graph(self):
        g = self.graphs[0]
        lp = g.plots[0].plots['plot0'][0]

        integrated_age_label = lp.overlays[-3]
        plateau_age_label = lp.overlays[-2]

        sel = lp.index.metadata['selections']

        ans = g.analyses
#        ages = self._get_ages(ans, unzip=False)
#        k39s = [a.k39 for a in ans]

#        plateau_age, platbounds, nplateau_steps = self._get_plateau(ages, k39s, ans, exclude=sel)
        plateau_age, platbounds, plateau_mswd, valid_mswd, nplateau_steps = self._get_plateau(ans, exclude=sel)
#        n = platbounds[1] - platbounds[0]

        # provide 1s errors
#        platbounds = find_plateaus(ages, errors, k39s, overlap_sigma=2, exclude=sel)

#        if sel and platbounds[0] != platbounds[1]:
#            #if the selection is not the last step
#            #increase the upper bound by the len of selection
#            if len(ages) not in sel:
#                platbounds[1] += len(sel)

        # get the plateau overlay
        po = lp.overlays[-1]
        po.plateau_bounds = platbounds

        if nplateau_steps == 0:
            plateau_age_label.visible = False
        else:
            plateau_age_label.visible = True
#            pans = g.analyses[platbounds[0]:platbounds[1]]
#            age = self._calculate_total_gas_age(pans)
#            pa, pe = age.nominal_value, plateau_age.std_dev()
            if not po.dragged:
                po.y = plateau_age.nominal_value
#            offset = 0
#            for si in sel:
#                if si > platbounds[0] and si < platbounds[1]:
#                    offset = len(sel)
#                    break

            text = self._build_plateau_age_label(plateau_age, plateau_mswd, valid_mswd, nplateau_steps)
            plateau_age_label.label_text = text

        filtered_analyses = [ai for (j, ai) in enumerate(ans)
                            if j not in sel]

        ages, errors = self._get_ages(filtered_analyses)
        tga = self._calculate_total_gas_age(filtered_analyses)
        text = self._build_integrated_age_label(tga, *self._get_mswd(ages, errors))
        integrated_age_label.label_text = text
#        mswd = calculate_mswd(ages, errors)
#        age, error = tga.nominal_value, tga.std_dev()
#        n = len(ages)
#        valid_mswd = validate_mswd(mswd, n)
#        integrated_age_label.label_text = self._build_integrated_age_label(age, error, mswd, valid_mswd, n)





#            self.results[i].mswd = mswd
#            if sel:
#                pass
#                #draw dp
#                dp.color = 'red'
#            else:
#                dp.color = 'transparent'

            # recalculate spectrum without selected
#            xs, ys, es, c39s = self._calculate_spectrum(self.analyses,
#                                                        'k39', excludes=sel)
#            lp.index.set_data(xs)
#            lp.value.set_data(ys)
#            lp.errors = es

        g.redraw()

    def get_ages(self, kind='weighted_mean', group_id=0):
        def factory(r):
            dm = IntegratedAnalysis(
                                    rid=r.labnumber,
                                    _age=r.weighted_mean_age,
                                    _error=r.weighted_mean_error,
                                    group_id=group_id,
                                    _rad40_percent=r.rad40_percent
                                    )
            return dm

        return [factory(ri) for ri in self.results]
#        return [(r.labnumber,
#                 getattr(r, '{}_age'.format(kind)),
#                 getattr(r, '{}_error'.format(kind)),
#                 group_id,
#                 ) for r in self.results]

#===============================================================================
# aux plots
#===============================================================================
#    def _add_aux_plot(self, g, xs, ys, y_errs, plotid):
#        pass
    def _filter_aux_plots(self, aux_plots):
        return [ap for ap in aux_plots if ap.name not in ('analysis_number',
                                                          'k39')]

    def _aux_plot_radiogenic_percent(self, g, analyses, plotid, group_id, **kw):

        xs, ys, es, c39s = self._calculate_spectrum(analyses,
                                                  group_id=group_id,
                                                  value_key='rad40_percent')
#        rads = [a.rad40_percent for a in analyses if a.group_id == group_id]

#        n = zip(nages, rads)
#        n = sorted(n, key=lambda x:x[0])
#        aages, rads = zip(*n)
#        rads, rad_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in rads])

        self._add_plot(g, xs, ys, es, group_id=group_id, plotid=plotid, cum39s=c39s, **kw)
#        self._add_aux_plot(g, aages,
#                           rads,
#                           None,
#                           rad_errs,
#                           padding,
#                           group_id,
#                           plotid=plotid,
#                           value_scale=value_scale
#                           )

    def _aux_plot_kca(self, g, analyses,
                      plotid,
                      group_id,
                      **kw):

        xs, ys, es, c39s = self._calculate_spectrum(analyses, group_id=group_id, value_key='kca')
        self._add_plot(g, xs, ys, es,
                       plotid=plotid,
                       group_id=group_id,
                       cum39s=c39s, **kw)
#        nages = aux_namespace['nages']
#        ages, k39s = zip(*[(a.age.nominal_value, a.k39) for a in analyses
#                           if a.group_id == group_id])
#        n = zip(nages, k39s)
#        n = sorted(n, key=lambda x:x[0])
#        aages, k39s = zip(*n)

#        k39, k39_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in k39s])
#        print ages, k39
#        self._add_plot(g, ages, k39, k39_errs,
#                           group_id=group_id,
#                           plotid=plotid,
#                           value_scale=value_scale
#                           )
    def _add_plateau_overlay(self, lp, bounds, c39s, age):
        ov = PlateauOverlay(component=lp, plateau_bounds=bounds,
                            cumulative39s=hstack(([0], c39s)),
                            y=age
                            )
        lp.overlays.append(ov)

        tool = PlateauTool(component=ov)
        lp.tools.insert(0, tool)

    def _get_metadata_label_text(self):
        # sigmas displayed as separate chars in Illustrator
        # use the 's' instead
        ustr = u'data {}s, age {}s'.format(self.plotter_options.step_nsigma,
                                           self.plotter_options.nsigma)
#        ustr = u'data 1\u03c3, age {}\u03c3'.format(self.plotter_options.nsigma)
#        ustr = 'data 1s, age {}s'.format(self.nsigma)
        return ustr
#============= EOF =============================================
