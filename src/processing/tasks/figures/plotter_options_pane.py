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
from traits.api import HasTraits, Any
from traitsui.api import View, Item, HGroup, EnumEditor, UItem, InstanceEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
#============= standard library imports ========================
#============= local library imports  ==========================

class PlotterOptionsPane(TraitsDockPane):
    '''
        Pane for displaying the active editor's plotter options manager
    '''
    id = 'pychron.processing.figures.plotter_options'

    name = 'Plot Options'
    pom = Any
    def traits_view(self):
        v = View(
                 UItem('pom',
                       editor=InstanceEditor(),
                       style='custom',
                       width= -400
                       )
#                 HGroup(
#                    UItem('plotter_options',
#                         editor=EnumEditor(name='plotter_options_list'),
#                         tooltip='List of available plot options'
#                         ),
#                    UItem('add_options', tooltip='Add new plot options',
#
#                         ),
#                    UItem('delete_options',
#                         tooltip='Delete current plot options',
#                         enabled_when='object.plotter_options.name!="Default"',
# #                         show_label=False
#                         ),
#                        ),
#                   UItem('plotter_options',
#                        style='custom'),
                 )
        return v

#============= EOF =============================================
