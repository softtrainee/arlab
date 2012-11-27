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
#import re
#from uncertainties import ufloat
#============= local library imports  ==========================
from src.database.isotope_analysis.summary import Summary, fixed_width, floatfmt
from src.database.isotope_analysis.fit_selector import FitSelector
from src.constants import NULL_STR
PLUSMINUS = u'\u00b1'
try:
    PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)
except UnicodeEncodeError:
    PLUSMINUS = '+/-'
    PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)


class AnalysisSummary(Summary):
    fit_selector = Instance(FitSelector)

    def _build_summary(self):
        record = self.record

        isos = record.isotope_keys
        isos = list(reversed(isos))
        if not isos:
            isos = []

        #add header
        columns = [('Det.', 0),
                   ('Iso.', 0),
                   ('Int.', 12), (PLUSMINUS_ERR, 18),
                   ('Fit', 4),
                   ('Baseline', 10), (PLUSMINUS_ERR, 18),
                   ('Blank', 13), (PLUSMINUS_ERR, 18)
                   ]
        widths = [w for _, w in columns]

        header = 'Det. Iso.  Int.       ' + PLUSMINUS_ERR + '           Fit '
        header += 'Baseline  ' + PLUSMINUS_ERR + '           Blank       ' + PLUSMINUS_ERR + '           '

        underline_width = len(header)

        #add metadata
        self._make_keyword('Analysis ID', record.record_id, width=30)
        self._make_keyword('Date', record.rundate)
        self._make_keyword('Time', record.runtime, new_line=True)

        #add extraction
        self._make_keyword('Mass Spectrometer', record.mass_spectrometer, width=30)
        self._make_keyword('Extraction Device', record.extract_device, new_line=True)
        exs = [
                ('Position', record.position),
                ('Extract', '{} ({})'.format(record.extract_value, record.extract_units)),
                ('Duration', '{} (s)'.format(record.extract_duration)),
                ('Cleanup', '{} (s)'.format(record.cleanup_duration)),
                ]
        n = len(exs)
        for i, (name, value) in enumerate(exs):
            self._make_keyword(name, value, True if i == n - 1 else False)

        #add j
        j, je = record.j
        ee = u'\u00b1{} ({})'.format(floatfmt(je), self.calc_percent_error(j, je))
        self._make_keyword('J', '{} {}'.format(j, ee), new_line=True)

        #add sensitivity
        s = record.sensitivity
        m = record.sensitivity_multiplier

        if s is not None:
            if m is None:
                m = 1
            ss = s * m
        else:
            ss = NULL_STR

        self._make_keyword('Sensitivity', ss, new_line=True)


        #added header
        self.add_text(header, underline=True, bold=True)

        #add isotopes
        n = len(isos) - 1
        for i, iso in enumerate(isos):
            self._make_signals(n, i, iso, widths)

        #add corrected signals
        m = 'Baseline Corrected Signals          Fully Corrected Signals'
        self.add_text('{{:<{}s}}'.format(underline_width).format(m), underline=True, bold=True)
        widths = [5, 12, 10, 5, 12, 10]
        for i, iso in enumerate(isos):
            self._make_corrected_signals(n, i, iso, widths, underline_width)

        #add corrected values
        m = 'Corrected Values'
        self.add_text('{{:<{}s}}'.format(underline_width).format(m), underline=True, bold=True)
#
        rec = self.record
        arar_result = rec.arar_result
        if arar_result:
            rad40 = arar_result['rad40']
            tot40 = arar_result['tot40']
            k39 = arar_result['k39']
            s36 = arar_result['s36']
            s39dec_cor = arar_result['s39decay_cor']
            s40 = arar_result['s40']

            self._make_ratio('%40*', rad40, tot40, scalar=100)
            self._make_ratio('40/36', s40, s36)
            self._make_ratio('40/39K', s40, k39)
            self._make_ratio('40/39', s40, s39dec_cor)
            self._make_ratio('40*/36', rad40, s36)
            self._make_ratio('40*/39K', rad40, k39, underline_width=underline_width - 2)

        self.add_text(' ')

        v, e = self.record.age
        try:
            ej = arar_result['age_err_wo_jerr'] / record.age_scalar
        except TypeError:
            ej = 0

        e = u'\u00b1{} ({})'.format(floatfmt(e), self.calc_percent_error(v, e))
        ej = u'\u00b1{} ({})'.format(floatfmt(ej), self.calc_percent_error(v, ej))

        kca = self.record.kca
        kv = kca.nominal_value
        ek = kca.std_dev()
        ek = u'\u00b1{} ({})'.format(floatfmt(ek, 3), self.calc_percent_error(kv, ek))

        self._make_keyword('K/Ca', '{:0.2f} {}'.format(kv, ek),
                           new_line=True, underline=underline_width)
        self.add_text('  ')
        self._make_keyword('Age', '{:0.4f} {} ({})'.format(v, e, record.age_units), new_line=True)
        self.add_text('             {} (Exclude Error in J)'.format(ej))

    def _make_ratio(self, name, nom, dem, scalar=1, underline_width=0):
        try:
            rr = nom / dem * scalar
            v, e = rr.nominal_value, rr.std_dev()
        except ZeroDivisionError:
            v, e = 0, 0

        ee = '{} ({})'.format(floatfmt(e), self.calc_percent_error(v, e))
        ms = [floatfmt(v), ee]
        msg = ''.join([fixed_width(m, 15) for m in ms])

        underline = False
        if underline_width:
            underline = True
            msg = '{{:<{}s}}'.format(underline_width).format(msg)
        self.add_text(fixed_width(name, 10), bold=True, new_line=False,
                   underline=underline)
        self.add_text(msg, size=11, underline=underline)



    def _make_corrected_signals(self, n, i, iso, widths, lh):
        sig, base = self._get_signal_and_baseline(iso)

        s1 = sig - base
#        if fully_correct:
        arar = self.record.arar_result

#        s2 = ufloat((0, 0))
        s2 = None
        if arar:
            iso = iso.replace('Ar', 's')
            if iso in arar:
                s2 = arar[iso]

        sv1 = s1.nominal_value
        se1 = s1.std_dev()

        if not s2 is None:
            sv2 = s2.nominal_value
            se2 = s2.std_dev()
            bse2 = '{} ({})'.format(floatfmt(se2), self.calc_percent_error(sv2, se2))
            sv2 = floatfmt(sv2)
        else:
            sv2 = '---'
            bse2 = '---'

        bse1 = '{} ({})'.format(floatfmt(se1), self.calc_percent_error(sv1, se1))
        msgs = [
                floatfmt(sv1),
                bse1,
                ' ',
                sv2,
                bse2
                ]
        msg = ''.join([fixed_width(m, w) for m, w in zip(msgs, widths[1:])])
        if i == n:
            lh = lh + widths[0] - 2
            msg = '{{:<{}s}}\n'.format(lh).format(msg)

        self.add_text(fixed_width(iso, widths[0]), bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(msg, size=11, underline=i == n)

    def _get_signal_and_baseline(self, iso):
        sig = self.record.signals[iso]
        base = self.record.signals['{}bs'.format(iso)]
        return sig.uvalue, base.uvalue

    def _make_signals(self, n, i, iso, widths):
        sg = self.record.signal_graph
        pi = n - i
        fit = sg.get_fit(pi) if sg else ' '
        sig, base = self._get_signal_and_baseline(iso)

        det = sg.plots[pi].detector
        try:
            blank = self.record.signals['{}bl'.format(iso)]
            blank = blank.uvalue
            bls = blank.nominal_value
            ble = blank.std_dev()
        except KeyError:
            bls, ble = 0, 0

        sv = sig.nominal_value
        se = sig.std_dev()

        bs = base.nominal_value
        be = base.std_dev()

        sse = '{} ({})'.format(floatfmt(se), self.calc_percent_error(sv, se))
        bse = '{} ({})'.format(floatfmt(be), self.calc_percent_error(bs, be))
        ble = '{} ({})'.format(floatfmt(ble), self.calc_percent_error(bls, ble))

        msgs = [
                floatfmt(sv),
                sse,
                fit[0].upper(),

                floatfmt(bs),
                bse,
                floatfmt(bls),
                ble
                ]

        msg = ''.join([fixed_width(m, w) for m, w in zip(msgs, widths[2:])])
        if i == n:
            msg += '\n'
#        print width(iso, widths[0]), widths[0]
#        d.add_text(iso, bold=True,
#                  new_line=False,
#                  underline=i == n)
        self.add_text(fixed_width(det, 5),
                   bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(fixed_width(iso, 6),
                   bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(msg, size=11, underline=i == n)

#    def _display_default(self):
#        return RichTextDisplay(default_size=12,
#                               width=700,
#                               selectable=True,
#                               default_color='black',
#                               font_name='Bitstream Vera Sans Mono'
##                               font_name='Monaco'
#                               )

    def traits_view(self):
        v = View(Item('display', height=0.75, show_label=False, style='custom'),
                 Item('fit_selector', height=0.25, show_label=False, style='custom'))
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
