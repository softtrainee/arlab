#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions_laser_plugin import FusionsLaserPlugin

class FusionsDiodePlugin(FusionsLaserPlugin):
    '''
    '''
    id = 'pychron.fusions.diode'
    name = 'fusions_diode_manager'
    klass = ('src.managers.laser_managers.fusions_diode_manager', 'FusionsDiodeManager')
#============= EOF ====================================
