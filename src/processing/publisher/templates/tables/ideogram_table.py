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
from src.processing.publisher.templates.tables.pdf_table import PDFTable, \
    RowItem, Row, Superscript, Title, Subscript, SummaryRow, NamedParameter
from src.constants import PLUSMINUS, ARGON_KEYS
from src.helpers.formatting import floatfmt
def DefaultInt(value=45):
    return Int(value)

class IdeogramTable(PDFTable):
    status_width = Int(5)
    id_width = Int(20)
    power_width = Int(30)
    moles_width = Int(50)

    low = Int(0)
    high = Int(200)
    ar40_width = DefaultInt()
    ar40_error_width = DefaultInt()
    ar39_width = DefaultInt()
    ar39_error_width = DefaultInt()
    ar38_width = DefaultInt()
    ar38_error_width = DefaultInt()
    ar37_width = DefaultInt()
    ar37_error_width = DefaultInt()
    ar36_width = DefaultInt()
    ar36_error_width = DefaultInt()

    _sample_summary_row1 = None
    _sample_summary_row2 = None

    def make(self, analyses):
        if self.add_title:
            rows = self.make_title()
        else:
            rows = [[]]

        a = analyses[0]
        rows.extend(self._make_sample_summary(a.sample,
                                          a.labnumber_aliquot, a.j,
                                         a.material,
                                         '---',
                                         a.ic_factor
                                         )
                    )
        if self.add_header:
            rows.extend(self._make_header())

        for ai in analyses:
            r = self._make_analysis_row(ai)
            rows.append(r)

        rows.extend(self._make_summary_row(analyses))
        rows.extend(self._make_footer_rows())

        return self._make(rows)

    def make_title(self):
        a40 = Superscript(40)
        a39 = Superscript(39)
        v = 'Table {}. {}Ar/{}Ar analytical data'.format(self.number, a40, a39)
        return [Title(value=v, fontsize=10,
                       fontname='Helvetica-Bold')]

    def _make_sample_summary(self, sample, labnumber, j, material, igsn, ic):
        if not isinstance(j, tuple):
            j = j.nominal_value, j.std_dev

        if not isinstance(ic, tuple):
            ic = ic.nominal_value, ic.std_dev

#        pm = self._plusminus()

        line1 = Row(fontsize=8)
        line1.add_item(value=NamedParameter('Sample', sample), span=5)
        line1.add_item(value=NamedParameter('Lab #', labnumber), span=2)

        js = '{:0.2E} {}{:0.2E}'.format(j[0], PLUSMINUS, j[1])
        line1.add_item(value=NamedParameter('J', js), span=3)
        ics = '{:0.3f} {}{:0.4f}'.format(ic[0], PLUSMINUS, ic[1])
        line1.add_item(value=NamedParameter('IC', ics), span=3)

        line2 = Row(fontsize=8)
        line2.add_item(value=NamedParameter('Material', material), span=5)
        line2.add_item(value=NamedParameter('IGSN', igsn), span=2)

        self._sample_summary_row1 = line1
        self._sample_summary_row2 = line2

        return [line1, line2]

    def _make_header(self):
        sigma = self._plusminus_sigma()
        super_ar = lambda x: '{}Ar'.format(Superscript(x))

        _102fa = '(10{} fA)'.format(Superscript(2))
        _103fa = '(10{} fA)'.format(Superscript(3))
        minus_102fa = '(10{} fA)'.format(Superscript(-2))

        line = [
                ('', ''),
                ('N', ''),
                ('Power', '(W)'),
                (super_ar(40), ''),
                (super_ar(40), _103fa), (sigma, ''),
                (super_ar(39), _103fa), (sigma, ''),
                (super_ar(38), ''), (sigma, ''),
                (super_ar(37), ''), (sigma, ''),
                (super_ar(36), ''), (sigma, minus_102fa),
                ('%{}*'.format(super_ar(40)), ''),
                ('{}*/{}{}'.format(super_ar(40),
                                   super_ar(39),
                                   Subscript('K')), ''),
                ('Age', '(Ma)'), (sigma, ''),
                ('K/Ca', ''),
                ('Blank', 'type'),
                (super_ar(40), ''), (sigma, ''),
                (super_ar(39), ''), (sigma, ''),
                (super_ar(38), ''), (sigma, ''),
                (super_ar(37), ''), (sigma, ''),
                (super_ar(36), ''), (sigma, ''),
              ]

        name_row, unit_row = zip(*line)

        default_fontsize = 6
        nrow = Row(fontsize=default_fontsize)
        for ni in name_row:
            if len(ni) == 2:
                ni, fontsize = ni
            else:
                fontsize = default_fontsize
            nrow.add_item(value=ni, fontsize=fontsize)

        default_fontsize = 6
        urow = Row(fontsize=default_fontsize)
        for ni in unit_row:
            if len(ni) == 2:
                ni, fontsize = ni
            else:
                fontsize = default_fontsize
            urow.add_item(value=ni,
                          fontsize=fontsize)
        return [
                nrow.render(),
                urow
                ]

    def _make_analysis_row(self, analysis):
#        floatfmt = self.floatfmt
        def fmt_attr(v, key='nominal_value', n=5, scale=1, **kw):
            if isinstance(v, tuple):
                if key == 'std_dev':
                    v = v[1]
                else:
                    v = v[0]
            else:
                v = getattr(v, key)

            v = v / float(scale)

            return floatfmt(v, n=n, max_width=8, **kw)

        def error(**kw):
            return lambda x: fmt_attr(x, key='std_dev', **kw)
        def value(**kw):
            return lambda x: fmt_attr(x, key='nominal_value', **kw)

        default_fontsize = 6
        row = Row(fontsize=default_fontsize)
        attrs = (
                 ('status', lambda x: '' if x == 0 else 'x'),
                 ('aliquot_step', '{}',),
                 ('extract_value', '{}'),
                 ('moles_Ar40', value()),

                 #==============================================================
                 # signals
                 #==============================================================
                 ('Ar40', value(scale=1e3)),
                 ('Ar40', error()),
                 ('Ar39', value(scale=1e3)),
                 ('Ar39', error()),
                 ('Ar38', value()),
                 ('Ar38', error()),
                 ('Ar37', value()),
                 ('Ar37', error()),
                 ('Ar36', value()),
                 ('Ar36', error(scale=1e3)),

                 #==============================================================
                 # computed
                 #==============================================================
                 ('rad40_percent', value(n=1)),
                 ('R', value(n=5)),
                 ('age', value(n=2)),
                 ('age', error(n=4)),
                 ('k_ca', value(n=1)),
                 #==============================================================
                 # blanks
                 #==============================================================
                 ('blank_fit', '{}'),
                 ('Ar40_blank', value()),
                 ('Ar40_blank', error()),

                 ('Ar39_blank', value()),
                 ('Ar39_blank', error()),

                 ('Ar38_blank', value()),
                 ('Ar38_blank', error()),

                 ('Ar37_blank', value()),
                 ('Ar37_blank', error()),

                 ('Ar36_blank', value()),
                 ('Ar36_blank', error()),
                 )
        for args in attrs:
            if len(args) == 3:
                attr, fmt, fontsize = args
            else:
                attr, fmt = args
                fontsize = default_fontsize

            v = getattr(analysis, attr)
            row.add_item(value=v, fmt=fmt, fontsize=fontsize)

        nrow = row
        return nrow

    def _make_summary_row(self, analyses):
#        rows = []
        ages, errors = zip(*[(ai.age.nominal_value, ai.age.std_dev) for ai in analyses])
        n = len(analyses)
        row = SummaryRow()

        wm, we = calculate_weighted_mean(ages, errors)
        wm = floatfmt(wm, n=3)
        we = floatfmt(we, n=4)
#
        mswd = calculate_mswd(ages, errors)
        mswd = floatfmt(mswd, n=3)

        row.add_item(value='n={}'.format(n), span=3)
        row.add_item(value=u'weighted mean= {} {}{}'.format(wm, PLUSMINUS, we),
                     span=3)
        row.add_item(value=u'mswd= {}'.format(mswd),
                     span=3)

        return [row]

    def _make_footer_rows(self):
        return []
#===============================================================================
# table formatting
#===============================================================================
    def _get_style(self, rows):

        '''
            set TableStyle 
            add styles for row/col blocks
            
            style.add('SPAN', (col_s, row_s), (col_e, row_e))
        '''
        # (col, row)
        style = TableStyle()
        title_row = 0
        sample_row = 1
        sample_row2 = 2
        name_row = 3
        unit_row = 4

#        style.add('GRID', (0, 0), (-1, -1), 0.25, colors.red)
        style.add('ALIGN', (1, 0), (-1, -1), 'CENTER')
        style.add('LEFTPADDING', (1, name_row), (-1, -1), 1)

        # set style for title row
        if self.add_title:
            style.add('SPAN', (0, title_row), (-1, title_row))
            style.add('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black)

        # set style for sample row
        for s, e in self._sample_summary_row1.spans:
            style.add('SPAN', (s, sample_row), (e, sample_row))
            style.add('LINEBELOW', (s, sample_row), (e, sample_row), 1.5, colors.black)

        for s, e in self._sample_summary_row2.spans:
            style.add('SPAN', (s, sample_row2), (e, sample_row2))

        # set style for name header
        style.add('LINEABOVE', (0, name_row), (-1, name_row), 1.5, colors.black)

        # set style for unit header
        style.add('LINEBELOW', (0, unit_row), (-1, unit_row), 1.5, colors.black)

        # set style for summary rows
        summary_idxs = [(i, v) for i, v in enumerate(rows)
                      if isinstance(v, SummaryRow)]
        for idx, summary in summary_idxs:
            style.add('LINEABOVE', (0, idx), (-1, idx), 1.5, colors.black)
            for si, se in summary.spans:
                style.add('SPAN', (si, idx), (se, idx))  # n

        return style

    def _set_column_widths(self, ta):
        scale = lambda x: x / 100.*inch
#        print ta._argW
        ta._argW[0] = scale(self.status_width)
        ta._argW[1] = scale(self.id_width)
        ta._argW[2] = scale(self.power_width)

        ta._argW[3] = scale(self.moles_width)

        for i, n in enumerate(['ar40', 'ar39', 'ar38', 'ar37', 'ar36']):
            w = 4 + 2 * i
            ta._argW[w] = scale(getattr(self, '{}_width'.format(n)))
            ta._argW[w + 1] = scale(getattr(self, '{}_error_width'.format(n)))

        ta._argW[14] = 0.4 * inch  # rad40
        ta._argW[15] = 0.7 * inch  # rad40/k39
        ta._argW[16] = 0.5 * inch  # age
        ta._argW[17] = 0.5 * inch  # age err

        ta._argW[18] = 0.4 * inch  # blank fit type

        start = 19
        for i, n in enumerate(['ar40', 'ar39', 'ar38', 'ar37', 'ar36']):
            ta._argW[start + 2 * i] = scale(getattr(self, '{}_width'.format(n)))
            ta._argW[start + 2 * i + 1] = scale(getattr(self, '{}_error_width'.format(n)))


    def set_widths(self, widths):
        for k, v in widths.iteritems():
            setattr(self, k, v)

    def get_widths(self):
        widths = dict()
        for a in map(str.lower, ARGON_KEYS):
            for k in ('{}_width'.format(a),
                           '{}_error_width'.format(a)
                           ):
                widths[k] = getattr(self, k)
        return widths

#===============================================================================
# views
#===============================================================================
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

if __name__ == '__main__':
    t = IdeogramTable()
    t.configure_traits()


#============= EOF =============================================
# def _set_font(self, row, fontsize, default=None):
#        '''
#            fontsize: int, broadcast to all cols in row
#                      list or tuple
#                            same len as row. zip fontsize and row
#                            different lens should be list of tuples
#                            [(idx,fontsize)....]
#            default: int
#                       size to use if fontsize is a list a not fully populated
#        '''
#        if not isinstance(fontsize, (list, tuple)):
#            fontsize = (fontsize,) * len(row)
#
#        if len(fontsize) != len(row):
#            for idx, fi in fontsize:
#                row[idx] = self._new_paragraph(u'<font size={}>{}</font>'.format(fi, row[idx]))
#            if default:
#                idxs = [idx for idx, fi in fontsize]
#                for i, ri in enumerate(row):
#                    if i in idxs:
#                        continue
#                    row[i] = self._new_paragraph(u'<font size={}>{}</font>'.format(default, ri))
#
#        else:
#            row = zip(fontsize, row)
#            func = lambda x:self._new_paragraph(u'<font size={}>{}</font>'.format(x[0], x[1]))
#            row = map(func, row)
#        return row
