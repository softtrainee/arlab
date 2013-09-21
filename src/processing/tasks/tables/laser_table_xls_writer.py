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
from traits.api import HasTraits, Bool , Instance
from traitsui.api import View, Item
#============= standard library imports ========================
from itertools import groupby
#============= local library imports  ==========================
from src.loggable import Loggable
from xlwt.Workbook import Workbook
from xlwt.Style import XFStyle, default_style
from xlwt.Formatting import Borders
from xlwt import Alignment

class LaserTableXLSOptions(HasTraits):
    use_sample_sheets = Bool(True)

def value(x, k):
    x = getattr(x, k)
    return x.nominal_value

def error(x, k):
    x = getattr(x, k)
    return x.std_dev

def blank_value(x, k):
    x = x.isotopes[k]
    return x.blank.uvalue.nominal_value

def blank_error(x, k):
    x = x.isotopes[k]
    return x.blank.uvalue.std_dev


class LaserTableXLSWriter(Loggable):
    options = Instance(LaserTableXLSOptions, ())

    columns = (
                    ('Status', 'status'),
                    ('N', 'aliquot_step_str'),
                    ('Power', 'extract_value'),

#                     'Moles_40Ar',
                    ('Ar40', 'Ar40', value),
                    ('Ar40Er', 'Ar40', error),
                    ('Ar39', 'Ar39', value),
                    ('Ar39Er', 'Ar39', error),
                    ('Ar38', 'Ar38', value),
                    ('Ar38Er', 'Ar38', error),
                    ('Ar37', 'Ar37', value),
                    ('Ar37Er', 'Ar37', error),
                    ('Ar36', 'Ar36', value),
                    ('Ar36Er', 'Ar36', error),

                    # blanks
                    ('Ar40', 'Ar40', blank_value),
                    ('Ar40Er', 'Ar40', blank_error),
                    ('Ar39', 'Ar39', blank_value),
                    ('Ar39Er', 'Ar39', blank_error),
                    ('Ar38', 'Ar38', blank_value),
                    ('Ar38Er', 'Ar38', blank_error),
                    ('Ar37', 'Ar37', blank_value),
                    ('Ar37Er', 'Ar37', blank_error),
                    ('Ar36', 'Ar36', blank_value),
                    ('Ar36Er', 'Ar36', blank_error),

                    )

    def build(self, p, ans, means, title):
        wb = self._new_workbook()
        options = self.options
        if options.use_sample_sheets:
            key = lambda x:x.sample
            for sam, ais in groupby(ans, key=key):
                sh = self._add_sample_sheet(wb, sam)
                ais = list(ais)

                self._add_metadata(sh, ais[0])
                self._add_header_row(sh, 2)
                self._add_analyses(sh, ais, start=4)
        wb.save(p)

    def _new_workbook(self):
        return Workbook()

    def _add_metadata(self, sh, refans):
        for i, c in enumerate(('labnumber', 'sample', 'material')):
            sh.write(0, i, getattr(refans, c))
        for i, c in enumerate(('irradiation', 'irradiation_level')):
            sh.write(1, i, getattr(refans, c))

    def _add_sample_sheet(self, wb, sample):
        sh = wb.add_sheet(sample)
        return sh

    def _add_header_row(self, sheet, hrow=0):
        style = XFStyle()
        al = Alignment()
        al.horz = Alignment.HORZ_CENTER
        style.alignment = al

        names = [c[0] for c in self.columns]

        sheet.write(hrow, 13, 'Blanks', style=style)
        sheet.merge(hrow, hrow, 13, 22)

        borders = Borders()
        borders.bottom = 2
        style.borders = borders

        for i, ci in enumerate(names):
            sheet.write(hrow + 1, i, ci, style=style)



    def _add_analyses(self, sheet, ans, start):
        for i, ai in enumerate(ans):
            self._add_analysis(sheet, i + start, ai)

    def _add_analysis(self, sheet, row, ai):

        status = 'X' if ai.tag else ''

        sheet.write(row, 0, status)
        for j, c in enumerate(self.columns[1:]):
            attr = c[1]
            if len(c) == 3:
                getter = c[2]
            else:
                getter = getattr

            txt = getter(ai, attr)

            style = default_style
            sheet.write(row, j + 1, txt, style)


#============= EOF =============================================
