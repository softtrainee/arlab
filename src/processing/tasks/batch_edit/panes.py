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
from traits.api import HasTraits, Float, Str, List, Bool, Button, Property
from traitsui.api import View, VGroup, UItem, \
    HGroup, TableEditor, ButtonEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from pyface.image_resource import ImageResource

from src.helpers.isotope_utils import sort_isotopes
from src.paths import paths

#============= standard library imports ========================
#============= local library imports  ==========================
class UValue(HasTraits):
    nominal_value = Float
    std_dev = Float
    name = Str
    use = Bool

    def _nominal_value_changed(self, old, new):
        if old:
            self.use = True

    def _std_dev_changed(self, old, new):
        if old:
            self.use = True


class BatchEditPane(TraitsDockPane):
    values = List
    blanks = List
    #     unknowns = List

    db_sens_button = Button
    sens_value = Property(Float, depends_on='_sens_value')
    _sens_value = Float

    def populate(self, unks):


        keys = set([ki for ui in unks
                    for ki in ui.isotope_keys])
        keys = sort_isotopes(list(keys))

        blanks = []
        for ki in keys:
            blank = next((bi for bi in self.blanks if bi.name == ki), None)
            if blank is None:
                blank = UValue(name=ki)
            blanks.append(blank)

        self.blanks = blanks

        keys = set([iso.detector for ui in unks
                    for iso in ui.isotopes.itervalues()
        ])
        keys = sort_isotopes(list(keys))
        values = []
        for ki in keys:
            # vi.name includes "IC "
            value = next((vi for vi in self.values if vi.name[3:] == ki), None)
            if value is None:
                value = UValue(name='IC {}'.format(ki))
            values.append(value)

        self.values = [UValue(name='disc')] + values

    #===============================================================================
    # property get/set
    #===============================================================================
    def _get_sens_value(self):
        return self._sens_value

    def _set_sens_value(self, v):
        self._sens_value = v

    def _validate_sens_value(self, v):
        return self._validate_float(v)


    def _validate_float(self, v):
        try:
            return float(v)
        except ValueError:
            pass


        #===============================================================================
        # views
        #===============================================================================

    def _discrimination_group(self):
        cols = [
            ObjectColumn(name='name', editable=False),
            ObjectColumn(name='nominal_value',
                         width=75,
                         label='Value'),
            ObjectColumn(name='std_dev',
                         width=75,
                         label='Error'),
            CheckboxColumn(name='use', label='Use')
        ]
        grp = VGroup(UItem('values', editor=TableEditor(columns=cols,
                                                        sortable=False, )),
                     label='Detectors'
        )
        return grp

    def _blanks_group(self):
        cols = [
            ObjectColumn(name='name', editable=False),
            ObjectColumn(name='nominal_value',
                         width=75,
                         label='Value'),
            ObjectColumn(name='std_dev',
                         width=75,
                         label='Error'),
            CheckboxColumn(name='use', label='Use')
        ]
        grp = VGroup(UItem('blanks', editor=TableEditor(columns=cols,
                                                        sortable=False,
        )),
                     label='Blanks'
        )
        return grp

    def _sensitivity_group(self):
        im = ImageResource(
            name='database_go.png',
            search_path=paths.icon_search_path

        )
        beditor = ButtonEditor(image=im)

        grp = VGroup(
            HGroup(
                UItem('sens_value', ),
                UItem('db_sens_button',
                      style='custom',
                      editor=beditor)
            ),

            label='Sensitivity'
        )

        return grp

    def _values_default(self):
        v = [
            UValue(name='disc.'),
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
                self._blanks_group(),
                self._sensitivity_group()
            )
        )
        return v

    #============= EOF =============================================
