# @PydevCodeAnalysisIgnore
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
from traits.api import Float
from traitsui.api import View, Item, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.corrections.correction import Correction

class FixedValueCorrection(Correction):
    value = Float
    error = Float
    def _value_changed(self):
        self.use = True
    def _error_changed(self):
        self.use = True

    def traits_view(self):
        v = View(HGroup(
                        Item('name', style='readonly', show_label=False),
                        Item('use', show_label=False),
                        Item('value', show_label=False),
                        Item('error', show_label=False),
                        ))
        return v
#============= EOF =============================================
