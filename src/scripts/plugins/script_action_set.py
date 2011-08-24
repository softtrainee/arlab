#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class ScriptActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.script.action_set'
    actions = [
               Action(name = 'New',
                      path = 'MenuBar/File/Script',
                      class_name = 'src.scripts.plugins.script_actions:NewScriptAction'),

               Action(name = 'Run',
                      path = 'MenuBar/File/Script',
                      class_name = 'src.scripts.plugins.script_actions:RunScriptAction'),

               Action(name = 'Power Map',
                      path = 'MenuBar/File/Script/Open',
                      class_name = 'src.scripts.plugins.script_actions:PowerMapAction'),

              ]
#============= EOF ====================================
