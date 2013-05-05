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
    RowItem, Row, Superscript, Title, Subscript, SummaryRow, NamedParameter, \
    AnalysisRow, Anchor, FootNoteRow, FooterRow
from src.constants import PLUSMINUS, ARGON_KEYS
from src.helpers.formatting import floatfmt
from reportlab.platypus.paragraph import Paragraph
def DefaultInt(value=40):
    return Int(value)

class IdeogramTable(PDFTable):
    status_width = Int(5)
    id_width = Int(20)
    power_width = Int(30)
    moles_width = Int(50)

    low = Int(0)
    high = Int(200)
    ar40_width = DefaultInt(value=45)
    ar40_error_width = DefaultInt()
    ar39_width = DefaultInt(value=45)
    ar39_error_width = DefaultInt()
    ar38_width = DefaultInt()
    ar38_error_width = DefaultInt()
    ar37_width = DefaultInt()
    ar37_error_width = DefaultInt()
    ar36_width = DefaultInt()
    ar36_error_width = DefaultInt(value=50)

    _sample_summary_row1 = None
    _sample_summary_row2 = None
    _footnotes = None
    def make(self, analyses):
        self._footnotes = []

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

        def factory(f):
            r = FootNoteRow(fontsize=7)
            r.add_item(value=f)
            return r

        rows.extend([factory(fi) for fi in self._footnotes])
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

        n = len(self._footnotes)
        link, tag = Anchor('BLANK_{}'.format(id(self)), n + 1)

        self._footnotes.append(tag('Blank Type', 'LR= Linear Regression, AVE= Average'))

        line = [
                ('', ''),
                ('N', ''),
                ('Power', '(%)'),
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
                (link('Blank'), 'type'),
                (super_ar(40), ''), (sigma, ''),
                (super_ar(39), ''), (sigma, ''),
                (super_ar(38), ''), (sigma, ''),
                (super_ar(37), ''), (sigma, ''),
                (super_ar(36), ''), (sigma, ''),
              ]

        name_row, unit_row = zip(*line)

        default_fontsize = 8
        nrow = Row(fontsize=default_fontsize)
        for i, ni in enumerate(name_row):
            nrow.add_item(value=ni)

        default_fontsize = 7
        urow = Row(fontsize=default_fontsize)
        for ni in unit_row:
            urow.add_item(value=ni)
        return [
                nrow.render(),
                urow,
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
        row = AnalysisRow(fontsize=default_fontsize)
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
                 ('k_ca', value(n=2)),
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
        row = SummaryRow(fontsize=6)

        wm, we = calculate_weighted_mean(ages, errors)
        wm = floatfmt(wm, n=3)
        we = floatfmt(we, n=4)
#
        mswd = calculate_mswd(ages, errors)
        mswd = floatfmt(mswd, n=3)

        row.add_item(value='n={}'.format(n), span=3)
        row.add_blank_item(n=10)
        row.add_item(value=u'Weighted Mean= {} {}{} (Ma)'.format(wm, PLUSMINUS, we),
                     span=3)
        row.add_item(value=u'MSWD= {}'.format(mswd),
                     span=3)

        return [row]

    def _make_footer_rows(self):
        rows = []
        df = 7
        for v in ('Constants used', 'Atmospheric argon ratios'):
            row = FooterRow(fontsize=df)
            row.add_item(value=v, span= -1)
            rows.append(row)


        for n, d, v, e, r in (
                          (40, 36, 295.5, 0.5, 'Nier (1950)'),
                          (40, 38, 0.1880, 0.5, 'Nier (1950)'),
                          ):
            row = FooterRow(fontsize=df)
            row.add_item(value='({}Ar/{}Ar){}'.format(
                                                Superscript(n),
                                                Superscript(d),
#                                                'A'
                                                Subscript('A'),

                                                ),
                         span=3
                         )
            row.add_item(value=u'{} {}{}'.format(v, PLUSMINUS, e),
                         span=2)
            row.add_item(value=r, span= -1)
            rows.append(row)


        row = FooterRow(fontsize=df)
        row.add_item(value='Interferring isotope production ratios', span= -1)
        rows.append(row)
        for n, d, s, v, e, r in (
                          (40, 39, 'K'  , 295.5     , 0.5   , 'Nier (1950)'),
                          (38, 39, 'K'  , 0.1880    , 0.5   , 'Nier (1950)'),
                          (37, 39, 'K'  , 0.1880    , 0.5   , 'Nier (1950)'),
                          (39, 37, 'Ca' , 295.5     , 0.5   , 'Nier (1950)'),
                          (38, 37, 'Ca' , 0.1880    , 0.5   , 'Nier (1950)'),
                          (36, 37, 'Ca' , 0.1880    , 0.5   , 'Nier (1950)'),
                          ):
            row = FooterRow(fontsize=df)
            row.add_item(value='({}Ar/{}Ar){}'.format(
                                                Superscript(n),
                                                Superscript(d),
                                                Subscript(s),
                                                ),
                         span=3
                         )
            row.add_item(value=u'{} {}{}'.format(v, PLUSMINUS, e),
                         span=2)
            row.add_item(value=r, span= -1)
            rows.append(row)

        row = FooterRow(fontsize=df)
        row.add_item(value='Decay constants', span= -1)
        rows.append(row)

        for i, E, dl, v, e, r in (
                                  (40, 'K', u'\u03BB\u03B5', 1, 0, 'Foo (1990)'),
                                  (40, 'K', u'\u03BB\u03B2', 1, 0, 'Foo (1990)'),
                                  (39, 'Ar', '', 1, 0, 'Foo (1990)'),
                                  (37, 'Ar', '', 1, 0, 'Foo (1990)'),
                                  ):
            row = FooterRow(fontsize=df)
            row.add_item(value=u'{}{} {}'.format(Superscript(i), E, dl), span=3)
            row.add_item(value=u'{} {}{} a{}'.format(v, PLUSMINUS, e, Superscript(-1)), span=2)
            row.add_item(value=r, span= -1)
            rows.append(row)

        return rows


#===============================================================================
# table formatting
#===============================================================================
    def _get_style(self, rows):

        '''
            set TableStyle 
            add styles for row/col blocks
            
            style.add('SPAN', (col_s, row_s), (col_e, row_e))
            
            also set row heights
        '''
        _get_idxs = lambda x: self._get_idxs(rows, x)
        _get_se = lambda x: (x[0][0], x[-1][0])
        # (col, row)
        style = TableStyle()
        title_row = 0
        sample_row = 1
        sample_row2 = 2
        name_row = 3
        unit_row = 4

        style.add('GRID', (0, 0), (-1, -1), 0.25, colors.red)
        style.add('ALIGN', (0, unit_row), (-1, -1), 'LEFT')
        style.add('LEFTPADDING', (0, unit_row), (-1, -1), 1)


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
#        summary_idxs = [(i, v) for i, v in enumerate(rows)
#                      if isinstance(v, SummaryRow)]
        summary_idxs = _get_idxs(SummaryRow)
        for idx, summary in summary_idxs:
            style.add('LINEABOVE', (0, idx), (-1, idx), 1.5, colors.black)
            for si, se in summary.spans:
                style.add('SPAN', (si, idx), (se, idx))

        analysis_idxs = _get_idxs(AnalysisRow)
        sidx, eidx = _get_se(analysis_idxs)
#        sidx, eidx = analysis_idxs[0][0], analysis_idxs[-1][0]
        style.add('VALIGN', (0, sidx), (-1, eidx), 'MIDDLE')
        style.add('ALIGN', (0, sidx), (-1, eidx), 'CENTER')

        for idx, _analysis in analysis_idxs:
            if idx % 2 == 0:
                style.add('BACKGROUND', (0, idx), (-1, idx),
                          colors.lightgrey,
                          )

        # set for footnot rows
        footnote_idxs = _get_idxs(FootNoteRow)
        sidx, eidx = _get_se(footnote_idxs)
        style.add('VALIGN', (0, sidx), (-1, eidx), 'MIDDLE')
        for idx, _v in footnote_idxs:
            style.add('SPAN', (0, idx), (-1, idx))
#            style.add('VALIGN', (1, idx), (-1, idx), 'MIDDLE')

        footer_idxs = _get_idxs(FooterRow)
        sidx, eidx = _get_se(footer_idxs)
        style.add('VALIGN', (0, sidx), (-1, eidx), 'MIDDLE')
        for idx, v in footer_idxs:
            for si, se in v.spans:
                style.add('SPAN', (si, idx), (se, idx))

        return style

    def _set_row_heights(self, ta, rows):
        a_idxs = self._get_idxs(rows, AnalysisRow)

        for a, v in a_idxs:
#            print a, v
            ta._argH[a] = 0.18 * inch

        a_idxs = self._get_idxs(rows, (FooterRow, FootNoteRow))
        for a, v in a_idxs:
            ta._argH[a] = 0.19 * inch


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

        ta._argW[18] = 0.4 * inch  # k/ca
        ta._argW[19] = 0.5 * inch  # blank fit type

        start = 20
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
