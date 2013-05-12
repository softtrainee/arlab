#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Any, Float, DelegatesTo
from traitsui.api import View, Item, EnumEditor, Group
#============= standard library imports ========================
from numpy import linspace, exp
import random
import time
#============= local library imports  ==========================
from spectrometer_task import SpectrometerTask
from src.globals import globalv

def psuedo_peak(center, start, stop, step, magnitude=500, peak_width=0.008):
    x = linspace(start, stop, step)
    gaussian = lambda x: magnitude * exp(-((center - x) / peak_width) ** 2)

    for i, d in enumerate(gaussian(x)):
        if abs(center - x[i]) < peak_width:
#            d = magnitude
            d = magnitude + magnitude / 50.0 * random.random()
        yield d

class MagnetScan(SpectrometerTask):
#    graph = Any
    detectors = DelegatesTo('spectrometer')
    reference_detector = Any
#    execute = Event
#    execute_label = Property(depends_on='_alive')
#    _alive = Bool

    start_mass = Float(36)
    stop_mass = Float(40)
    step_mass = Float(1)
#    title = 'Magnet Scan'
#    def _scan_dac(self, values, det, delay=850):
#
#        graph = self.graph
#        spec = self.spectrometer
#
#        mag = spec.magnet
#        mag.settling_time = 0.5
#        if globalv.experiment_debug:
#            delay = 1
#            mag.settling_time = 0.001
#
#        peak_generator = psuedo_peak(values[len(values) / 2] + 0.001, values[0], values[-1], len(values))
#
#        do = values[0]
#        mag.set_dac(do, verbose=False)
#        time.sleep(delay / 1000.)
#
#        intensity = spec.get_intensity(det)
#        if globalv.experiment_debug:
#            intensity = peak_generator.next()
#        intensities = [intensity]
#
# #        if graph:
# #            graph.add_datum(
# #                            (do, intensity),
# ##                            update_y_limits=True,
# #                            do_after=1)
#
#        for di in values[1:]:
#            if not self.isAlive():
#                break
#
#            mag.set_dac(di, verbose=False)
#
#            intensity = spec.get_intensity(det)
#
# #            debug
#            if globalv.experiment_debug:
#                intensity = peak_generator.next()
#
#            intensities.append(intensity)
#            if graph:
#                graph.add_datum(
#                                (di, intensity),
#                                update_y_limits=True,
#                                do_after=1)
#
#            time.sleep(delay / 1000.)
#
#        return intensities

    def _scan_dac(self, values, det, delay=850):

        spec = self.spectrometer

        mag = spec.magnet
        mag.settling_time = 0.5
        if globalv.experiment_debug:
            delay = 1
            mag.settling_time = 0.01

        peak_generator = psuedo_peak(values[len(values) / 2] + 0.001, values[0], values[-1], len(values))
        do = values[0]
        intensities = self._magnet_step_hook(do,
                                             delay=3,
                                             detector=det,
                                             peak_generator=peak_generator)
        self._graph_hook(do, intensities)
        rintensities = [intensities]

        delay = delay / 1000.
        for di in values[1:]:
            if not self.isAlive():
                break

            mag.set_dac(di, verbose=False)
            intensities = self._magnet_step_hook(di, det, delay=delay,
                                                 peak_generator=peak_generator)
            self._graph_hook(di, intensities, update_y_limits=True)

            rintensities.append(intensities)

#            time.sleep(delay / 1000.)

        return rintensities

    def _graph_hook(self, di, intensity, **kw):
        graph = self.graph
        if graph:
            graph.add_datum(
                            (di, intensity),
#                            update_y_limits=True,
                            do_after=1,
                            **kw
                            )

    def _magnet_step_hook(self, di, detector=None, peak_generator=None, delay=None):


        spec = self.spectrometer
        spec.magnet.set_dac(di, verbose=False)
        if delay:
            time.sleep(delay)
        intensity = spec.get_intensity(detector)

#            debug
        if globalv.experiment_debug:
            intensity = peak_generator.next()

        return intensity

    def _execute(self):
        sm = self.start_mass
        em = self.stop_mass
        stm = self.step_mass
        if abs(sm - em) > stm:
    #        ds = mag.calculate_dac(sm)
            self._do_scan(sm, em, stm)
            self._alive = False
            self._post_execute()

    def _do_scan(self, sm, em, stm, directions=None, map_mass=True):
        # default to forward scan
        if directions is None:
            directions = [1]
        elif isinstance(directions, str):
            if directions == 'Decrease':
                directions = [-1]
            elif directions == 'Oscillate':
                def oscillate():
                    i = 0
                    while 1:
                        if i % 2 == 0:
                            yield 1
                        else:
                            yield -1
                        i += 1
                directions = oscillate()
            else:
                directions = [1]

        spec = self.spectrometer
        mag = spec.magnet
        if map_mass:
            ds = spec.correct_dac(self.reference_detector,
                                      mag.map_mass_to_dac(sm))
            de = spec.correct_dac(self.reference_detector,
                                  mag.map_mass_to_dac(em))


#        de = mag.calculate_dac(em)
            massdev = abs(sm - em)
            dacdev = abs(ds - de)

            stm = stm / float(massdev) * dacdev
            sm, em = ds, de

        for di in directions:
            if not self._alive:
                return

            if di == -1:
                sm, em = em, sm
            values = self._calc_step_values(sm, em, stm)
            if not self._scan_dac(values, self.reference_detector):
                return

        return True

    def _post_execute(self):
        pass

    def _reference_detector_default(self):
        return self.detectors[0]

    def traits_view(self):
        v = View(
                 Group(
                       Item('reference_detector', editor=EnumEditor(name='detectors')),
                       Item('start_mass', label='Start'),
                       Item('stop_mass', label='Stop'),
                       Item('step_mass', label='Step'),
                       label='Magnet Scan',
                       show_border=True
                       )
#                 buttons=['OK', 'Cancel'],
#                 title=self.title
#                  HGroup(spring, Item('execute', editor=ButtonEditor(label_value='execute_label'),
#                        show_label=False))

                  )
        return v

#============= EOF =============================================
