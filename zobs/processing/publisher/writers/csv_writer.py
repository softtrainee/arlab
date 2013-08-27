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
from traits.api import List

#============= standard library imports ========================
import csv
#============= local library imports  ==========================
from src.processing.publisher.writers.writer import BaseWriter


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
#============= EOF =============================================
