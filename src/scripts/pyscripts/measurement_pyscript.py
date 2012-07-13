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
#============= standard library imports ========================
from pyscript import PyScript
import time
from src.scripts.pyscripts.pyscript import verbose_skip
#============= local library imports  ==========================




class MeasurementPyScript(PyScript):
    automated_run = Any
    _time_zero = None

    _series_count = 0
    _regress_id = 0
    def get_commands(self):
        cmds = super(MeasurementPyScript, self).get_commands()
        cmds += ['baselines', 'position', 'set_time_zero', 'peak_center',
                 'detectors', 'collect', 'regress', 'sniff',

                 'set_ysymmetry', 'set_zsymmetry', 'set_zfocus',
                 'set_extraction_lens', 'set_deflection'

                 ]
        return cmds

#===============================================================================
# commands
#===============================================================================
    @verbose_skip
    def sniff(self, ncounts):
        self.arun.do_sniff(ncounts,
                           self._time_zero,
                           series=self._series_count
                           )
        self._series_count += 1

    @verbose_skip
    def regress(self, kind):

        self.arun.regress(kind, series=self._regress_id)
        self._series_count += 3

    @verbose_skip
    def set_time_zero(self):
        self._time_zero = time.time()

    @verbose_skip
    def collect(self, ncounts=200, integration_time=1):
#        print 'cooooll', ncounts, self._time_zero, integration_time
        self.arun.do_data_collection(ncounts, self._time_zero,
                      series=self._series_count,
                      #update_x=True
                      )
        self._regress_id = self._series_count
        self._series_count += 1

    @verbose_skip
    def detectors(self, *dets):
        if dets:
            self.arun.activate_detectors(dets)

    @verbose_skip
    def baselines(self, ncounts, position=None, detector=None):
        '''
            if detector is not none then it is peak hopped
        '''
        self.arun.do_baselines(ncounts, self._time_zero,
                               position=position,
                               detector=detector,
                               series=self._series_count
                              )
        self._series_count += 1

    @verbose_skip
    def peak_center(self):
        self.arun.do_peak_center()

    @verbose_skip
    def position(self, pos, detector='AX'):
        arun = self.arun

        func = arun.set_magnet_position
        if isinstance(pos, str):
            dac = None
        else:
            dac = pos

        func(pos, detector=detector, dac=dac)

    @verbose_skip
    def set_ysymmetry(self, v):
        self.arun.set_spectrometer_parameter('SetYSymmetry', v)

    @verbose_skip
    def set_zsymmetry(self, v):
        self.arun.set_spectrometer_parameter('SetZSymmetry', v)

    @verbose_skip
    def set_zfocus(self, v):
        self.arun.set_spectrometer_parameter('SetZFocus', v)

    @verbose_skip
    def set_extraction_lens(self, v):
        self.arun.set_spectrometer_parameter('SetExtractionLens', v)

    @verbose_skip
    def set_deflection(self, detname, v):
        v = '{},{}'.format(detname, v)
        self.arun.set_spectrometer_parameter('SetDeflection', v)


#============= EOF =============================================
