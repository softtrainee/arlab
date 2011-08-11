#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class LaserActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.laser.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [
#               Action(name = 'Stage Manager',
#                      path = 'MenuBar/Lasers',
#                      class_name = 'src.lasers.plugins.fusions_laser_actions:OpenStageManagerAction'),
#                
                Action(name = 'Laser Manager',
                       path = 'MenuBar/Lasers',
                       class_name = 'src.lasers.plugins.laser_actions:OpenLaserManagerAction'
                       ),

                Action(name = 'Configure Motion Controller',
                       path = 'MenuBar/Lasers',
                       class_name = 'src.lasers.plugins.laser_actions:OpenMotionControllerManagerAction'
                       ),


                Action(name = 'Pattern Manager',
                       path = 'MenuBar/Lasers/Pattern',
                       class_name = 'src.lasers.plugins.laser_actions:OpenPatternManagerAction'),
                Action(name = 'Execute Pattern',
                       path = 'MenuBar/Lasers/Pattern',
                       class_name = 'src.lasers.plugins.laser_actions:ExecutePatternAction'
                       ),

                Action(name = 'Power Map',
                       path = 'MenuBar/Lasers/Scans',
                       class_name = 'src.lasers.plugins.laser_actions:PowerMapAction'
                       ),
                Action(name = 'Pulse',
                       path = 'MenuBar/Lasers/Scans',
                       class_name = 'src.lasers.plugins.laser_actions:PulseAction'
                       ),
                Action(name = 'Step Heat',
                       path = 'MenuBar/Lasers/Scans',
                       class_name = 'src.lasers.plugins.laser_actions:StepHeatAction'
                       ),
                Action(name = 'Power Scan',
                       path = 'MenuBar/Lasers/Scans',
                       class_name = 'src.lasers.plugins.laser_actions:PowerScanAction'
                       ),
                Action(name = 'Loading Position',
                       path = 'MenuBar/Lasers',
                       class_name = 'src.lasers.plugins.laser_actions:MoveLoadPositionAction'
                       ),
                Action(name = 'Open Power Scan',
                       path = 'MenuBar/Lasers/Results',
                       class_name = 'src.lasers.plugins.laser_actions:OpenPowerScanGraphAction'
                       ),
                Action(name = 'Open Power Map',
                       path = 'MenuBar/Lasers/Results',
                       class_name = 'src.lasers.plugins.laser_actions:OpenPowerMapAction'
                       ),



             ]
#============= EOF ====================================
