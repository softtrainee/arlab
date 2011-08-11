#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.laser_plugin import LaserPlugin

class SynradCO2Plugin(LaserPlugin):
    '''
    '''
    id = 'pychron.synrad.co2'
    MANAGERS = 'pychron.hardware.managers'

    name = 'synrad_co2_manager'
    klass = ('src.managers.laser_managers.synrad_co2_manager', 'SynradCO2Manager')

