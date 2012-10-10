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
from traits.api import Any, Float, Event, Property, Bool
from traitsui.api import View, Item, ButtonEditor, HGroup, spring
#============= standard library imports ========================
from numpy import linspace, exp
import random
import time
#============= local library imports  ==========================
from spectrometer_task import SpectrometerTask
from globals import globalv

def psuedo_peak(center, start, stop, step, magnitude=500, peak_width=0.008):
    x = linspace(start, stop, step)
    gaussian = lambda x: magnitude * exp(-((center - x) / peak_width) ** 2)

    for i, d in enumerate(gaussian(x)):
        if abs(center - x[i]) < peak_width:
            d = magnitude + magnitude / 50.0 * random.random()
        yield d

class MagnetScan(SpectrometerTask):
    graph = Any

#    execute = Event
#    execute_label = Property(depends_on='_alive')
#    _alive = Bool

    start_mass = Float(36)
    stop_mass = Float(40)
    step_mass = Float(1)

    def _scan_dac(self, values, det, delay=850):

        graph = self.graph
        spec = self.spectrometer

        mag = spec.magnet
        mag.settling_time = 0.5
        if globalv.experiment_debug:
            delay = 1
            mag.settling_time = 0.001

        peak_generator = psuedo_peak(values[len(values) / 2] + 0.001, values[0], values[-1], len(values))

        do = values[0]
        mag.set_dac(do, verbose=False)
        time.sleep(delay / 1000.)

        intensity = spec.get_intensity(det)
        if globalv.experiment_debug:
            intensity = peak_generator.next()
        intensities = [intensity]

        if graph:
            graph.add_datum(
                            (do, intensity),
#                            update_y_limits=True,
                            do_after=1)

        for di in values[1:]:
            if not self.isAlive():
                break

            mag.set_dac(di, verbose=False)

            intensity = spec.get_intensity(det)

#            debug
            if globalv.experiment_debug:
                intensity = peak_generator.next()

            intensities.append(intensity)
            if graph:
                graph.add_datum(
                                (di, intensity),
                                update_y_limits=True,
                                do_after=1)

            time.sleep(delay / 1000.)

        return intensities

    def _execute(self):
        spec = self.spectrometer
        mag = spec.magnet
        sm = self.start_mass
        em = self.stop_mass
        stm = self.step_mass
        if abs(sm - em) > stm:
    #        ds = mag.calculate_dac(sm)
            ds = spec.correct_dac(self.detector,
                                  mag.map_mass_to_dac(sm))
            de = spec.correct_dac(self.detector,
                                  mag.map_mass_to_dac(em))


    #        de = mag.calculate_dac(em)
            massdev = abs(sm - em)
            dacdev = abs(ds - de)

            dacstep = stm / float(massdev) * dacdev

            values = self._calc_dacvalues(ds, de, dacstep)
            self._scan_dac(values, self.reference_detector.name)
            self._alive = False

    def _calc_dacvalues(self, start, end, width):
        sign = 1 if start < end else -1
        nsteps = abs(end - start + width * sign) / width

        return linspace(start, end, nsteps)

    def traits_view(self):
        v = View(Item('start_mass', label='Start'),
                 Item('stop_mass', label='Stop'),
                  Item('step_mass', label='Step'),
                  HGroup(spring, Item('execute', editor=ButtonEditor(label_value='execute_label'),
                        show_label=False))

                  )
        return v
#============= EOF =============================================
