'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
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

