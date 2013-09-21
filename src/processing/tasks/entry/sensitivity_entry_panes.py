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
from traits.api import HasTraits, Property, Str, Int
from traitsui.api import View, Item, TabularEditor, VGroup, spring, HGroup, \
    EnumEditor, ImageEditor, VFold, UItem, Spring
from pyface.tasks.traits_task_pane import TraitsTaskPane
# from src.irradiation.irradiated_position import IrradiatedPositionAdapter
# from pyface.tasks.traits_dock_pane import TraitsDockPane
# from src.ui.custom_label_editor import CustomLabel
from traitsui.tabular_adapter import TabularAdapter
# from src.processing.entry.irradiated_position import IrradiatedPositionAdapter
# from traitsui.editors.progress_editor import ProgressEditor
#============= standard library imports ========================
#============= local library imports  ==========================
class SensitivityAdapter(TabularAdapter):
    columns = [
#                ('', 'placeholder'),
               ('Spectrometer', 'mass_spectrometer'),
               ('Sensitivity', 'sensitivity'),
               ('User', 'user'),
               ('Date', 'create_date'),
               ('Note', 'note')]

#     placeholder_text = Str('')
#     placeholder_width = Int(2)


#    mass_spectrometer_width = Int(40)

class SensitivityPane(TraitsTaskPane):
    id = 'pychron.entry.sensitivty'
    def traits_view(self):
        v = View(Item('records',
                         editor=TabularEditor(adapter=SensitivityAdapter(),
                                              editable=False
#                                               refresh='refresh_table',
#                                               multi_select=True,
#                                               selected='selected',
#                                               operations=['edit']
#                                                 operations=[]
                                              ),
                         show_label=False
                         )
                 )
        return v






#============= EOF =============================================
