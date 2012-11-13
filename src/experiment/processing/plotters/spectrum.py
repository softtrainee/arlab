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
from traits.api import Any, Int
#============= standard library imports ========================
from numpy import array, Inf, where, average
#============= local library imports  ==========================
#from src.graph.stacked_graph import StackedGraph
from src.experiment.processing.plotters.results_tabular_adapter import SpectrumResults, \
    SpectrumResultsAdapter
from src.experiment.processing.plotters.plotter import Plotter, mStackedGraph
from src.stats.core import calculate_mswd
from enable.base_tool import BaseTool
from chaco.abstract_overlay import AbstractOverlay
#from enable.enable_traits import Pointer
from enable.colors import color_table
from src.experiment.processing.argon_calculations import age_equation
#from chaco.plot_label import PlotLabel
#from enable.font_metrics_provider import font_metrics_provider
#from chaco.data_label import DataLabel


class SpectrumTool(BaseTool):
    spectrum = Any
    group_id = Int
    def normal_left_down(self, event):
        pt = event.x, event.y
        if self.component.hittest(pt):

            d = self.component.map_data(pt)
#            print d
            cs = self.spectrum.cumulative39s[self.group_id]

            t = where(cs < d)[0]
            if len(t):
                tt = t[-1] + 1
            else:
                tt = 0

            sels = self.component.index.metadata['selections']
            self.component.index.metadata['selections'] = list(set(sels) ^ set([tt]))

            #replot excluding the selected point
            #plot origin with dash line
            #see ideogram for example
#            self.spectrum._update_graph()
            self.component.invalidate_and_redraw()

    def normal_mouse_move(self, event):
        pt = event.x, event.y
        if self.component.hittest(pt):
            event.window.set_pointer('cross')
        else:
            event.window.set_pointer('arrow')
#            print t
#            print cs, d
#            print t
#            print self.spectrum.cumulative39s[self.group_id].index(d)

#class SpectrumOverlay(AbstractOverlay):
#    group_id = 0
#    def overlay(self, component, gc, *args, **kw):
#        sels = self.component.index.metadata['selections']
#
#        xs = self.component.index.get_data()
#        ys = self.component.value.get_data()
#        n = len(xs)
#        xs = xs[1:n / 2 - 1:2]
#        yu = ys[1:n / 2 - 1:2]
#        yl = ys[n / 2::2][::-1]
##        print yl
#        for si in sels:
#            if si == 0:
#                p2 = 0, yl[si]
#                p3 = 0, yu[si]
#                p4 = xs[si], yu[si]
#                p5 = xs[si], yl[si]
#                p1 = p2
#                p6 = p5
#
#            else:
#                p2 = xs[si - 1], yl[si]
#                p3 = xs[si - 1], yu[si]
#                p4 = xs[si], yu[si]
#                p5 = xs[si], yl[si]
#
#                p1 = xs[si - 1], yu[si - 1]
#
#                if yl[si] > yu[si + 1]:
#                    p6 = xs[si], yu[si + 1]
#                else:
#                    p6 = xs[si], yl[si + 1]
#                p7 = p6
#                p8 = p5
#
#                p9 = p2
#                p10 = p1
#
#            pts = self.component.map_screen([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
#
#            pts[1][1] -= 0.5
#            pts[2][1] += 1
#            pts[3][1] += 1
#            pts[4][1] -= 0.5
#            pts[4][0] += 1
#
#            pts[6][0] -= 1
#            pts[7][0] -= 1
#            pts[8][0] += 1
#            pts[9][0] += 1
#            gc.set_fill_color((1, 0, 0))
#            gc.set_stroke_color((1, 0, 0))
#            gc.set_line_width(1)
##            gc.set_line_width(0)
##            print pts
#            x = pts[1][0]
#            y = pts[1][1]
#            w = pts[3][0] - pts[1][0]
#            h = pts[3][1] - pts[4][1]
##            gc.rect(x, y - 0.5, w + 1, h + 1)
#
#            gc.lines(pts)
#            gc.draw_path()


class SpectrumErrorOverlay(AbstractOverlay):
    def overlay(self, component, gc, *args, **kw):
        with gc:
            xs = self.component.index.get_data()
            ys = self.component.value.get_data()
            es = self.component.errors
            sels = self.component.index.metadata['selections']


    #        print sels
            n = len(xs)
            xs = xs.reshape(n / 2, 2)
            ys = ys.reshape(n / 2, 2)
            es = es.reshape(n / 2, 2)
            for i, ((xa, xb), (ya, yb), (ea, eb)) in enumerate(zip(xs, ys, es)):
                p1 = xa, ya - ea
                p2 = xa, ya + ea
                p3 = xb, ya - ea
                p4 = xb, ya + ea
                p1, p2, p3, p4 = self.component.map_screen([p1, p2, p3, p4])
                x = p1[0]
                y = p1[1]
                w = p3[0] - p1[0]
                h = p2[1] - p1[1]
                if i in sels:
                    gc.set_fill_color((1, 0, 0))
                else:
#                    gc.set_fill_color((0, 0, 0))
                    c = self.component.color
                    if isinstance(c, str):
                        c = color_table[c]

                    gc.set_fill_color(c)
                gc.rect(x, y, w + 1, h)
                gc.fill_path()

class Spectrum(Plotter):

    def _get_adapter(self):
        return SpectrumResultsAdapter

    def build(self, analyses=None, padding=None, excludes=None):
        if analyses is None:
            analyses = self.analyses
##
##        if padding is None:
##            padding = self.padding
#
        self.analyses = analyses
##        self.padding = padding
#
#        g = StackedGraph(panel_height=200, equi_stack=False,
#                         container_dict=dict(padding=5,
#                                             bgcolor='lightgray')
#                         )

        if padding is None:
            padding = [50, 5 , 35, 35]

        g = mStackedGraph(panel_height=200,
                            equi_stack=False,
                            container_dict=dict(padding=0),
                            plotter=self
                            )
        g.clear()

        g.new_plot(padding=padding)
        g.set_x_title('cumulative 39Ar')

        g.set_y_title('Age (Ma)')

        group_ids = list(set([a.group_id for a in analyses]))
        ma, mi = -Inf, Inf
        self.cumulative39s = []
        labels = []
        for group_id in group_ids:
            anals = [a for a in analyses if a.group_id == group_id]
#            print len(anals), len(analyses)
            miage, maage, label = self._add_spectrum(g, anals, group_id)

            ma = max(ma, maage)
            mi = min(mi, miage)
            labels.append(label)

        offset = (ma - mi) / len(labels) * 0.25
        for i, l in enumerate(labels):
            l.data_point = (50 + i,
#                            mi,
                            mi + offset * i
                            )
        g.set_y_limits(min=mi, max=ma, pad='0.1')
        self.graph = g
        return g

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

    def _calculate_spectrum(self, analyses, index_key, excludes=None):
        if excludes is None:
            excludes = []
        ages = [a.age for a in analyses]
        ar39s = [getattr(a, index_key).nominal_value for a in analyses]
        xs = []
        ys = []
        es = []
        sar = sum(ar39s)
        prev = 0
        c39s = []
#        steps = []
        for i, ((ai, ei), ar) in enumerate(zip(ages, ar39s)):
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

        return array(xs), array(ys), array(es), array(c39s)

    def _add_spectrum(self, g, analyses, group_id, index_key='k39'):
        xs, ys, es, c39s = self._calculate_spectrum(analyses, index_key)

#            steps.append((ai, ei))

#        self.steps.append(steps)
        self.cumulative39s.append(c39s)
#        ys.append(ai)
#        es.append(ei)
#        xs.append(100)

        #main age line
        ds, _p = g.new_series(xs, ys)

#        ds, _p = g.new_series(xs, ys,
##                             visible=False,
#                             color='transparent',
#                             line_style='dash')
        ds.index.sort_order = 'ascending'
        ds.index.on_trait_change(self._update_graph, 'metadata_changed')
#        #error box
#        xs = array(xs)
        ys = array(ys)
        es = array(es)
#
##        ox = xs[:]
#
##        xs.reverse()
#        xp = hstack((xs[:] , xs[::-1]))
        yl = (ys - es)[::-1]
        yu = ys + es
        miages = min(yl)
        maages = max(yu)
#        yp = hstack((yu, yl))
#
#        s, _p = g.new_series(x=xp, y=yp, type='polygon')
        sp = SpectrumTool(ds, spectrum=self, group_id=group_id)
        ds.tools.append(sp)
#    
        ds.errors = es
        sp = SpectrumErrorOverlay(component=ds, spectrum=self, group_id=group_id)
        ds.overlays.append(sp)

        mswd = calculate_mswd(ys, es)

        ages, errors = zip(*[(a.age[0], a.age[1]) for a in analyses])
        ages = array(ages)

        mean_age = ages.mean()
        mean_error = ages.std()

        weights = array(errors) ** -2

        weighted_mean_age, ss = average(ages, weights=weights, returned=True)
        weighted_mean_error = ss ** -0.5

#        weighted_mean_error
        tga = self._calculate_total_gas_age(analyses)
        #print 'tga', tga.nominal_value, tga.std_dev()
        #print 'mean', mean_age, mean_error
        #print 'wmean', weighted_mean_age, weighted_mean_error
        print '----------'

        age = mean_age
        error = mean_error
#        pl = DataLabel(
#                       component=ds,
#                       data_point=(50, miages),
#                       label_position='top right',
#                       label_text=u'{:0.3f} \u00b1{:0.3f}'.format(age, error),
#                       border_visible=False,
#                       bgcolor='transparent',
#                       show_label_coords=False,
#                       marker_visible=False,
#                       font='modern 24'
#                       )
#        
#        ds.overlays.append(pl)


        text = u'{:0.3f} \u00b1{:0.3f}'.format(age, error)
        dl = self._add_data_label(ds, text, (50, miages),
                                  arrow_visible=False,
                                  font='modern 18'
                                  )


        self.results.append(SpectrumResults(
                                           labnumber=self.get_labnumber(analyses),
                                           mean_age=mean_age,
                                           mean_error=mean_error,
                                           weighted_mean_age=weighted_mean_age,
                                           weighted_mean_error=weighted_mean_error,
                                           tga=tga.nominal_value,
                                           tga_error=tga.std_dev(),
                                           mswd=mswd
                                           ))

        return miages, maages, dl

    def _update_graph(self, new):
        g = self.graph
        for i, p in enumerate(g.plots):
            lp = p.plots['plot0'][0]
#            dp = p.plots['plot1'][0]
#            print pp
            sel = lp.index.metadata['selections']

            ages, errors = zip(*[a.age for j, a in enumerate(self.analyses) if j not in sel])
            mswd = calculate_mswd(ages, errors)
            self.results[i].mswd = mswd
#            if sel:
#                pass
#                #draw dp
#                dp.color = 'red'
#            else:
#                dp.color = 'transparent'

            #recalculate spectrum without selected
#            xs, ys, es, c39s = self._calculate_spectrum(self.analyses,
#                                                        'k39', excludes=sel)
#            lp.index.set_data(xs)
#            lp.value.set_data(ys)
#            lp.errors = es

        g.redraw()

    def get_ages(self, kind='weighted_mean'):
        return [(r.labnumber,
                 getattr(r, '{}_age'.format(r)),
                 getattr(r, '{}_error'.format(r)),) for r in self.results]


#============= EOF =============================================
