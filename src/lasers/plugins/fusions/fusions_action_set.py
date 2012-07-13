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
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
#from src.lasers.plugins.laser_action_set import LaserActionSet

class FusionsActionSet(WorkbenchActionSet):
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
        results_path = 'MenuBar/Results/{}'.format(self.name)

        return [
                Action(name='Laser Manager',
                       path=laser_path,
                       class_name='{}OpenLaserManagerAction'.format(self.action_path)
                       ),
                Action(name='Configure Motion Controller',
                       path=laser_path,
                       class_name='{}OpenMotionControllerManagerAction'.format(self.action_path)
                       ),
                Action(name='Power Calibration',
                       path=laser_path,
                       class_name='{}PowerCalibrationAction'.format(self.action_path)
                       ),
                Action(name='Power Map',
                       path=laser_path,
                       class_name='{}PowerMapAction'.format(self.action_path)
                       ),
                Action(name='Open',
                       path='{}/Visualizer'.format(laser_path),
                       class_name='{}OpenStageVisualizerAction'.format(self.action_path)
                       ),
                Action(name='Load...',
                       path='{}/Visualizer'.format(laser_path),
                       class_name='{}LoadStageVisualizerAction'.format(self.action_path)
                       ),

                #===============================================================
                # 
                #===============================================================
                Action(name='Beam',
                       path='{}/Initialize'.format(laser_path),
                       class_name='{}InitializeBeamAction'.format(self.action_path)
                       ),
                Action(name='Zoom',
                       path='{}/Initialize'.format(laser_path),
                       class_name='{}InitializeZoomAction'.format(self.action_path)
                       ),

                #===============================================================
                # results
                #===============================================================
                Action(name='Power Recording',
                       path=results_path,
                       class_name='{}OpenPowerRecordGraphAction'.format(self.action_path)
                       ),
                Action(name='Power Map',
                       path=results_path,
                       class_name='{}OpenPowerMapAction'.format(self.action_path)
                       ),
                Action(name='Video',
                       path=results_path,
                       class_name='{}OpenVideoAction'.format(self.action_path)
                       ),
                Action(name='Power Calibration',
                       path=results_path,
                       class_name='{}OpenPowerCalibrationAction'.format(self.action_path)
                       )
                ]

#============= EOF ====================================
