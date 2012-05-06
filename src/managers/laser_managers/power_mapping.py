'''
Copyright 2012 Jake Ross

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
#============= enthought library imports =======================
from traits.api import HasTraits, Float, Int, Any, Instance
from traitsui.api import View, Item, VGroup, HGroup
from pyface.timer.do_later import do_after
#============= standard library imports ========================
import time
import numpy as np
from enable.component_editor import ComponentEditor
from src.canvas.canvas2D.raster_canvas import RasterCanvas
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.loggable import Loggable
from src.database.data_warehouse import DataWarehouse
from src.helpers.datetime_tools import generate_datestamp
#============= local library imports  ==========================


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

class PowerMapping(Loggable):
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
        root = '/usr/local/pychron/powermapsdb'
        dw = DataWarehouse(root=root)
#                           os.path.join(data_dir, base_dir))
        dw.build_warehouse()
        dm.new_frame(base_frame_name='powermap-{}'.format(generate_datestamp()),
                    directory=dw.get_current_dir())
        t = dm.new_table('/', 'power_map', table_style='PowerMap')
        t._v_attrs['bounds'] = self.padding

        return dm

    def _execute_(self):
        self.info('executing')
        lm = self.parent.laser_manager

        lm.simulation = True
        sm = lm.stage_manager

        canvas = self.canvas

#        # enable the laser
        lm.enable_laser()
#
        beam_diam = self.beam_diameter
        rpwr = self.request_power
        padding = self.padding
        step_len = self.step_length

        nsteps = int(padding / step_len)

        steps = xrange(-nsteps, nsteps + 1)
        canvas.set_parameters(steps, steps)
        canvas.request_redraw()
        if hasattr(lm, 'set_beam_diameter'):
            '''
                synrad co2 does not have auto beam setting
            '''
            lm.set_beam_diameter(beam_diam)

        lm.set_laser_power(rpwr)

        xsteps = steps
        ysteps = steps

        cx = self.center_x
        cy = self.center_y

        gaussian_power_generator = power_generator(len(xsteps))
        dm = self._load_data_manager()
        tab = dm.get_table('power_map', '/')

        print lm.simulation
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

                if not self.isAlive():
                    break

                if lm.simulation:
                    mag = gaussian_power_generator.next()
                else:

                    if i == 0:
                        #sleep for 1.5 nsecs to let the detector cool off.
                        #usually gets blasted as the laser moves into position
                        time.sleep(1.5)
                    mag = 0
                    for c in range(self.integration):
#                        mag += analog_power_meter.read_power_meter(verbose=False)
                        time.sleep(0.01)

                    mag /= self.integration

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
