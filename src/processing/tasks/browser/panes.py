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
    VSplit, TabularEditor, EnumEditor, Group, DateEditor, StyledDateEditor, Heading
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traitsui.tabular_adapter import TabularAdapter
# from src.experiment.utilities.identifier import make_runid
# from traitsui.table_column import ObjectColumn
# from traitsui.list_str_adapter import ListStrAdapter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.panes import new_button_editor
from src.ui.tabular_editor import myTabularEditor


class BrowserAdapter(TabularAdapter):
    font = 'arial 10'


class ProjectAdapter(BrowserAdapter):
    columns = [('Name', 'name')]


class AnalysisAdapter(BrowserAdapter):
    columns = [('RunID', 'record_id'),
               ('Tag', 'tag'),
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
    multi_select = True
    analyses_defined = Str('1')

    def _get_browser_group(self):
        project_grp = VGroup(
            HGroup(Label('Filter'),
                   UItem('project_filter',
                         width=75
                   ),
                   new_button_editor('clear_selection_button',
                                     'cross',
                                     tooltip='Clear selected'),
            ),
            UItem('projects',
                  editor=TabularEditor(editable=False,
                                       selected='selected_project',
                                       adapter=ProjectAdapter(),
                                       multi_select=True
                  ),
                  width=75
            )
        )
        sample_grp = VGroup(
            HGroup(
                #Label('Filter'),
                UItem('sample_filter_parameter',
                      editor=EnumEditor(name='sample_filter_parameters')),
                UItem('sample_filter',
                      width=75),
                UItem('sample_filter',
                      editor=EnumEditor(name='sample_filter_values'),
                      width=-25),
                UItem('filter_non_run_samples',
                      tooltip='Omit non-analyzed samples'),
            ),
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

        grp = VSplit(
            project_grp,
            sample_grp,
            self._get_analysis_group(),
            label='Project/Sample'
        )

        return grp

    def _get_date_group(self):
        f_grp = HGroup(
            UItem('analysis_type',
                  editor=EnumEditor(name='analysis_types')),
            UItem('mass_spectrometer',
                  editor=EnumEditor(name='mass_spectrometers')),
            UItem('extraction_device',
                  editor=EnumEditor(name='extraction_devices')),
        )

        grp = VGroup(
            f_grp,
            Heading('Start'),
            UItem('start_date',
                  editor=DateEditor(allow_future=False),
                  style='custom'),
            UItem('start_time', ),
            Item('_'),
            Heading('End'),
            UItem('end_date',
                  editor=DateEditor(allow_future=False),
                  style='custom'),
            UItem('end_time', ),
        )
        return VSplit(grp,
                      self._get_analysis_group(base='danalysis'),
                      label='Date'
        )

    def _get_analysis_group(self, base='analysis'):
        def make_name(name):
            return 'object.{}_table.{}'.format(base, name)

        analysis_grp = VGroup(
            HGroup(
                #Label('Filter'),
                UItem(make_name('analysis_filter_parameter'),
                      editor=EnumEditor(name=make_name('analysis_filter_parameters'))),
                UItem(make_name('analysis_filter_comparator')),
                UItem(make_name('analysis_filter'),
                      width=75),
                UItem(make_name('analysis_filter'),
                      editor=EnumEditor(name=make_name('analysis_filter_values')),
                      width=-25),
                new_button_editor(make_name('configure_analysis_filter'), 'cog',
                                  tooltip='Configure/Advanced query'
                ),
            ),
            UItem(make_name('analyses'),
                  editor=myTabularEditor(
                      adapter=AnalysisAdapter(),
                      #                                                       editable=False,
                      operations=['move'],
                      selected=make_name('selected_analysis'),
                      multi_select=self.multi_select,
                      drag_external=True

                  ),
                  #                                  editor=ListStrEditor(editable=False,
                  #                                           selected='selected_analysis'
                  #                                           )
                  width=300
            ),
            HGroup(
                new_button_editor(make_name('backward'),
                                  'control_rewind'
                ),
                spring,
                UItem(make_name('limit')),
                spring,
                new_button_editor(make_name('forward'),
                                  'control_fastforward'),
                UItem(make_name('page')),
                Item(make_name('omit_invalid'))
            ),
            defined_when=self.analyses_defined,
        )
        return analysis_grp

    def traits_view(self):
        v = View(
            Group(
                self._get_browser_group(),
                self._get_date_group(),
                layout='tabbed'
            )

        )

        return v


#============= EOF =============================================
