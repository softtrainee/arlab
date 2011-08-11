#============= enthought library imports =======================
#from envisage.ui.action.api import Action#, Group, Menu, ToolBar
#from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.laser_action_set import LaserActionSet

class SynradCO2ActionSet(LaserActionSet):
    '''
    '''
    id = 'pychron.synrad_co2.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
#    actions = [
##               Action(name = 'Stage Manager',
##                      path = 'MenuBar/Lasers',
##                      class_name = 'src.lasers.plugins.fusions_laser_actions:OpenStageManagerAction'),
##                

#============= EOF ====================================
