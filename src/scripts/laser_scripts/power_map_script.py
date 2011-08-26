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
import numpy as np
import time

#=============local library imports  ==========================
from laser_power_script import LaserPowerScript
from src.managers.data_managers.h5_data_manager import H5DataManager

def gaussian(height, center_x, center_y, width_x, width_y):
    '''
            @type center_x: C{str}
            @param center_x:

            @type center_y: C{str}
            @param center_y:

            @type width_x: C{str}
            @param width_x:

            @type width_y: C{str}
            @param width_y:
    '''
    """Returns a gaussian function with the given parameters"""
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


class PowerMapScript(LaserPowerScript):
    '''
        G{classtree}
    '''
    center_x = 25#4.0
    center_y = 25#-12.675
    request_pwr = 0
    style = 1
    nsteps = 10
    power_meter_range = 1
    power_meter_warmup_time = None
    parent_group = 'root.molectron.'

    def set_data_frame(self):
        '''
        '''
        if LaserPowerScript.set_data_frame(self):
#        if super(PowerMapScript, self).set_data_frame():
            self.data_manager.add_group('molectron')
            return True

    def _run_(self, *args):
        '''
            @type *args: C{str}
            @param *args:
        '''

        manager = self.manager
        raster_manager = manager.raster_manager
        self.add_display_text('Starting Power Map')

        manager.enable_laser()
        if not self.isAlive():
            self.info('laser not enabled')
            return

        for i, line in enumerate(self._file_contents_):
            if not self.isAlive():
                break

            if i != 0:
                #delay before next run
                time.sleep(5)

            self.add_display_text('executing %s' % line, log = True)
            args = line.split(',')
            #beam diameter (mm), padding(mm), step len (mm), power (PowerUnits)
            if len(args) == 4:
                self.beam_diameter = float(args[0])
                self.padding = padding = float(args[1])
                self.step_len = step_len = float(args[2])
                self.request_pwr = float(args[3])

                nsteps = int(padding / step_len)
                self.steps = steps = xrange(-nsteps, nsteps + 1)
                raster_manager.set_canvas_parameters(steps, steps)

                bd = self.beam_diameter
                if int(bd) != bd:
                    run_id = 'beamdiameter%s' % '_'.join(('%s' % bd).split('.'))
                else:
                    run_id = 'beamdiameter%02i' % bd

                run_id, table = self.setup_table(run_id)

                self.execute_map(run_id, table)
                manager.reset_laser_monitor()
            else:
                self.warning('Invalid step %s' % line)

        self.clean_up()

        self.info('power mapping finished ')

    def setup_table(self, table, parent = 'root.molectron'):
        '''
            @type table: C{str}
            @param table:

            @type parent: C{str}
            @param parent:
        '''
        dm = self.data_manager

        run_id = dm.add_table(table, parent = parent, table_style = 'PowerMap')

        table = '%s%s' % (self.parent_group, run_id)
        dm.set_table_attribute('beam_diameter', self.beam_diameter, table)
        dm.set_table_attribute('step_len', self.step_len, table)
        dm.set_table_attribute('power_meter_range', self.power_meter_range, table)
        dm.set_table_attribute('power_request', self.request_pwr, table)
        dm.set_table_attribute('padding', self.padding, table)

        return run_id, table



    def execute_map(self, run_id, table):
        '''
        '''
        start_time = time.time()
        manager = self.manager
        data_manager = self.data_manager

        bd = self.beam_diameter

        #set beam diameter
        self.add_display_text('setting beam diameter %0.1f' % bd)
        manager.set_beam_diameter(bd)

        manager.set_laser_power(self.request_pwr)

        #measure baseline
        #progress_display.add_text(msg = 'measuring baseline')

#        baseline_padding = 0.5
#        x = self.center_x - self.step_len * len(self.steps) / 2.0 - baseline_padding
#        y = self.center_y - self.step_len * len(self.steps) / 2.0 - baseline_padding
#        #progress.add_text(msg='baseline position %0.3f,%0.3f'%(x,y))
#
#        self.move_to_baseline(x, y)

        self.warm_up(duration = self.power_meter_warmup_time)
#        b1 = self._measure_baseline()
#        data_manager.set_table_attribute('baseline1', b1, table)

        self.add_display_text('measure power map')

        #slow motion while mapping for smoother moves
        manager.stage_manager.stage_controller.set_low_speed()

        #raster beam to producee a power map
        self._power_map(run_id)

        #reset to normal speed
        manager.stage_manager.stage_controller.set_normal_speed()

        if self.isAlive():
#            progress_display.add_text(msg = 'measure baseline')
#            x = self.center_x + self.step_len * len(self.steps) / 2.0 + baseline_padding
#            y = self.center_y + self.step_len * len(self.steps) / 2.0 + baseline_padding
#            progress_display.add_text(msg = 'baseline position %0.3f,%0.3f' % (x, y))
#    
#            self.move_to_baseline(x, y)
#            b2 = self._measure_baseline()
#    
#            data_manager.set_table_attribute('baseline2', b2, table)
##    
            s = 1.0 if manager.simulation else 3600.0

            duration = (time.time() - start_time) / s
            self.add_display_text('run complete duration =%0.2f' % duration, log = True)

            data_manager.set_table_attribute('duration', duration, table)

    def warm_up(self, duration = None):
        '''
            @type duration: C{str}
            @param duration:
        '''
        self.info('warming up detector')
        if duration is None:
            baseline_std = 100
            tolerance = 0.5
            self.info('warm until baseline std < %s' % tolerance)
            apm = self.manager.analog_power_meter
            baseline_values = np.array([])
            n = 10

            while baseline_std >= tolerance:

                if not self.isAlive():
                    break
                b = apm.read_power_meter()
                baseline_values = np.hstack([baseline_values[-n + 1:], [b]])
                if len(baseline_values) >= n:
                    baseline_std = np.std(baseline_values)
                time.sleep(0.1)

        else:
            self.add_display_text('Warming up power meter for %s (secs)' % self.power_meter_warmup_time, log = True)
            if not self.manager.logic_board.simulation:
                time.sleep(duration)

    def move_to_baseline(self, x, y):
        '''
            @type x: C{str}
            @param x:

            @type y: C{str}
            @param y:
        '''
        msg = 'moving to baseline position %0.3f, %0.3f' % (x, y)
        self.add_display_text(msg, log = True)

        self.manager.stage_manager.linear_move_to(x, y, block = True)

    def _measure_baseline(self,):
        '''
            @type : C{str}
            @param :
        '''

        self.info('measuring baseline')

        #move to baseline point
        analog_power_meter = self.manager.analog_power_meter
        integrate = 10
        mag = 0
        for i in range(integrate):
            mag += analog_power_meter.read_power_meter()
        mag /= integrate
        return mag

    def _power_map(self, run_id):
        '''
            @type run_id: C{str}
            @param run_id:
        '''
        manager = self.manager
        stage_manager = manager.stage_manager

        raster_manager = manager.raster_manager
        data_manager = self.data_manager

        analog_power_meter = manager.analog_power_meter
        xsteps = self.steps
        ysteps = self.steps
        step_len = self.step_len
        gaussian_power_generator = power_generator(len(xsteps))


        for j, yi in enumerate(ysteps):
            if not self.isAlive():
                break
#            al,fail= self.isAlive()
#            if not al:
#                user_cancel=True
#                break
            #move to next row
            #self.info(' move to row %i ' % j)
            ny = (yi * step_len) + self.center_y
            #nm.linear_move_to(yaxis = ny, block = True, grouped_move =True )
            for i, xi in enumerate(xsteps):
                if not self.isAlive():
                    break

                nx = (xi * step_len) + self.center_x
                self.info('moving to step %i, %i (%0.3f,%0.3f)' % (j, i, nx, ny))
                if not manager.simulation:
                    stage_manager.linear_move_to(nx, ny, block = True, grouped_move = False)

                if not self.isAlive():
                    break

                integrate = 10
                self.info('sample power meter average %i counts' % integrate)

                if manager.simulation:
                    mag = gaussian_power_generator.next()

                else:
                    mag = 0
                    for c in range(integrate):
                        mag += analog_power_meter.read_power_meter()
                        time.sleep(0.1)
                    mag /= integrate

                raster_manager.set_cell_value(i, j, mag,
                                              #refresh = not manager.simulation
                                              )
                data_manager.record(dict(x = xi, y = yi, row = j, col = i, power = mag), table = '%s%s' % (self.parent_group, run_id))

                if manager.simulation:
                    time.sleep(0.25)



    def _data_manager_factory(self):
        '''
        '''
        return H5DataManager()





#    def center(self):
#        '''
#        '''
#        if self.manager.simulation:
#            return True
#        #turn on laser and set to zero power
#        self.manager.enable_laser()
#
#        #move to the center point and verify reading power
#        #block until finished move
#        #self.manager.stage_controller.multiple_axis_move([(1, self.center_x), (2, self.center_y)], block = True)
#        self.manager.stage_manager.linear_move_to(xaxis=self.center_x,
#                                                     yaxis=self.center_y)
#        r=True
##        self.manager.set_laser_power(self.request_pwr)
##        #delay 2 secs to equilibrate
##
##        time.sleep(2)
##        if self.manager.analog_power_meter.read_power_meter() > 1:
##            r = True
##        else:
##            r = False
##        
##        self.manager.set_laser_power(0)
#        return r
