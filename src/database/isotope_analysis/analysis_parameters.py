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
from traits.api import HasTraits, Str, Float, Bool, Property
from traitsui.api import View, Item, HGroup, Label, Spring, EnumEditor
from src.constants import FIT_TYPES, PLUSMINUS

#============= standard library imports ========================
#============= local library imports  ==========================

class AnalysisParameters(HasTraits):
    fit = Str  # Enum('linear', 'parabolic', 'cubic')
    filterstr = Str(enter_set=True, auto_set=False)
    name = Str
    intercept = Property(depends_on='_intercept')
    error = Property(depends_on='_error')
    _intercept = Float
    _error = Float
#    analysis = Any
#    fittypes = List(FIT_TYPES)
    show = Bool(False)
    filter_outliers = Bool(True)

    def _get_intercept(self):

        return'{:<12s}'.format('{:0.5f}'.format(self._intercept))

    def _get_error(self):
        e = self._error
        try:
            ee = abs(e / self._intercept * 100)
            ee = '{:0.2f}'.format(ee)
        except ZeroDivisionError:
            ee = 'Inf'
        e = '{:0.6f}'.format(e)
        return u'{}{:<12s}({}%)'.format(PLUSMINUS, e, ee)

#    def _name_changed(self):
#        if self.name == 'Ar40':
#            self.show = True

    def traits_view(self):
        v = View(HGroup(Label(self.name),
                        Spring(width=50 - 10 * len(self.name), springy=False),
                        Item('show', show_label=False),
                        Item('fit', editor=EnumEditor(values=FIT_TYPES),
                             show_label=False,
                             enabled_when='show'
                             ),
#                        Item('fit[]', style='custom',
#                              editor=BoundEnumEditor(values=['linear', 'parabolic', 'cubic'],
#
#                                                     )),
                        Item('filterstr[]', enabled_when='show'),
                        Item('filter_outliers',
                             enabled_when='show',
                             show_label=False),
                        Spring(width=20, springy=False),
                        Item('intercept',
                              style='readonly',
                              show_label=False,
                              ),
                        Item('error',
                              show_label=False,
                              style='readonly')
                        )
                 )
        return v
#============= EOF =============================================
