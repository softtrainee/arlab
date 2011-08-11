#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class PychronWorkbenchActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.workbench.action_set'
    actions = [

               Action(name = 'Save',
                      path = 'MenuBar/File',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.SaveAction'),
               Action(name = 'Save As',
                      path = 'MenuBar/File',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.SaveAsAction'),
               Action(name = 'Logger',
                      path = 'MenuBar/Help',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.LoggerAction'),
               Action(name = 'Help Page',
                      path = 'MenuBar/Help',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.GotoHelpPageAction'),
               Action(name = 'API',
                      path = 'MenuBar/Help',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.GotoAPIPageAction'),
               Action(name = 'Check For Updates',
                      path = 'MenuBar/Help',
                      class_name = 'src.envisage.plugins.pychron_workbench_actions.OpenUpdateManagerAction'),
#               Action(name = 'Refresh Source',
#                      path = 'MenuBar/Tools',
#                      class_name = 'src.envisage.plugins.workbench.workbench_actions.RefreshSourceAction'),



               ]
#============= EOF ====================================
