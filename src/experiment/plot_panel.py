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
from traits.api import HasTraits, Any, Instance, Int, Property, List, on_trait_change, Dict, Bool
from traitsui.api import View, Item, Group, HGroup, spring
from src.graph.graph import Graph
from src.viewable import ViewableHandler, Viewable
from src.displays.rich_text_display import RichTextDisplay
from src.graph.regression_graph import StackedRegressionGraph
from uncertainties import ufloat
#============= standard library imports ========================
#from numpy import Inf
#from pyface.timer.do_later import do_later
#============= local library imports  ==========================
class PlotPanelHandler(ViewableHandler):
    pass
class PlotPanel(Viewable):
    automated_run = Any
    graph = Instance(Graph)
    window_x = 0
    window_y = 0
    window_title = ''

    ncounts = Property(Int(enter_set=True, auto_set=False), depends_on='_ncounts')
    _ncounts = Int

    detector = None
    detectors = List
    isotopes = Property(depends_on='detectors')

    stack_order = 'bottom_to_top'
    series_cnt = 0
    ratio_display = Instance(RichTextDisplay)
    signal_display = Instance(RichTextDisplay)

    signals = Dict
    baselines = Dict
    correct_for_baseline = Bool(True)
    isbaseline = Bool(False)

    ratios = ['Ar40:Ar36', 'Ar40:Ar39', ]

    @on_trait_change('graph:regression_results')
    def _update_display(self, new):
        if new:
            for iso, reg in zip(self.isotopes, new):
                try:
                    vv = reg.coefficients[-1]
                    ee = reg.coefficient_errors[-1]
                    if self.isbaseline:
                        self.baselines[iso] = ufloat((vv, ee))
                    else:
                        self.signals[iso] = ufloat((vv, ee))
                except TypeError:
                    break
            else:
                self._print_results()

    @on_trait_change('correct_for_baseline')
    def _print_results(self):
        def func():
            self._print_signals()
            self._print_ratios()
#        do_later(func)
        func()

    def _print_ratios(self):
        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)

        display = self.ratio_display
        display.freeze()
        display.clear()
        cfb = self.correct_for_baseline

        regs = self.graph.regressors
        def func(ra):
#        for ra in self.ratios:
            u, l = ra.split(':')
            try:
                ru = self.signals[u]
                rl = self.signals[l]
            except KeyError:
                return ''

            try:
                ruf = self._get_fit(regs[self.isotopes.index(u)])
                rlf = self._get_fit(regs[self.isotopes.index(l)])
            except IndexError:
                return ''

            if cfb:
                bu = ufloat((0, 0))
                bl = ufloat((0, 0))
                try:
                    bu = self.baselines[u]
                    bl = self.baselines[u]
                except KeyError:
                    pass
                rr = (ru - bu) / (rl - bl)
            else:
                rr = ru / rl

            res = '{}/{}={} '.format(u, l, pad('{:0.4f}'.format(rr.nominal_value))) + \
                  u'\u00b1 ' + pad(format('{:0.4f}'.format(rr.std_dev())), n=6) + \
                    pad(' {}/{} '.format(ruf, rlf), n=4) + \
                    self._get_pee(rr)
            return res

        ts = [func(ra) for ra in self.ratios]
        display.add_text('\n'.join(ts))
        display.thaw()

    def _print_signals(self):
        display = self.signal_display
        cfb = self.correct_for_baseline
        display.freeze()
        display.clear()
        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)

#        ts = []
#        for iso in self.isotopes:
#            try:
#                us = self.signals[iso]
#            except KeyError:
#                us = ufloat((0, 0))
#
#            ub = ufloat((0, 0))
#            if cfb:
#                try:
#                    ub = self.baselines[iso]
#                except KeyError:
#                    pass
#
#            uv = us - ub
#            vv = uv.nominal_value
#            ee = uv.std_dev()
##            try:
##                pee = abs(ee / vv * 100)
##            except ZeroDivisionError:
##                pee = 0
#
#            v = pad('{:0.4f}'.format(vv))
#            e = pad('{:0.4f}'.format(ee), n=6)
#            v = v + u' \u00b1 ' + e + self._get_pee(uv)
#            ts.append('{}={:>10s}'.format(iso, v))

        def func(iso):
            try:
                us = self.signals[iso]
            except KeyError:
                us = ufloat((0, 0))

            ub = ufloat((0, 0))
            if cfb:
                try:
                    ub = self.baselines[iso]
                except KeyError:
                    pass

            uv = us - ub
            vv = uv.nominal_value
            ee = uv.std_dev()
#            try:
#                pee = abs(ee / vv * 100)
#            except ZeroDivisionError:
#                pee = 0

            v = pad('{:0.4f}'.format(vv))
            e = pad('{:0.4f}'.format(ee), n=6)
            v = v + u' \u00b1 ' + e + self._get_pee(uv)
            return '{}={:>10s}'.format(iso, v)

        ts = [func(iso) for iso in self.isotopes]
        display.add_text('\n'.join(ts))
        display.thaw()

    def _get_pee(self, uv):
        vv = uv.nominal_value
        ee = uv.std_dev()
        try:
            pee = abs(ee / vv * 100)
        except ZeroDivisionError:
            pee = 0

        return '({:0.2f}%)'.format(pee)

    def _get_fit(self, reg):
        try:
            deg = reg.degree
            if deg in [1, 2, 3]:
                return ['L', 'P', 'C'][deg - 1]
        except AttributeError:
            return reg.error_calc

    def close(self, isok):
        self.automated_run.truncate('Immediate')
        return isok

    def _get_ncounts(self):
        return self._ncounts

    def _set_ncounts(self, v):
        self.info('{} set to terminate after {} counts'.format(self.window_title, v))
        self._ncounts = v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        return StackedRegressionGraph(container_dict=dict(padding=5, bgcolor='gray',
                                                stack_order=self.stack_order
                                             ),
                                      use_data_tool=False
                                      )
    def traits_view(self):
        v = View(
                 Item('graph', show_label=False, style='custom'),
                 Group(
                     Group(
                           HGroup(Item('correct_for_baseline'), spring),
                           HGroup(
                               Item('signal_display', width=0.4, show_label=False, style='custom'),
                               Item('ratio_display', width=0.6, show_label=False, style='custom'),
                           ),
                           label='Results'
                           ),
                     Group(
                           Item('ncounts'),
                           label='Controls',
                           ),
                       layout='tabbed'
                       ),
                 width=600,
                 height=725,
                 x=self.window_x,
                 y=self.window_y,
                 title=self.window_title,
                 handler=PlotPanelHandler
                 )
        return v

    def _get_isotopes(self):
        return [d.isotope for d in self.detectors]
#===============================================================================
# defaults
#===============================================================================
    def _signal_display_default(self):
        return RichTextDisplay(height=100,
                               default_color='black',
                               default_size=12,
#                               width=0.25
                               )
    def _ratio_display_default(self):
        return RichTextDisplay(height=100,
                               default_color='black',
                               default_size=12,
#                               width=0.75
                               )
#============= EOF =============================================
