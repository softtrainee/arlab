#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
#from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.laser_action_set import LaserActionSet

class FusionsLaserActionSet(LaserActionSet):
    '''
    '''
    id = 'pychron.fusions_laser.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]

    def __init__(self, *args, **kw):
        super(FusionsLaserActionSet, self).__init__(*args, **kw)
        self.actions += [
                Action(name = 'Calibrate Camera',
                       path = 'MenuBar/Lasers',
                       class_name = 'src.lasers.plugins.fusions_laser_actions:OpenCalibrationManagerAction'
                       ),

                    ]
#============= EOF ====================================
