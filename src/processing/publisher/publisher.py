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
from traits.api import HasTraits, List
#============= standard library imports ========================
from reportlab.platypus.doctemplate import SimpleDocTemplate
#from reportlab.platypus.tables import Table, TableStyle
#from reportlab.lib.styles import getSampleStyleSheet
#from reportlab.platypus import Paragraph
#from reportlab.lib.units import inch

#============= local library imports  ==========================
from src.loggable import Loggable
from src.processing.publisher.templates.tables.spectrum import SpectrumTable
from src.processing.publisher.templates.tables.ideogram_table import IdeogramTable
import csv
import os
from reportlab.lib.units import inch
#from reportlab.lib import colors



class Publisher(Loggable):
    def writer(self, out, kind='pdf'):
        if kind == 'pdf':
            klass = PDFWriter
        elif kind == 'csv':
            klass = CSVWriter
        elif kind == 'massspec':
            klass = MassSpecCSVWriter
        pub = klass(filename=out)
        return pub

#    def publish(self, samples, out, kind='pdf'):
#        if kind == 'pdf':
#            klass = PDFPublisher
#
#        pub = klass(filename=out)
#        pub.add_spectrum_table([1, 2])
##        for si in samples:
##            pass
##            pub.add_spectrum()
##            pub.add_sample(si)
#
#        pub.publish()
class BaseWriter(Loggable):
    filename = ''
    def publish(self):
        pass

class CSVWriter(BaseWriter):
    _rows = List
    header = ['record_id',
              'age_value', 'age_error',
              'temp_status',
              'group_id', 'graph_id']
    subheader = None
    delimiter = ','
    attrs = None
    def _add_header(self):
        header_row = self.header
        self._rows.append(header_row)
        if self.subheader:
            self._rows.append(self.subheader)

    def add_ideogram_table(self, analyses, title=False, header=False, add_group_marker=True):

        if header:
            self._add_header()

        attrs = self.attrs
        if not attrs:
            attrs = self.header

        for ai in analyses:
            row = [getattr(ai, hi) for hi in attrs]
            self._rows.append(row)
        if add_group_marker:
            self.add_group_marker()

    def add_group_marker(self):
        self._rows.append([])

    def publish(self):
        with open(self.filename, 'w') as fp:
            writer = csv.writer(fp, delimiter=self.delimiter)
            for ri in self._rows:
                writer.writerow(ri)

class MassSpecCSVWriter(CSVWriter):
    delimiter = ','
    header = ['Run ID# (pref. XXXX-XX)',
            'Sample',
             'J',
            'J',
            'Status (0=OK, 1=Deleted)',
            'Moles 39Ar X 10^-14',
            'Moles 40Arr X 10^-14',
            '40Ar*/39Ar,%40Ar*',
            '%40Ar*',
            '39K/Ktotal',
            '36Ar/39Ar  (corrected for D and decay)',
            '36ArCa/36ArTotal',
            '38Cl/39Ar',
            '38Cl/39Ar',
            '37Ar/39Ar',
            '37Ar/39Ar',
            'Power or Temp.',
            'Age',
            'Age Error(w/o  J;  irr. Param. Opt.)',
            '40Ar',
            '40Ar',
            '39Ar',
            '39Ar',
            '38Ar',
            '38Ar',
            '37Ar',
            '37Ar',
            '36Ar',
            '36Ar',
            'Isoch. 40/36',
            'Isoch 39/36',
            '% i40/36',
            '% i39/36',
            '% i39/40',
            'Cor. Coef. 40/39',
            'Cor.Coef. 36/39']
    attrs = ['record_id', 'sample', 'j', 'jerr', 'status',
             '', '', '', '', '', '', '', '', '', '', '', '',
             'age_value', 'age_error'
             ]

    subheader = ['Required',
            'Required',
            'Required',
            'Required',
            'Required',
            'Req. moles plot',
            'Req. moles plot',
            'Req. spectrum',
            'Req. pct. Rad. Plot',
            'Opt. In pct. Rad. Plot',
            'Opt. In spec. if use Exclude Ca39 Opt. For spectrum table',
            'Opt. For spectrum table',
            'Req. Cl / K plot',
            'Opt. In Cl / K plot',
            'Req. Ca / K plot',
            'Opt. In Ca / K plot',
            'Opt.',
            'Req. spectrum, age-prob.',
            'Req. spectrum, age-prob.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Requred spectrum',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. spec. isot. Recomb.',
            'Req. for isochron',
            'Req. for isochron',
            'Req. inv. isoch.',
            'Req. conv. isoch.',
            'Req. inv. isoch.',
            'Req. conv. isoch.',
            'Req. inv. isoch.']

    def add_group_marker(self):
        self._rows.append(['<new_group>'])


class PDFWriter(BaseWriter):
    _text = ''
#    def __init__(self,*args,**kw):
    _flowables = List

    def add_ideogram_table(self, analyses,
                           configure_table=True,
                           add_title=False, add_header=False, tablenum=1, **kw):
        ta = IdeogramTable()
        if configure_table:
            info = ta.edit_traits(kind='modal')
            if not info.result:
                return True

        ta.add_header = add_header
        ta.add_title = add_title
        ta.number = tablenum
        fta = ta.make(analyses)
        self._flowables.append(fta)

    def add_spectrum_table(self, samples):

        ta = SpectrumTable()
        fta = ta.make(samples)
        self._flowables.append(fta)


    def add_sample(self):
        pass

    def publish(self):
        doc = SimpleDocTemplate(self.filename,
                                leftMargin=0.5 * inch,
                                rightMargin=0.5 * inch
                                )
        doc.build(self._flowables)


class DummyAnalysis(HasTraits):
    @property
    def age_value(self):
        return 10.23543626543
    @property
    def age_error(self):
        return 0.03421435345
    def __getattr__(self, attr):
        return ''

if __name__ == '__main__':
    out = '/Users/ross/Sandbox/publish.txt'

    pub = Publisher()
    pi = pub.writer(out, kind='massspec')

    ans = [DummyAnalysis(record_id='4000-{:02n}'.format(i)) for i in range(5)]
    pi.add_ideogram_table(ans, title=True, header=True)
    ans = [DummyAnalysis(record_id='5000-{:02n}'.format(i)) for i in range(5)]
    pi.add_ideogram_table(ans)
    ans = [DummyAnalysis(record_id='6000-{:02n}'.format(i)) for i in range(5)]
    pi.add_ideogram_table(ans)
    ans = [DummyAnalysis(record_id='7000-{:02n}'.format(i)) for i in range(5)]
    pi.add_ideogram_table(ans)
    pi.publish()
#============= EOF =============================================
