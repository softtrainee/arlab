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
from traits.api import HasTraits, Button, List, Instance
from traitsui.api import View, Item, UItem, HGroup, VGroup, spring
from pyface.tasks.traits_dock_pane import TraitsDockPane
from src.ui.tabular_editor import myTabularEditor
from traitsui.tabular_adapter import TabularAdapter
from src.processing.tasks.analysis_edit.ianalysis_edit_tool import IAnalysisEditTool
#============= standard library imports ========================
#============= local library imports  ==========================

class UnknownsAdapter(TabularAdapter):
    columns = [('Run ID', 'record_id')]

class ReferencesAdapter(TabularAdapter):
    columns = [('Run ID', 'record_id')]

class TablePane(TraitsDockPane):

    append_button = Button
    replace_button = Button
    items = List

    def traits_view(self):
        v = View(VGroup(
                      HGroup(
                             UItem('append_button'),
                             UItem('replace_button'),
                             ),
                      UItem('items', editor=myTabularEditor(adapter=self.adapter_klass()))
                      )
               )
        return v

class UnknownsPane(TablePane):
    id = 'pychron.analysis_edit.unknowns'
    name = 'Unknowns'
    adapter_klass = UnknownsAdapter

class ReferencesPane(TablePane):
    name = 'References'
    id = 'pychron.analysis_edit.references'
    adapter_klass = ReferencesAdapter


class ControlsPane(TraitsDockPane):
    save_button = Button('Save')
    tool = Instance(IAnalysisEditTool)
    id = 'pychron.analysis_edit.controls'
    name = 'Controls'
    def traits_view(self):
        v = View(
                 VGroup(
                        UItem('tool', style='custom'),
                        HGroup(spring, UItem('save_button'))
                        )
                 )
        return v
#============= EOF =============================================
