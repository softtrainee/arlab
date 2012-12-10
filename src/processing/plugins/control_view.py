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
from traits.api import HasTraits, Button, Any
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================


class ControlView(HasTraits):
    plot_ideogram = Button('Ideogram')
    plot_isochron = Button('Isochron')
    application = Any
    def _plot_ideogram_fired(self):
        man = self.application.get_service('src.processing.processing_manager.ProcessingManager')
        man.plot_ideogram()

    def _plot_isochron_fired(self):
        man = self.application.get_service('src.processing.processing_manager.ProcessingManager')
        man.plot_isochron()

    def traits_view(self):
        v = View(
                 Item('plot_ideogram', show_label=False),
                 Item('plot_isochron', show_label=False),

                 )
        return v
#============= EOF =============================================
