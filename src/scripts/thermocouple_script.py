#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



#============= enthought library imports =======================

#============= standard library imports ========================

import time
#============= local library imports  ==========================

from src.scripts.file_script import FileScript
from src.scripts.core.script_helper import equilibrate

class ThermocoupleScript(FileScript):
    def load_file(self):
        '''
        '''

        self.equilibrate_setpoint = self._file_contents_[0].strip() in ['True', 'true', 'TRUE', '1']

        args = self._file_contents_[1].split(',')
        self.outside_eq_n = float(args[0])

        self.outside_eq_std_tol = float(args[1])
        self.outside_eq_mean_tol = float(args[2])

        args = self._file_contents_[2].split(',')

        self.inside_eq_n = float(args[0])
        self.inside_eq_std_tol = float(args[1])
        self.inside_eq_mean_tol = float(args[2])

        self._file_contents_ = self._file_contents_[3:]
    def _run_(self):
        '''
        '''
        for r in self._file_contents_:
            if self.isAlive():
                args = r.strip().split(',')
                time_at_T = 600
                time_btw_steps = 360
                if len(args) == 2:
                    time_at_T = float(args[1])
                if len(args) == 3:
                    time_at_T = float(args[1])
                    time_btw_steps = int(args[2])
                self._execute_step(int(args[0]), time_at_T, time_btw_steps)
            else:
                break

    def kill_script(self):
        '''
        '''
#        super(ThermocoupleScript, self).kill_script()
        FileScript.kill_script(self)
        self.manager.d_Eurotherm.set_process_setpoint(0)

    def _execute_step(self, setpoint, time_at_T, time_btw_steps):
        '''
            @type setpoint: C{str}
            @param setpoint:

            @type time_at_T: C{str}
            @param time_at_T:

            @type time_btw_steps: C{str}
            @param time_btw_steps:
        '''
        di = self.manager.d_DPi32TemperatureMonitor
        eu = self.manager.d_Eurotherm
        eu.set_process_setpoint(setpoint)
        self.log('Set furnace to %0.2f' % setpoint)

        if self.equilibrate_setpoint:
            eqt = equilibrate(self, eu.get_process_value, setpoint,
                            n=self.outside_eq_n,
                            mean_tolerance=self.outside_eq_mean_tol,
                            std_tolerance=self.outside_eq_std_tol)
            self.log('outside eqtime = %0.2f' % eqt)

        self.log('time at temperature %s' % time_at_T)
        time.sleep(time_at_T)


        if self.equilibrate_setpoint:
            eqt = equilibrate(self, di.get_process_value, setpoint, std_check=True,
                            n=self.inside_eq_n,
                            std_tolerance=self.inside_eq_std_tol
                            )
            self.log('inside eqtime = %0.2f' % eqt)
        else:
            eu.set_process_setpoint(0)
            self.log('Set Furnace to 0')

        self.log('time btw steps %s' % time_btw_steps)
        time.sleep(time_btw_steps)

    def log(self, a):
        '''
            @type a: C{str}
            @param a:
        '''
        if self.logger is not None:
            self.info(a)
            self.add_output(a)

#============= EOF ====================================
