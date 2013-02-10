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
from traits.api import HasTraits, Any, Event, Property, Bool
import yaml
import time
from threading import Thread
from src.loggable import Loggable
import os
from src.paths import paths

class LaserScriptExecutor(Loggable):
    laser_manager = Any
    _executing = Bool(False)
    _cancel = False
    execute_button = Event
    execute_label = Property(depends_on='_executing')

    def _get_execute_label(self):
        return 'Stop' if self._executing else 'Execute'

    def _execute_button_fired(self):
        name = os.path.join(paths.scripts_dir, 'uv_laser.yaml')
        self.execute(name)

    def execute(self, name):
        if self._executing:
            self._cancel = True
            self._executing = False
        else:
            self._cancel = False
            self._executing = True
            t = Thread(target=self._execute, args=(name,))
            t.start()
#        self._execute(name)

    def _execute(self, name):
        self.info('starting LaserScript {}'.format(name))

        lm = self.laser_manager
        sm = lm.stage_manager
        atl = lm.atl_controller

        with open(name, 'r') as fp:
            d = yaml.load(fp.read())

            motor = d['motor']
            if motor == 'z':
                def motor_iteration(p):
                    sm.set_z(p, block=True)

            else:
                motor = lm.get_motor(motor)
                def motor_iteration(p):
                    motor.trait_set(data_position=p)
                    motor.block(4)

            sx, sy = d['start']
            xstep = d['xstep']
            ystep = d['ystep']
#            ny=d['y_nsteps']
#            nx=d['x_nsteps']
            ncols = d['ncols']
            ms = d['motor_start']
            me = d['motor_stop']
            mstep = d['motor_step']

            n = (abs(ms - me) + 1) / mstep

            nx = ncols
            ny = int(n / int(ncols))

#            nb = d['nburst']
            v = d['velocity']
#            atl.set_nburst(nb)
#            sm.linear_move(sx,sy,block=True)
            for r in range(ny):
                if self._cancel:
                    break

                for c in range(nx):
                    if self._cancel:
                        break

                    dp = ms + (r * nx + c) * mstep
                    x, y = sx + c * xstep, sy + r * ystep

                    sm.linear_move(x, y, velocity=v, block=True)
                    if self._cancel:
                        break

                    motor_iteration(dp)
                    if self._cancel:
                        break

                    lm.single_burst()

            else:
                self.info('LaserScript truncated at row={}, col={}'.format(r, c))

            self._executing = False
            self.info('LaserScript finished'.format(name))

if __name__ == '__main__':
    lm = LaserScriptExecutor()
    name = '/Users/uv/Pychrondata_uv/scripts/uv_laser.yaml'
    lm.execute(name)
