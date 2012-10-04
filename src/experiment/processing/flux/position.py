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
from traits.api import HasTraits, Float, Int, Bool
#from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
class Position(HasTraits):
    labnumber = Int
    hole = Int
    x = Float
    y = Float
    j = Float
    jerr = Float
    pred_j = Float
    pred_jerr = Float
    use_j = Bool(True)
    save = Bool(True)

    @property
    def ar40(self):
        return (1, 0.1)

    @property
    def ar39(self):
        return (0.5, 0.1)

    @property
    def residual(self):
        if self.j:
            return (self.j - self.pred_j) / self.j * 100
        else:
            return 0
#============= EOF =============================================
