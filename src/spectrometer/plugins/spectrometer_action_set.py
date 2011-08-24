#============= enthought library imports =======================
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class SpectrometerActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.spectrometer.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [
#               Action(name = 'Stage Manager',
#                      path = 'MenuBar/Lasers',
#                      class_name = 'src.lasers.plugins.fusions_laser_actions:OpenStageManagerAction'),
#                
                Action(name = 'Peak Center',
                       path = 'MenuBar/Spec',
                       class_name = 'src.spectrometer.plugins.spectrometer_actions:PeakCenterAction'
                       ),
                Action(name = 'Mag Field Calibration',
                       path = 'MenuBar/Spec',
                       class_name = 'src.spectrometer.plugins.spectrometer_actions:MagFieldCalibrationAction'
                       ),
                       ]