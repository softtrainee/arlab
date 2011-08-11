#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class ExtractionLineActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.extraction_line.action_set'
    actions = [

               Action(name = 'Extraction Line Manager',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.extraction_line_actions:OpenExtractionLineManager'
                      ),

               Action(name = 'Load Canvas',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.extraction_line_actions:LoadCanvasAction'),
               Action(name = 'Refresh Canvas',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.extraction_line_actions:RefreshCanvasAction'),
               Action(name = 'Canvas Views',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.extraction_line_actions:OpenViewControllerAction'),
               Action(name = 'Device Streamer',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.extraction_line_actions:OpenDeviceStreamerAction'),


              ]
#============= EOF ====================================
