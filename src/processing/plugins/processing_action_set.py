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

BASE = 'src.processing.plugins.processing_actions'
PATH = 'MenuBar/Process'
SETSPATH = 'MenuBar/Experiment/Sets...'

class ProcessingActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.processing.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [
               Action(name='Series...',
                      path=PATH,
                      class_name='{}:NewSeriesAction'.format(BASE)
                    ),
               Action(name='Ideogram...',
                      path=PATH,
                      class_name='{}:NewIdeogramAction'.format(BASE)
                    ),
               Action(name='Spectrum...',
                      path=PATH,
                      class_name='{}:NewSpectrumAction'.format(BASE)
                    ),
               Action(name='Inverse Isochron...',
                      path=PATH,
                      class_name='{}:NewInverseIsochronAction'.format(BASE)
                    ),

               Action(name='Blanks...',
                      path=PATH + '/Apply Corrections',
                      class_name='{}:ApplyBlankAction'.format(BASE)
                    ),
               Action(name='Backgrounds...',
                      path=PATH + '/Apply Corrections',
                      class_name='{}:ApplyBackgroundAction'.format(BASE)
                    ),
               Action(name='Detector Intercalibration...',
                      path=PATH + '/Apply Corrections',
                      class_name='{}:ApplyDetectorIntercalibrationAction'.format(BASE)
                    ),

               Action(name='Find...',
                      path=PATH,
                      class_name='{}:OpenSelectorAction'.format(BASE)
                    ),

               Action(name='Figures...',
                      path=PATH,
                      class_name='{}:OpenFiguresAction'.format(BASE)
                    ),
               Action(name='Save Figure...',
                      path=PATH,
                      class_name='{}:SaveFigureAction'.format(BASE)
                    ),
               Action(name='Export PDF...',
                      path=PATH + '/Export Figure Table',
                      class_name='{}:ExportPDFFigureTableAction'.format(BASE)
                    ),
               Action(name='Export CSV...',
                      path=PATH + '/Export Figure Table',
                      class_name='{}:ExportCSVFigureTableAction'.format(BASE)
                    ),
               Action(name='Export Figure...',
                      path=PATH,
                      class_name='{}:ExportPDFFigureAction'.format(BASE)
                    ),
               Action(name='Calculate Flux',
                      path=PATH,
                      class_name='{}:CalculateFluxAction'.format(BASE)
                      ),
               Action(name='View Analysis Table',
                      path=PATH,
                      class_name='{}:ViewAnalysisTableAction'.format(BASE)
                      ),

               Action(name='Open Projects',
                      path=PATH,
                      class_name='{}:ProjectViewAction'.format(BASE)
                      )





#               Action(name='New Workspace...',
#                      path=PATH,
#                      class_name='{}:NewWorkspaceAction'.format(BASE)
#                    ),
#               Action(name='Open Workspace...',
#                      path=PATH,
#                      class_name='{}:OpenWorkspaceAction'.format(BASE)
#                    ),
#               Action(name='New Figure',
#                      path=PATH,
#                      class_name='{}:NewFigureAction'.format(BASE)
#                    ),
             ]
#============= EOF ====================================
