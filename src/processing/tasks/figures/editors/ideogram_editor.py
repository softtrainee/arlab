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
from traits.api import HasTraits, Instance

#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.figures.figure_editor import FigureEditor
from src.processing.plotter_options_manager import IdeogramOptionsManager
from src.processing.plotters.figure_container import FigureContainer
from src.processing.tasks.figures.editors.auto_controls import AutoIdeogramControl


class IdeogramEditor(FigureEditor):
    plotter_options_manager = Instance(IdeogramOptionsManager, ())
    basename = 'ideo'
    def get_component(self, ans, plotter_options):
        if plotter_options is None:
            pom = IdeogramOptionsManager()
            plotter_options = pom.plotter_options

        from src.processing.plotters.ideogram.ideogram_model import IdeogramModel
        model = IdeogramModel(plot_options=plotter_options)
        model.analyses = ans
        iv = FigureContainer(model=model)
        return iv.component

class AutoIdeogramEditor(IdeogramEditor):
    auto_figure_control = Instance(AutoIdeogramControl, ())

#============= EOF =============================================
