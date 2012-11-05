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
from traits.api import HasTraits, Str, Enum, Float, Any, List, Bool, Property
from traitsui.api import View, Item, HGroup, Label, Spring, EnumEditor
#from constants import FIT_TYPES
#============= standard library imports ========================
#import wx
#============= local library imports  ==========================
FIT_TYPES = ['linear', 'parabolic', 'cubic', u'average \u00b1SD', u'average \u00b1SEM']

class AnalysisParameters(HasTraits):
    fit = Str#Enum('linear', 'parabolic', 'cubic')
    filterstr = Str(enter_set=True, auto_set=False)
    name = Str
    intercept = Property(depends_on='_intercept')
    error = Property(depends_on='_error')
    _intercept = Float
    _error = Float
#    analysis = Any
    fittypes = List(FIT_TYPES)
    show = Bool(False)

    def _get_intercept(self):

        return'{:<12s}'.format('{:0.5f}'.format(self._intercept))

    def _get_error(self):
        e = self._error
        try:
            ee = abs(e / self._intercept * 100)
        except ZeroDivisionError:
            ee = 'Inf'
        e = '{:0.6f}'.format(e)
        return u'\u00b1{:<12s}({:0.2f}%)'.format(e, ee)

    def _name_changed(self):
        if self.name == 'Ar40':
            self.show = True

    def traits_view(self):
        v = View(HGroup(Label(self.name),
                        Spring(width=50 - 10 * len(self.name), springy=False),
                        Item('show', show_label=False),
                        Item('fit', editor=EnumEditor(name='fittypes'),
                             show_label=False),
#                        Item('fit[]', style='custom',
#                              editor=BoundEnumEditor(values=['linear', 'parabolic', 'cubic'],
#
#                                                     )),
                        Item('filterstr[]'),
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
