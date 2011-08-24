#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class SVNActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.svn.action_set'
    actions = [
               Action(name = 'Update Software',
                      path = 'MenuBar/Help',
                      class_name = 'src.svn.plugins.svn_actions:UpdateToHeadAction'),


              ]
#============= EOF ====================================
