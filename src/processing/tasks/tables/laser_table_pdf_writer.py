#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Int
#============= standard library imports ========================
#============= local library imports  ==========================
from src.pdf.base_pdf_writer import BasePDFWriter
from src.helpers.formatting import floatfmt
from src.pdf.items import Row, Subscript, Superscript
from reportlab.lib.units import inch

def DefaultInt(value=40):
    return Int(value)

class TableSpec(HasTraits):
    status_width = Int(5)
    id_width = Int(20)
    power_width = Int(30)
    moles_width = Int(50)


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

class LaserTablePDFWriter(BasePDFWriter):
    def _build(self, doc, ans):


        flowables = []

        t = self._make_table(ans)
        flowables.append(t)

        frames = [self._default_frame(doc)]
        template = self._new_page_template(frames)

        return flowables, (template,)

    def _make_table(self, analyses):
        style = self._new_style()
        data = []

        header = self._make_header()
        data.extend(header)

        for ai in analyses:
            r = self._make_analysis_row(ai)
            data.append(r)

        t = self._new_table(style, data)

        spec = TableSpec()
        self._set_column_widths(t, spec)
        return t

    def _make_header(self):
        sigma = u'\u00b1 1\u03c3'
#         sigma = self._plusminus_sigma()
        super_ar = lambda x: '{}Ar'.format(Superscript(x))

        _102fa = '(10{} fA)'.format(Superscript(2))
        _103fa = '(10{} fA)'.format(Superscript(3))
        minus_102fa = '(10{} fA)'.format(Superscript(-2))

#         blank = self._make_footnote('BLANK',
#                                    'Blank Type', 'LR= Linear Regression, AVE= Average',
#                                    'Blank')
        blank = 'Blank Type'
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
                (blank, 'type'),
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
                urow.render()
                ]
    def _make_analysis_row(self, analysis):
        default_fontsize = 6
        row = Row(fontsize=default_fontsize)
        value = self._value
        error = self._error
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
                 ('Ar40_blank_err', error()),

                 ('Ar39_blank', value()),
                 ('Ar39_blank_err', error()),

                 ('Ar38_blank', value()),
                 ('Ar38_blank_err', error()),

                 ('Ar37_blank', value()),
                 ('Ar37_blank_err', error()),

                 ('Ar36_blank', value()),
                 ('Ar36_blank_err', error()),
                 )
        for args in attrs:
            if len(args) == 3:
                attr, fmt, fontsize = args
            else:
                attr, fmt = args
                fontsize = default_fontsize

            v = getattr(analysis, attr)
            row.add_item(value=v, fmt=fmt, fontsize=fontsize)

        return row.render()

    def _set_column_widths(self, ta, spec):
        scale = lambda x: x / 100.*inch
        ta._argW[0] = scale(spec.status_width)
        ta._argW[1] = scale(spec.id_width)
        ta._argW[2] = scale(spec.power_width)

        ta._argW[3] = scale(spec.moles_width)

        for i, n in enumerate(['ar40', 'ar39', 'ar38', 'ar37', 'ar36']):
            w = 4 + 2 * i
            ta._argW[w] = scale(getattr(spec, '{}_width'.format(n)))
            ta._argW[w + 1] = scale(getattr(spec, '{}_error_width'.format(n)))

        ta._argW[14] = 0.4 * inch  # rad40
        ta._argW[15] = 0.7 * inch  # rad40/k39
        ta._argW[16] = 0.5 * inch  # age
        ta._argW[17] = 0.5 * inch  # age err

        ta._argW[18] = 0.4 * inch  # k/ca
        ta._argW[19] = 0.5 * inch  # blank fit type

        start = 20
        for i, n in enumerate(['ar40', 'ar39', 'ar38', 'ar37', 'ar36']):
            ta._argW[start + 2 * i] = scale(getattr(spec, '{}_width'.format(n)))
            ta._argW[start + 2 * i + 1] = scale(getattr(spec, '{}_error_width'.format(n)))

#===============================================================================
#
#===============================================================================
    def _fmt_attr(self, v, key='nominal_value', n=5, scale=1, **kw):
        if v is None:
            return ''

        if isinstance(v, tuple):
            if key == 'std_dev':
                v = v[1]
            else:
                v = v[0]
        elif isinstance(v, (float, int)):
            pass
        else:

            v = getattr(v, key)

        v = v / float(scale)

        return floatfmt(v, n=n, max_width=8, **kw)

    def _error(self, **kw):
        return lambda x: self._fmt_attr(x, key='std_dev', **kw)

    def _value(self, **kw):
        return lambda x: self._fmt_attr(x, key='nominal_value', **kw)

#============= EOF =============================================
