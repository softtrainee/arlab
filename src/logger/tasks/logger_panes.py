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
from traits.api import HasTraits, Any, Instance
from traitsui.api import View, Item, UItem
from pyface.tasks.traits_task_pane import TraitsTaskPane

#============= standard library imports ========================
#============= local library imports  ==========================

class DisplayPane(TraitsTaskPane):
    logger = Instance('src.displays.display.DisplayController')
    def traits_view(self):
        v = View(UItem('logger', style='custom'))

        return v
#============= EOF =============================================