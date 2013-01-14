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
from traits.api import Instance, Property, Str
from traitsui.api import View, Item, HGroup, EnumEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.isotope_analysis.summary import Summary
from src.database.isotope_analysis.fit_selector import FitSelector
from src.constants import NULL_STR, PLUSMINUS, PLUSMINUS_ERR



class AnalysisSummary(Summary):
    fit_selector = Instance(FitSelector)
    selected_history = Str
    histories = Property

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
        self._make_keyword('J', '{} {}{}'.format(j, PLUSMINUS, self.make_error(j, je)),
                           new_line=True)

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
        arar_result = record.arar_result
        if arar_result:
            rad40 = arar_result['rad40']
            k39 = arar_result['k39']
            s36 = arar_result['s36']
            s39dec_cor = arar_result['s39decay_cor']
            s40 = arar_result['s40']

            self._make_ratio('%40*', rad40, s40, scalar=100)
            self._make_ratio('40/36', s40, s36)
            self._make_ratio('40/39K', s40, k39)
            self._make_ratio('40/39', s40, s39dec_cor)
            self._make_ratio('40*/36', rad40, s36)
            self._make_ratio('40*/39K', rad40, k39, underline_width=underline_width - 2)

        self.add_text(' ')

        age = record.age
        try:
            ej = arar_result['age_err_wo_jerr'] / record.age_scalar
        except TypeError:
            ej = 0

        kca = self.record.kca
        kcl = self.record.kcl
        self._make_keyword('K/Ca', '{} {}{}'.format(self.floatfmt(kca.nominal_value, n=2),
                                                    PLUSMINUS,
                                                    self.make_error(kca.nominal_value, kca.std_dev())),
                            new_line=True)

        self._make_keyword('K/Cl', '{} {}{}'.format(self.floatfmt(kcl.nominal_value, n=2),
                                                    PLUSMINUS,
                                                    self.make_error(kcl.nominal_value, kcl.std_dev())),
                            new_line=True, underline=underline_width)

        self.add_text('  ')
        self._make_keyword('Age', '{} {}{} ({})'.format(self.floatfmt(age.nominal_value, n=4),
                                                        PLUSMINUS,
                                                        self.make_error(age.nominal_value, age.std_dev()),
                                                        record.age_units),
                           new_line=True
                           )
        self.add_text('             {}{} (Exclude Error in J)'.format(PLUSMINUS,
                                                                      self.make_error(age.nominal_value, ej)
                                                                      ))

    def _make_ratio(self, name, nom, dem, scalar=1, underline_width=0):
        try:
            rr = nom / dem * scalar
            v, e = rr.nominal_value, rr.std_dev()
        except ZeroDivisionError:
            v, e = 0, 0

        ms = [self.floatfmt(v), self.make_error(v, e)]
        msg = ''.join([self.fixed_width(m, 15) for m in ms])

        underline = False
        if underline_width:
            underline = True
            msg = '{{:<{}s}}'.format(underline_width).format(msg)

        self.add_text(self.fixed_width(name, 10), bold=True, new_line=False,
                   underline=underline)
        self.add_text(msg, size=11, underline=underline)

    def _make_corrected_signals(self, n, i, iso, widths, lh):
        sigs = self.record.signals
        intercept = sigs[iso]
        base = sigs['{}bs'.format(iso)]

        s1 = intercept - base
        sv1 = self.floatfmt(s1.nominal_value)
        bse1 = self.make_error(s1.nominal_value, s1.std_dev())

        arar = self.record.arar_result
        s2 = None
        if arar:
            iso = iso.replace('Ar', 's')
            if iso in arar:
                s2 = arar[iso]

        if not s2 is None:
            sv2 = self.floatfmt(s2.nominal_value)
            bse2 = self.make_error(s2.nominal_value, s2.std_dev())
        else:
            sv2 = NULL_STR
            bse2 = NULL_STR

        msgs = [sv1, bse1,
                ' ',
                sv2, bse2]
        msg = ''.join([self.fixed_width(m, w) for m, w in zip(msgs, widths[1:])])
        if i == n:
            lh = lh + widths[0] - 2
            msg = '{{:<{}s}}\n'.format(lh).format(msg)

        self.add_text(self.fixed_width(iso, widths[0]), bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(msg, size=11, underline=i == n)

    def _make_signals(self, n, i, iso, widths):
        sg = self.record.signal_graph
        pi = n - i
        det = sg.plots[pi].detector

        fit = sg.get_fit(pi) if sg else ' '
        sv, se = self._get_signal(iso)
        bv, be = self._get_signal('{}bs'.format(iso))
        blv, ble = self._get_signal('{}bl'.format(iso))

        msgs = [
                self.floatfmt(sv),
                self.make_error(sv, se),
                fit[0].upper(),
                self.floatfmt(bv),
                self.make_error(bv, be),
                self.floatfmt(blv),
                self.make_error(blv, ble)
                ]

        msg = ''.join([self.fixed_width(m, w) for m, w in zip(msgs, widths[2:])])
        if i == n:
            msg += '\n'

        self.add_text(self.fixed_width(det, 5),
                   bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(self.fixed_width(iso, 6),
                   bold=True,
                  new_line=False,
                  underline=i == n)
        self.add_text(msg, size=11, underline=i == n)

    def _get_histories(self):
        histories = []
        if self.record.dbrecord.arar_histories:
            histories = [hi.create_date for hi in self.record.dbrecord.arar_histories]

        return ['Collection'] + histories

    def _get_signal(self, iso):
        signals = self.record.signals
        try:
            sig = signals[iso].uvalue
            v = sig.nominal_value
            e = sig.std_dev()
        except KeyError:
            v, e = 0, 0
        return v, e

    def traits_view(self):
        v = View(HGroup(Item('selected_history', show_label=False,
                             editor=EnumEditor(name='histories'))),
                 Item('display', height=0.75, show_label=False, style='custom'),
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
