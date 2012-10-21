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
from src.displays.rich_text_display import RichTextDisplay
from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.fit_selector import FitSelector

PLUSMINUS = unicode('\xb1')
PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)
class AnalysisSummary(Summary):

    display = Instance(RichTextDisplay)
    fit_selector = Instance(FitSelector)

    def _build_summary(self):
        d = self.display
        d.clear()

        record = self.record

        isos = record.isos
        isos = sorted(isos, key=lambda x: re.sub('\D', '', x))
        isos.reverse()

        d.add_text('Labnumber={}-{}'.format(record.labnumber, record.aliquot), bold=True)
        d.add_text('date={} time={}'.format(record.rundate, record.runtime), bold=True)

        floatfmt = lambda m, i = 5: '{{:0.{}f}}'.format(i).format(m)
        width = lambda m, i: '{{:<{}s}}'.format(i).format(m)

        #add header
        columns = [('Iso.', 5),
                   ('Int.', 12), (PLUSMINUS_ERR, 12),
                   ('Fit', 11),
                   ('Baseline', 12), (PLUSMINUS_ERR, 15),
#                   ('Blank', 12), (PLUSMINUS_ERR, 12)
                   ]
        widths = [w for _, w in columns]

        msg = 'Iso.   Int.             ' + PLUSMINUS_ERR + '         Fit'
        msg += '           Baseline     ' + PLUSMINUS_ERR + '             '
#        msg = ''.join([width(m, w) for m, w in columns])
        d.add_text(msg, underline=True, bold=True)

        #add isotopes
        n = len(isos) - 1
        for i, iso in enumerate(isos):
            self._make_signals(n, i, iso, floatfmt, width, widths)

#        d.add_text('\n')

        m = 'Corrected Signals'
        d.add_text('{:<39s}'.format(m), underline=True, bold=True)

        signals = dict()
        for i, iso in enumerate(isos):
            s = self._make_corrected_signals(n, i, iso, floatfmt, width, widths)
            signals[iso] = s

#        d.add_text([' '])
#        d.add_text(' ')
        m = 'Corrected Ratios'
        d.add_text('{:<39s}'.format(m), underline=True, bold=True)
#
        ratios = ['Ar40/Ar36', 'Ar40/Ar39']
        n = len(ratios) - 1
        for i, r in enumerate(ratios):
            nu, de = r.split('/')
            rr = signals[nu] / signals[de]
            v, e = rr.nominal_value, rr.std_dev()
            pe = e / v * 100
            ms = [r, floatfmt(v), floatfmt(e), '({}%)'.format(floatfmt(pe, i=2))]
#            msg = ''.join([width(m, w) for m, w in zip(msgs, widths)])
            msg = ''.join([width(m, 10) for m in ms])
#
            if i == n:
                msg += '\n'
            d.add_text(msg, underline=i == n)


        v, e = self.record.age
        e = u' \u00b1' + '{:0.3f}'.format(e)
        d.add_text('age={:0.3f} {}'.format(v, e))

    def _make_corrected_signals(self, n, i, iso, floatfmt, width, widths):
        d = self.display

        pi = n - i
        sig, base = self._get_signal_and_baseline(pi)
        s = sig - base
        try:
            pe = abs(s.std_dev() / s.nominal_value * 100)
        except ZeroDivisionError:
            pe = 0
        msgs = [
                iso,
                floatfmt(s.nominal_value),
                floatfmt(s.std_dev()),
                '({}%)'.format(floatfmt(pe, i=2))
                ]
        msg = ''.join([width(m, w) for m, w in zip(msgs, widths)])
        if i == n:
            msg += '\n'
        d.add_text(msg, underline=i == n)

        return s

    def _get_signal_and_baseline(self, pi):
        sg = self.record.signal_graph
        bg = self.record.baseline_graph

        reg = sg.regressors[pi]
        inter = reg.predict(0)
        inter_err = reg.coefficient_errors[-1]

        reg = bg.regressors[pi]
        base = reg.predict(0)
        base_err = reg.coefficient_errors[-1]
        return ufloat((inter, inter_err)), ufloat((base, base_err))

    def _make_signals(self, n, i, iso, floatfmt, width, widths):
        sg = self.record.signal_graph
        d = self.display
        pi = n - i
        fit = sg.get_fit(pi) if sg else '---'
        sig, base = self._get_signal_and_baseline(pi)

        blank = 0
        blank_err = 0
        msgs = [
                iso,
                floatfmt(sig.nominal_value),
                floatfmt(sig.std_dev()),
                fit,
                floatfmt(base.nominal_value),
                floatfmt(base.std_dev()),
#                    floatfmt(blank),
#                    floatfmt(blank_err)
                ]
        msg = ''.join([width(m, w) for m, w in zip(msgs, widths)])
        if i == n:
            msg += '\n'
        d.add_text(msg, underline=i == n)

    def _display_default(self):
        return RichTextDisplay(default_size=12,
                               width=700,
                               selectable=True,
                               default_color='black',
                               font_name='Bitstream Vera Sans Mono'
#                               font_name='Monaco'
                               )

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
