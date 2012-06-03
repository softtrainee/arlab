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
class HardwareActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.hardware.action_set'

    p = 'src.hardware.plugins.hardware_actions'
    actions = [
               Action(name='Hardware Manager',
                      path='MenuBar/File',
                      class_name='{}:OpenHardwareManagerAction'.format(p)),
               Action(name='Register Device...',
                      path='MenuBar/File',
                      class_name='{}:RegisterDeviceAction'.format(p)),
               Action(name='Remote Hardware Server',
                      path='MenuBar/File',
                      class_name='{}:OpenRemoteHardwareServerAction'.format(p)),
               Action(name='Device Scans...',
                      path='MenuBar/Results',
                      class_name='{}:OpenDeviceScansAction'.format(p)),

              ]
#============= EOF ====================================
