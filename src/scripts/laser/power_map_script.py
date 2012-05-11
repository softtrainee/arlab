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
from traits.api import Instance, Int, Float, HasTraits, List, Any, Button, Property
from traitsui.api import View, Item, HGroup, Label, spring, Handler
from enable.api import ComponentEditor
from pyface.timer.do_later import do_after


#============= standard library imports ========================
import time
import numpy as np
import os
from threading import Thread, Event
#============= local library imports  ==========================

from src.scripts.core.core_script import CoreScript
from src.canvas.canvas2D.raster_canvas import RasterCanvas
from src.helpers.filetools import parse_file
from power_map_script_parser import PowerMapScriptParser



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

class PowerMapHandler(Handler):
    def close(self, info, isok):
        info.object.kill_script()
        return True

class PowerMapStep(HasTraits):
    beam_diameter = Float
    padding = Float
    step_length = Float
    power = Float
    integration = Int
    est_duration = Property(depends_on='padding,step_length')
    duration = Float
    def _get_est_duration(self):
        nsecs = 0
        if self.step_length > 0:
            n = int(self.padding / self.step_length)
            const = 1
            sec_per_step = self.integration * (0.01 + const)

            nsecs = int(n * n * sec_per_step)


        h = nsecs / 3600
        m = (nsecs % 3600) / 60
        s = (nsecs % 3600) % 60

        time_padding = 0.5 #increase duration by 50%
        self.duration = nsecs / 60.0 * (1 + time_padding)

        return '{:02n}:{:02n}:{:02n}'.format(h, m, s)


class PowerMapScript(CoreScript):
    '''
    '''

    parser_klass = PowerMapScriptParser
    canvas = Instance(RasterCanvas)
    center_x = Float
    center_y = Float
    steps = List
    selected = Any
    cnt = 0
    integration = 10
    def load_steps(self):
        self.steps = []
        self.cnt = 0
        p = os.path.join(self.source_dir, self.file_name)
        for l in parse_file(p):
            args = l.split(',')
            self.steps.append(PowerMapStep(beam_diameter=float(args[0]),
                                           padding=float(args[1]),
                                           step_length=float(args[2]),
                                           power=float(args[3]),
                                           integration=self.integration
                                           )

                              )

    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText

        doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')
        doc.add_heading('Power Map Documentation', heading=2, color='red')

        doc.add_heading('Parameters', heading=3)
        doc.add_text('Beam Diam, Padding, Step len, Power<br>')
        doc.add_list(['Beam diameter (0-6) -- approx. laser beam diameter',
                      'Padding -- Number of steps +/- from center',
                      'Step length (mm) -- 2 * padding * step length = length of map side',
                      'Power setting (0-100) -- percent of total power'])

        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])

        r2 = HTMLText('1,5,0.1,10.', face='courier', size='2')
        table.add_row([r2])
        return doc

    def load(self):
        ok = False
        if self.manager is not None:
            ok = True
            stm = self.manager.stage_manager

            self.center_x = stm.stage_controller.x
            self.center_y = stm.stage_controller.y

            info = self.edit_traits(view='set_center_view')
            if not info.result:
                ok = False

        else:
            self.warning('No Laser Manager')
        return ok

    def _pre_run_(self):

        if self.manager.enable_laser():
            #slow motion while mapping for smoother moves
            #self.manager.stage_manager.stage_controller.set_low_speed()

            return True



    def get_frame_header(self):
        header = [['x', 'y', 'power']]
        return header

#    def set_graph(self):
#        self.edit_traits(view = 'canvas_view')

    def _kill_script(self):
        # turn on velocity calculation
        for a in self.manager.stage_manager.stage_controller.axes.itervalues():
            a.calculate_parameters = True


        self.manager.disable_laser()

    def raw_statement(self, args):

        if len(args) == 4:
            bd = float(args[0])
            padding = float(args[1])
            step_len = float(args[2])
            request_pwr = float(args[3])

            nsteps = int(padding / step_len)
            steps = xrange(-nsteps, nsteps + 1)
            self.set_data_frame(base_frame_name='beam%.1f_' % bd)

            self.selected = self.steps[self.cnt]
            self.cnt += 1

            self._execute_map(bd, request_pwr, steps, step_len, padding)
            self.data_manager.write_metadata([['Beam', 'Padding', 'StepLength', 'Power'],
                                               list(args)])


    def _execute_map(self, *args):
        func = getattr(self, '_{}_scan'.format(self.kind))
        func(*args)

    def _fast_scan(self, beam_diam, rpwr, steps, step_len, padding):
        from src.graph.graph3D import Graph3D

        stage_manager = self.manager.stage_manager
        analog_power_meter = self.manager.analog_power_meter
        stage_controller = stage_manager.stage_controller


        graph = Graph3D()
        s = graph.scene

        do_after(1, graph.edit_traits)

        offset = 1

        #nrows should be calculates so  result is a square
        nrows = int(padding * 2 / offset) + 1

        cx = self.center_x
        cy = self.center_y
        xx = []
        yy = []
        zz = []

        # turn off velocity calculation

        for a in stage_controller.axes.itervalues():
            a.calculate_parameters = False

        stage_controller._set_single_axis_motion_parameters(pdict=dict(key='x', acceleration=2,
                                                                          deceleration=2,
                                                                          velocity=1.25
                                                                          ))
        stage_controller._set_single_axis_motion_parameters(pdict=dict(key='y', acceleration=2,
                                                                          deceleration=2,
                                                                          velocity=1.25
                                                                          ))

        for i in range(nrows):
            y = cy - padding + i * offset
            if i % 2 == 0:
                p1 = cx - padding, y
                p2 = cx + padding, y
            else:
                p2 = cx - padding, y
                p1 = cx + padding, y


            stage_controller.linear_move(p1[0], p1[1], block=True, grouped_move=False)

            #wait at the start for a bit to let the detector settle
            #time.sleep(0.5)

            stage_controller.linear_move(p2[0], p2[1],
                                                        block=False, grouped_move=False)

            #sleep time required to reach cvt zone

            max_len = 50
            event = Event()
            axkey = 'x'
            t = Thread(target=stage_controller.at_velocity, args=(axkey, event))
            t.start()

#            nvalues = random.randint(0, 0) + max_len
#            j = 0
#            while j <= nvalues:
            xs = []
            ys = []
            zs = []
            while not event.isSet():
                #collect power data

                x, y = stage_controller.get_xy()
                mag = analog_power_meter.read_power_meter()#verbose = False)

#                d = j / float(max_len) * 3.3
#                d = d if i % 2 == 0 else -d
#                x = p1[0] + d
#                y = p1[1]
                mag = 10 - 0.125 * (x - cx) * (x - cx)
#                j += 1

                xs.append(x)
                ys.append(y)
                zs.append(mag)

            #sort the lists
            data = sorted(zip(xs, ys, zs), key=lambda d:d[0])
            xs = [d[0] for d in data]
            ys = [d[1] for d in data]
            zs = [d[2] for d in data]

            #truncate the lists
            xs = xs[:max_len]
            ys = ys[:max_len]
            zs = zs[:max_len]

            xx.append(xs)
            yy.append(ys)
            zz.append(zs)

#            do_after(1, s.mlab.plot3d, np.asarray(xs), np.asarray(ys), np.asarray(zs), np.asarray(zs))#, asarray(zz)[0])
#            do_after(1, s.mlab.mesh, np.asarray(xx), np.asarray(yy), np.asarray(zz))
#            s.mlab.plot3d(np.asarray(xs), np.asarray(ys), np.asarray(zs), np.asarray(zs))#, asarray(zz)[0])

            do_after(1, s.mlab.mesh, np.asarray(xx), np.asarray(yy), np.asarray(zz))

    def _normal_scan(self, beam_diam, rpwr, steps, step_len, padding):
        manager = self.manager
        stage_manager = manager.stage_manager
        analog_power_meter = manager.analog_power_meter

        canvas = self.canvas
        canvas.set_parameters(steps, steps)

        if hasattr(manager, 'set_beam_diameter'):
            '''
                synrad co2 does not have auto beam setting
            '''
            manager.set_beam_diameter(beam_diam)

        manager.set_laser_power(rpwr)

        xsteps = steps
        ysteps = steps

        cx = self.center_x
        cy = self.center_y

        gaussian_power_generator = power_generator(len(xsteps))

        stage_manager.stage_controller._set_single_axis_motion_parameters(pdict=dict(key='x', acceleration=2,
                                                                          deceleration=2,
                                                                          velocity=1
                                                                          ))
        stage_manager.stage_controller._set_single_axis_motion_parameters(pdict=dict(key='y', acceleration=2,
                                                                          deceleration=2,
                                                                          velocity=1
                                                                          ))

        manager.set_laser_monitor_duration(self.selected.duration)

        for j, yi in enumerate(ysteps):
            if not self.isAlive():
                break

            ny = (yi * step_len) + cy
            for i, xi in enumerate(xsteps):
                if not self.isAlive():
                    break
                nx = (xi * step_len) + cx

                stage_manager.stage_controller.linear_move(nx, ny, verbose=False, block=True, grouped_move=False)
                if not self.isAlive():
                    break

                if manager.simulation:
                    mag = gaussian_power_generator.next()
                else:

                    if i == 0:
                        #sleep for 1.5 nsecs to let the detector cool off.
                        #usually gets blasted as the laser moves into position
                        time.sleep(1.5)
                    mag = 0
                    for c in range(self.integration):
                        mag += analog_power_meter.read_power_meter(verbose=False)
                        time.sleep(0.01)

                    mag /= self.integration

                datum = (i, j, mag)
                do_after(1, canvas.set_cell_value, *datum)
                self.data_manager.write_to_frame(datum)

                if manager.simulation:
                    time.sleep(0.1)

        canvas.request_redraw()

    def _canvas_default(self):
        return RasterCanvas()

#============= views ===================================
    def set_center_view(self):
        v = View(HGroup(spring, Label('Set Center Position'), spring),
                 Item('center_x', format_str='%0.3f'),
                 Item('center_y', format_str='%0.3f'),
                 kind='modal',
                 buttons=['OK', 'Cancel'],
                 title='Define Center'
                 )
        return v

    def canvas_view(self):
        v = View(Item('canvas', show_label=False,
                    editor=ComponentEditor(),
                    ),
                    resizable=True,
                    height=625,
                    width=625,
                    #title = 'Raster Manager',
                    handler=PowerMapHandler
                    )
        return v

class D(HasTraits):
    test = Button
    def traits_view(self):
        return View('test')
    def _test_fired(self):
        p = PowerMapScript()
        padding = 1.5
        step_len = 0.05
        nsteps = int(padding / step_len)
        steps = xrange(-nsteps, nsteps + 1)
        p._fast_scan(10, 10, steps, step_len, padding)

if __name__ == '__main__':
    D().configure_traits()
#============= EOF ====================================
