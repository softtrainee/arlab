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
from traits.api import Str, Property, List, Bool, Button
from traitsui.api import View, Item, EnumEditor, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.initialization_parser import InitializationParser
from src.hardware.core.i_core_device import ICoreDevice

BLANK_STR = '------'

class RegisterManager(Manager):
    plugin = Str(BLANK_STR)
    manager = Str(BLANK_STR)

    name = Str
    klass = Str(BLANK_STR)
    enabled = Bool
    write = Bool
    register = Button

    plugins = Property(depends_on='_plugins')
    _plugins = List
    managers = Property(depends_on='_managers')
    _managers = List

    klasses = Property

    def _register_fired(self):
        if self.name and self.klass is not BLANK_STR:
            app = self.application
            if app:
                PROTOCOLS = dict(
                               ExtractionLine='src.extraction_line.extraction_line_manager.ExtractionLineManager',
                               FusionsCO2='src.lasers.laser_managers.fusions_co2_manager.FusionsCO2Manager',
                               FusionsDiode='src.lasers.laser_managers.fusions_diode_manager.FusionsDiodeManager',

                               )
                man = self
                if self.plugin is not BLANK_STR:
                    man = app.get_service(PROTOCOLS[self.plugin])
                    if self.manager is not BLANK_STR:
                        man = getattr(man, self.manager)

                if not app.get_service(ICoreDevice, 'name=="{}"'.format(self.name)):

                    dev = man.create_device(self.name,
                                             dev_class=self.klass)
                    dev.bootstrap()
                    dev.post_initialize()
                    app.register_service(ICoreDevice, dev, {'display': True})

                    hm = app.get_service('src.managers.hardware_manager.HardwareManager')
                    hm.load_devices()

    def _get_klasses(self):
        from src.hardware import HW_PACKAGE_MAP
        return [BLANK_STR] + HW_PACKAGE_MAP.keys()

    def load(self):
        ip = InitializationParser()
        self._plugins = ip.get_plugins(category='hardware', all=True)
        self.plugin = self._plugins[0]

    def get_managers(self, plugin):
        ip = InitializationParser()
        p = ip.get_plugin(plugin, category='hardware')
        return [BLANK_STR] + ip.get_managers(p, all=True)

    def _plugin_changed(self):
        mans = self.get_managers(self.plugin)
        self._managers = mans
        self.manager = self._managers[0] if self._managers else BLANK_STR

    def _get_plugins(self):
        return self._plugins

    def _get_managers(self):
        return self._managers

    def traits_view(self):
        v = View(
                 HGroup(
                        Item('plugin', editor=EnumEditor(name='object.plugins')),
                        Item('manager', editor=EnumEditor(name='object.managers'))
                        ),
                 Item('name'), Item('enabled'),
                 Item('klass', editor=EnumEditor(name='object.klasses')),
                 Item('register')
                 )
        return v

if __name__ == '__main__':
    m = RegisterManager()
    m.load()
    m.configure_traits()
#============= EOF =============================================
