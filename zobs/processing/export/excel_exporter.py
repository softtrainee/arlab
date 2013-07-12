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
from src.processing.export.base import Exporter
import xlwt
from datetime import datetime
#============= standard library imports ========================
#============= local library imports  ==========================

class ExcelExporter(Exporter):
    def _export(self, p):
        wb = xlwt.Workbook()
        ws = wb.add_sheet('raw')

        def writerow(ri, r):
            for ci, c in enumerate(r):
                ws.write(ri, ci, c)

        writerow(0, self.header)
        for ri, ai in enumerate(self.figure.analyses):
            row = self._make_raw_row(ai)
            writerow(ri + 1, row)

        date_style = xlwt.XFStyle()
        date_style.num_format_str = 'DD-MM-YY'
        ws = wb.add_sheet('metadata')
        ws.write(0, 0, 'Save Date')
        ws.write(0, 1, datetime.now(), date_style)

        ws.write(1, 0, 'Version')
        ws.write(1, 1, '0.1')

        wb.save(p)
#============= EOF =============================================
