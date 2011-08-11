#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from laser_handler import LaserHandler

class SynradHandler(LaserHandler):
    manager_name = 'Synrad'
    def SetLaserPower(self, manager, data):
        result = 'OK'
        try:
            data = float(data)
            manager.set_laser_power(data)
        except TypeError:
            result = 'Invalid power value {}'.format(data)

        return result

#============= views ===================================
#============= EOF ====================================
