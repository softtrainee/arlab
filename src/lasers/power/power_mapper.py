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
from numpy import exp, mgrid, linspace, hstack, array, rot90
from src.helpers.datetime_tools import generate_datestamp
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.consumer_mixin import ConsumerMixin
import random
from scipy.interpolate.ndgriddata import griddata
from src.graph.contour_graph import ContourGraph
from src.graph.graph import Graph
from chaco.plot_containers import HPlotContainer


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


class PowerMapper(Loggable, ConsumerMixin):
    laser_manager = Any
    canvas = Any
    graph = Any
    nintegrations = Int(5)
    data_manager = Instance(H5DataManager, ())

    _alive = False
    completed = Event
    def make_component(self, padding):
        cg = ContourGraph()

        cg.new_plot(title='Beam Space',
                    xtitle='X mm',
                    ytitle='Y mm',
                    )

        g = Graph()
        g.new_plot(
                   title='Motor Space',
                   xtitle='X mm',
                     ytitle='Power')
        g.new_series(
                     )

        self.graph = g
        self.contour_graph = cg
        c = HPlotContainer()
        c.add(g.plotcontainer)
        c.add(cg.plotcontainer)

        return c

    def stop(self):
        self._alive = False

    def do_power_mapping(self, bd, rp, cx, cy, padding, step_len):
        self._padding = padding

        self.info('executing discrete scan')
        self.info('beam diameter={} request_power={}'.format(bd, rp))

        self.setup_consumer(func=self._add_data)
        lm = self.laser_manager
        if lm is not None:
            self._alive = True
            # enable the laser
            lm.enable_laser()

            lm.set_motor('beam', bd)

            lm.set_laser_power(rp)
            discrete = False
            if discrete:
                self._discrete_scan(cx, cy, padding, step_len)
            else:
                self._continuous_scan(cx, cy, padding, step_len)

            self._alive = False
            self.completed = True
        else:
            self.warning_dialog('No Laser Manager available')

        # stop the consumer
        self._should_consume = False

    def _add_data(self, v):
        tab, x, y, col, row, mag, sid = v
        self._write_datum(tab, x, y, col, row, mag)
        self.graph.add_datum((x, mag), series=sid)
        self.graph.redraw()

        self._xs = hstack((self._xs, x))
        self._ys = hstack((self._ys, y))
        self._zs = hstack((self._zs, mag))
        if col and row > 1:
            cg = self.contour_graph

            xi = linspace(-0.5, 0.5, 100)
            yi = linspace(-0.5, 0.5, 100)
            X = xi[None, :]
            Y = yi[:, None]

            xx = self._xs
            yy = self._ys
            z = self._zs

#             print 'xx-----', xx
#             print 'yy-----', yy
            zd = griddata((xx, yy), z, (X, Y),
                        method='cubic',
                        fill_value=0)


            zd = rot90(zd, k=2)
#             zd = zd.T
#             print zd
            if not cg.plots[0].plots.keys():
                padding = self._padding
                cg.new_series(z=zd,
                              xbounds=(-padding, padding),
                              ybounds=(-padding, padding),
                              style='contour')
            else:
                cg.plots[0].data.set_data('z0', zd)

            cg.redraw()


    def _continuous_scan(self, cx, cy, padding, step_len):
        _nrows, row_gen = self._row_generator(cx, cy, padding, step_len)
        lm = self.laser_manager
        sm = lm.stage_manager
        apm = lm.get_device('analog_power_meter')
        i = 0
        self._xs, self._ys, self._zs = array([]), array([]), array([])
        tab = self._new_data_table(padding)
        while 1:
            if not self._alive:
                break
            try:
                row, ny = row_gen.next()
            except StopIteration:
                break

            if i % 2 == 0:
                sx = cx - padding
                ex = cx + padding
            else:
                sx = cx + padding
                ex = cx - padding

            sc = sm.stage_controller
            # move to start position
            sc.linear_move(sx, ny, block=True)
            time.sleep(1)

            # move to start position
            self.info('move to end {},{}'.format(ex, ny))
            sc.linear_move(ex, ny, block=False, velocity=0.5)

            self.graph.new_series(color='black')
            sid = len(self.graph.series[0]) - 1

            if lm.simulation:
                n = 21
                r = random.random()
                if r < 0.25:
                    n += 1
                elif r > 0.75:
                    n -= 1
                for i in range(n):
                    x, y = i * 0.1 - 1, ny
                    mag = row + random.random()
                    self.add_consumable((tab, x, y, i, row, mag, sid))
            else:
                while 1:
                    x, y = sc.x, sc.y
                    mag = apm.read_power_meter(verbose=False)
                    if not sc.timer.isActive():
                        self.add_consumable((tab, x, y, 1, row, mag, sid))
                        break
                    else:
                        self.add_consumable((tab, x, y, 0, row, mag, sid))

#                     time.sleep(0.1)

            i += 1


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
        nr['col'] = c
        nr['row'] = r
        nr['x'] = nx
        nr['y'] = ny
        nr['power'] = mag
        nr.append()
        tab.flush()


    def _row_generator(self, cx, cy, padding, step_len):
        nsteps = int(padding / step_len)
        ysteps = xrange(-nsteps, nsteps + 1)

        self.graph.set_x_limits(cx - padding, cx + padding, pad='0.1')
        def gen():
            for j, yi in enumerate(ysteps):
                ny = (yi * step_len) + cy
                yield j, ny
        return nsteps, gen()

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


