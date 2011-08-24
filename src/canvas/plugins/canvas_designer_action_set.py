#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class CanvasDesignerActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.canvas.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [Action(name = 'New Canvas',
                      path = 'MenuBar/File',
                    class_name = 'src.canvas.plugins.canvas_designer_actions:NewCanvasAction'

                    ),
                Action(name = 'Open Canvas',
                       path = 'MenuBar/File',
                       class_name = 'src.canvas.plugins.canvas_designer_actions:OpenCanvasAction'

                       ),

             ]
#============= EOF ====================================
