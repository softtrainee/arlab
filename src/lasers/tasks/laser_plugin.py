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
from traits.api import List
from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
from envisage.ui.tasks.task_factory import TaskFactory
from src.lasers.tasks.laser_task import FusionsDiodeTask
from src.lasers.laser_managers.ilaser_manager import ILaserManager
from src.helpers.parsers.initialization_parser import InitializationParser
import os
from src.paths import paths
from src.lasers.tasks.laser_preferences import FusionsDiodePreferencesPane
from pyface.tasks.action.schema_addition import SchemaAddition
from envisage.ui.tasks.task_extension import TaskExtension
from src.lasers.tasks.laser_actions import OpenScannerAction
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseLaserPlugin(BaseTaskPlugin):
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
                          factory=self._manager_factory)
        return [so]

    def _manager_factory(self):
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
#        app = self.application
        d = []

        if self.klass is not None:
            d = [dict(name=self.name,
                     manager=self._get_manager())]

        return d

    def _get_manager(self):
        return self.application.get_service(ILaserManager, 'name=="{}"'.format(self.name))

class FusionsPlugin(BaseLaserPlugin):
    pass

class FusionsDiodePlugin(FusionsPlugin):
    id = 'pychron.fusions.diode'
    name = 'fusions_diode'
    klass = ('src.lasers.laser_managers.fusions_diode_manager', 'FusionsDiodeManager')

    def _my_task_extensions_default(self):
        def factory():
            return OpenScannerAction(self._get_manager())

        return [TaskExtension(actions=[SchemaAddition(id='open_scan',
                                                        factory=factory,
#                                                      factory=OpenScannerAction,
#                                                      factory=OpenFlagManagerAction,
                                                        path='MenuBar/Extraction'), ])]

    def _preferences_default(self):
        root = paths.preferences_dir
        path = os.path.join(root, 'preferences.ini')
        if not os.path.isfile(path):
            with open(path, 'w') as fp:
                pass
        return ['file://{}'.format(path)]

    def _preferences_panes_default(self):
        return [FusionsDiodePreferencesPane]

    def _tasks_default(self):
        return [TaskFactory(id='tasks.fusions.diode',
                            factory=self._task_factory,
                            name='Fusions Diode'
                            )
                ]

    def _task_factory(self):
#        print self._get_manager()
        t = FusionsDiodeTask(manager=self._get_manager())
        return t

#============= EOF =============================================
