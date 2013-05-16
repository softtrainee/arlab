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
from traitsui.api import View, HGroup, Item, UItem, \
    InstanceEditor, EnumEditor
from pyface.tasks.traits_task_pane import TraitsTaskPane
from pyface.tasks.split_editor_area_pane import SplitEditorAreaPane
from pyface.tasks.traits_dock_pane import TraitsDockPane
#============= standard library imports ========================
#============= local library imports  ==========================

class ProcessorPane(SplitEditorAreaPane):
    pass
#    def traits_view(self):
#        v = View(
#                 UItem('graphs',
#                       style='custom',
#                      editor=ListEditor(
#                                        use_notebook=True,
#                                        show_notebook_menu=True
# #                                        editor=InstanceEditor(),
# #                                        dock_style='vertical'
#                                        )
#                      )
#
#                 )
#        return v
class TablePane(TraitsDockPane):
    pass
class SelectionPane(TraitsDockPane):
    pass
class OptionsPane(TraitsDockPane):
    name = 'Plot Options'
    id = 'pychron.processing.options'
    def traits_view(self):
        v = View(
                 HGroup(
                    Item('plotter_options', show_label=False,
                         editor=EnumEditor(name='plotter_options_list'),
                         tooltip='List of available plot options'
                         ),
                    Item('add_options', tooltip='Add new plot options',
                         show_label=False),
                    Item('delete_options',
                         tooltip='Delete current plot options',
                         enabled_when='object.plotter_options.name!="Default"',
                         show_label=False),
                        ),
                   Item('plotter_options', show_label=False,
                        style='custom'),
                 )
        return v
#============= EOF =============================================
