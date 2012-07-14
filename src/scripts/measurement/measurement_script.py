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
from pyface.timer.api import Timer, do_after
#============= standard library imports ========================
import time
from numpy import array, vstack
#============= local library imports  ==========================
from src.scripts.core.core_script import CoreScript
from src.helpers.datetime_tools import time_generator
from src.scripts.measurement.measurement_script_parser import MeasurementScriptParser

#def ppr():
#    x = 1
#    while 1:
#
#        c = [(-1.5, 2000), (-1.2, 1000), (1, 500), (1, 50), (1, 10) ]
##        yield [coeffs[1] / 10 * random.random() + np.polyval(coeffs, x) for coeffs in c]
#        yield [np.polyval(coeffs, x) for coeffs in c]
#        x += 1
#pseudo_peak_regressions = ppr()
#pc_window_cnt = 0
class MeasurementScript(CoreScript):
    parser_klass = MeasurementScriptParser
    identifier = 1
#    record_data = True
    time_zero = None
    time_generator = None
    stream_timer = None
    ncycles = 1
    integration_time = 10

    pre_peak = False
    pre_baseline = False
    post_peak = False
    post_baseline = False

    measurements = None
    prev_mass = 0
    signals = None

    def set_time_zero(self, t=None):
        self.time_zero = t
        if t is None:
            self.time_zero = t = time.time()
            self.time_generator = time_generator(start=t)

    def pre_cycle(self):
        if self.pre_peak:
            self.manager.peak_center(
                                 center_pos=40
                                 )
        if self.pre_baseline:
            pass

    def cycle(self):
        for n in range(self.ncycles):
            for mass, settle, peak_center, baseline in self.measurements:
                self.info('setting mass {}'.format(mass))
                if abs(self.prev_mass - mass) > 0.5:
                    #this  should be handled automatically my spectrometer
                    #blank beam
                    time.sleep(settle / 1000.0)

                if peak_center:
                    self.manager.peak_center(center_pos=mass, update_pos=True)
                if baseline:
                    pass

                time.sleep(self.integration_time)
                self.record()

                self.prev_mass = mass

    def post_cycle(self):
        if self.post_peak:
            self.manager.peak_center(
                                 center_pos=40
                                 )
        if self.post_baseline:
            pass

    def record(self):
        t = self.time_generator.next()
        #d = pseudo_peak_regressions.next()
        d = 0
        #come
        d.reverse()

        datum = [t] + d
        self.info('get data {},{}'.format(*datum))
        self.data_manager.write_to_frame(datum)

        data = [(t, di) for di in d]
        if self.signals is None:
            self.signals = array(datum)
        else:
            self.signals = vstack((self.signals, datum))

        do_after(1, self.graph.add_data, data)

        '''
            if we have enough datapoints calculate an age
            
        '''
        '''
        tzero_val = [self.graph.get_intercept(plotid = i) for i in range(5)]
        if tzero_val[0] is not None:
#            do the age calculation
#            for simplicity now lets assume 40 and 39 are 0,1
            ar40 = tzero_val[0]
            ar39 = tzero_val[1]
            ar36 = tzero_val[4]
#            use a calculation_manager to calculate an age
            age=cm.calculate_age(identifier = self.identifier, ar40 = ar40,
                                        ar39 = ar39,
                                        ar36 = ar36)
            self.info('age = {} (Ma)'.format(age))
        '''

    def stream(self):
        if self.time_zero is None:
            self.set_time_zero()
        try:
            t = time.time() - self.time_zero
            d = self.data_gen.next()

            self.info('get data {},{}'.format(t, d))
            #record data to file
            self.data_manager.write_to_frame([d])
        except StopIteration:
            self.info('{} finished'.format(self.name))
            raise StopIteration

#===============================================================================
# statement handlers
#===============================================================================
    def measure_statement(self, mass, settle, peak_center, baseline):
            self.measurements.append((mass, settle, peak_center, baseline))

    def stream_statement(self):
        self.info('stream')
        self.measurement_timer = Timer(250, self.stream)
        do_after(1, self.measurement_timer.Start)
#===============================================================================
# core script protocol
#===============================================================================
    def _kill_script(self):
        if self.stream_timer is not None:
            self.stream_timer.Stop()

    def _post_run(self):
        '''
            
        '''
        if self.measurements:
            #if the time generator isnt set ie set_time_zero was never called
            #call it now
            if self.time_generator is None:
                self.set_time_zero()

            #get the current mass
            self.prev_mass = 40
            self.pre_cycle()
            self.cycle()

            self.post_cycle()
            return True

    def set_graph(self):
        from src.graph.regression_graph import StackedRegressionGraph

        g = StackedRegressionGraph(
                         window_title='Peak Regression {}'.format('foo'),
                         window_height=800,
                         window_y=25,
                         show_regression_editor=False
                         )


        cups = ['H2', 'H1', 'AX', 'L1', 'L2']
        cups.reverse()
        for i, cup in enumerate(cups):
            g.new_plot(bounds=(50, 125),
                       show_legend=True)
            g.new_series(plotid=i,
                         fit_type='parabolic',

                         type='scatter', marker='circle', marker_size=1.0)
            g.set_series_label(cup, plotid=i)
        g.set_x_limits(min=0, max=60)
        g.set_x_title('Time (sec)')

        do_after(5, g.edit_traits)
        self.graph = g

    def load(self):

        #trim off metadata
        for k, c in [('ncycles', int), ('integration_time', float),
                  ('pre_peak', 'bool'), ('pre_baseline', 'bool'),
                  ('post_peak', 'bool'), ('post_baseline', 'bool'),
                  ]:
            v = self._file_contents_.pop(0)
            if c == 'bool':
                v = True if v in ['True', 'T', 't', 'true'] else False
            else:
                v = c(v)
            setattr(self, k, v)

        self.set_data_frame('analysis{:05n}_'.format(self.identifier))
        self.measurements = []
        return True
#============= EOF =============================================
#    def measure(self, mass, settle, peak_center):
#
#        self.info('setting mass {}'.format(mass))
#        if abs(self.prev_mass - mass) > 0.5:
#            #this  should be handled automatically my spectrometer
#            #blank beam
#            time.sleep(settle / 1000.0)
#
#        if peak_center:
#            self.manager.peak_center(center_pos = mass, update_pos = True)
#
#        time.sleep(self.integration_time)
#        self.record()
#
#        self.prev_mass = mass
#    def _peak_center_step(self, di):
#        g = self.peak_graph
#
#        if self.cfirst:
#            self.cfirst = False
#            x = di
#        else:
#            x = self.x
#        spec = self.manager.spectrometer
#
#        if spec.simulation:
#            intensity = self.peak_generator.next()
#        else:
#            intensity = self.data[DETECTOR_ORDER.index(self.reference_detector)]
#
#        self.intensities.append(intensity)
#        g.add_datum((x, intensity), update_y_limits = True)
#
#        try:
#            x = self.gen.next()
#        except StopIteration:
#            spec.finish_peak_center(g, self.dac_values, self.intensities)
#
#            self.centering = False
#            return
#
#        self.x = x
#        spec.magnet.set_dac(x)
#
#    def _measure_step(self, cond, mg):
#        self.data = self.manager.spectrometer.get_intensities()
#        if self.first and cond:
#            cond.acquire()
#            self.first = False
#
#        if self.centering:
#            self._peak_center_step(None)
#        else:
#            try:
#                m, n = mg.next()
#            except StopIteration, e:
#                try:
#                    cond.notify()
#                    cond.release()
#                finally:
#                    raise StopIteration
#
#            self.measure(*m[1])



#            mg = ((mi, n) for n in range(self.ncycles) for mi in enumerate(self.measurements))
#
#            #do the first 
#            self._measure_step(None, mg)
#            self.first = True
#            cond = Condition()
##            with cond:
#            cond.acquire()
#            t = Timer(self.integration_time * 1000, self._measure_step, cond, mg)
#            self.measurement_timer = t
#            t.Start()
#            cond.wait()
#            cond.release()
#    def peak_center(self, mass):
#
#        self.info('peak centering at {} '.format(mass))
#
#        '''
#            if mass is a string assume its a moleculer weight key ie Ar40
#            else mass is a float like 39.962
#        '''
#
#        global pc_window_cnt
#        graph = Graph(window_title = 'Peak Centering',
#                              window_x = 175 + pc_window_cnt * 25,
#                              window_y = 25 + pc_window_cnt * 25,
#                              )
#        spec = self.manager.spectrometer
#
#        dac = spec.magnet.get_dac_for_mass(mass)
#        pc_window_cnt += 1
#
#        wnd = spec.pc_window
#        start = dac - wnd
#        end = dac + wnd
#        step_len = spec.pc_step_width
#
#        spec._peak_center_graph_factory(graph, start, end)
#        do_later(graph.edit_traits)
#
#        self.centering = True
#
#        sign = 1 if start < end else - 1
#        nsteps = abs(end - start + step_len * sign) / step_len
#        dac_values = np.linspace(start, end, nsteps)
#        self.dac_values = dac_values
#        self.peak_generator = psuedo_peak(dac, start, end, nsteps)
#
#        self.first = True
#        self.x = 0
#        self.gen = (i for i in dac_values)
#        self.intensities = []
#        self.peak_graph = graph
#        di = self.gen.next()
#
#        self.cfirst = True
#        self._peak_center_step(di)
