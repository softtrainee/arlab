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
from traits.api import String, Instance, Int, Property, List, Dict, Any, Enum, Str, DelegatesTo, Float
from traitsui.api import View, Item, VGroup, EnumEditor, RangeEditor
from pyface.timer.api import Timer, do_later, do_after
#from pyface.timer.do_later import do_later

#============= standard library imports ========================
import numpy as np
import time
import random
from threading import Thread

#============= local library imports  ==========================
from src.data_processing.regression.regressor import Regressor
from src.spectrometer.source import Source
from src.spectrometer.magnet import Magnet
from src.spectrometer.detector import Detector
from src.spectrometer.molecular_weights import MOLECULAR_WEIGHTS, MOLECULAR_WEIGHT_KEYS
from src.graph.graph import Graph
from src.spectrometer.spectrometer_device import SpectrometerDevice
from src.graph.regression_graph import RegressionGraph
from src.helpers.paths import data_dir
import os
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.helpers.filetools import unique_dir

DETECTOR_ORDER = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
debug = False

def psuedo_peak(center, start, stop, step, magnitude=500, peak_width=0.002):
    x = np.linspace(start, stop, step)
    gaussian = lambda x: magnitude * np.exp(-((center - x) / peak_width) ** 2)

    for i, d in enumerate(gaussian(x)):
        if abs(center - x[i]) < 0.00125:
            d = magnitude + magnitude / 50.0 * random.random()
        yield d


class Spectrometer(SpectrometerDevice):
    regressor = Instance(Regressor, ())
    magnet = Instance(Magnet, ())
    source = Instance(Source, ())
    detectors = Property(List, depends_on='_detectors')
    _detectors = Dict()
    detector_names = Dict

    microcontroller = Any
    integration_time = Enum(0.065536, 0.131072, 0.262144, 0.524288,
                            1.048576, 2.097152, 4.194304, 8.388608,
                            16.777216, 33.554432, 67.108864)

    reference_detector = Str('H1')
    magnet_dac = DelegatesTo('magnet')
    _magnet_dac = DelegatesTo('magnet')

    magnet_dacmin = DelegatesTo('magnet')
    magnet_dacmax = DelegatesTo('magnet')

    current_hv = DelegatesTo('source')
    scan_timer = None

    databuffer = String

    molecular_weight = Str('Ar40')
    sub_cup_configurations = List

    sub_cup_configuration = Property(depends_on='_sub_cup_configuration')
    _sub_cup_configuration = Str

    peak_center_results = None
    data_manager = Instance(CSVDataManager, ())

    dc_start = Int(0)
    dc_stop = Int(500)
    dc_step = Int(50)
    dc_stepmin = Int(1)
    dc_stepmax = Int(1000)
    dc_threshold = Int(3)
    dc_npeak_centers = Int(3)

    pc_window_cnt = 0
    pc_window = Float(0.015)
    pc_step_width = Float(0.0005)


    _alive = False

    peak_center_graph = None

    def deflection_calibration(self):
        self.info('Deflection Calibration')

        #load an air shot

#        ec = ExtractionLineScript(source_dir = os.path.join(scripts_dir, 'extraction_scripts'),
#                                  file_name = 'air_shot.rs'
#                                  )

        #ec.bootstrap()
        #ec.join()

        self._alive = True
#        for det , mass in [('H2', 'Ar38'), ('H1', 'Ar39'), ('AX', 'Ar40'), ('L1', 41), ('L2', 42)]:
#        for det , mass in [('H2', 'Ar38'), ('H1', 'Ar39'), ('AX', 'Ar40'), ('L1', 41), ('L2', 42)]:
#        for det , mass in [('L1', 'PM41'), ('H2', 'Ar38')]:#, ('L1', 40.9), ('L2', 41.8)]:
        #for det, mass in [('H2', 'Ar38')]:
        for det, mass in [('CDD', 'Ar39')]:
            '''
                 use mftable to calculate the nominal center_pos
                 
                 other option is to just find these values using qtegra empirically
                 
                 ie jump to mass 
                 
            '''
            if not self.isAlive():
                break
            self.reference_detector = det
            self.molecular_weight = mass
            self.cup_deflection_calibration(mass)

    def cup_deflection_calibration(self, mass):

        self.info('{} deflection calibration'.format(self.reference_detector))

        rgraph = RegressionGraph(window_x=100,
                                window_y=50)
        rgraph.new_plot()
        rgraph.new_series(yer=[])

        root_dir = unique_dir(os.path.join(data_dir, 'magfield'), '{}_def_calibration'.format(self.reference_detector))
#        if not os.path.exists(root_dir):
#            os.mkdir(root_dir)

        dm = self.data_manager

        p = os.path.join(root_dir, 'defl_vs_dac.csv')
        deflection_frame_key = dm.new_frame(path=p)

        dm.write_to_frame(['Deflection (V)', '40{} DAC'.format(self.reference_detector)],
                          frame_key=deflection_frame_key)

        start = self.dc_start
        stop = self.dc_stop
        width = self.dc_step
        nstep = (stop - start) / width + 1

        npeak_centers = self.dc_npeak_centers
        self.info('Deflection scan parameters start={}, stop={}, stepwidth={}, nstep={}'.format(start, stop, width, nstep))
        self.info('Reference detector {}'.format(self.reference_detector))
        self.info('Peak centers per step n={}'.format(npeak_centers))

        for i, ni in enumerate(np.linspace(start, stop, nstep)):
            if not self.isAlive():
                break
            self.info('Deflection step {} {} (V)'.format(i + 1, ni))
            self._detectors[self.reference_detector].deflection = ni
            ds = []
            for n in range(npeak_centers):
                if not self.isAlive():
                    break
                self.info('Peak center ni = {}'.format(n + 1))

                p = os.path.join(root_dir, 'peak_scan_{:02n}_{:02n}.csv'.format(int(ni), n))
                dm.new_frame(path=p)
                dm.write_to_frame(['DAC (V)', 'Intensity (fA)'])

                graph = Graph(window_title='Peak Centering',
                              window_x=175 + i * 25 + n * 5,
                              window_y=25 + i * 25 + n * 5
                              )

                self.peak_center(graph=graph,
                                  update_mftable=True,
                                  update_pos=False,
                                  center_pos=mass
                                  )

                if self.isAlive():
                    #write scan to file
                    dm.write_to_frame(zip(graph.get_data(), graph.get_data(axis=1)))

                    if npeak_centers > 1:
                        if not self.simulation:
                            time.sleep(1)

                    if self.peak_center_results:
                        d = (ni, self.peak_center_results[0][1])
                        ds.append(self.peak_center_results[0][1])
                        dm.write_to_frame(list(d), frame_key=deflection_frame_key)

                        #write the centering results to the centering file
                        dm.write_to_frame([('#{}'.format(x), y) for x, y in  zip(graph.get_data(series=1), graph.get_data(series=1, axis=1))])

            if self.peak_center_results:
                rgraph.add_datum((ni, np.mean(ds), np.std(ds)))

            if i == 2:
                do_later(rgraph.edit_traits)

            #delay so we can view graph momonetarily
            if not self.simulation and self.isAlive():
                time.sleep(2)

        self.info('deflection calibration finished')

    def set_microcontroller(self, m):
        self.magnet.microcontroller = m
        self.source.microcontroller = m
        self.microcontroller = m
        for d in self._detectors.itervalues():
            d.microcontroller = m

    def get_hv_correction(self, current=False):
        cur = self.source.current_hv
        if current:
            cur = self.source.read_hv()
        return self.source.nominal_hv / cur

    def set_magnet_position(self, v, dac=None):
        #get the detector we are aiming for
#        _target_det = self._detectors[self.reference_detector]
#        get position relative to axial
#        rp = target_det.relative_position
        #convert to axial space
        #x = v / rp
        #adjust to the for HV
        hv_correction = self.get_hv_correction()

        #need to adjust for the steering voltage on this detector
#        sv = target_det.steering_voltage

        self.magnet.set_axial_mass(v, hv_correction, dac=dac)
#===============================================================================
# change handlers
#===============================================================================
    def _molecular_weight_changed(self):
        self.set_magnet_position(MOLECULAR_WEIGHTS[self.molecular_weight])

#    def _integration_time_changed(self):
#        if self.microcontroller:
#            self.microcontroller.ask('SetIntegrationTime {}'.format(self.integration_time))
#            self.reset_scan_timer()

#===============================================================================
# timers
#===============================================================================

    def reset_scan_timer(self):
        if self.scan_timer is not None:
            self.scan_timer.Stop()
        self._timer_factory()

    def stop(self):
        if self._alive == True:
            self.info('Calibration canceled by user')
            self._alive = False
            return False
        else:
            self._alive = False
            return True
#        if self.centering_timer and self.centering_timer.IsRunning():
#            self.centering_timer.Stop()
#            self.info('Peak centering stopped by user')
#            self._timer_factory()
#        else:
#            return True
#===============================================================================
# peak centering
#===============================================================================
    def isAlive(self):
        return self._alive


    def peak_center(self, update_mftable=False, graph=None, update_pos=True, center_pos=None):
        '''
            default is to set position by mass
            if mass is a str it needs to be a mol wt key ie Ar40
            else should be float ie 39.962
        '''
        self.peak_center_results = None
        self.info('Peak center')
        if graph is None:
            if self.peak_center_graph is None:
                graph = Graph(window_title='Peak Centering',
                              window_x=300 + self.pc_window_cnt * 25,
                              window_y=25 + self.pc_window_cnt * 25
                              )
                self.pc_window_cnt += 1
                self.peak_center_graph = graph
            else:
                graph = self.peak_center_graph

        graph.close()
        graph.clear()
        do_later(graph.edit_traits)

#        else:
#            graph.clear()
#            graph.close()

        #graph.edit_traits()
        '''
            center pos needs to be ne axial dac units now
        '''

        if isinstance(center_pos, str):
            '''
                passing in a mol weight key ie Ar40
                get_dac_for_mass can take a str or a float 
                if str assumes key else assumes mass
            '''
            center_pos = self.magnet.get_dac_for_mass(center_pos)

        if center_pos is None:
            #center at current position
            m = self.magnet.read_dac()
            if isinstance(m, str) and 'ERROR' in m:
                m = 6.01
        else:
            m = center_pos

        ntries = 2
        success = False
        result = None

        for i in range(ntries):
            if not self.isAlive():
                break
            wnd = self.pc_window

            start = m - wnd * (i + 1)
            end = m + wnd * (i + 1)
            self.info('Scan parameters center={} start={} end={} step width={}'.format(m, start, end, self.pc_step_width))

            self._peak_center_graph_factory(graph, start, end)

            width = self.pc_step_width
            try:
                if self.simulation:
                    width = 0.001
            except AttributeError:
                width = 0.001

            self.intensities = []
            sign = 1 if start < end else -1
            nsteps = abs(end - start + width * sign) / width
            dac_values = np.linspace(start, end, nsteps)
            self.peak_generator = psuedo_peak(m + 0.001, start, end, nsteps)

            if self.scan_timer and self.scan_timer.IsRunning():
                self.scan_timer.Stop()

            t = Thread(target=self.scan_dac, args=(dac_values, graph))
            t.start()
            t.join()

            self._timer_factory()
            if not self.isAlive():
                break

            result = self.finish_peak_center(graph, dac_values, self.intensities)
            if result is not None:
#                adjust the center position for nominal high voltage
                xs = result[0]
                refpos = xs[1] / self.get_hv_correction(current=True)

                if update_mftable:
#                    update the field table
                    self.magnet.update_mftable(self.molecular_weight, refpos)
                success = True
                break

        if not success:
            self.warning('Peak centering failed')
        elif update_pos:
#            force magnet update
            self.set_magnet_position(MOLECULAR_WEIGHTS[self.molecular_weight])


    def finish_peak_center(self, graph, dac_values, intensities, plotid=0):
        result = self.calculate_peak_center(dac_values, intensities)
        if result is not None:
            xs, ys, mx, my = result
            graph.set_data(xs, plotid=plotid, series=1)
            graph.set_data(ys, plotid=plotid, series=1, axis=1)

            graph.set_data(mx, plotid=plotid, series=2)
            graph.set_data(my, plotid=plotid, series=2, axis=1)

            graph.add_vertical_rule(xs[1])
            self.peak_center_results = result
#            xs = result[0]

            #adjust the center position for nominal high voltage
            refpos = xs[1] / self.get_hv_correction(current=True)
            self.info('''{} Peak center results
                                        current hv = {}  {}
                                        nominal hv = {}  {}'''.format(self.reference_detector,
                                                                      xs[1], self.source.current_hv,
                                                                      refpos, self.source.nominal_hv,
                                                                      ),
                       decorate=False
                       )


        return result

    def scan_dac(self, dac_values, graph):
        period = self.integration_time
        if self.simulation:
            period = 0.05

        gen = (i for i in dac_values)


        #move to first position and delay 
        self.magnet.set_dac(gen.next())
        time.sleep(2)

        while 1:
            if not self.isAlive():
                break
            try:
                dac = gen.next()
                self.magnet.set_dac(dac)
                time.sleep(period)

                data = self.get_intensities()
                if self.simulation:
                    intensity = self.peak_generator.next()

                if data is not None:
#                    if self.simulation:
#                        intensity = self.peak_generator.next()
#                    else:

                    intensity = data[DETECTOR_ORDER.index(self.reference_detector)][1]
#                print intensity, self.reference_detector
                self.intensities.append(intensity)
                graph.add_datum(
                                (dac, intensity),
                                update_y_limits=True,
                                do_after=1)
#                do_after(1, graph.add_datum, (dac, intensity), update_y_limits=True)

            except StopIteration:
                break

    def calculate_peak_center(self, x, y):
        peak_threshold = self.dc_threshold

        peak_percent = 0.5
        x = np.array(x)
        y = np.array(y)

        ma = np.max(y)

        if ma < peak_threshold:
            self.warning('No peak greater than {}. max = {}'.format(peak_threshold, ma))
            return

        cindex = np.where(y == ma)[0][0]
        mx = x[cindex]
        my = ma
        #look backward for point that is peak_percent% of max
        for i in range(cindex, cindex - 50, -1):
            #this prevent looping around to the end of the list
            if i < 0:
                self.warning('PeakCenterError: could not find a low pos')
                return

            try:
                if y[i] < (ma * peak_percent):
                    break
            except IndexError:
                '''
                could not find a low pos
                '''
                self.warning('PeakCenterError: could not find a low pos')
                return

        lx = x[i]
        ly = y[i]

        #look forward for point that is 80% of max
        for i in range(cindex, cindex + 50, 1):
            try:
                if y[i] < (ma * peak_percent):
                    break
            except IndexError:
                '''
                    could not find a high pos
                '''
                self.warning('PeakCenterError: could not find a high pos')
                return

        hx = x[i]
        hy = y[i]

        cx = (hx + lx) / 2.0
        cy = ma

        cindex = i - 5
        #check to see if were on a plateau
        yppts = y[cindex - 2:cindex + 2]
        rdict = self.regressor.linear(range(len(yppts)), yppts)
        std = rdict['statistics']['stddev']
        slope = rdict['coefficients'][0]

        if std > 5 and abs(slope) < 1:
            self.warning('No peak plateau std = {} slope = {}'.format(std, slope))
            return
        else:
            self.info('peak plateau std = {} slope = {}'.format(std, slope))
        return [lx, cx, hx ], [ly, cy, hy], [mx], [my]

#===============================================================================
# factories
#===============================================================================
    def _timer_factory(self):
        mult = 1000

        self.scan_timer = Timer((self.integration_time + 0.025) * mult, self.get_intensities)
        self.scan_timer.Start()

    def _peak_center_graph_factory(self, graph, start, end, title=''):
        graph.container_dict = dict(padding=[10, 0, 30, 10])
        graph.clear()
        graph.new_plot(title='{}'.format(title),
                       xtitle='DAC (V)',
                       ytitle='Intensity (fA)',
                       )

        graph.new_series(type='scatter', marker='circle',
                         marker_size=1.25
                         )
        graph.new_series(type='scatter', marker='circle',
                         marker_size=4
                         )
        graph.new_series(type='scatter', marker='circle',
                         marker_size=4,
                         color='green'
                         )

        graph.plots[0].value_range.tight_bounds = False
        graph.set_x_limits(min=min(start, end), max=max(start, end))

#===============================================================================
# property get/set
#===============================================================================

    def _get_detectors(self):
        ds = []
        for di in DETECTOR_ORDER:
            ds.append(self._detectors[di])
        return ds

    def _get_sub_cup_configuration(self):
        return self._sub_cup_configuration

    def _set_sub_cup_configuration(self, v):
        self._sub_cup_configuration = v
        self.microcontroller.ask('SetSubCupConfiguration {}'.format(v))

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        pc_group = VGroup(Item('pc_window', label='Window'),
                        Item('pc_step_width', label='Step'),
                        show_border=True,
                        label='Peak Center'
                        )
        dc_group = VGroup(Item('dc_threshold', label='Threshold (fA)'),
                          Item('dc_start', label='Start'),
                        Item('dc_stop', label='Stop'),
                        Item('dc_step', label='Step', editor=RangeEditor(
                                                                             low_name='dc_stepmin',
                                                                             high_name='dc_stepmax',
                                                                             mode='spinner')),
                        Item('dc_npeak_centers', label='NPeak Centers', editor=RangeEditor(
                                                                             low_name='dc_stepmin',
                                                                             high_name='dc_stepmax',
                                                                             mode='spinner')),
                        show_border=True,
                        label='Steering Calibration'
                        )
        v = View(
                Item('integration_time'),
                Item('molecular_weight', editor=EnumEditor(values=MOLECULAR_WEIGHT_KEYS)),
                Item('sub_cup_configuration', show_label=False,
                     editor=EnumEditor(values=self.sub_cup_configurations)),
                Item('reference_detector', show_label=False, style='custom',
                                            editor=EnumEditor(
                                                               values=self.detector_names,
                                                               cols=len(self.detector_names)
                                                               )),
                Item('magnet_dac', editor=RangeEditor(low_name='magnet_dacmin',
                                                      high_name='magnet_dacmax',
                                                      mode='slider'
                                                      )),
                pc_group,
                dc_group
                )
        return v

#===============================================================================
# load
#===============================================================================
    def load_configurations(self):
        self.sub_cup_configurations = ['A', 'B', 'C']
        self._sub_cup_configuration = 'B'
        if self.microcontroller is not None:

            scc = self.microcontroller.ask('GetSubCupConfigurationList Argon', verbose=False)
            if scc:
                if 'ERROR' not in scc:
                    self.sub_cup_configurations = scc.split('\r')

            n = self.microcontroller.ask('GetActiveSubCupConfiguration')
            if n:
                if 'ERROR' not in n:
                    self._sub_cup_configuration = n

        self.molecular_weight = 'Ar40'

    def load(self):
        self.detector_names = {'H2':'1:H2', 'H1':'2:H1',
                                'AX':'3:AX',
                                'L1':'4:L1', 'L2':'5:L2',
                                 'CDD':'6:CDD'}
#        self.reference_detector = 'AX'

        self._detectors = dict(H2=Detector(name='H2', relative_position=1.2, active=True),
                              H1=Detector(name='H1', relative_position=1.1, active=True),
                              AX=Detector(name='AX', relative_position=1, active=True),
                              L1=Detector(name='L1', relative_position=0.9, active=True),
                              L2=Detector(name='L2', relative_position=0.8, active=True),
                              CDD=Detector(name='CDD', relative_position=0.7, active=False),
                              )

        self.magnet.load()
#===============================================================================
# signals
#===============================================================================
    def get_intensities(self, record=True, tagged=True):
        if not self.microcontroller:
            return

        datastr = self.microcontroller.ask('GetData', verbose=False)
        keys = []
        signals = []
        if not 'ERROR' in datastr:
            try:
                data = [float(d) for d in datastr.split(',')]
            except:

                if tagged:
                    data = [d for d in datastr.split(',')]
                    for i in range(0, len(data), 2):
                        keys.append(data[i])
                        signals.append(float(data[i + 1]))

        else:
            data = [5 + random.random() for _i in range(6)]

        if not tagged:
            #update the detector current value
            for det, dat in zip(self.detectors, data):

                if det.active:
                    det.intensity = dat
                else:
                    det.intensity = 0
            rdata = data
        else:
            data = []
            rdata = []
            for det in self.detectors:
                sig = 0
                if det.name in keys:
                    sig = signals[keys.index(det.name)]
                rdata.append(sig)
                data.append((det.name, sig))

        if record:
            self.databuffer = ','.join([str(yi) for yi in rdata])

        return data

    def get_intensity(self, key):

        index = DETECTOR_ORDER.index(key)
        data = self.get_intensities()
        if data is not None:
            data = data[index]

        return data
#============= EOF =============================================
#    def _peak_center_scan_step(self, di, graph, plotid, cond):
##       3print cond
#        if self.first:
#            self.first = False
#            x = di
#            cond.acquire()
#        else:
#            x = self.x
#        data = self.get_intensities()
#        if data is not None:
#            if self.simulation:
#                intensity = self.peak_generator.next()
#            else:
#                intensity = data[DETECTOR_ORDER.index(self.reference_detector)]
#
#            self.intensities.append(intensity)
#            graph.add_datum((x, intensity), plotid = plotid, update_y_limits = True)
#
#        try:
#            x = self.gen.next()
#        except StopIteration:
#            try:
#                cond.notify()
#                cond.release()
#            finally:
#                raise StopIteration
#
#        self.x = x
#        self.magnet.set_dac(x)
#    def _peak_center(self, graph, update_mftable, update_pos, center_pos):

#    def _peak_center_scan(self, start, end, step_len, graph, ppc = 40, plotid = 0):
#
#        #stop the scan timer and use peak scan timer
#        self.intensities = []
#        sign = 1 if start < end else - 1
#        nsteps = abs(end - start + step_len * sign) / step_len
#        dac_values = np.linspace(start, end, nsteps)
#        self.peak_generator = psuedo_peak(ppc, start, end, nsteps)
#
#        self.first = True
#        self.x = 0
#        self.gen = (i for i in dac_values)
#        period = self.integration_time * 1000
#        if self.simulation:
#            period = 150
#
#        #do first dac move
##        di = self.gen.next()
##        self.magnet.set_dac(di)
##        time.sleep(2)
#
#        if self.scan_timer.IsRunning():
#            self.scan_timer.Stop()

#        t = Thread(target = self.scan, args = (dac_values, graph))
#        t.start()
#        t.join()
#===============================================================================
# old
#===============================================================================
#        if self.condition is None:
#            cond = Condition()
#        with cond:
#            if self.centering_timer is not None:
#                self.centering_timer.Stop()
#
#            self.centering_timer = Timer(period, self._peak_center_scan_step, di, graph, plotid, cond)
#            self.centering_timer.Start()
#
#            cond.wait()
#===============================================================================
# old end
#===============================================================================

        #restart the scan timer
#        self._timer_factory()
#
#        return self.finish_peak_center(graph, dac_values, self.intensities)
