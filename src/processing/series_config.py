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
from traits.api import HasTraits, Bool, Str, Enum, on_trait_change, Any, Property
from traitsui.api import View, Item, HGroup, EnumEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class SeriesConfig(HasTraits):
    label = Str
    show = Bool
    show_baseline = Bool

    fit = Str('---')
    fits = Property

    fit_baseline = Enum('---', 'Linear', 'Parabolic', 'Cubic', 'Average')
    parent = Any(transient=True)

    def _get_fits(self):
        return ['---', 'Linear', 'Parabolic', 'Cubic', 'Average']

    @on_trait_change('show,show_baseline,fit,fit_baseline')
    def _change(self):
        if self.parent:
            self.parent.refresh()

    def traits_view(self):
        v = View(HGroup(Item('show', label=self.label),
                        Item('fit', editor=EnumEditor(name='fits'), show_label=False),
                        Item('show_baseline', label='Baseline'),
                        Item('fit_baseline', show_label=False),
                        )
                 )
        return v
#============= EOF =============================================
