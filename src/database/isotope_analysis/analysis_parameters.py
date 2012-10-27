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
from traits.api import HasTraits, Str, Enum, Float, Any, List
from traitsui.api import View, Item, HGroup, Label, Spring, EnumEditor
#============= standard library imports ========================
#import wx
#============= local library imports  ==========================


class AnalysisParameters(HasTraits):
    fit = Str#Enum('linear', 'parabolic', 'cubic')
    filterstr = Str(enter_set=True, auto_set=False)
    name = Str
    intercept = Float
    error = Float
#    analysis = Any
    fittypes = List(['linear', 'parabolic', 'cubic', u'average \u00b1SD', u'average \u00b1SEM'])
    def traits_view(self):
        v = View(HGroup(Label(self.name),
                        Spring(width=50 - 10 * len(self.name), springy=False),
                        Item('fit', editor=EnumEditor(name='fittypes'),
                             show_label=False),
#                        Item('fit[]', style='custom',
#                              editor=BoundEnumEditor(values=['linear', 'parabolic', 'cubic'],
#
#                                                     )),
                        Item('filterstr[]'),
                        Spring(width=50, springy=False),
                        Item('intercept', format_str='%0.5f',
                              style='readonly'),
                        Item('error', format_str='%0.5f',
                              style='readonly')
                        )
                 )
        return v
#============= EOF =============================================
