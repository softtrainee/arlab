#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import List
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.helpers.parsers.initialization_parser import InitializationParser
from src.lasers.laser_managers.ilaser_manager import ILaserManager

class LaserPlugin(CorePlugin):
    '''
        
    '''
    MANAGERS = 'pychron.hardware.managers'

    klass = None
    name = None
    def _service_offers_default(self):
        '''
        '''
        if self.klass is None:
            raise NotImplementedError

        so = self.service_offer_factory(
#                          protocol='.'.join(self.klass),
                          protocol=ILaserManager,
#                          'src.lasers.laser_managers.laser_manager.ILaserManager',
                          factory=self._factory)

        return [so]

    def _factory(self):
        '''
        '''
#        factory = __import__(self.klass[0], fromlist=[self.klass[1]])

        ip = InitializationParser()
        plugin = ip.get_plugin(self.klass[1].replace('Manager', ''), category='hardware')
#        mode = plugin.get('mode')
        mode = ip.get_parameter(plugin, 'mode')

        if mode == 'client':
            klass = ip.get_parameter(plugin, 'klass')
            if klass is None:
                klass = 'PychronLaserManager'

            pkg = 'src.lasers.laser_managers.pychron_laser_manager'
            try:
                tag = ip.get_parameter(plugin, 'communications', element=True)
#                tag = plugin.find('communications')
                params = dict()
                for attr in ['host', 'port', 'kind']:
                    try:
                        params[attr] = tag.find(attr).text.strip()
                    except Exception, e:
                        print e
            except Exception, e:
                print e
            params['name'] = self.name
            factory = __import__(pkg, fromlist=[klass])
            m = getattr(factory, klass)(**params)
        else:
            factory = __import__(self.klass[0], fromlist=[self.klass[1]])
            m = getattr(factory, self.klass[1])()

        m.bootstrap()
        m.plugin_id = self.id
        m.bind_preferences(self.id)
        return m

    managers = List(contributes_to=MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        d = []

        if self.klass is not None:
            d = [dict(name=self.name,
                     manager=app.get_service(ILaserManager, 'name=="{}"'.format(self.name)
                                             ))]
        # print '_managers default', d, self.name
        return d
#============= EOF ====================================
