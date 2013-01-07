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
from traits.api import Float, Range, Int
from traitsui.api import View, Item, VGroup, HGroup, Label, spring, RangeEditor
#============= standard library imports ========================
from reportlab.platypus.tables import TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
#============= local library imports  ==========================
from src.stats.core import calculate_weighted_mean, calculate_mswd
from src.processing.publisher.templates.tables.pdf_table import PDFTable

class IdeogramTable(PDFTable):
    status_width = Int(5)
    id_width = Int(20)
    power_width = Int(30)
    moles_width = Int(50)

    low = Int(0)
    high = Int(200)
    ar40_width = Int(40)
    ar40_error_width = Int(40)
    ar39_width = Int(40)
    ar39_error_width = Int(40)
    ar38_width = Int(40)
    ar38_error_width = Int(40)
    ar37_width = Int(40)
    ar37_error_width = Int(40)
    ar36_width = Int(40)
    ar36_error_width = Int(40)

    def _value_error_width_factory(self, name):
        top = HGroup(Label(name.capitalize()), spring, Label('Error'), spring)
        bottom = HGroup(self._width_factory('{}_width'.format(name)),
                        self._width_factory('{}_error_width'.format(name)))
        return VGroup(top, bottom)

    def _single_value_width_factory(self, name):
        top = HGroup(Label(name.capitalize()))
        bottom = self._width_factory('{}_width'.format(name))
        return VGroup(top, bottom)

    def _width_factory(self, name):
        return Item(name,
                    editor=RangeEditor(mode='spinner', low_name='low', high_name='high'),
                    show_label=False)

    def traits_view(self):
        contents = []
        for n in ['status', 'id', 'power']:
            contents.append(self._single_value_width_factory(n))

        for n in ['ar40', 'ar39', 'ar38', 'ar37', 'ar36']:
            contents.append(self._value_error_width_factory(n))

        column_widths = HGroup(*contents)
        v = View(column_widths,
                 buttons=['OK', 'Cancel']
                 )
        return v



    def make(self, analyses):
        if self.add_title:
            rows = self.make_title()

        a = analyses[0]
        rows += self.make_sample_summary(a.sample, a.labnumber, a.j,
                                         a.material,
                                         '---'
                                         )
        if self.add_header:
            rows += self._make_header()

        for ai in analyses:
            r = self._make_analysis_row(ai)
            rows.append(r)

#        rows+=self._make_summary_row(analyses)

        return self._make(rows)

    def _make_summary_row(self, analyses):
        rows = []
        ages, errors = zip(*[(ai.age_value, ai.age_error) for ai in analyses])
        n = len(analyses)
        row = ['', 'n= {}'.format(n)]
        rows.append(row)

        wm, we = calculate_weighted_mean(ages, errors)
        wm = self.floatfmt(wm, n=3)
        we = self.floatfmt(we, n=4)
        row = ['', u'weighted mean= {} \u00b1{}'.format(wm, we)]
        rows.append(row)

        mswd = calculate_mswd(ages, errors)
        mswd = self.floatfmt(mswd, n=3)
        row = ['', u'mswd= {}'.format(mswd)]
        rows.append(row)
        return rows

    def make_title(self):
        title = self._new_paragraph('<font size=10 name="Helvetica-Bold">Table {}. <super>40</super>Ar/<super>39</super>Ar analytical data.</font>'.format(self.number))
        return [[title]]

    def make_sample_summary(self, sample, labnumber, j, material, igsn):
        line1 = ['Sample: {}'.format(sample),
                 '', '', '',
                 'Lab #: {}'.format(labnumber),
                 '',
                 u'j: {:0.7f}\u00b1{:0.8f}'.format(*j),
                 ]
        line1 = self._set_font(line1, 8)

        line2 = ['Material: {}'.format(material),
                 '', '', '',
                 'IGSN #: {}'.format(igsn)
                 ]
        line2 = self._set_font(line2, 8)

#        line3 = []
#        line3 = self._set_font(line3, 10)

        return [line1, line2]
#        return [line1, line2, line3]
    def _make_header(self):
        sigma = self._plusminus_sigma()
#        sigma = '1s'
        header = []
#        header.append([])

        super_ar = lambda x: '<super>{}</super>Ar'.format(x)
        name_line = ['', 'N', 'Power',
                   super_ar(40),
                   super_ar(40), sigma,
                   super_ar(39), sigma,
                   super_ar(38), sigma,
                   super_ar(37), sigma,
                   super_ar(36), sigma,
                   '%<super>40</super>Ar*',
                   '%<super>40</super>Ar*/<super>39</super>Ar<sub>K</sub>',
                   ]
        name_line = self._set_font(name_line, 7)
        header.append(name_line)

        unit_line = ['', '', '(W)', '(moles)', '(10<super>3</super> fA)', '', '(10<super>3</super> fA)',
                     '', '', '', '', '', '', '(10<super>-2</super> fA)'
                     ]
        unit_line = self._set_font(unit_line, 6)

        header.append(unit_line)

        return header

    def _make_analysis_row(self, analysis):
        rad40 = analysis.arar_result['rad40']
        k39 = analysis.k39

        R = rad40 / k39
        row = ['' if analysis.status == 0 else 'x',
               analysis.aliquot,
               analysis.extract_value,
               self.floatfmt(analysis.moles_Ar40, n=3),
               self.floatfmt(analysis.Ar40.nominal_value, n=3, scale=1e3),
               self.floatfmt(analysis.Ar40.std_dev(), n=3),
               self.floatfmt(analysis.Ar39.nominal_value, n=3, scale=1e3),
               self.floatfmt(analysis.Ar39.std_dev(), n=3),
               self.floatfmt(analysis.Ar38.nominal_value, n=2),
               self.floatfmt(analysis.Ar38.std_dev(), n=3),
               self.floatfmt(analysis.Ar37.nominal_value, n=2),
               self.floatfmt(analysis.Ar37.std_dev(), n=3),
               self.floatfmt(analysis.Ar36.nominal_value, n=3),
               self.floatfmt(analysis.Ar36.std_dev(), n=3, scale=1e-2),
               self.floatfmt(analysis.rad40_percent.nominal_value, n=2),
               self.floatfmt(R.nominal_value, n=3)
               ]

        row = self._set_font(row, 6)
        return row

    def _set_font(self, row, fontsize):
        func = lambda x:self._new_paragraph(u'<font size={}>{}</font>'.format(fontsize, x))
        row = map(func, row)
        return row

    def _get_style(self):
        style = TableStyle()
        if self.add_title:
            #(col, row)
            #make first row span entire table
            style.add('SPAN', (0, 0), (-1, 0))
            style.add('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black)

            style.add('SPAN', (0, 1), (4, 1)) #sample
            style.add('SPAN', (4, 1), (6, 1)) #labnumber
            style.add('LINEBELOW', (0, 1), (5, 1), 1.5, colors.black)

            style.add('SPAN', (6, 1), (-1, 1)) #j

            style.add('SPAN', (0, 2), (4, 2)) #material
            style.add('SPAN', (4, 2), (6, 2)) #igsn

            style.add('LINEABOVE', (0, 3), (-1, 3), 1.5, colors.black)
            style.add('LINEBELOW', (0, 4), (-1, 4), 1.5, colors.black)

            style.add('GRID', (0, 0), (-1, -1), 0.25, colors.red)
#            style.add('ALIGN', (1, 0), (-1, -1), 'CENTER')

            style.add('LEFTPADDING', (1, 3), (-1, -1), 1)

#            style.add('SPAN', (0, 3), (5, 1))
#            style.add('SPAN', (0, 5), (7, 1))

        return style

    def _set_column_widths(self, ta):
        scale = lambda x: x / 100.*inch
        ta._argW[0] = scale(self.status_width)
        ta._argW[1] = scale(self.id_width)
        ta._argW[2] = scale(self.power_width)

        ta._argW[3] = scale(self.moles_width)

        for i, n in enumerate(['ar40', 'ar39', 'ar38', 'ar37', 'ar36']):
            w = 4 + 2 * i
            ta._argW[w] = scale(getattr(self, '{}_width'.format(n)))
            ta._argW[w + 1] = scale(getattr(self, '{}_error_width'.format(n)))

#        #set isotope widths 40-37
#        for i in range(8):
#            w = 0.4 if i % 2 == 0 else 0.4
#            ta._argW[4 + i] = w * inch

#        ta._argW[12] = 0.4 * inch #36
#        ta._argW[13] = 0.6 * inch #36err

        ta._argW[14] = 0.5 * inch #rad40
        ta._argW[15] = 0.8 * inch #rad40/k39


if __name__ == '__main__':
    t = IdeogramTable()
    t.configure_traits()
#============= EOF =============================================
