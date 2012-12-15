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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.processing.publisher.templates.tables.pdf_table import PDFTable
from reportlab.platypus.tables import TableStyle
from reportlab.lib.units import inch
from src.stats.core import calculate_weighted_mean, calculate_mswd
#============= standard library imports ========================
#============= local library imports  ==========================

class IdeogramTable(PDFTable):
    def create(self, analyses, title, header):
        rows = self.create_header(title, header)
        for ai in analyses:
            r = self._make_analysis_row(ai)
            rows.append(r)
        self._create_summary_row(rows, analyses)

        return self._create(rows, title, header)

    def _create_summary_row(self, rows, analyses):
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

    def _create_header(self, tablen, use_title, use_header):
        header = []
        if use_title:
            title = self._new_paragraph('<font size=10 name="Helvetica-Bold">Table {}. <super>40</super>Ar/<super>39</super>Ar analytical data.</font>'.format(tablen))
            header = [[title]]

        if use_header:
            sigma = self._new_paragraph(self._plusminus_sigma())
            header += [
                      [],
                      ['', 'ID', 'Power', 'Age', sigma],
                      []
                      ]
        else:
            header += [[]]

        return header


    def _make_analysis_row(self, analysis):


        row = ['', analysis.record_id,
               analysis.extract_value,
               self.floatfmt(analysis.age_value),
               self.floatfmt(analysis.age_error, n=6)
               ]

        return row

    def _get_style(self, use_title, use_header):
        style = TableStyle()
        if use_title:
            #make first row span entire table
            style.add('SPAN', (0, 0), (-1, 0))

        return style

    def _set_column_widths(self, ta):
        ta._argW[0] = 0.17 * inch
        ta._argW[1] = 0.7 * inch
        ta._argW[2] = 1.5 * inch
        ta._argW[3] = 1.5 * inch
        ta._argW[4] = 1.5 * inch



#============= EOF =============================================
