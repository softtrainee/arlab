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
from traits.api import HasTraits, Str, Float, Bool, Int, on_trait_change, Property
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
#============= local library imports  ==========================
class BaseIrradiatedPosition(HasTraits):
    labnumber = Str
    material = Str
    sample = Str
    hole = Int
    project = Str
    j = Float(0)
    j_err = Float(0)
    pred_j = Float
    pred_j_err = Float
    x = Float
    y = Float
    residual = Property(depends_on='j,pred_j')

    use = Bool
    save = Bool
    def _get_residual(self):
        pe = 0
        if self.pred_j:
            try:
                pe = abs(self.j - self.pred_j) / self.j * 100
            except ZeroDivisionError:
                pe = 0
        return pe


class IrradiatedPosition(BaseIrradiatedPosition):
#    labnumber = Str
#    material = Str
#    sample = Str
#    hole = Int
#    project = Str
    size = Str
    weight = Str
    note = Str
#    j = Float
#    j_err = Float

    auto_assigned = Bool(False)
#
    @on_trait_change('labnumber,sample, project, material')
    def _update_auto_assigned(self, obj, name, old, new):
#        print 'ol', name, old, new
        if old:
            self.auto_assigned = False

class BaseIrradiatedPositionAdapter(TabularAdapter):
    columns = [
               ('Hole', 'hole'),
               ('Labnumber', 'labnumber'),
               ('Sample', 'sample'),
               ('Project', 'project'),
               ('J', 'j'),
               (u'\u00b1J', 'j_err'),
               ('Note', 'note')
             ]

    hole_width = Int(45)

class IrradiatedPositionAdapter(TabularAdapter):
    columns = [
               ('Hole', 'hole'),
               ('Labnumber', 'labnumber'),
               ('Sample', 'sample'),
               ('Project', 'project'),
               ('Material', 'material'),
               ('Size', 'size'),
               ('Weight', 'weight'),
               ('J', 'j'),
               (u'\u00b1J', 'j_err'),
               ('Note', 'note')
             ]
#    hole_can_edit = False
    hole_width = Int(45)
#    def _get_hole_width(self):
#        return 35

    def get_bg_color(self, obj, trait, row):
        item = getattr(obj, trait)[row]
        if item.auto_assigned:
            return '#B0C4DE'
#============= EOF =============================================
