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
from traits.api import Any
from traitsui.api import View, Item, TableEditor, ButtonEditor
from src.spectrometer.tasks.spectrometer_task import SpectrometerTask
import os
from src.paths import paths
import ConfigParser
#============= standard library imports ========================
#============= local library imports  ==========================


class RelativeDetectorPositions(SpectrometerTask):
    ion_optics_manager = Any
    def _execute(self):
        self.info('starting relative positions calculation')
        ion = self.ion_optics_manager
        #peak center on the axial detector
        t = ion.do_peak_center('AX', 'Ar36', save=False)
        t.join()

        axial_dac = ion.peak_center_result
        if axial_dac is not None:

            rps = []
            #peak center on all detectors
            for d in self.spectrometer.detectors:
                if not self.isAlive():
                    self.info('canceling relative detector position calculation')
                    break
                if d.name is not 'AX':
                    t = ion.do_peak_center(d.name, 'Ar36', save=False)
                    t.join()
                    if ion.peak_center_result is None:
                        self.info('canceling relative detector position calculation')
                        break

                    rp = ion.peak_center_result / axial_dac
                    d.relative_position = rp
                    rps.append((d.name, rp))
                    self.info('calculated relative position {} to AX = {}'.format(d.name, rp))

            else:
                self.info('finished calculating relative detector positions')

                config = ConfigParser.ConfigParser()
                p = os.path.join(paths.spectrometer_dir, 'detectors.cfg')
                config.read(p)
                for name, rp in rps:
                    self.info('{}={:0.6f}'.format(name, rp))
                    config.set(name, 'relative_position', rp)

                with open(p, 'w') as f:
                    config.write(f)
    def _end(self):
        self.ion_optics_manager.cancel_peak_center()

    def traits_view(self):
        return View(Item('execute', editor=ButtonEditor(label_value='execute_label')),
                    resizable=True
                    )
#============= EOF =============================================
