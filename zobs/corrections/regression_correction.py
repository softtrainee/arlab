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
from traits.api import  Str
from traitsui.api import View, Item, EnumEditor, HGroup, spring, Spring
from src.constants import FIT_TYPES_INTERPOLATE
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.corrections.correction import Correction

class RegressionCorrection(Correction):
    fit = Str(FIT_TYPES_INTERPOLATE[0])

    def traits_view(self):
        v = View(HGroup(Item('name', style='readonly', show_label=False),
                        spring,
                        Item('use', show_label=False),
                        Item('fit', editor=EnumEditor(values=FIT_TYPES_INTERPOLATE),
                             show_label=False,
                             enabled_when='use'
                             ),
                        Spring(springy=False, width=100)
                        )
                 )
        return v
#============= EOF =============================================
