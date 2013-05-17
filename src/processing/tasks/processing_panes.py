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

def make_pom_name(name):
    return 'object.active_plotter_options.{}'.format(name)

def PomUItem(name, *args, **kw):
    return UItem(make_pom_name(name), *args, **kw)

class OptionsPane(TraitsDockPane):
    name = 'Plot Options'
    id = 'pychron.processing.options'
    def traits_view(self):
        v = View(
                 HGroup(
                    PomUItem('plotter_options',
                         editor=EnumEditor(name=make_pom_name('plotter_options_list')),
                         tooltip='List of available plot options'
                         ),
                    PomUItem('add_options', tooltip='Add new plot options',

                         ),
                    PomUItem('delete_options',
                         tooltip='Delete current plot options',
                         enabled_when='object.plotter_options.name!="Default"',
#                         show_label=False
                         ),
                        ),
                   PomUItem('plotter_options',

                        style='custom'),
                 )
        return v
#============= EOF =============================================
