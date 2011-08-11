#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class HardwareActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.hardware.action_set'
    actions = [
               Action(name = 'Hardware Manager',
                      path = 'MenuBar/Extraction Line',
                      class_name = 'src.hardware.plugins.hardware_actions:OpenHardwareManagerAction'),

              ]
#============= EOF ====================================
