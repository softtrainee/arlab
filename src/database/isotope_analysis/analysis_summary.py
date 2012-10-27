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
from traits.api import Instance
from traitsui.api import View, Item
#============= standard library imports ========================
import re
from uncertainties import ufloat
#============= local library imports  ==========================
from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.fit_selector import FitSelector
import math

PLUSMINUS = unicode('\xb1')
PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)
class AnalysisSummary(Summary):
    fit_selector = Instance(FitSelector)

    def _build_summary(self):
        d = self.display
        d.clear()

        record = self.record

        isos = record.isos
        if isos:
            isos = sorted(isos, key=lambda x: re.sub('\D', '', x))
            isos.reverse()
        else:
            isos = []

        d.add_text('Labnumber={}-{}'.format(record.labnumber, record.aliquot), bold=True)
        d.add_text('date={} time={}'.format(record.rundate, record.runtime), bold=True)
        j, j_err = record.j
        d.add_text('J={} {}{}'.format(j, u'\u00b1', j_err))
        def floatfmt(m, i=6):
            if abs(m) < 10 ** -i:
                return '{:0.2e}'.format(m)
            else:
                return '{{:0.{}f}}'.format(i).format(m)
#        floatfmt = lambda m, i = 5: '{{:0.{}f}}'.format(i).format(m)
        width = lambda m, i: '{{:<{}s}}'.format(i).format(m)

        #add header
        columns = [('Iso.', 5),
                   ('Int.', 12), (PLUSMINUS_ERR, 20),
                   ('Fit', 11),
                   ('Baseline', 12), (PLUSMINUS_ERR, 18),
                   ('Blank', 12), (PLUSMINUS_ERR, 18)
                   ]
        widths = [w for _, w in columns]

        msg = 'Iso.   Int.             ' + PLUSMINUS_ERR + '                      Fit'
        msg += '         Baseline     ' + PLUSMINUS_ERR + '                    Blank         ' + PLUSMINUS_ERR
#        msg = ''.join([width(m, w) for m, w in columns])
        d.add_text(msg, underline=True, bold=True)

        #add isotopes
        n = len(isos) - 1
        for i, iso in enumerate(isos):
            self._make_signals(n, i, iso, floatfmt, width, widths)
#        for i, iso in enumerate(isos):
#            self._make_blanks(n, i, iso, floatfmt, width, widths)

#        d.add_text('\n')

        m = 'Baseline Corrected Signals'
        d.add_text('{:<39s}'.format(m), underline=True, bold=True)

#        signals = dict()
        for i, iso in enumerate(isos):
            self._make_corrected_signals(n, i, iso, floatfmt, width, widths)

        m = 'Fully Corrected Signals'
        d.add_text('{:<39s}'.format(m), underline=True, bold=True)

#        signals = dict()
        for i, iso in enumerate(isos):
            self._make_corrected_signals(n, i, iso, floatfmt, width, widths,
                                         fully_correct=True)

        m = 'Corrected Values'
        d.add_text('{:<39s}'.format(m), underline=True, bold=True)
#
        rec = self.record
        arar_result = rec.arar_result
        if arar_result:
            def make_ratio(r, nom, dem, scalar=1, underline=False):
                try:
                    rr = nom / dem * scalar
                    v, e = rr.nominal_value, rr.std_dev()
                except ZeroDivisionError:
                    v, e = 0, 0

                ee = '{} ({})'.format(floatfmt(e), self.calc_percent_error(v, e))
                ms = [floatfmt(v), ee]
                msg = ''.join([width(m, 15) for m in ms])
                d.add_text(width(r, 10), bold=True, new_line=False,
                           underline=underline)
                d.add_text(msg, underline=underline, size=11)

            rad40 = arar_result['rad40']
            tot40 = arar_result['tot40']
            k39 = arar_result['k39']
            atm36 = arar_result['atm36']

            make_ratio('%40*', rad40, tot40, scalar=100)
            make_ratio('40/36', tot40, atm36)
            make_ratio('40/39', tot40, k39)
            make_ratio('40*/36', rad40, atm36)
            make_ratio('40*/39', rad40, k39, underline=True)

        d.add_text(' ')

        v, e = self.record.age
        e = u' \u00b1' + '{:0.3f}'.format(e)
        d.add_text('age={:0.3f} {}'.format(v, e))

    def _make_corrected_signals(self, n, i, iso, floatfmt, width, widths,
                                fully_correct=False):
        d = self.display

        pi = n - i
        sig, base = self._get_signal_and_baseline(pi)

        s = sig - base
        if fully_correct:
            arar = self.record.arar_result
            if arar:
                iso = iso.replace('Ar', 's')
                s = arar[iso]


        sv = s.nominal_value
        se = s.std_dev()
        bse = '{} ({})'.format(floatfmt(se), self.calc_percent_error(sv, se))
        msgs = [
#                iso,
                floatfmt(sv),
                bse
                ]
        msg = ''.join([width(m, w) for m, w in zip(msgs, widths[1:])])
        if i == n:
            msg += '\n'
#        d.add_text(msg, underline=i == n)
        d.add_text(width(iso, widths[0]), bold=True,
                  new_line=False,
                  underline=i == n)
        d.add_text(msg, size=11, underline=i == n)
        return s

    def _get_signal_and_baseline(self, pi):
        sg = self.record.signal_graph
        bg = self.record.baseline_graph

        reg = sg.regressors[pi]
        inter = reg.predict(0)
        inter_err = reg.coefficient_errors[-1]
        if bg:
            reg = bg.regressors[pi]
            base = reg.predict(0)
            base_err = reg.coefficient_errors[-1]
        else:
            base = 0
            base_err = 0

        return ufloat((inter, inter_err)), ufloat((base, base_err))

    def _make_signals(self, n, i, iso, floatfmt, width, widths):
        sg = self.record.signal_graph
        d = self.display
        pi = n - i
        fit = sg.get_fit(pi) if sg else '---'
        sig, base = self._get_signal_and_baseline(pi)

        blank = self.record.signals['{}bl'.format(iso)]
        blank = blank.uvalue
        bls = blank.nominal_value
        ble = blank.std_dev()

        sv = sig.nominal_value
        se = sig.std_dev()

        bs = base.nominal_value
        be = base.std_dev()

        sse = '{} ({})'.format(floatfmt(se), self.calc_percent_error(sv, se))
        bse = '{} ({})'.format(floatfmt(be), self.calc_percent_error(bs, be))
        ble = '{} ({})'.format(floatfmt(ble), self.calc_percent_error(bls, ble))

        msgs = [
#                iso,
                floatfmt(sv),
                sse,
                fit,

                floatfmt(bs),
                bse,
                floatfmt(bls),
                ble
                ]

        msg = ''.join([width(m, w) for m, w in zip(msgs, widths[1:])])
        if i == n:
            msg += '\n'
#        print width(iso, widths[0]), widths[0]
#        d.add_text(iso, bold=True,
#                  new_line=False,
#                  underline=i == n)
        d.add_text(width(iso, 6),
                   bold=True,
                  new_line=False,
                  underline=i == n)
        d.add_text(msg, size=11, underline=i == n)

#    def _display_default(self):
#        return RichTextDisplay(default_size=12,
#                               width=700,
#                               selectable=True,
#                               default_color='black',
#                               font_name='Bitstream Vera Sans Mono'
##                               font_name='Monaco'
#                               )

    def traits_view(self):
        v = View(Item('display', height=0.8, show_label=False, style='custom'),
                 Item('fit_selector', height=0.2, show_label=False, style='custom'))
        return v


#============= EOF =============================================
#class AnalysisSummary2(HasTraits):
#    age = Float
#    error = Float
#    record = Any
#
#    summary = Property(depends_on='age,err')
#
#    header1 = ['ID', 'Date', 'Time']
#    header2 = ['Detector', 'Signal']
#
#    def _get_summary(self):
#        from jinja2 import Template
#        doc = '''
#{{header1}}
#{{data1}}
#
#Name:{{record.filename}}
#Root:{{record.directory}}
#
#{{header2}}
#{%- for k,v in signals %}
#{{k}}\t{{v}} 
#{%- endfor %}
#
#Age : {{obj.age}}\xb1{{obj.error}}    
#'''
#
#        data1 = map(lambda x: getattr(self.record, x), ['rid', 'rundate', 'runtime'])
#
#        temp = Template(doc)
#        join = lambda f, n: ('\t' * n).join(f)
##        join = '\t\t\t'.join
#        entab = lambda x:map('{}'.format, map(str, x))
#        makerow = lambda x, n: join(entab(x), n)
#        record = self.record
#        r = temp.render(record=record,
#                           header1=makerow(self.header1, 3),
#                           header2=makerow(self.header2, 1),
#                           data1=makerow(data1, 3),
#                           signals=zip(record.det_keys,
#                                       record.intercepts
#                                       ),
#                           obj=self,
#                           )
#        return r
#
#    def traits_view(self):
##        s = 51
#        ha1 = wx.TextAttr()
#        f = wx.Font(12, wx.MODERN, wx.NORMAL,
#                         wx.NORMAL, False, u'Consolas')
#        f.SetUnderlined(True)
#        ha1.SetFont(f)
#        ha1.SetTabs([200, ])
#
#        f.SetUnderlined(False)
#        f.SetPointSize(10)
#        f.SetWeight(wx.FONTWEIGHT_NORMAL)
#
#        da = wx.TextAttr(colText=(255, 100, 0))
#        da.SetFont(f)
#
#        ha2 = wx.TextAttr()
#        f.SetPointSize(12)
#        f.SetUnderlined(True)
#        ha2.SetFont(f)
#
#        ba = wx.TextAttr()
#        f.SetUnderlined(False)
#        ba.SetFont(f)
#        f.SetPointSize(10)
#
#        styles = {1:ha1,
#                  2:da,
#                  (3, 4, 5, 6):ba,
#                  7:ha2,
#                  (8, 9, 10, 11):ba
#                  }
#
#        v = View(Item('summary', show_label=False,
##                      editor=HTMLEditor()
#                        style='custom',
#                        editor=SelectableReadonlyTextEditor(
#                        styles=styles,
#                        )
#                      )
#                 )
#        return v
