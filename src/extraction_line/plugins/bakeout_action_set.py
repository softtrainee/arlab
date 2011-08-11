#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class BakeoutActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.bakeout.action_set'

    actions = [
               Action(name = 'Bakeout',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.extraction_line.plugins.bakeout_actions:OpenBakeoutManagerAction'
                      )
             ]
#============= EOF ====================================
