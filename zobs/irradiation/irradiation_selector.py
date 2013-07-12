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
from traits.api import HasTraits, Property, Any, cached_property, String
from traitsui.api import View, Item, EnumEditor, HGroup, VGroup, spring
#============= standard library imports ========================
#============= local library imports  ==========================

class IrradiationSelector(HasTraits):
    db = Any
    irradiations = Property
    levels = Property(depends_on='irradiation')

    irradiation = String
    level = String
    def traits_view(self):
        v = View(
                 HGroup(
                        VGroup(Item('irradiation', editor=EnumEditor(name='irradiations')),
                               Item('level', editor=EnumEditor(name='levels'))
                               ),
                        spring
                        ),
               )

        return v

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_irradiations(self):
#        r = ['NM-Test', 'NM-100', 'NM-200']
        r = [str(ri.name) for ri in self.db.get_irradiations() if ri.name]
        if r and not self.irradiation:
            self.irradiation = r[-1]
        return r

    @cached_property
    def _get_levels(self):
        r = []
        irrad = self.db.get_irradiation(self.irradiation)
        if irrad:
            r = [str(ri.name) for ri in irrad.levels]
            if r:  # and not self.level:
                self.level = r[0]
#                print self.level
        return r
#============= EOF =============================================
