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
#============= standard library imports ========================
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.units import inch
#============= local library imports  ==========================
STYLES = getSampleStyleSheet()

class PDFTable(object):
    _table = None
    def _new_paragraph(self, t, s='Normal'):
        style = STYLES[s]
        p = Paragraph(t, style)
        return p

    def _plusminus_sigma(self, n=1):
        s = unicode('\xb1{}'.format(n)) + unicode('\x73', encoding='Symbol')
        return s

    def zap_orphans(self, trows, trip_row=38):
        s = len(trows) % trip_row
        if s < 2:
            self.sample_rowids[-1] += 1
            trows.insert(-1, [])
            if not s:
                self.sample_rowids[-1] += 1
                trows.insert(-1, [])

    def floatfmt(self, v, n=5):
        fmt = '{{:0.{}f}}'.format(n)
        return fmt.format(v)

    def create_header(self, use_title, use_header, tablenum=1):
        rows = []
        header = self._create_header(tablenum, use_title, use_header)
        rows += header
        return rows

    def _create(self, rows, use_title, use_header):
        ts = Table(rows)
        self._set_column_widths(ts)
        self._set_row_heights(ts)
        s = self._get_style(use_title, use_header)
        ts.setStyle(s)
        return ts

    def _set_column_widths(self, ta):
        ta._argW[0] = 0.17 * inch
#        ta._argW[2] = 0.5 * inch

    def _set_row_heights(self, ts):
        pass
    def _get_style(self):
        pass
#============= EOF =============================================
