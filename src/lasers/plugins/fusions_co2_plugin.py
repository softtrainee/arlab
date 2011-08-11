#============= enthought library imports =======================
#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions_laser_plugin import FusionsLaserPlugin

class FusionsCO2Plugin(FusionsLaserPlugin):
    '''
    '''
    id = 'pychron.fusions.co2'

    name = 'fusions_co2_manager'
    klass = ('src.managers.laser_managers.fusions_co2_manager', 'FusionsCO2Manager')
#============= EOF ====================================
