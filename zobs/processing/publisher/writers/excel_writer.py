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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.processing.publisher.writers.writer import BaseWriter
from xlwt.Workbook import Workbook
from xlwt import Style
from xlwt.Style import XFStyle
from xlwt.Formatting import Borders
#============= standard library imports ========================
#============= local library imports  ==========================

class ExcelWriter(BaseWriter):
    _sheet_count = 0
    def __init__(self, *args, **kw):
        super(ExcelWriter, self).__init__(*args, **kw)
        self._wb = Workbook()

    def add_ideogram_table(self, analyses,
                           widths=None,
#                           configure_table=True,
                           add_title=False, add_header=False, tablenum=1, **kw):

        sh = self._wb.add_sheet(analyses[0].labnumber)
#                                'sheet{:02n}'.format(self._sheet_count))
        self._sheet_count += 1

        cols = ['Status', 'N', 'Power', 'Moles_40Ar',
                'Ar40', 'Ar40Er',
                'Ar39', 'Ar39Er',
                'Ar38', 'Ar38Er',
                'Ar37', 'Ar37Er',
                'Ar36', 'Ar36Er',
                'Blank',
                'Ar40', 'Ar40Er',
                'Ar39', 'Ar39Er',
                'Ar38', 'Ar38Er',
                'Ar37', 'Ar37Er',
                'Ar36', 'Ar36Er'
                ]
        # write header row
        hrow = 0
        borders = Borders()
        borders.bottom = 2
        style = XFStyle()
        style.borders = borders
        for i, ci in enumerate(cols):
            sh.write(hrow, i, ci, style=style)

        numstyle = XFStyle()
        numstyle.num_format_str = '0.00'
        from operator import attrgetter
        def getnominal_value(attr):
            def get(x):
                v = getattr(x, attr)
                return float(v.nominal_value)
            return get

        def getstd_dev(attr):
            def get(x):
                v = getattr(x, attr)
                return float(v.std_dev)
            return get

        def getfloat(attr):
            def get(x):
                v = getattr(x, attr)
                return float(v)

            return get

        def null_value():
            return lambda x: ''
        attrs = [(attrgetter('step'),),
                 (getfloat('extract_value'),),
                 (null_value(),),
                 (getnominal_value('Ar40'),),
                 (getstd_dev('Ar40'),),
                 (getnominal_value('Ar39'),),
                 (getstd_dev('Ar39'),),
                 (getnominal_value('Ar38'),),
                 (getstd_dev('Ar38'),),
                 (getnominal_value('Ar37'),),
                 (getstd_dev('Ar37'),),
                 (getnominal_value('Ar36'),),
                 (getstd_dev('Ar36'),),
                 (null_value(),),
                 (getnominal_value('Ar40_blank'),),
                 (getstd_dev('Ar40_blank'),),
                 (getnominal_value('Ar39_blank'),),
                 (getstd_dev('Ar39_blank'),),
                 (getnominal_value('Ar38_blank'),),
                 (getstd_dev('Ar38_blank'),),
                 (getnominal_value('Ar37_blank'),),
                 (getstd_dev('Ar37_blank'),),
                 (getnominal_value('Ar36_blank'),),
                 (getstd_dev('Ar36_blank'),),

                 ]

        for i, ai in enumerate(analyses):
            for j, arg in enumerate(attrs):
                if len(arg) == 2:
                    func, style = arg
                else:
                    func, style = arg[0], Style.default_style
                sh.write(i + hrow + 1, 1 + j, func(ai),
                         style
                         )



    def publish(self):
        self._wb.save(self.filename)
#============= EOF =============================================
