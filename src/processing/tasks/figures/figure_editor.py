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
from traits.api import HasTraits, Any, Instance, on_trait_change
from traitsui.api import View, Item, UItem
#============= standard library imports ========================
#============= local library imports  ==========================
from enable.component_editor import ComponentEditor as EnableComponentEditor
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.processing.plotter_options_manager import IdeogramOptionsManager, \
    SpectrumOptionsManager

class FigureEditor(BaseTraitsEditor):
    component = Any
    tool = Any
    plotter_options_manager = Any
    processor = Any

    def traits_view(self):
        v = View(UItem('component',
                       style='custom',
                       width=700,
                       editor=EnableComponentEditor()))
        return v


class IdeogramEditor(FigureEditor):
    plotter_options_manager = Instance(IdeogramOptionsManager, ())
#    @on_trait_change('plotter_options_manager.plotter_options.[+, aux_plots:+]')
#    def _update_options(self, name, new):
#        po = self.plotter_options_manager.plotter_options
#        self.processor.new_ideogram(plotter_options=po)

class SpectrumEditor(FigureEditor):
    plotter_options_manager = Instance(SpectrumOptionsManager, ())
#============= EOF =============================================
