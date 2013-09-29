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
from traits.api import HasTraits, Property, Int, Bool, Str
from traitsui.api import View, Item, UItem, VGroup, HGroup, Label, spring, \
    VSplit, TabularEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traitsui.tabular_adapter import TabularAdapter
# from src.experiment.utilities.identifier import make_runid
# from traitsui.table_column import ObjectColumn
# from traitsui.list_str_adapter import ListStrAdapter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.ui.tabular_editor import myTabularEditor

class BrowserAdapter(TabularAdapter):
    font = 'arial 10'

class ProjectAdapter(BrowserAdapter):
    columns = [('Name', 'name')]

class AnalysisAdapter(BrowserAdapter):
    columns = [('RunID', 'record_id'),
                ('Iso Fits', 'iso_fit_status'),
                ('Blank', 'blank_fit_status'),
                ('IC', 'ic_fit_status'),
                ('Flux', 'flux_fit_status'),
               ]
#     record_id_text = Property
#     blank_fit_status_text = Property
#     flux_fit_status_text = Property
#     iso_fit_status_text = Property
#     ic_fit_status_text = Property

    record_id_width = Int(65)
    odd_bg_color = 'lightgray'
    font = 'arial 10'


class SampleAdapter(BrowserAdapter):

    columns = [('Sample', 'name'), ('Material', 'material')]
#     material_text = Property
    odd_bg_color = 'lightgray'

#     def _get_material_text(self):
#         n = ''
#         n = self.item.material
#         return n

class BrowserPane(TraitsDockPane):
    name = 'Browser'
    id = 'pychron.browser'
    multi_select = False
    analyses_defined = Str('1')

    def traits_view(self):
        projectgrp = VGroup(
                            HGroup(Label('Filter'),
                                   UItem('project_filter',
                                         width=75
                                         )),
                            UItem('projects',
                                editor=TabularEditor(editable=False,
                                          selected='selected_project',
                                          adapter=ProjectAdapter()
                                          ),
                                width=75
                                )
                          )
        samplegrp = VGroup(
                           HGroup(Label('Filter'),
                                  UItem('sample_filter',
                                        width=75)),
                           UItem('samples',
                                editor=TabularEditor(
                                                     adapter=SampleAdapter(),
                                                     editable=False,
                                                     selected='selected_sample',
                                                     multi_select=True,
                                                     dclicked='dclicked_sample',
                                                     ),
                                 width=75
                                )
                          )
        analysisgrp = VGroup(
                           HGroup(Label('Filter'),
                                  UItem('analysis_filter',
                                        width=75)),
                           UItem('analyses',
                                 editor=myTabularEditor(
                                                      adapter=AnalysisAdapter(),
#                                                       editable=False,
                                                      operations=['move'],
                                                      selected='selected_analysis',
                                                      multi_select=self.multi_select,
                                                      drag_external=True

                                                      ),
#                                  editor=ListStrEditor(editable=False,
#                                           selected='selected_analysis'
#                                           )
                                width=300
                                 ),
                            HGroup(spring, Item('omit_invalid')),
                            defined_when=self.analyses_defined,
                           )

        v = View(
                VSplit(
                        projectgrp,
                        samplegrp,
                        analysisgrp
#                         ),
                        )
                )

        return v



#============= EOF =============================================
