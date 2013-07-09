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
from traits.api import Any, Instance, Int, Property, List, on_trait_change, Dict, Bool, \
    Str, CInt, HasTraits, Event
from traitsui.api import View, Item, Group, HGroup, spring, VSplit, UItem, \
    HSplit, VGroup
from src.graph.graph import Graph
from src.viewable import ViewableHandler, Viewable

from src.graph.regression_graph import StackedRegressionGraph
from uncertainties import ufloat
# from src.helpers.traitsui_shortcuts import instance_item
from src.constants import PLUSMINUS
from src.processing.arar_age import ArArAge
# from src.helpers.formatting import floatfmt
from src.displays.display import DisplayController
from src.ui.text_table import TextTableAdapter, SimpleTextTableAdapter, \
    RatiosAdapter, ValueErrorAdapter, MultiTextTableAdapter
from src.ui.qt.text_table_editor import TextTableEditor, FastTextTableEditor
# from src.database.records.ui.analysis_summary import SignalAdapter
from src.experiment.display_signal import DisplaySignal, DisplayRatio, DisplayValue
from src.loggable import Loggable

#============= standard library imports ========================
#============= local library imports  ==========================

HEIGHT = 250
ERROR_WIDTH = 10
VALUE_WIDTH = 12

# class SignalAdapter(SimpleTextTableAdapter):
class SignalAdapter(MultiTextTableAdapter):
    columns = [
               [
                   ('Iso.', 'isotope', str, 6),
                   ('Det.', 'detector', str, 5),
                   ('Fit', 'fit', str, 4),
                   ('Intercept', 'intercept_value', None, VALUE_WIDTH),
                   (u'{}1s'.format(PLUSMINUS), 'intercept_error', None, ERROR_WIDTH),
                   (u'{}%'.format(PLUSMINUS), 'intercept_error_percent', str, ERROR_WIDTH - 1),
                   ('Raw(fA)', 'raw_value', None, VALUE_WIDTH),
                   (u'{}1s'.format(PLUSMINUS), 'raw_error', None, ERROR_WIDTH),
                   (u'{}%'.format(PLUSMINUS), 'raw_error_percent', str, ERROR_WIDTH - 1),
                ],
               [
                   ('Iso.', 'isotope', str, 6),
                   ('Det.', 'detector', str, 5),
                   ('Fit', 'baseline_fit', str, 4),
                   ('Baseline', 'baseline_value', None, VALUE_WIDTH),
                   (u'{}1s'.format(PLUSMINUS), 'baseline_error', None, ERROR_WIDTH),
                   (u'{}%'.format(PLUSMINUS), 'baseline_error_percent', str, ERROR_WIDTH - 1),
                   ('Blank', 'blank_value', None, VALUE_WIDTH),
                   (u'{}1s'.format(PLUSMINUS), 'blank_error', None, ERROR_WIDTH),
                   (u'{}%'.format(PLUSMINUS), 'blank_error_percent', str, ERROR_WIDTH - 1),
                ]
             ]


# class PlotPanelHandler(ViewableHandler):
#    pass

# class PlotPanel(Viewable):
class PlotPanel(Loggable):
#    automated_run = Any
    arar_age = Instance(ArArAge)
    sample = Str
    irradiation = Str
    graph = Instance(Graph)
#    window_x = 0
#    window_y = 0
#    window_title = ''
    plot_title = Str

    ncounts = Property(Int(enter_set=True, auto_set=False), depends_on='_ncounts')
    _ncounts = CInt

#    detector = None
    detectors = List
    fits = List
    isotopes = Property(depends_on='detectors')

    stack_order = 'bottom_to_top'
    series_cnt = 0

    ratio_display = Instance(DisplayController)
    signal_display = Instance(DisplayController)
    summary_display = Instance(DisplayController)
    fit_display = Instance(DisplayController)

    display_signals = List
    display_ratios = List
    display_summary = List
#    refresh = Event

    signals = Dict
    baselines = Dict
    blanks = Dict
    correct_for_baseline = Bool(True)
    correct_for_blank = Bool(True)
    isbaseline = Bool(False)

    ratios = ['Ar40:Ar36', 'Ar40:Ar39', ]
    info_func=None
    
    def info(self, *args, **kw):
        if self.info_func:
            self.info_func(*args, **kw)
        else:
            super(PlotPanel,self).info(*args, **kw)
    def reset(self):
        self.clear_displays()
        self.graph = self._graph_factory()

    def create(self, dets):
        '''
            dets: list of Detector instances
        '''

        g = self.graph
#        g.suppress_regression = True
#        # construct plot panels graph

        for i, det in enumerate(dets):
            g.new_plot(
                       title=self.plot_title if i == 0 else '',
                       ytitle='{} {} (fA)'.format(det.name, det.isotope),
                       xtitle='time (s)',
                       padding_left=60,
                       padding_right=10,
                       )

        g.set_x_limits(min=0, max=400)
#
#        g.suppress_regression = False
        self.detectors = dets

    def clear_displays(self):
        self._print_results()

    @on_trait_change('graph:regression_results')
    def _update_display(self, new):
        if new:
            arar_age = self.arar_age
            for iso, reg in zip(self.isotopes, new):
                try:
                    vv = reg.predict(0)
                    ee = reg.predict_error(0)
                    u = ufloat(vv, ee)
                    if self.isbaseline:
                        self.baselines[iso] = u
                        if arar_age:
                            arar_age.set_baseline(iso, (vv, ee))
                    else:
                        self.signals[iso] = u
                        if arar_age:
                            arar_age.set_isotope(iso, (vv, ee))

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
        self.display_signals = self._make_display_signals()
        self.display_ratios = self._make_display_ratios()
        self.display_summary = self._make_display_summary()

    def _make_display_summary(self):
        def factory(n, v):
            if isinstance(v, tuple):
                sv, se = v
            else:
                sv = v.nominal_value
                se = v.std_dev

            return DisplayValue(name=n, value=sv, error=se)

        arar_age = self.arar_age
        summary = []
        if arar_age:
            # call age first
            # loads all the other attrs
            age = arar_age.age
            summary = [
                       factory(name, v) for name, v in
                       [
                        ('Age', age),
                        ('', ('', arar_age.age_error_wo_j)),
                        ('J', arar_age.j),
                        ('K/Ca', arar_age.kca),
                        ('K/Cl', arar_age.kcl),
                        ('*40Ar %', arar_age.rad40_percent),
                        ('IC', arar_age.ic_factor)
                        ]
                     ]

        return summary

    def _make_display_ratios(self):
        cfb = self.correct_for_baseline
        cfbl = self.correct_for_blank
        base = self.baselines
        blank = self.blanks

        def factory(n, d, scalar=1):
            r = DisplayRatio(name='{}/{}'.format(n, d))
            try:
                sn = self.signals[n]
                sd = self.signals[d]
            except KeyError:
                return r

            for ci, dd in ((cfb, base), (cfbl, blank)):
                if ci:
                    try:
                        sn -= dd[n]
                        sd -= dd[d]
                    except KeyError:
                        pass
            try:
                rr = (sn / sd) * scalar
                v, e = rr.nominal_value, rr.std_dev
            except ZeroDivisionError:
                v, e = 0, 0
            r.value = v
            r.error = e

            return r

        ratios = [('Ar40', 'Ar39'), ('Ar40', 'Ar36')]
        return [factory(*args) for args in ratios]

    def _make_display_signals(self):
        sig = self.signals
        base = self.baselines
        blank = self.blanks
        cfb = self.correct_for_baseline
        cfbl = self.correct_for_blank
        def factory(det, fi):
            iso = det.isotope
            if iso in sig:
                v = sig[iso]
            else:
                v = ufloat(0, 0)

            if iso in base:
                bv = base[iso]
            else:
                bv = ufloat(0, 0)

            if iso in blank:
                blv = blank[iso]
            else:
                blv = ufloat(0, 0)

            iv = v
            if cfb:
                iv = iv - bv

            if cfbl:
                iv = iv - blv

            return DisplaySignal(isotope=iso,
                                 detector=det.name,
                                 fit=fi[0].upper(),
                                 intercept_value=iv.nominal_value,
                                 intercept_error=iv.std_dev,
                                 raw_value=v.nominal_value,
                                 raw_error=v.std_dev,
                                 baseline_value=bv.nominal_value,
                                 baseline_error=bv.std_dev,
                                 blank_value=blv.nominal_value,
                                 blank_error=blv.std_dev,
                                 )

        return [factory(det, fi) for det, fi in zip(self.detectors, self.fits)]

    def _get_ncounts(self):
        return self._ncounts

    def _set_ncounts(self, v):
        self.info('{} set to terminate after {} counts'.format(self.plot_title, v))
        self._ncounts = v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        return StackedRegressionGraph(container_dict=dict(padding=5, bgcolor='gray',
                                                stack_order=self.stack_order
                                             ),
                                             bind_index=False,
                                             use_data_tool=False,
                                             use_inspector_tool=True,
                                             padding_bottom=35
                                      )

    def graph_view(self):
        gg = self._get_graph_group()
        gg.height = 0.90

        v = View(
                  VSplit(
                        gg,
                        Group(
                              Item('ncounts'),
                              label='Controls',
                             ),
                        )
                 )
        return v

    def summary_view(self):
        g = self._get_display_group()
#         g.orientation = 'vertical'
#         g.layout = 'normal'
        v = View(g)
        return v

    def _get_display_group(self):
        results_grp = Group(
#                             HGroup(
#                                   Item('correct_for_baseline'),
#                                   Item('correct_for_blank'),
#                                   spring),
                            UItem('display_signals',
                                  editor=FastTextTableEditor(adapter=SignalAdapter(),
                                                         bg_color='lightyellow',
                                                         header_color='lightgray',
                                                         font_size=10
                                                         ),
                                         width=0.8
                                         ),
                                label='Results'
                            )

        ratios_grp = Group(UItem('display_ratios',
                                         editor=FastTextTableEditor(adapter=RatiosAdapter(),
                                                         bg_color='lightyellow',
                                                         header_color='lightgray'
                                                         ),
                                        ),
                           label='Ratios'
                           )
        summary_grp = Group(
                           UItem('display_summary',
                                 editor=FastTextTableEditor(adapter=ValueErrorAdapter(),
                                                        bg_color='lightyellow',
                                                        header_color='lightgray'
                                                        )
                                 ),
                            label='Summary'
                          )
        display_grp = Group(
                            results_grp,
                            ratios_grp,
                            summary_grp,
                            layout='tabbed'
                            )

        return display_grp

    def _get_graph_group(self):
        graph_grp = Item('graph', show_label=False,
                         style='custom')
        return graph_grp

    def traits_view(self):
        gg = self._get_graph_group()
        gg.height = 0.72

        v = View(
                 VSplit(
                        gg,
                        VGroup(
                              Item('ncounts'),
                               self._get_display_group()
                             ),

                        ),
#                 width=650,
#                 height=0.9,
#                 x=self.window_x,
#                 y=self.window_y,
#                 title=self.window_title,
#                 handler=PlotPanelHandler
                 )
        return v

    def _get_isotopes(self):
        return [d.isotope for d in self.detectors]
#============= EOF =============================================

#    def _display_factory(self):
#        return  DisplayController(height=HEIGHT,
#                               default_color='black',
#                               default_size=12,
# #                               scroll_to_bottom=False,
#                               bg_color='#FFFFCC'
#                               )
#===============================================================================
# defaults
#===============================================================================
#    def _fit_display_default(self):
#        return self._display_factory()

#    def _summary_display_default(self):
#        return self._display_factory()

#    def _signal_display_default(self):
#        return self._display_factory()

#    def _ratio_display_default(self):
#        return self._display_factory()

#    def _get_fit(self, reg):
#        try:
#            deg = reg.degree
#            if deg in [1, 2, 3]:
#                return ['L', 'P', 'C'][deg - 1]
#        except AttributeError:
#            return reg.error_calc

#    def closed(self, isok):
#        self.close_event = True
#        self.automated_run.truncate('Immediate')
#        return isok
# def _print_signals(self, display):
#        def get_value(iso):
#            try:
#                us = self.signals[iso]
#            except KeyError:
#                us = ufloat(0, 0)
#
#            ubs = ufloat(0, 0)
#            ubl = ufloat(0, 0)
#            if self.correct_for_baseline:
#                try:
#                    ubs = self.baselines[iso]
#                except KeyError:
#                    pass
#            if self.correct_for_blank:
#                try:
#                    ubl = self.blanks[iso]
#                except KeyError:
#                    pass
#
#            return us - ubs - ubl
#
#        self._print_('', get_value, display)
#        self.add_text(display, ' ' * 80, underline=True)
#
#
#    def _print_baselines(self, display):
#        def get_value(iso):
#            try:
#                ub = self.baselines[iso]
#            except KeyError:
#                ub = ufloat(0, 0)
#            return ub
#
#        self._print_('bs', get_value, display)
#
#    def _print_blanks(self, display):
#        def get_value(iso):
#            try:
#                ub = self.blanks[iso]
#            except KeyError:
#                ub = ufloat(0, 0)
#            return ub
#
#        self._print_('bl', get_value, display)
#
#    def _print_(self, name, get_value, display):
# #        display = self.signal_display
#        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)
#
#        def func(iso):
#            uv = get_value(iso)
#            vv = uv.nominal_value
#            ee = uv.std_dev
#
#            v = pad('{:0.5f}'.format(vv))
#            e = pad('{:0.6f}'.format(ee), n=6)
#            pe = self._get_pee(uv)
# #             v = v + u' {}'.format(PLUSMINUS) + e + self._get_pee(uv)
#
#            return '{}{}={} {}{} {}'.format(iso, name, v, PLUSMINUS, e, pe)
#
# #             return '{}{}={:>10s}'.format(iso, name, v)
#
#        ts = [func(iso) for iso in self.isotopes]
#        self.add_text(display, '\n'.join(ts))
#
#    def _get_pee(self, uv, error=None):
#        if uv is not None:
#            vv = uv.nominal_value
#            ee = uv.std_dev
#        else:
#            vv, ee = 0, 0
#
#        if error is not None:
#            ee = error
#
#        try:
#            pee = abs(ee / vv * 100)
#        except ZeroDivisionError:
#            pee = 0
#
#        return '({:0.2f}%)'.format(pee)
# def add_text(self, disp, *args, **kw):
#        kw['gui'] = False
#        disp.add_text(*args, **kw)
#
#    def _floatfmt(self, f, n=5):
#        return floatfmt(f, n)
#
#    def _print_parameter(self, display, name, uvalue, sig_figs=(3, 4), **kw):
#        name = '{:<15s}'.format(name)
#
#        if not uvalue:
#            v, e = 0, 0
#        else:
#            v, e = uvalue.nominal_value, uvalue.std_dev
#
#        v = self._floatfmt(v, sig_figs[0])
#        e = self._floatfmt(e, sig_figs[1])
#
#        msg = u'{}= {} {}{}{}'.format(name, v, PLUSMINUS, e, self._get_pee(uvalue))
#        self.add_text(display, msg, **kw)
#
#    def _print_summary(self, display):
#        self.add_text(display, '{:<15s}= {}'.format('Sample', self.sample))
#        self.add_text(display, '{:<15s}= {}'.format('Irradiation', self.irradiation))
#
#        arar_age = self.arar_age
#        if arar_age:
#            # call age first
#            # loads all the other attrs
#            age = arar_age.age
#
#            j = arar_age.j
#            rad40 = arar_age.rad40_percent
#            kca = arar_age.kca
#            kcl = arar_age.kcl
#            ic = arar_age.ic_factor
#
#            self._print_parameter(display, 'Age', age)
#
#            err = arar_age.age_error_wo_j
#            pee = self._get_pee(age, error=err)
#            self.add_text(display, '{:<15s}=       {:0.4f}{}'.format('Error w/o J', err, pee))
#
#            self._print_parameter(display, 'J', j, sig_figs=(5, 6))
#            self._print_parameter(display, 'ICFactor', ic)
#            self._print_parameter(display, '% rad40', rad40)
#            self._print_parameter(display, 'K/Ca', kca)
#            self._print_parameter(display, 'K/Cl', kcl)
#
#    def _print_fits(self, display):
#        fits = self.fits
#        detectors = self.detectors
#        for fit, det in zip(fits, detectors):
#            self.add_text(display, '{} {}= {}'.format(det.name,
#                                                      det.isotope, fit))
#
# #        for det, (iso, fit) in self.fits:
# #            self.add_text(display, '{} {}= {}'.format(det, iso, fit))
#
#    def _print_ratios(self, display):
#        pad = lambda x, n = 9:'{{:>{}s}}'.format(n).format(x)
#
# #        display = self.ratio_display
#        cfb = self.correct_for_baseline
#
#        def func(ra):
#            u, l = ra.split(':')
#            try:
#                ru = self.signals[u]
#                rl = self.signals[l]
#            except KeyError:
#                return ''
#
#            if cfb:
#                bu = ufloat(0, 0)
#                bl = ufloat(0, 0)
#                try:
#                    bu = self.baselines[u]
#                    bl = self.baselines[l]
#                except KeyError:
#                    pass
#                try:
#                    rr = (ru - bu) / (rl - bl)
#                except ZeroDivisionError:
#                    rr = ufloat(0, 0)
#            else:
#                try:
#                    rr = ru / rl
#                except ZeroDivisionError:
#                    rr = ufloat(0, 0)
#
#            res = '{}/{}={} '.format(u, l, pad('{:0.4f}'.format(rr.nominal_value))) + \
#                  PLUSMINUS + pad(format('{:0.4f}'.format(rr.std_dev)), n=6) + \
#                    self._get_pee(rr)
#            return res
#
#        ts = [func(ra) for ra in self.ratios]
#        self.add_text(display, '\n'.join(ts))
#        self.add_text(display, ' ' * 80, underline=True)
