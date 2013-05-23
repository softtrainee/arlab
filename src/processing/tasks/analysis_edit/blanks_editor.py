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
from traits.api import HasTraits, Instance, Str, Bool, List, implements
from traitsui.api import View, Item, UItem, ListEditor, InstanceEditor, \
    EnumEditor, HGroup, VGroup, spring, Label, Spring
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.graph.graph import Graph
from src.constants import FIT_TYPES
from src.processing.tasks.analysis_edit.ianalysis_edit_tool import IAnalysisEditTool

#============= standard library imports ========================
#============= local library imports  ==========================
class Fit(HasTraits):
    name = Str
    use = Bool
    show = Bool
    fit = Str
    def traits_view(self):
        v = View(HGroup(
                        UItem('name', style='readonly'),
                        UItem('show'),
                        UItem('fit', editor=EnumEditor(values=FIT_TYPES),
                             enabled_when='show'
                             ),
                        UItem('use'),
                        )
                 )
        return v

class FitSelector(HasTraits):
    implements(IAnalysisEditTool)
    fits = List(Fit)
    def traits_view(self):
        header = HGroup(
                        Spring(springy=False, width=50),
                        Label('Show'),
                        spring,
                        Label('Use'),
                        spring,
                        )
        v = View(
                 VGroup(
                        header,
                        Item('fits',
                             style='custom',
                             show_label=False,
                             editor=ListEditor(mutable=False,
                                            editor=InstanceEditor(),
                                            style='custom'
                                                )))
                 )
        return v

    def _fits_default(self):
        return [Fit(name='Ar40')]

class BlanksEditor(BaseTraitsEditor):
    graph = Instance(Graph)
    name = Str
    tool = Instance(FitSelector, ())

    def traits_view(self):
        v = View(UItem('graph', style='custom'))
        return v

    def _graph_default(self):
        g = Graph()
        g.new_plot()
        g.new_series([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 2, 5])
        return g
#============= EOF =============================================
