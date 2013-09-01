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
from traits.api import List, Property, Int, Any, Str, Bool, cached_property
from traitsui.api import View, Item, UItem, HGroup, spring


#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.ui.tabular_editor import myTabularEditor
from src.processing.tasks.tables.editors.adapters import LaserTableAdapter, \
    LaserTableMeanAdapter
from src.processing.analysis_means import Mean
from src.processing.tasks.tables.editors.base_table_editor import BaseTableEditor
from src.processing.tasks.tables.laser_table_pdf_writer import LaserTablePDFWriter


class LaserTableEditor(BaseTableEditor):

    means = Property(List, depends_on='items[]')
    show_blanks = Bool(True)

    def make_table(self, title):
        ans = self._clean_items()
        means = self.means

        t = LaserTablePDFWriter(
                                orientation='landscape'
                                )

        t.col_widths = self._get_column_widths()

        p = '/Users/ross/Sandbox/aaatable.pdf'

        t.build(p, ans, means, title=title)
        return p

    def _get_column_widths(self):
        status_width = 6

        ac = map(lambda x: x * 0.6, self.col_widths)
        cs = [status_width]
        cs.extend(ac)

        return cs

    @cached_property
    def _get_means(self):
        return [Mean(analyses=self._clean_items()), ]

    def _show_blanks_changed(self, new):
        if new:
            self.items = self.oitems
        else:
            self.items = self._clean_items()

    def traits_view(self):
        v = View(
                 HGroup(spring, Item('show_blanks')),
                 UItem('items',
                       editor=myTabularEditor(adapter=LaserTableAdapter(),
                                              editable=False,
                                              col_widths='col_widths',
                                              selected='selected',
                                              multi_select=True
#                                               auto_resize=True,
#                                               stretch_last_section=False
                                            )

                       ),
                UItem('means',
                      editor=myTabularEditor(adapter=LaserTableMeanAdapter(),
                                             editable=False,
                                             auto_update=False
                                             )
                      )



                 )
        return v
#============= EOF =============================================
