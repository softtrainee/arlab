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
from traits.api import HasTraits, Str, List, Float
from traitsui.api import View, Item, EnumEditor, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================

class Level(HasTraits):
    name = Str
    tray = Str
    z = Float
    trays = List
    def traits_view(self):
        v = View(HGroup(Item('name'),
                        Item('tray', show_label=False, editor=EnumEditor(name='trays'))),
                 buttons=['OK', 'Cancel']
                 )
        return v

    def _trays_changed(self):
        self.tray = self.trays[0]
#    def _tray_default(self):
#        return self.trays[0]
#============= EOF =============================================
