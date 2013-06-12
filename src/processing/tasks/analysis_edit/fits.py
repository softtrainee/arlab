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
from traits.api import HasTraits, Str, Bool, Property, on_trait_change, \
    List, Event, Enum
from traitsui.api import View, Item, HGroup, VGroup, Spring, spring, \
    UItem, EnumEditor, ListEditor, InstanceEditor, Label, TableEditor
from src.constants import FIT_TYPES, FIT_TYPES_INTERPOLATE
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
#============= standard library imports ========================
#============= local library imports  ==========================
class Fit(HasTraits):
    name = Str
    use = Bool
    show = Bool
    fit_types = Property
#     fit = Enum(FIT_TYPES)
    fit = Str
    valid = Property(depends_on=('fit, use, show'))

    def _fit_default(self):
        return self.fit_types[0]

    def _get_fit_types(self):
        return FIT_TYPES

    def _get_valid(self):
        return self.use and self.show and self.fit

    def _show_changed(self):
        self.use = self.show

    def traits_view(self):
        v = View(HGroup(
                        UItem('name', style='readonly'),
                        UItem('show'),
                        UItem('fit',
                              editor=EnumEditor(name='fit_types'),
                              enabled_when='show',
                              width=-50,
                             ),
                        UItem('use'),
                        )
                 )
        return v

class FitSelector(HasTraits):

    fits = List(Fit)
    update_needed = Event
    fit_klass = Fit
    def traits_view(self):

        cols = [ObjectColumn(name='name', editable=False),
                CheckboxColumn(name='show'),
                ObjectColumn(name='fit',
                             editor=EnumEditor(name='fit_types',
                                               ),
                             ),
                CheckboxColumn(name='use')
                ]
        editor = TableEditor(columns=cols,
                             sortable=False,
                             )

        v = View(UItem('fits',
                       style='custom',
                       editor=editor
                       ))
        return v

    def traits_view2(self):
        header = HGroup(
                        Spring(springy=False, width=50),
                        Label('Show'),
                        spring,
                        Label('Use'),
                        spring,
                        )
        v = View(
                 VGroup(
                        header,
                        Item('fits',
                             style='custom',
                             show_label=False,
                             editor=ListEditor(mutable=False,
                                            editor=InstanceEditor(),
                                            style='custom'
                                                )))
                 )
        return v

    @on_trait_change('fits:[show, fit]')
    def _fit_changed(self):
        self.update_needed = True

    def load_fits(self, keys):
        self.fits = [
                     self.fit_klass(name=ki) for ki in keys
                    ]

class InterpolationFit(Fit):
    def _get_fit_types(self):
        return FIT_TYPES_INTERPOLATE

class InterpolationFitSelector(FitSelector):
    fit_klass = InterpolationFit

#============= EOF =============================================
