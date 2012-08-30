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
from src.paths import paths
import os
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.helpers.filetools import unique_dir

DETECTOR_ORDER = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
debug = False




class Spectrometer(SpectrometerDevice):
    regressor = Instance(Regressor, ())
    magnet = Instance(Magnet, ())
    source = Instance(Source, ())

    detectors = List(Detector)
#    detectors = Property(List, depends_on='_detectors')
#    _detectors = Dict()
#    detector_names = Dict

    microcontroller = Any
    integration_time = Enum(0.065536, 0.131072, 0.262144, 0.524288,
                            1.048576, 2.097152, 4.194304, 8.388608,
                            16.777216, 33.554432, 67.108864)

    reference_detector = Str('H1')

    magnet_dac = DelegatesTo('magnet', prefix='dac')
#    _magnet_dac = DelegatesTo('magnet', prefix='_dac')

    magnet_dacmin = DelegatesTo('magnet', prefix='dacmin')
    magnet_dacmax = DelegatesTo('magnet', prefix='dacmin')

    current_hv = DelegatesTo('source')
    scan_timer = None

    databuffer = String

    molecular_weight = Str('Ar40')
    sub_cup_configurations = List

    sub_cup_configuration = Property(depends_on='_sub_cup_configuration')
    _sub_cup_configuration = Str

#    peak_center_results = None
#    data_manager = Instance(CSVDataManager, ())

    dc_start = Int(0)
    dc_stop = Int(500)
    dc_step = Int(50)
    dc_stepmin = Int(1)
    dc_stepmax = Int(1000)
    dc_threshold = Int(3)
    dc_npeak_centers = Int(3)

#    pc_window_cnt = 0
#    pc_window = Float(0.015)
#    pc_step_width = Float(0.0005)

    _alive = False

    peak_center_graph = None
    def set_parameter(self, name, v):
        cmd = '{} {}'.format(name, v)
        self.microcontroller.ask(cmd)

    def set_microcontroller(self, m):
        self.magnet.microcontroller = m
        self.source.microcontroller = m
        self.microcontroller = m
        for d in self.detectors:
            d.microcontroller = m

    def get_detector(self, name):
        return next((det for det in self.detectors if det.name == name), None)
#    def get_hv_correction(self, current=False):
#        cur = self.source.current_hv
#        if current:
#            cur = self.source.read_hv()
#
#        if cur is None:
#            cor = 1
#        else:
#            cor = self.source.nominal_hv / cur
#        return cor

#    def get_relative_detector_position(self, det):
#        '''
#            return position relative to ref detector in dac space
#        '''
#        if det is None:
#            return 0
#        else:
#            return 0

#    def set_magnet_position(self, pos, detector=None):
#        #calculate the dac value for pos is on the reference detector
#        #the mftable should be set to the ref detector
#        dac = self.magnet.calculate_dac(pos)
#
#        #correct for detector
#        #calculate the dac so that this position is shifted onto the given
#        #detector. 
##        dac += self.get_detector_position(detector)
#
#        #correct for deflection
#        self.magnet.dac = dac
#
#        #correct for hv
#        dac *= self.get_hv_correction(current=True)

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




#    def scan_dac(self, dac_values, graph):
#        period = self.integration_time
#        if self.simulation:
#            period = 0.05
#
#        gen = (i for i in dac_values)
#
#
#        #move to first position and delay 
#        self.magnet.set_dac(gen.next())
#        time.sleep(2)
#
#        while 1:
#            if not self.isAlive():
#                break
#            try:
#                dac = gen.next()
#                self.magnet.set_dac(dac)
#                time.sleep(period)
#
#                data = self.get_intensities()
#                if self.simulation:
#                    intensity = self.peak_generator.next()
#
#                if data is not None:
##                    if self.simulation:
##                        intensity = self.peak_generator.next()
##                    else:
#
#                    intensity = data[DETECTOR_ORDER.index(self.reference_detector)][1]
##                print intensity, self.reference_detector
#                self.intensities.append(intensity)
#                graph.add_datum(
#                                (dac, intensity),
#                                update_y_limits=True,
#                                do_after=1)
##                do_after(1, graph.add_datum, (dac, intensity), update_y_limits=True)
#
#            except StopIteration:
#                break

#    def calculate_peak_center(self, x, y):
#        peak_threshold = self.dc_threshold
#
#        peak_percent = 0.5
#        x = np.array(x)
#        y = np.array(y)
#
#        ma = np.max(y)
#
#        if ma < peak_threshold:
#            self.warning('No peak greater than {}. max = {}'.format(peak_threshold, ma))
#            return
#
#        cindex = np.where(y == ma)[0][0]
#        mx = x[cindex]
#        my = ma
#        #look backward for point that is peak_percent% of max
#        for i in range(cindex, cindex - 50, -1):
#            #this prevent looping around to the end of the list
#            if i < 0:
#                self.warning('PeakCenterError: could not find a low pos')
#                return
#
#            try:
#                if y[i] < (ma * peak_percent):
#                    break
#            except IndexError:
#                '''
#                could not find a low pos
#                '''
#                self.warning('PeakCenterError: could not find a low pos')
#                return
#
#        lx = x[i]
#        ly = y[i]
#
#        #look forward for point that is 80% of max
#        for i in range(cindex, cindex + 50, 1):
#            try:
#                if y[i] < (ma * peak_percent):
#                    break
#            except IndexError:
#                '''
#                    could not find a high pos
#                '''
#                self.warning('PeakCenterError: could not find a high pos')
#                return
#
#        hx = x[i]
#        hy = y[i]
#
#        cx = (hx + lx) / 2.0
#        cy = ma
#
#        cindex = i - 5
#        #check to see if were on a plateau
#        yppts = y[cindex - 2:cindex + 2]
#        rdict = self.regressor.linear(range(len(yppts)), yppts)
#        std = rdict['statistics']['stddev']
#        slope = rdict['coefficients'][0]
#
#        if std > 5 and abs(slope) < 1:
#            self.warning('No peak plateau std = {} slope = {}'.format(std, slope))
#            return
#        else:
#            self.info('peak plateau std = {} slope = {}'.format(std, slope))
#        return [lx, cx, hx ], [ly, cy, hy], [mx], [my]

#===============================================================================
# factories
#===============================================================================
    def _timer_factory(self):
        mult = 1000

        self.scan_timer = Timer((self.integration_time + 0.025) * mult, self.get_intensities)
        self.scan_timer.Start()



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
#        self.detector_names = {'H2':'1:H2', 'H1':'2:H1',
#                                'AX':'3:AX',
#                                'L1':'4:L1', 'L2':'5:L2',
#                                 'CDD':'6:CDD'}
##        self.reference_detector = 'AX'

#        self._detectors = dict(H2=Detector(name='H2', relative_position=1.2, active=True),
#                              H1=Detector(name='H1', relative_position=1.1, active=True),
#                              AX=Detector(name='AX', relative_position=1, active=True),
#                              L1=Detector(name='L1', relative_position=0.9, active=True),
#                              L2=Detector(name='L2', relative_position=0.8, active=True),
#                              CDD=Detector(name='CDD', relative_position=0.7, active=False),
#                              )
        self.detectors = [Detector(name='H2', color='black', relative_position=1.2, active=True, isotope='Ar41'),
                          Detector(name='H1', color='red', relative_position=1.1, active=True, isotope='Ar40'),
                          Detector(name='AX', color='violet', relative_position=1, active=True, isotope='Ar39'),
                          Detector(name='L1', color='maroon', relative_position=0.9, active=True, isotope='Ar38'),
                          Detector(name='L2', color='yellow', relative_position=0.8, active=True, isotope='Ar37'),
                          Detector(name='CDD', color='lime green', relative_position=0.7, active=False, isotope='Ar36')]

        self.magnet.load()
#===============================================================================
# signals
#===============================================================================
    def get_intensities(self, record=True, tagged=True):
        if not self.microcontroller:
            return

        datastr = self.microcontroller.ask('GetData', verbose=False)
#        keys = []
        signals = []
        if datastr:
            if not 'ERROR' in datastr:
                try:
                    data = [float(d) for d in datastr.split(',')]
                except:

                    if tagged:
                        data = [d for d in datastr.split(',')]

                        keys = [data[i] for i in range(0, len(data), 2)]
                        signals = map(float, [data[i + 1] for i in range(0, len(data), 2)])
#
#                        for i in range(0, len(data), 2):
#                            keys.append(data[i])
#                            signals.append(float(data[i + 1]))
        else:
            signals = [5 + random.random() for _i in range(6)]
            if tagged:
                keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']

        return keys, signals
#        if not tagged:
#            #update the detector current value
##            for det, dat in zip(self.detectors, data):
##
##                if det.active:
##                    det.intensity = dat
##                else:
##                    det.intensity = 0
#            rdata = data
#        else:
#            return []
#            data = []
#            rdata = []
#            for det in self.detectors:
#                sig = 0
#                if det.name in keys:
#                    sig = signals[keys.index(det.name)]
#                rdata.append(sig)
#                data.append((det.name, sig))
#
#        if record:
#            self.databuffer = ','.join([str(yi) for yi in rdata])

#        return data

    def get_intensity(self, key):

#        index = DETECTOR_ORDER.index(key)
        data = self.get_intensities()
        if data is not None:
            keys, signals = data
            return signals[keys.index(key)]

#        return data
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
