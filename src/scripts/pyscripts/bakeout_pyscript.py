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
from traits.api import Any
#============= standard library imports ========================
from numpy import linspace
#============= local library imports  ==========================
from src.scripts.pyscripts.pyscript import PyScript
import time
from src.helpers.paths import doc_html_dir
import os
HTML_HELP = '''
<tr>
    <td>setpoint</td>
    <td>temp,duration[,units]</td>
    <td>set controller to setpoint for n hours</td>
    <td>setpoint(100,4)</td>
</tr>
<tr>
    <td>ramp</td>
    <td>setpoint,rate[,start,period]</td>
    <td>ramp to setpoint at rate C/hr</td>
    <td>ramp(100,60,start=50)</td>
</tr>

'''


TIMEDICT = dict(s=1, m=60.0, h=60.0 * 60.0)


class BakeoutPyScript(PyScript):
    controller = Any

    def _get_help_hook(self):
#        return HTML_HELP_PATH
        return HTML_HELP

    def get_help_path(self):
        p = os.path.join(doc_html_dir, 'bakeout_scripting.html')
        return p

    def _get_commands(self):
        cmds = super(BakeoutPyScript, self)._get_commands()
        cmds += ['setpoint', 'ramp']
        return cmds

    def ramp(self, setpoint, rate, start=None, period=60):
        setpoint = float(setpoint)
        rate = float(rate)
        period = float(period)
        if self._syntax_checking or self._cancel:
            return

        c = self.controller
        if start is None:
            start = 25
            if c is not None:
                #possible to just read the process_value 
                #for now force a query to the device
                #TODO: is this necessary
                ctemp = int(c.get_temperature())
                start = max(start, ctemp)

        self.info('ramping from {} to {} rate= {} C/h, period= {} s'.format(start,
                                                                    setpoint,
                                                                    rate,
                                                                    period
                                                                    ))

        dT = setpoint - start
        dur = abs(dT / rate)
        if c is not None:
            c.duration = dur

        #convert period to hours
#        hperiod = period / 3600.
#        steps = linspace(start, setpoint, dur * 3600 / float(period))

        check_period = 0.5
        samples_per_hr = 3600 / float(period)
        steps = linspace(start, setpoint, dur * samples_per_hr)
        for si in steps:
            if self._cancel:
                break
            self._set_setpoint(si)
            if period > 5:
                for _ in xrange(int(period / check_period)):
                    if self._cancel:
                        break
                    time.sleep(check_period)
                else:
                    continue
                break
            else:
                time.sleep(period)

    def setpoint(self, temp, duration, units='h'):
        ts = TIMEDICT[units]
        if self._syntax_checking or self._cancel:
            return

        #convert duration from units to seconds

        duration *= ts
        self.info('setting setpoint to {} for {}'.format(temp, duration))
        c = self.controller
        if c is not None:
            self._set_setpoint(temp)
            #convert back to hours
            self.controller.duration = duration / 3600.

        self._block(duration)

    def _set_setpoint(self, sp):
        self.info('setting setpoint to {}'.format(sp))
        c = self.controller
        if c is None:
            return

        if c.setpoint == sp:
            c.set_closed_loop_setpoint(sp)
        else:
            c.setpoint = sp
#============= EOF ====================================
