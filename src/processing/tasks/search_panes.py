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
from traits.api import HasTraits, Int
from traitsui.api import View, Item, InstanceEditor, ListEditor, \
    VGroup, UItem, spring, HGroup, VSplit

from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.ui.tabular_editor import myTabularEditor
from traitsui.tabular_adapter import TabularAdapter
from src.ui.custom_label_editor import CustomLabel
#============= standard library imports ========================
#============= local library imports  ==========================

class QueryPane(TraitsDockPane):
    id = 'pychron.search.query'
    name = 'Query'
    def traits_view(self):
        results_grp = VGroup(
                        HGroup(CustomLabel('num_records'), spring, Item('limit')),
                        Item('records',
                             style='custom',
                             editor=myTabularEditor(adapter=ResultsAdapter(),
                                                    selected='selected',
                                                    scroll_to_row='scroll_to_row',
#                                                    selected_row='selected_row',
                                                    update='update',
                                                    column_clicked='column_clicked',
#                                                    editable=False,
                                                    multi_select=True,
                                                    operations=['move'],
                                                    editable=True,
                                                    drag_external=True,
                                                    dclicked='dclicked'
                                                    ),
                             show_label=False,
#                               height=0.75,
#                               width=600,
                            )
                        )
        query_grp = VGroup(
                        CustomLabel('dbstring', color='red'),
                        Item('queries', show_label=False,
                                   style='custom',
                                   height=0.25,
                                   editor=ListEditor(mutable=False,
                                                  style='custom',
                                                  editor=InstanceEditor())
                             ),
                        HGroup(spring, UItem('search')))


        v = View(
                 VSplit(
                        results_grp,
                        query_grp
                        )
                 )
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
    font = 'monospace 10'
#    rid_width = Int(50)
    labnumber_width = Int(50)
    mass_spectrometer_width = Int(50)
    aliquot_width = Int(50)
    timestamp_width = Int(110)


# class ResultsPane(TraitsDockPane):
#    id = 'pychron.search.results'
#    name = 'Results'
#    def traits_view(self):
#        v = View(
#
#                 )
#        return v
#============= EOF =============================================
