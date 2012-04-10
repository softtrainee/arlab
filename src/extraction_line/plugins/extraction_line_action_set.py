'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
BASENAME = 'src.extraction_line.plugins.extraction_line_actions:{}'
MPATH = 'MenuBar/Extraction Line'
class ExtractionLineActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.extraction_line.action_set'
    actions = [

               Action(name='Extraction Line Manager',
                      path=MPATH,
                      class_name=BASENAME.format('OpenExtractionLineManager')
                      ),

               Action(name='Load Canvas',
                      path=MPATH,
                      class_name=BASENAME.format('LoadCanvasAction')
                      ),
               Action(name='Refresh Canvas',
                      path=MPATH,
                      class_name=BASENAME.format('RefreshCanvasAction')
                      ),
               Action(name='Canvas Views',
                      path=MPATH,
                      class_name=BASENAME.format('OpenViewControllerAction')
                      ),
                Action(name='Open PyScript Editor',
                       path=MPATH,
                       class_name=BASENAME.format('OpenPyScriptEditorAction'),
#               Action(name='Device Streamer',
#                      path='MenuBar/Extraction Line',
#                      class_name='src.extraction_line.plugins.extraction_line_actions:OpenDeviceStreamerAction'),
                       )

              ]
#============= EOF ====================================
