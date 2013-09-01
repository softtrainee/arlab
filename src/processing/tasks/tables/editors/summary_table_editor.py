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
from traitsui.api import View, UItem
from src.processing.tasks.tables.editors.base_table_editor import BaseTableEditor
from src.ui.tabular_editor import myTabularEditor
from src.processing.tasks.tables.editors.summary_adapter import SummaryTabularAdapter
from src.processing.tasks.tables.summary_table_pdf_writer import SummaryTablePDFWriter
#============= standard library imports ========================
#============= local library imports  ==========================


class SummaryTableEditor(BaseTableEditor):

    def make_table(self, title):
        samples = self.items
        t = SummaryTablePDFWriter()

        t.col_widths = self._get_column_widths()

        p = '/Users/ross/Sandbox/aaasumtable.pdf'

        t.build(p, samples, title=title)
        return p

    def _get_column_widths(self):
        cs = []
        ac = map(lambda x: x * 0.6, self.col_widths)
        cs.extend(ac)

        return cs

    def traits_view(self):
        v = View(UItem('items', editor=myTabularEditor(
                                                      adapter=SummaryTabularAdapter(),
                                                      editable=True,
                                                      operations=['delete', 'move'],
                                                      col_widths='col_widths'
                                                      )))
        return v


#============= EOF =============================================
