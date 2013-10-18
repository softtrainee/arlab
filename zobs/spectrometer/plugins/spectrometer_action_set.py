# @PydevCodeAnalysisIgnore
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
from envisage.ui.action.api import Action  # , Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================
#============= local library imports  ==========================
PATH = 'MenuBar/Spectrometer'
BASE = 'src.spectrometer.plugins.spectrometer_actions'


class SpectrometerActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.spectrometer.action_set'

    actions = [
                Action(name='Peak Center',
                       path=PATH + '/IonOptics',
                       class_name='{}:PeakCenterAction'.format(BASE)
                       ),
                Action(name='Coincidence',
                       path=PATH + '/IonOptics',
                       class_name='{}:CoincidenceScanAction'.format(BASE)
                       ),
                Action(name='CDD Op. Voltage',
                       path=PATH + '/Utitilies',
                       class_name='{}:CDDOperateVoltageAction'.format(BASE)
                       ),
                Action(name='Scan',
                       path=PATH,
                       class_name='{}:OpenScanManagerAction'.format(BASE)
                       ),
                Action(name='Relative Positions',
                       path=PATH + '/Utitilies',
                       class_name='{}:RelativePositionsAction'.format(BASE)
                       )
                       ]
