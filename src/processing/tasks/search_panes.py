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
from traits.api import HasTraits, Int, Property
from traitsui.api import View, Item, InstanceEditor, ListEditor, \
    VGroup, UItem, spring, HGroup, VSplit, EnumEditor, TableEditor, VFold, \
    ButtonEditor

from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.ui.tabular_editor import myTabularEditor
from traitsui.tabular_adapter import TabularAdapter
from src.ui.custom_label_editor import CustomLabel
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from src.database.core.query import Query
from traitsui.table_filter import TableFilter
from src.paths import paths
from pyface.image_resource import ImageResource
import os
#============= standard library imports ========================
#============= local library imports  ==========================
def selector_name(name):
    return 'object.selector.{}'.format(name)


class QueryPane(TraitsDockPane):
    id = 'pychron.search.query'
    name = 'Query'

    def _table_editor(self):
        cols = [
                CheckboxColumn(name='use', label='',
                               width=30),
                ObjectColumn(name='parameter',
                             editor=EnumEditor(name='parameters'),
                             label='Param.',
                             width=125
                             ),
                ObjectColumn(name='comparator',
                             editor=EnumEditor(name='comparisons'),
                             label='',
                             width=50
                             ),
#                 ObjectColumn(name='criterion'),
                ObjectColumn(name='criterion',
                             editor=EnumEditor(name='criteria'),
                             label='Value',
                             width=125
                             ),
                ]


        editor = TableEditor(columns=cols,
                             deletable=True,
                             show_toolbar=True,
                             sortable=False,
                             selected=selector_name('selected_queries'),
                             selection_mode='rows',

#                              auto_size=True
                             row_factory=self.model.database_selector.query_factory,
#                              auto_add=True
                             )

        return editor
    def traits_view(self):
#         editor = ListEditor(mutable=False,
#                           style='custom',
#                           editor=InstanceEditor())
#
        editor = self._table_editor()
        query_itm = Item(selector_name('queries'), show_label=False,
                                   style='custom',
                                   editor=editor,
#                                    editor=ListEditor(mutable=False,
#                                                   style='custom',
#                                                   editor=InstanceEditor()),
#                              height=0.25,
#                             visible_when='kind=="Database"',
                             )

        filter_grp = HGroup(UItem(selector_name('mass_spectrometer'),
                                 label='Spec.',
                                 editor=EnumEditor(name=selector_name('mass_spectrometers')),
                              ),
                            UItem(selector_name('analysis_type'),
                              editor=EnumEditor(name=selector_name('analysis_types')),
                              ),
                            UItem(selector_name('search'),
                               ),
                            )
        query_grp = VGroup(
                         query_itm,
                         filter_grp,
                         visible_when='kind=="Database"',
#                          label='Query'
                         )
        v = View(

                 VGroup(
                        HGroup(
                               UItem('kind'),
                               UItem('open_button',
                                     visible_when='kind=="File"'
                                     )
                               ),

                        HGroup(spring,

                               UItem(selector_name('add_query_button'),
                                    style='custom',
                                    editor=ButtonEditor(label='',
                                                        image=ImageResource(name='add.png',

                                                                            search_path=[
                                                                                         paths.icons,
                                                                                         paths.app_resources,
                                                                                         ]
                                                                            ),
                                                        )


                                     ),
                               UItem(selector_name('delete_query_button'),
                                    style='custom',
                                    editor=ButtonEditor(image=ImageResource(name='delete.png',
                                                                            search_path=[
                                                                                         paths.icons,
                                                                                         paths.app_resources,
                                                                                         ]
                                                                            ))

                                     ),
                               visible_when='kind=="Database"'),
                        query_grp,
#                         VSplit(
#                         VFold(
#                                results_grp,
#                                ),
#                         filter_grp
                        )
                 )
        return v

class ResultsPane(TraitsDockPane):
    id = 'pychron.search.results'
    name = 'Results'
    def traits_view(self):
        results_grp = VGroup(
                             CustomLabel(selector_name('id_string'), color='red'),
                             HGroup(
                                    CustomLabel(selector_name('num_records')), spring,
                                    Item(selector_name('limit'))),
                             Item(selector_name('records'),
                                    style='custom',
                                    editor=myTabularEditor(adapter=ResultsAdapter(),
                                                           selected=selector_name('selected'),
                                                           scroll_to_row=selector_name('scroll_to_row'),
#                                                            update='update',
                                                           column_clicked=selector_name('column_clicked'),
                                                           multi_select=True,
                                                           operations=['move'],
                                                           editable=True,
                                                           drag_external=True,
                                                           dclicked=selector_name('dclicked')
                                                           ),
                                    show_label=False,
#                                     height=0.75
                                    ),
                             label='Results'
                        )

        v = View(results_grp)
        return v

class ResultsAdapter(TabularAdapter):
    columns = [
#               ('ID', 'rid'),
               ('Lab. #', 'labnumber'),
               ('Aliquot', 'aliquot'),
               ('Analysis Time', 'timestamp'),
#               ('Time', 'runtime'),
               ('Irradiation', 'irradiation_info'),
               ('Spec.', 'mass_spectrometer'),
               ('Type', 'analysis_type')
#               ('Irradiation', 'irradiation_level')
               ]
    font = 'monospace 12'
#    rid_width = Int(50)
    labnumber_width = Int(50)
    mass_spectrometer_width = Int(50)
    aliquot_width = Int(50)
    timestamp_width = Int(110)
    irradiation_info_width = Int(65)

    aliquot_text = Property

    def _get_aliquot_text(self):
        return '{:02n}{}'.format(self.item.aliquot, self.item.step)

# class ResultsPane(TraitsDockPane):
#    id = 'pychron.search.results'
#    name = 'Results'
#    def traits_view(self):
#        v = View(
#
#                 )
#        return v
#============= EOF =============================================
