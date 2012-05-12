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
from traits.api import Float, Int, Any, Instance, Enum
from traitsui.api import View, Item, VGroup, HGroup
from pyface.timer.do_later import do_after
#============= standard library imports ========================
import time
import numpy as np
from enable.component_editor import ComponentEditor
from threading import Event, Thread

#============= local library imports  ==========================
from src.canvas.canvas2D.raster_canvas import RasterCanvas
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.loggable import Loggable
from src.database.data_warehouse import DataWarehouse
from src.helpers.datetime_tools import generate_datestamp
import random
from src.graph.graph import Graph
from src.helpers.paths import co2laser_db_root
#from src.graph.graph3D import Graph3D


def gaussian(height, center_x, center_y, width_x, width_y):
    '''
    Returns a gaussian function with the given parameters
    '''

    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x, y: height * np.exp(
 -(((center_x - x) / width_x) ** 2 + ((center_y - y) / width_y) ** 2) / 2)

def power_generator(nsteps):
    '''
    '''
    x, y = np.mgrid[0:nsteps, 0:nsteps]
    data = gaussian(2, 5, 5, 5, 5)(x, y)#+np.random.random(x.shape)
    i = 0
    j = 0
    while 1:
        yield data[i][j]
        j += 1
        if j == nsteps:
            i += 1
            j = 0
def xygenerator():
    i = 0
    j = 0
    while 1:
        x = i
        y = j
        if j == 10:
            i += 1
            j = 0
        else:
            j += 1


        yield x, y
xygen = xygenerator()

class PowerMapping(Loggable):
#    kind = Enum('discrete', 'continuous')
    beam_diameter = Float(1)
    request_power = Float(1)
    padding = Float(1.0)
    step_length = Float(0.25)
    center_x = Float(0)
    center_y = Float(0)
    integration = Int(1)

#    laser_manager = Any(transient=True)
    canvas = Instance(RasterCanvas, transient=True)
    parent = Any(transient=True)

    window_x = Int
    window_y = Int
    display_name = ''

    def _canvas_default(self):
        return RasterCanvas()

    def isAlive(self):
        return self.parent.isAlive()

    def _load_data_manager(self):
        dm = H5DataManager()
        root = '/usr/local/pychron/powermaps'
        dw = DataWarehouse(root=co2laser_db_root)
#                           os.path.join(data_dir, base_dir))
        dw.build_warehouse()
        dm.new_frame(base_frame_name='powermap-{}'.format(generate_datestamp()),
                    directory=dw.get_current_dir())
        t = dm.new_table('/', 'power_map', table_style='PowerMap')
        t._v_attrs['bounds'] = self.padding

        return dm

    def _execute_(self):
        self.info('executing discrete scan')
        self.info('beam diameter={} request_power={}'.format(self.beam_diameter,
                                                             self.request_power))
        lm = self.parent.laser_manager
        # enable the laser
        lm.enable_laser()
        if hasattr(lm, 'set_beam_diameter'):
            '''
                synrad co2 does not have auto beam setting
            '''
            lm.set_beam_diameter(self.beam_diameter)

        lm.set_laser_power(self.request_power)

        self._discrete_scan()

    def _discrete_scan(self):
        lm = self.parent.laser_manager
        sm = lm.stage_manager
        canvas = self.canvas

        padding = self.padding
        step_len = self.step_length

        nsteps = int(padding / step_len)

        steps = xrange(-nsteps, nsteps + 1)
        canvas.set_parameters(steps, steps)
        canvas.request_redraw()

        xsteps = steps
        ysteps = steps

        cx = self.center_x
        cy = self.center_y

        gaussian_power_generator = power_generator(len(xsteps))
        dm = self._load_data_manager()
        tab = dm.get_table('power_map', '/')

        for j, yi in enumerate(ysteps):

            if not self.isAlive():
                break

            ny = (yi * step_len) + cy
            for i, xi in enumerate(xsteps):
                if not self.isAlive():
                    break

                nx = (xi * step_len) + cx
                if not lm.simulation:
                    sm.linear_move(nx, ny, verbose=False, block=True, grouped_move=False)
                    if i == 0:
                        #sleep for 1.5 nsecs to let the detector cool off.
                        #usually gets blasted as the laser moves into position
                        time.sleep(1.5)
                    mag = 0
                    for _ in range(self.integration):
#                        mag += analog_power_meter.read_power_meter(verbose=False)
                        time.sleep(0.01)

                    mag /= self.integration
                else:
                    mag = gaussian_power_generator.next()


                datum = (i, j, mag)
                do_after(10, canvas.set_cell_value, *datum)
#                self.data_manager.write_to_frame(datum)
#
                #write to the table
#                print tab
                nr = tab.row
                nr['row'] = i
                nr['col'] = j
                nr['x'] = nx
                nr['y'] = ny
                nr['power'] = mag
                nr.append()
                tab.flush()

                if lm.simulation:
                    time.sleep(0.01)

        if self.isAlive():
            self.parent._save_to_db(dm.get_current_path())
            dm.close()

        self._alive = False
        canvas.request_redraw()

    def _get_configure_group(self):
        cfg_grp = VGroup(Item('beam_diameter'),
                    Item('request_power'),
                    Item('padding'),
                    Item('step_length'),
                    Item('center_x'),
                    Item('center_y'),

                    )
        return cfg_grp

    def configure_view(self):
        cgrp = self._get_configure_group()
        return View(cgrp,
                    buttons=['OK', 'Cancel'],
                    title='Configure Power Mapping'
                    )

    def traits_view(self):
        canvas_grp = VGroup(Item('canvas', show_label=False,
                                     editor=ComponentEditor()))
        cfg_grp = self._get_configure_group()
        cfg_grp.style = 'readonly'

        return View(
                    HGroup(
                           cfg_grp,
                           canvas_grp
                           ),
                    x=self.window_x,
                    y=self.window_y,
                    width=700,
                    height=600,
                    title='Power Mapping - {}'.format(self.display_name)
                    )

#============= EOF =============================================
# def _continuous_scan(self):
#
#        g = Graph()
#        g.new_plot()
#        g.new_series(type='cmap_scatter')
#        do_after(1, g.edit_traits)
#
#        lm = self.parent.laser_manager
#        padding = self.padding
#
#        sm = lm.stage_manager
##        analog_power_meter = lm.analog_power_meter
#        stage_controller = sm.stage_controller
#
##        graph = Graph3D()
##        s = graph.scene
#
##        do_after(1, graph.edit_traits)
#
#        offset = 1
#
#        #nrows should be calculates so  result is a square
#        nrows = int(padding * 2 / offset) + 1
#
#        cx = self.center_x
#        cy = self.center_y
#        xx = []
#        yy = []
#        zz = []
#
#        gaussian_power_generator = power_generator(nrows)
#
#        # turn off velocity calculation
#        if not lm.simulation:
#            for a in stage_controller.axes.itervalues():
#                a.calculate_parameters = False
#
#            stage_controller._set_single_axis_motion_parameters(pdict=dict(key='x', acceleration=2,
#                                                                              deceleration=2,
#                                                                              velocity=1.25
#                                                                              ))
#            stage_controller._set_single_axis_motion_parameters(pdict=dict(key='y', acceleration=2,
#                                                                              deceleration=2,
#                                                                              velocity=1.25
#                                                                          ))
#        data = g.plots[0].data
#        for i in range(nrows):
#            y = cy - padding + i * offset
#            if i % 2 == 0:
#                p1 = cx - padding, y
#                p2 = cx + padding, y
#            else:
#                p2 = cx - padding, y
#                p1 = cx + padding, y
#
#
#            self.info('scanning row {} {} {}'.format(i + 1, p1, p2))
#            sm.linear_move(p1[0], p1[1], block=True, grouped_move=False)
#
#            #wait at the start for a bit to let the detector settle
#            #time.sleep(0.5)
#
#            sm.linear_move(p2[0], p2[1], block=False, grouped_move=False)
#
#            #sleep time required to reach cvt zone
#
##            max_len = 50
#            event = Event()
#            axkey = 'x'
#            t = Thread(target=stage_controller.at_velocity, args=(axkey, event))
#            t.start()
#            j = 0
#            while not event.isSet():
##                print i
#                if sm.simulation:
#                    x = p1[0] + j
#                    y = i
#                else:
#                    x, y = stage_controller.get_xy()
#                j += 1
#
#                mag = random.random()
#
#                xs = np.hstack((data.get_data('x0'), [x]))
#                ys = np.hstack((data.get_data('y0'), [y]))
#                cs = np.hstack((data.get_data('c0'), [mag]))
#
#                data.set_data('x0', xs)
#                data.set_data('y0', ys)
#                data.set_data('c0', cs)
#
##                print xs
#                do_after(1, g.redraw)
#                time.sleep(0.1)

##            nvalues = random.randint(0, 0) + max_len
##            j = 0
##            while j <= nvalues:
#            xs = []
#            ys = []
#            zs = []
#            if not sm.simulation:
#                while not event.isSet():
#                    #collect power data
#                    x, y = stage_controller.get_xy()
#    #                mag = analog_power_meter.read_power_meter()#verbose = False)
#    #                d = j / float(max_len) * 3.3
#    #                d = d if i % 2 == 0 else -d
#    #                x = p1[0] + d
#    #                y = p1[1]
#                    mag = 10 - 0.125 * (x - cx) * (x - cx)
#    #                j += 1
#
#                    xs.append(x)
#                    ys.append(y)
#                    zs.append(mag)
#            else:
#                xs.append([a for a in range(10)])
#                ys.append([i for _ in range(10)])
#                zs.append([random.random() for _ in range(10)])
#
#            #sort the lists
#            data = sorted(zip(xs, ys, zs), key=lambda d:d[0])
#            xs = [d[0] for d in data]
#            ys = [d[1] for d in data]
#            zs = [d[2] for d in data]
#
#            #truncate the lists
#            xs = xs[:max_len]
#            ys = ys[:max_len]
#            zs = zs[:max_len]
#
#            xx.append(xs)
#            yy.append(ys)
#            zz.append(zs)
#
#            print xx
#            do_after(1, s.mlab.plot3d, np.asarray(xs), np.asarray(ys), np.asarray(zs), np.asarray(zs))#, asarray(zz)[0])
#            do_after(1, s.mlab.mesh, np.asarray(xx), np.asarray(yy), np.asarray(zz))
#            s.mlab.plot3d(np.asarray(xs), np.asarray(ys), np.asarray(zs), np.asarray(zs))#, asarray(zz)[0])

#            do_after(1, s.mlab.mesh, np.asarray(xx), np.asarray(yy), np.asarray(zz))
