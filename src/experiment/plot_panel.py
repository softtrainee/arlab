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
from traits.api import Any, Instance, Int, Property, List, on_trait_change, Dict, Bool
from traitsui.api import View, Item, Group, HGroup, spring
from src.graph.graph import Graph
from src.viewable import ViewableHandler, Viewable
from src.displays.rich_text_display import RichTextDisplay
from src.graph.regression_graph import StackedRegressionGraph
from uncertainties import ufloat
from pyface.timer.do_later import do_later
from src.helpers.traitsui_shortcuts import instance_item
from src.constants import PLUSMINUS
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

#    detector = None
    detectors = List
    fits = List
    isotopes = Property(depends_on='detectors')

    stack_order = 'bottom_to_top'
    series_cnt = 0
    ratio_display = Instance(RichTextDisplay)
    signal_display = Instance(RichTextDisplay)
    summary_display = Instance(RichTextDisplay)
    fit_display = Instance(RichTextDisplay)

    signals = Dict
    baselines = Dict
    blanks = Dict
    correct_for_baseline = Bool(True)
    correct_for_blank = Bool(True)
    isbaseline = Bool(False)

    ratios = ['Ar40:Ar36', 'Ar40:Ar39', ]

    @on_trait_change('graph:regression_results')
    def _update_display(self, new):
        if new:
            arar_age = self.automated_run.arar_age
            for iso, reg in zip(self.isotopes, new):
                try:
                    vv = reg.predict(0)
                    ee = abs(reg.predict_error(0))
                    if self.isbaseline:
                        self.baselines[iso] = u = ufloat((vv, ee))
                        if arar_age:
                            arar_age.signals['{}bs'.format(iso)] = u
                    else:
                        self.signals[iso] = u = ufloat((vv, ee))
                        if arar_age:
                            arar_age.signals[iso] = u

                except TypeError, e:
                    print e
                    break
                except AssertionError, e:
                    print e
                    continue
            else:
                if arar_age:
                    arar_age.age_dirty = True
                self._print_results()

    @on_trait_change('correct_for_baseline, correct_for_blank')
    def _print_results(self):
        def wrapper(display, *args):
            display.freeze()
            display.clear(gui=False)
            for ai in args:
                ai(display)
            display.thaw()

        def func():
            wrapper(self.signal_display,
                    self._print_signals,
                    self._print_baselines
                    )
            wrapper(self.ratio_display,
                    self._print_ratios,
                    self._print_blanks
                    )
            wrapper(self.summary_display,
                    self._print_summary
                    )
            wrapper(self.fit_display,
                    self._print_fits
                    )

        do_later(func)

    def add_text(self, disp, *args, **kw):
        kw['gui'] = False
        disp.add_text(*args, **kw)

    def _print_parameter(self, display, name, uvalue, **kw):
        name = '{:<15s}'.format(name)
        msg = u'{}= {:0.3f} {}{:0.4f}{}'.format(name,
                                                    uvalue.nominal_value,
                                                    PLUSMINUS,
                                                    uvalue.std_dev(),
                                                    self._get_pee(uvalue)
                                                    )
        self.add_text(display, msg, **kw)

    def _print_summary(self, display):
        arar_age = self.automated_run.arar_age
        if arar_age:
            #call age first
            #loads all the other attrs
            age = arar_age.age

            j = ufloat(arar_age.j)
            rad40 = arar_age.rad40_percent
            kca = arar_age.kca
            kcl = arar_age.kcl

            self._print_parameter(display, 'Age', age)
            self._print_parameter(display, 'J', j)
            self._print_parameter(display, '% rad40', rad40)
            self._print_parameter(display, 'K/Ca', kca)
            self._print_parameter(display, 'K/Cl', kcl)

    def _print_fits(self, display):
        fits = self.fits
        detectors = self.detectors
        for fit, det in zip(fits, detectors):
            self.add_text(display, '{} {}= {}'.format(det.name,
                                                      det.isotope, fit))

#        for det, (iso, fit) in self.fits:
#            self.add_text(display, '{} {}= {}'.format(det, iso, fit))

    def _print_ratios(self, display):
        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)

#        display = self.ratio_display
        cfb = self.correct_for_baseline

        def func(ra):
            u, l = ra.split(':')
            try:
                ru = self.signals[u]
                rl = self.signals[l]
            except KeyError:
                return ''

            if cfb:
                bu = ufloat((0, 0))
                bl = ufloat((0, 0))
                try:
                    bu = self.baselines[u]
                    bl = self.baselines[l]
                except KeyError:
                    pass
                rr = (ru - bu) / (rl - bl)
            else:
                rr = ru / rl

            res = '{}/{}={} '.format(u, l, pad('{:0.4f}'.format(rr.nominal_value))) + \
                  PLUSMINUS + pad(format('{:0.4f}'.format(rr.std_dev())), n=6) + \
                    self._get_pee(rr)
            return res

        ts = [func(ra) for ra in self.ratios]
        self.add_text(display, '\n'.join(ts))
        self.add_text(display, ' ' * 80, underline=True)

    def _print_signals(self, display):
        def get_value(iso):
            try:
                us = self.signals[iso]
            except KeyError:
                us = ufloat((0, 0))

            ubs = ufloat((0, 0))
            ubl = ufloat((0, 0))
            if self.correct_for_baseline:
                try:
                    ubs = self.baselines[iso]
                except KeyError:
                    pass
            if self.correct_for_blank:
                try:
                    ubl = self.blanks[iso]
                except KeyError:
                    pass

            return us - ubs - ubl

        self._print_('', get_value, display)
        self.add_text(display, ' ' * 80, underline=True)


    def _print_baselines(self, display):
        def get_value(iso):
            try:
                ub = self.baselines[iso]
            except KeyError:
                ub = ufloat((0, 0))
            return ub

        self._print_('bs', get_value, display)

    def _print_blanks(self, display):
        def get_value(iso):
            try:
                ub = self.blanks[iso]
            except KeyError:
                ub = ufloat((0, 0))
            return ub

        self._print_('bl', get_value, display)

    def _print_(self, name, get_value, display):
#        display = self.signal_display
        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)

        def func(iso):
            uv = get_value(iso)
            vv = uv.nominal_value
            ee = uv.std_dev()

            v = pad('{:0.5f}'.format(vv))
            e = pad('{:0.6f}'.format(ee), n=6)
            v = v + u' {}'.format(PLUSMINUS) + e + self._get_pee(uv)
            return '{}{}={:>10s}'.format(iso, name, v)

        ts = [func(iso) for iso in self.isotopes]
        self.add_text(display, '\n'.join(ts))

    def _get_pee(self, uv):
        vv = uv.nominal_value
        ee = uv.std_dev()
        try:
            pee = abs(ee / vv * 100)
        except ZeroDivisionError:
            pee = 0

        return '({:0.2f}%)'.format(pee)

#    def _get_fit(self, reg):
#        try:
#            deg = reg.degree
#            if deg in [1, 2, 3]:
#                return ['L', 'P', 'C'][deg - 1]
#        except AttributeError:
#            return reg.error_calc

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
                                      bind_index=False,
                                      use_data_tool=False,
                                      use_inspector_tool=True
                                      )
    def traits_view(self):
        v = View(
                 Item('graph', show_label=False, style='custom'),
                 Group(
                     Group(
                           HGroup(
                                  Item('correct_for_baseline'),
                                  Item('correct_for_blank'),
                                  spring),
                           HGroup(
                               Item('signal_display', width=0.5, show_label=False, style='custom'),
                               Item('ratio_display', width=0.5, show_label=False, style='custom'),
                           ),
                           label='Results'
                           ),
                     Group(
                           instance_item('fit_display'),
                           label='Fit'),
                     Group(
                           instance_item('summary_display'),
                           label='Summary'),
                     Group(
                           Item('ncounts'),
                           label='Controls',
                           ),
                       layout='tabbed'
                       ),
                 width=600,
                 height=0.85,
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
    def _fit_display_default(self):
        return RichTextDisplay(height=220,
                               default_color='black',
                               default_size=12,
                               scroll_to_bottom=False,
                               bg_color='#FFFFCC'
                               )
    def _summary_display_default(self):
        return RichTextDisplay(height=220,
                               default_color='black',
                               default_size=12,
                               scroll_to_bottom=False,
                               bg_color='#FFFFCC'
                               )

    def _signal_display_default(self):
        return RichTextDisplay(height=220,
                               default_color='black',
                               default_size=12,
                               scroll_to_bottom=False,
                               bg_color='#FFFFCC'
#                               width=0.25
                               )
    def _ratio_display_default(self):
        return RichTextDisplay(height=220,
                               default_color='black',
                               default_size=12,
                               scroll_to_bottom=False,
                               bg_color='#FFFFCC'
#                               width=0.75
                               )
#============= EOF =============================================
