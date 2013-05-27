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
from traits.api import HasTraits, Float, Str, List, Bool
from traitsui.api import View, Item, VGroup, UItem, \
     Label, Spring, spring, HGroup, TableEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traitsui.table_column import ObjectColumn
from src.helpers.isotope_utils import sort_isotopes
from traitsui.extras.checkbox_column import CheckboxColumn
#============= standard library imports ========================
#============= local library imports  ==========================
class UValue(HasTraits):
    nominal_value = Float
    std_dev = Float
    name = Str
    use = Bool
    def _nominal_value_changed(self):
        self.use = True

    def _std_dev_changed(self):
        self.use = True

class BatchEditPane(TraitsDockPane):
    disc_value = Float
    values = List
    blanks = List
    unknowns = List
    def _unknowns_changed(self):
        keys = set([ki  for ui in self.unknowns
                        for ki in ui.isotope_keys])
        self.blanks = [UValue(name=ki) for ki in list(keys)]

    def _discrimination_group(self):
        cols = [
                ObjectColumn(name='name', editable=False),
                ObjectColumn(name='nominal_value', label='Value'),
                ObjectColumn(name='std_dev', label='Error'),
                CheckboxColumn(name='use', label='Use')
                ]
        grp = VGroup(UItem('values', editor=TableEditor(columns=cols)),
                     label='Detectors'
                     )
        return grp

    def _blanks_group(self):
        cols = [
                ObjectColumn(name='name', editable=False),
                ObjectColumn(name='nominal_value', label='Value'),
                ObjectColumn(name='std_dev', label='Error'),
                CheckboxColumn(name='use', label='Use')
                ]
        grp = VGroup(UItem('blanks', editor=TableEditor(columns=cols)),
                     label='Blanks'
                     )
        return grp

    def _values_default(self):
        v = [
             UValue(name='disc.'),
             UValue(name='ic'),
             ]
        return v

    def _blanks_default(self):
        v = [
             UValue(name='Ar40'),
             ]
        return v

    def traits_view(self):
        v = View(
                 VGroup(
                        self._discrimination_group(),
                        self._blanks_group()
                        )
                 )
        return v
#============= EOF =============================================
