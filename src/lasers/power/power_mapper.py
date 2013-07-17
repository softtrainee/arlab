#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Any, Int, Instance, Event
from traitsui.api import View, Item
from src.loggable import Loggable
import time
#============= standard library imports ========================
#============= local library imports  ==========================
from numpy import exp, mgrid
from src.helpers.datetime_tools import generate_datestamp
from src.managers.data_managers.h5_data_manager import H5DataManager

def power_generator(nsteps):
    '''
    '''
    def gaussian(height, center_x, center_y, width_x, width_y):
        '''
        Returns a gaussian function with the given parameters
        '''

        width_x = float(width_x)
        width_y = float(width_y)
        return lambda x, y: height * exp(
 -(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

    x, y = mgrid[0:nsteps, 0:nsteps]
    data = gaussian(2, 5, 5, 5, 5)(x, y)  # +np.random.random(x.shape)
    i = 0
    j = 0
    while 1:
        yield data[i][j]
        j += 1
        if j == nsteps:
            i += 1
            j = 0


class PowerMapper(Loggable):
    laser_manager = Any
    canvas = Any
    nintegrations = Int(5)
    data_manager = Instance(H5DataManager, ())

    _alive = False
    completed = Event

    def stop(self):
        self._alive = False

    def do_power_mapping(self, bd, rp, cx, cy, padding, step_len):
        self.info('executing discrete scan')
        self.info('beam diameter={} request_power={}'.format(bd, rp))

        lm = self.laser_manager
        if lm is not None:
            self._alive = True
            # enable the laser
            lm.enable_laser()

            lm.set_motor('beam', bd)

            lm.set_laser_power(rp)

            self._discrete_scan(cx, cy, padding, step_len)
            self._alive = False
            self.completed = True
        else:
            self.warning_dialog('No Laser Manager available')

    def _discrete_scan(self, cx, cy, padding, step_len):
        nsteps, step_gen = self._step_generator(cx, cy, padding, step_len)

        lm = self.laser_manager
        sm = lm.stage_manager
        apm = lm.get_device('analog_power_meter')

        if lm.simulation:
            pgen = power_generator(nsteps)

        tab = self._new_data_table(padding)

        while 1:
            if not self._alive:
                break
            try:
                col, nx, row, ny = step_gen.next()
            except StopIteration:
                break

            if lm.simulation:
                mag = pgen.next()
            else:
                sm.linear_move(nx, ny)
                if col == 0:
                    # sleep for 1.5 nsecs to let the detector cool off.
                    # usually gets blasted as the laser moves into position
                    time.sleep(1.5)

                mag = 0
                for _ in range(self.nintegrations):
                    mag += apm.read_power_meter(verbose=False)
                    time.sleep(0.01)

                mag /= self.integration

            self._write_datum(tab, nx, ny, col, row, mag)
            self.canvas.set_cell_value(col, row, mag)

    def _new_data_table(self, padding):
        dm = self.data_manager
#        root = '/usr/local/pychron/powermaps'
#         dw = DataWarehouse(root=paths.powermap_db_root)
#                           root=os.path.join(paths.co2laser_db_root, 'power_map'))
#                           os.path.join(data_dir, base_dir))
#         dw.build_warehouse()
        dm.new_frame(base_frame_name='powermap-{}'.format(generate_datestamp()),
#                      directory=dw.get_current_dir()
                     )
        t = dm.new_table('/', 'power_map', table_style='PowerMap')
        t._v_attrs['bounds'] = padding
        return t

    def _write_datum(self, tab, nx, ny, c, r, mag):
        nr = tab.row
        nr['row'] = r
        nr['col'] = c
        nr['x'] = nx
        nr['y'] = ny
        nr['power'] = mag
        nr.append()
        tab.flush()


    def _step_generator(self, cx, cy, padding, step_len):
        nsteps = int(padding / step_len)
        xsteps = xrange(-nsteps, nsteps + 1)
        ysteps = xrange(-nsteps, nsteps + 1)

        self.canvas.set_parameters(xsteps, ysteps)
        self.canvas.request_redraw()

        def gen():
            for j, yi in enumerate(ysteps):
                ny = (yi * step_len) + cy
                for i, xi in enumerate(xsteps):
                    nx = (xi * step_len) + cx
                    yield i, nx, j, ny

        return len(xsteps), gen()
#============= EOF =============================================


