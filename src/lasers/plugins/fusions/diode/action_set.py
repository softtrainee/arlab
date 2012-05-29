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
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
#from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions.fusions_action_set import FusionsActionSet

class FusionsDiodeActionSet(FusionsActionSet):
    '''
    '''
    id = 'pychron.fusions.diode.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    name = 'Diode'
    action_path = 'src.lasers.plugins.fusions.diode.actions:'
    def _actions_default(self):
        laser_path = 'MenuBar/Lasers/{}'.format(self.name)
#        results_path = 'MenuBar/Results/{}'.format(self.name)

        actions = [

                Action(name='Degas',
                       path=laser_path,
                       class_name='{}DegasAction'.format(self.action_path)
#                       class_name='src.lasers.plugins.laser_actions:OpenLaserManagerAction'
                       ),
                Action(name='Configure Watlow',
                       path='MenuBar/Lasers/{}'.format(self.name),
                       class_name='{}ConfigureWatlowAction'.format(self.action_path)
                       ),

                ]

        return super(FusionsDiodeActionSet, self)._actions_default() + actions
##                Action(name='Configure Motion Controller',
##                       path='MenuBar/Lasers/{}'.format(self.name),
##                       class_name='src.lasers.plugins.laser_actions:OpenMotionControllerManagerAction'
##                       ),
#
#
#                Action(name='Pattern Manager',
#                       path='MenuBar/Lasers/{}/Pattern'.format(self.name),
#                       class_name='src.lasers.plugins.laser_actions:OpenPatternManagerAction'),
#                Action(name='Execute Pattern',
#                       path='MenuBar/Lasers/{}/Pattern'.format(self.name),
#                       class_name='src.lasers.plugins.laser_actions:ExecutePatternAction'
#                       ),
#
#                Action(name='Power Map',
#                       path='MenuBar/Lasers/{}/Scans'.format(self.name),
#                       class_name='src.lasers.plugins.laser_actions:PowerMapAction'
#                       ),
##                Action(name='Pulse',
##                       path='MenuBar/Lasers/Scans',
##                       class_name='src.lasers.plugins.laser_actions:PulseAction'
##                       ),
##                Action(name='Step Heat',
##                       path='MenuBar/Lasers/Scans',
##                       class_name='src.lasers.plugins.laser_actions:StepHeatAction'
##                       ),
#                Action(name='Power Scan',
#                       path='MenuBar/Lasers/Scans',
#                       class_name='src.lasers.plugins.laser_actions:PowerScanAction'
#                       ),
##                Action(name='Loading Position',
##                       path='MenuBar/Lasers/{}'.format(self.name),
##                       class_name='src.lasers.plugins.laser_actions:MoveLoadPositionAction'
##                       ),
#                Action(name='Open Power Scan',
#                       path='MenuBar/Lasers/{}/Results'.format(self.name),
#                       class_name='src.lasers.plugins.laser_actions:OpenPowerScanGraphAction'
#                       ),
#                Action(name='Open Power Map',
#                       path='MenuBar/Lasers/{}/Results'.format(self.name),
#                       class_name='src.lasers.plugins.laser_actions:OpenPowerMapAction'
#                       ),
#
#                  Action(name='Calibrate Camera',
#                       path='MenuBar/Lasers/{}'.format(self.name),
#                       class_name='{}.actions:OpenCalibrationManagerAction'.format(self.action_path)
#                       ),

#             ]
#============= EOF ====================================
