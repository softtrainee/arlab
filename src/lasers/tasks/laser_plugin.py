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
from traits.api import List, Str
from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
from envisage.ui.tasks.task_factory import TaskFactory
from src.lasers.tasks.laser_task import FusionsDiodeTask, FusionsCO2Task
from src.lasers.laser_managers.ilaser_manager import ILaserManager
from src.helpers.parsers.initialization_parser import InitializationParser
import os
from src.paths import paths
from src.lasers.tasks.laser_preferences import FusionsDiodePreferencesPane, \
    FusionsCO2PreferencesPane
from pyface.tasks.action.schema_addition import SchemaAddition
from envisage.ui.tasks.task_extension import TaskExtension
from src.lasers.tasks.laser_actions import OpenScannerAction, \
    OpenAutoTunerAction, NewPatternAction, \
    OpenPatternAction, PowerMapAction, PowerCalibrationAction
from pyface.tasks.action.schema import SMenu, GroupSchema
from pyface.action.group import Group
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
                          protocol=ILaserManager,
                          factory=self._manager_factory)
        return [so]

    def _manager_factory(self):
        '''
        '''

        ip = InitializationParser()
        plugin = ip.get_plugin(self.klass[1].replace('Manager', ''), category='hardware')
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
                        print 'client comms fail', attr, e
            except Exception, e:
                print 'client comms fail', e

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
        d = []

        if self.klass is not None:
            d = [dict(name=self.name,
                     manager=self._get_manager())]

        return d

    def _get_manager(self):
        return self.application.get_service(ILaserManager, 'name=="{}"'.format(self.name))

    def _preferences_default(self):
        root = paths.preferences_dir
        path = os.path.join(root, 'preferences.ini')
        if not os.path.isfile(path):
            with open(path, 'w'):
                pass
        return ['file://{}'.format(path)]

class FusionsPlugin(BaseLaserPlugin):
    task_name = Str
    def _tasks_default(self):
        return [TaskFactory(id=self.id,
                            task_group='hardware',
                            factory=self._task_factory,
                            name=self.task_name
                            )
                ]

    sources = List(contributes_to='pychron.video.sources')
    def _sources_default(self):
        ip = InitializationParser()
        plugin = ip.get_plugin(self.task_name.replace(' ', ''),
                               category='hardware')
        source = ip.get_parameter(plugin, 'video_source')
        rs = []
        if source:
            rs = [(source, self.task_name)]
        return rs

    def _my_task_extensions_default(self):
        def efactory():
            return SMenu(id='Extraction', name='Extraction')
        return [TaskExtension(actions=[
                   SchemaAddition(id='Extraction',
                                  factory=efactory,
                                  path='MenuBar',
                                  before='Tools',
                                  after='View'
                                  ),
                   SchemaAddition(id='fusions_laser_group',
                                 factory=lambda: GroupSchema(id='FusionsLaserGroup'
                                                       ),
                                 path='MenuBar/Extraction'
                                 ),
                   SchemaAddition(id='pattern',
                                  factory=lambda:Group(
                                                       OpenPatternAction(),
                                                       NewPatternAction(),
                                                       ),
                                  path='MenuBar/Extraction'
                                  ),
                   SchemaAddition(id='power_map',
                                  factory=lambda: Group(
                                                        PowerMapAction(),
                                                        ),
                                  path='MenuBar/Extraction'
                                  ),
#                    SchemaAddition(id='power_calibration',
#                                   factory=lambda: Group(
#                                                         PowerCalibrationAction(),
#                                                         ),
#                                   path='MenuBar/Extraction'
#                                   )

                              ]
                            )
                       ]
class FusionsCO2Plugin(FusionsPlugin):
    id = 'pychron.fusions.co2'
    name = 'fusions_co2'
    klass = ('src.lasers.laser_managers.fusions_co2_manager', 'FusionsCO2Manager')
    task_name = 'Fusions CO2'

    def _task_factory(self):
        t = FusionsCO2Task(manager=self._get_manager())
        return t

    def _preferences_panes_default(self):
        return [FusionsCO2PreferencesPane]

    def _my_task_extensions_default(self):
        exts = super(FusionsCO2Plugin, self)._my_task_extensions_default()
        def factory_scan():
            return OpenScannerAction(self._get_manager())

#         def factory_tune():
#             return OpenAutoTunerAction(self._get_manager())

        return exts + [TaskExtension(actions=[
                                              SchemaAddition(id='fusions_co2_group',
                                                     factory=lambda: GroupSchema(id='FusionsCO2Group'
                                                                           ),
                                                     path='MenuBar/Extraction'
                                                     ),

                                              ]
                              )
                       ]

class FusionsDiodePlugin(FusionsPlugin):
    id = 'pychron.fusions.diode'
    name = 'fusions_diode'
    klass = ('src.lasers.laser_managers.fusions_diode_manager', 'FusionsDiodeManager')
    task_name = 'Fusions Diode'
    def _my_task_extensions_default(self):
        def factory_scan():
            return OpenScannerAction(self._get_manager())
        def factory_tune():
            return OpenAutoTunerAction(self._get_manager())

        exts = super(FusionsDiodePlugin, self)._my_task_extensions_default()
        return exts + [TaskExtension(actions=[
                        SchemaAddition(id='fusions_diode_group',
                         factory=lambda: GroupSchema(id='FusionsDiodeGroup'
                                               ),
                         path='MenuBar/Extraction'
                         ),
                           SchemaAddition(id='fusions_diode_group',
                                          factory=lambda: Group(),
                                          path='MenuBar/Extraction'
                                          ),
                           SchemaAddition(id='open_scan',
                                          factory=factory_scan,
                                        path='MenuBar/Extraction/FusionsDiodeGroup'),
                           SchemaAddition(id='open_autotune',
                                          factory=factory_tune,
                                        path='MenuBar/Extraction/FusionsDiodeGroup'),
                                       ]
                              )
                       ]

    def _preferences_panes_default(self):
        return [FusionsDiodePreferencesPane]


    def _task_factory(self):
#        print self._get_manager()
        t = FusionsDiodeTask(manager=self._get_manager())
        return t

#============= EOF =============================================
