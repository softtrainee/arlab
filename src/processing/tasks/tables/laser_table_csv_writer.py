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
# from traits.etsconfig.etsconfig import ETSConfig
# ETSConfig.toolkit = 'qt4'

#============= enthought library imports =======================
from traits.api import HasTraits, Any, Str, Callable, Either, List
#============= standard library imports ========================
import csv
#============= local library imports  ==========================
from src.processing.tasks.tables.laser_table_text_writer import LaserTableTextWriter


class CSVCell(HasTraits):
    txt = Any
    fmt = Either(Str, Callable)
    def render(self):
        txt = self.txt
        if txt is None:
            return ''

        fmt = self.fmt
        if fmt is None:
            fmt = str


        if isinstance(fmt, str):
            return fmt.format(txt)
        else:
            return fmt(txt)

class CSVRow(HasTraits):
    cells = List
    def render(self, writer):
        rows = [ci.render() for ci in self.cells]
        writer.writerow(rows)

    def write(self, c, v):
        while c >= len(self.cells) or not len(self.cells):
            self.cells.append(CSVCell())

        nc = self.cells[c]
        nc.txt = v


class CSVSheet(HasTraits):
    rows = List
    name = Str
    def render(self, writer):
        writer.writerow([self.name, ])
        for ri in self.rows:
            ri.render(writer)

        writer.writerow([])

    def write(self, r, c, v, *args, **kw):
        while r >= len(self.rows) or not len(self.rows):
            self.rows.append(CSVRow())

        nr = self.rows[r]
        nr.write(c, v)

    def merge(self, *args, **kw):
        pass


class CSVWorkbook(HasTraits):
    '''
     emulates an xlwt Workbook
    '''
    sheets = List

    def add_sheet(self, name):
        sh = CSVSheet(name=name)
        self.sheets.append(sh)
        return sh

    def save(self, p, **kw):
        with open(p, 'w') as fp:
            writer = csv.writer(fp)

            for sh in self.sheets:
                sh.render(writer)


class LaserTableCSVWriter(LaserTableTextWriter):
    def _new_workbook(self):
        return CSVWorkbook()


# if __name__ == '__main__':
#     l = LaserTableCSVWriter()
#     from src.processing.analyses.analysis import DBAnalysis
#     ans = [DBAnalysis(sample='foo', labnumber='11111') for i in range(5)]
#     ans.extend([DBAnalysis(sample='bar',
#                            labnumber='22222'
#                            ) for i in range(5)])
#     p = '/Users/ross/Sandbox/aaaatable.csv'
#     l.build(p, ans, [], 'foo')

#============= EOF =============================================
