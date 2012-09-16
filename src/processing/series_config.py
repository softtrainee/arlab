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
from traits.api import HasTraits, Bool, Str, Enum
from traitsui.api import View, Item, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================

class SeriesConfig(HasTraits):
    label = Str
    show = Bool
    show_baseline = Bool

    fit = Enum('Linear', 'Parabolic', 'Cubic', 'Average')
    fit_baseline = Enum('Linear', 'Parabolic', 'Cubic', 'Average')

    def traits_view(self):
        v = View(HGroup(Item('show', label=self.label),
                        Item('fit', show_label=False),
                        Item('show_baseline', label='Baseline'),
                        Item('fit_baseline', show_label=False),
                        )
                 )
        return v
#============= EOF =============================================
