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
from traits.api import HasTraits, Str, Property, List, Dict
from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup, VGroup
from src.managers.manager import Manager
#============= standard library imports ========================
#============= local library imports  ==========================
class RegisterManager(Manager):
    plugin = Str
    manager = Str

    plugins = Property(depends_on='_plugins')
    _plugins = List
    managers = Property(depends_on='_managers')
    _managers = Dict

    def load(self):
        self._managers = dict(pa=['a', 'b'],
                             pb=['c', 'd'])

        self._plugins = ['pa', 'pb']

        self.plugin = 'pa'

    def _get_plugins(self):
        return self._plugins

    def _get_managers(self):
        try:
            return self._managers[self.plugin]
        except KeyError:
            return []

    def traits_view(self):
        v = View(
                 HGroup(
                        Item('plugin', editor=EnumEditor(name='object.plugins')),
                        Item('manager', editor=EnumEditor(name='object.managers'))
                        )
                 )
        return v

if __name__ == '__main__':
    m = RegisterManager()
    m.load()
    m.configure_traits()
#============= EOF =============================================
