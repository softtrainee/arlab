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
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.publisher.templates.tables.pdf_table import PDFTable

class SpectrumTable(PDFTable):

    def create(self, samples, use_title):
        rows = self.create_header(use_title)

        self.int_plat_age_rowids = []
        self.sample_rowids = []
        self.sample_ends = []
        for s in samples:
            self.sample_rowids.append(len(rows))
            self._build_sample_rows(rows, s)
            self.sample_ends.append(len(rows))

        self._create(rows)

    def _build_sample_rows(self, trows, sample):
#        info_line = self._new_paragraph(u'<font size=9><b>{sample}</b></font>, <font size=7>{material}, {weight} mg, J={j}\xb1{jer}%, D={d}\xb1{der}, {irrad}, Lab#={l_number}</font>'.format(**sample.info))
#        trows.append(['', info_line])

#        analyses = sample.analyses
#        intage, intage_err = sample.get_isotopic_recombination_age()
#        tot39 = '{:0.1f}'.format(sample.get_total39())
#        kca, _er = sample.get_kca()
#        nsteps = sample.get_nsteps()
#        plateau_args = sample.get_plateau_steps()
#        n = len(sample.analyses)

        analyses = [1, 2, 3]
        intage, intage_err = 1, 0
        kca = 4
        nsteps = 1
        tot39 = 3
        plateau_args = None
        n = 1

        for i, a in enumerate(analyses):
            if i < 1:
                self.zap_orphans(trows)

            trows.append(str(i))
#            trows.append(a.get_data())

        intage_label = self._new_paragraph(u'<font size=9><b>Integrated age ' + self._plusminus_sigma(2) + '</b></font>')
        platage_label = self._new_paragraph(u'<font size=9><b>Plateau ' + self._plusminus_sigma(2) + '</b></font>')

        kca = '{:0.1f}'.format(kca)
        nsteps = 'n={}'.format(nsteps)

        ptot39, mswd, psteps, npsteps, plat39, age, err, kca, pkca = '', '', '', '', '', '', '', '', ''
        if plateau_args:
            ps, pe, pss = plateau_args
            ptot39 = '{:0.1f}'.format(sample.get_total39(plateau=True))
            mswd = '{:0.2f}'.format(sample.get_mswd())
            psteps = 'steps {}-{}'.format(ps, pe)
            npsteps = 'n={}'.format(pss)
            plat39 = '{:0.1f}'.format(sample.get_plateau_percent39())
            age, err = map('{:0.3f}'.format, sample.get_plateau_age())
            kca_args = sample.get_kca(plateau=True)
            pkca = self._new_paragraph(u'<font size=9>{:0.2f}\xb1{:0.2f}</font>'.format(*kca_args))

        self.int_plat_age_rowids.append(len(trows))
        trows.append(['', intage_label, '', '', nsteps, '', tot39, kca, '', '', '{:0.2f}'.format(intage), '{:0.2f}'.format(intage_err)])

        self.zap_widows(trows, n)

        trows.append(['', platage_label, '', psteps, npsteps, mswd, ptot39, pkca, '', plat39, age, err])
        trows.append([])

    def zap_widows(self, trows, n, trip_row=38, widow_rows=2):
        s = len(trows) % trip_row
        if s <= widow_rows:
            for i in range(n + widow_rows - s):
                trows.insert(-n - 2, [])
                self.sample_rowids[-1] += 1
                self.int_plat_age_rowids[-1] += 1

    def _get_style(self):
        tblstyle = TableStyle([
                               ('SPAN', (0, 0), (-1, 0)),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                               ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
#                            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
                               ('LINEBELOW', (0, 3), (-1, 3), 1.5, colors.black),
                               #('LINEBELOW', (0, 0), (-1, -1), 1, colors.red),

#                               ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),
                               ('ALIGN', (2, 0), (-1, -1), 'CENTER')
                              ])

        for ir in self.int_plat_age_rowids:
            tblstyle.add('SPAN', (1, ir), (3, ir))
            tblstyle.add('SPAN', (1, ir + 1), (2, ir + 1))

        for si in self.sample_rowids:
            tblstyle.add('SPAN', (1, si), (-1, si))

#        self._table.setStyle(tblstyle)

    def _set_row_heights(self, ta):
        ta._argH[1] = 0.0125 * inch
        ta._argH[4] = 0.2 * inch

        for s in self.sample_ends:
            try:
                ta._argH[s] = 0.25 * inch
            except IndexError:
                break

    def _set_column_widths(self, ta):
        ta._argW[0] = 0.17 * inch
        ta._argW[2] = 0.5 * inch
        st = 3
        ta._argW[st] = 0.6 * inch
        ta._argW[st + 1] = 0.6 * inch
        ta._argW[st + 2] = 0.6 * inch
        ta._argW[st + 3] = 0.7 * inch
        ta._argW[st + 4] = 0.5 * inch
        ta._argW[st + 5] = 0.5 * inch

    def _create_header(self, tablen, use_title, use_header):
        ar4039 = self._new_paragraph('<font size=9><super>40</super>Ar/<super>39</super>Ar</font>')
        ar3739 = self._new_paragraph('<font size=9><super>37</super>Ar/<super>39</super>Ar</font>')
        ar3639 = self._new_paragraph('<font size=9><super>36</super>Ar/<super>39</super>Ar</font>')
        ar39k = self._new_paragraph('<font size=9><super>39</super>Ar<sub>K</sub></font>')
        ar3639_mult = self._new_paragraph('<font size=7>(x 10<super>-3</super>)</font>')
        ar39k_mult = self._new_paragraph('<font size=7>(x 10<super>-15</super> mol)</font>')
        rad = self._new_paragraph('<font size=9><super>40</super>Ar*</font>')
        sigma = self._new_paragraph(self._plusminus_sigma())
        degrees = self._new_paragraph(unicode('(\xa1C)'))
        ar39 = self._new_paragraph('<font size=9><super>39</super>Ar</font>')
        header = []
        if use_title:
            title = self._new_paragraph('<font size=10 name="Helvetica-Bold">Table {}. <super>40</super>Ar/<super>39</super>Ar analytical data.</font>'.format(tablen))
            header = [[title, ]]

        if use_header:
            header += [
                 [],
                 ['', 'ID', 'Temp', ar4039 , ar3739, ar3639, ar39k, 'K/Ca', rad, ar39, 'Age', sigma],
                 ['', '', degrees, '', '', ar3639_mult, ar39k_mult, '', '(%)', '(%)', '(Ma)', '(Ma)'],
                 [],
#                 [info_line]
                 ]
        return header
#============= EOF =============================================
