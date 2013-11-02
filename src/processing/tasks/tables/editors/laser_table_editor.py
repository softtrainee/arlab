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
from traits.api import List, Property, cached_property
from traitsui.api import View, UItem


#============= standard library imports ========================
#============= local library imports  ==========================
from src.ui.tabular_editor import myTabularEditor
from src.processing.tasks.tables.editors.adapters import LaserTableAdapter, \
    LaserTableMeanAdapter
from src.processing.analysis_means import Mean
from src.processing.tasks.tables.editors.base_table_editor import BaseTableEditor

from itertools import groupby
from src.column_sorter_mixin import ColumnSorterMixin


class LaserTableEditor(BaseTableEditor, ColumnSorterMixin):
    means = Property(List, depends_on='items[]')
    #show_blanks = Bool(False)

    #     refresh_means = Event

    def _items_items_changed(self):
        self.refresh_needed = True

    def make_pdf_table(self, title):
        from src.processing.tables.laser_table_pdf_writer import LaserTablePDFWriter

        ans = self._clean_items()
        t = LaserTablePDFWriter(
            orientation='landscape',
            use_alternating_background=self.use_alternating_background
        )

        t.col_widths = self._get_column_widths()
        means = self.means

        p = self._get_save_path()
        #         p = '/Users/ross/Sandbox/aaaatable.pdf'
        if p:
            key = lambda x: x.sample
            ans = groupby(ans, key=key)
            t.build(p, ans, means, title=title)
            return p

    def make_xls_table(self, title):
        ans = self._clean_items()
        means = self.means
        from src.processing.tables.laser_table_xls_writer import LaserTableXLSWriter

        t = LaserTableXLSWriter()
        p = self._get_save_path(ext='.xls')
        #         p = '/Users/ross/Sandbox/aaaatable.xls'
        if p:
            t.build(p, ans, means, title)
            return p

    def make_csv_table(self, title):
        ans = self._clean_items()
        means = self.means
        from src.processing.tables.laser_table_csv_writer import LaserTableCSVWriter

        t = LaserTableCSVWriter()

        #         p = '/Users/ross/Sandbox/aaaatable.csv'
        p = self._get_save_path(ext='.csv')
        if p:
            t.build(p, ans, means, title)
            return p

    def _get_column_widths(self):
        '''
            exclude the first column from col widths
            it is displaying in pychron but not in the pdf
        '''
        status_width = 6

        ac = map(lambda x: x * 0.6, self.col_widths[1:])
        cs = [status_width]
        cs.extend(ac)

        return cs

    @cached_property
    def _get_means(self):
        key = lambda x: x.sample
        ans = self._clean_items()
        ms = [
            Mean(analyses=list(ais),
                 sample=sam
            )
            for sam, ais in groupby(ans, key=key)]
        return ms

    #         return [Mean(analyses=self._clean_items()), ]

    #def refresh_blanks(self):
    #    self._show_blanks_changed(self.show_blanks)
    #
    #def _show_blanks_changed(self, new):
    #    if new:
    #        self.items = self.oitems
    #    else:
    #        self.items = self._clean_items()

    def traits_view(self):
        v = View(
            #HGroup(spring, Item('show_blanks')),
            UItem('items',
                  editor=myTabularEditor(adapter=LaserTableAdapter(),
                                         #                                               editable=False,
                                         col_widths='col_widths',
                                         selected='selected',
                                         multi_select=True,
                                         auto_update=False,
                                         operations=['delete', 'move'],
                                         column_clicked='column_clicked'
                                         #                                               auto_resize=True,
                                         #                                               stretch_last_section=False
                  )

            ),
            UItem('means',
                  editor=myTabularEditor(adapter=LaserTableMeanAdapter(),
                                         #                                              auto_resize=True,
                                         editable=False,
                                         auto_update=False,
                                         refresh='refresh_needed'
                  )
            )


        )
        return v

    #============= EOF =============================================
