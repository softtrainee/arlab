#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, List, Property, Str, Enum
from traitsui.api import View, Item, HGroup, \
    TableEditor, ListEditor, InstanceEditor, EnumEditor
from constants import NULL_STR
#============= standard library imports ========================
#============= local library imports  ==========================
class PlotterOption(HasTraits):
    plot_name = Str(NULL_STR)
    plot_names = Property

    scale = Enum('linear', 'log')
    def _get_plot_names(self):
        return {NULL_STR:NULL_STR,
                'analysis_number':'Analysis Number',
                'radiogenic':'Radiogenic 40Ar',
                'kca':'K/Ca'
                }
    def traits_view(self):
        v = View(
                 HGroup(
                        Item('plot_name',
                             show_label=False,
                             editor=EnumEditor(name='plot_names')),

                        Item('scale', show_label=False)
                        ),
                )

        return v

class PlotterOptions(HasTraits):
    plots = List()
    def get_aux_plots(self):
        return reversed([pi
                for pi in self.plots if pi.plot_name != NULL_STR])

    def _plots_default(self):
        return [PlotterOption() for i in range(5)]

    def traits_view(self):
        v = View(Item('plots',
                      style='custom',
                      show_label=False,
                      editor=ListEditor(mutable=False,
                                        style='custom',
                                        editor=InstanceEditor())))
        return v
#============= EOF =============================================
