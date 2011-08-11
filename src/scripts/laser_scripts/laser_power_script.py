#@PydevCodeAnalysisIgnore

#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
#from src.scripts.file_script import FileScript
from laser_script import LaserScript
class LaserPowerScript(LaserScript):
    '''
        G{classtree}
    '''
    power_meter_range = 1
#    def load_file(self):
#        '''
#        '''
#        pass

#        self.power_meter_range = r = float(self._file_contents_[0][0])
#        self.manager.analog_power_meter.range = r

#        self._file_contents_ = self._file_contents_[1:]

