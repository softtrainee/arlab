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
from traits.api import Any, on_trait_change
#============= standard library imports ========================
from pyscript import PyScript
import time
from src.pyscripts.pyscript import verbose_skip
import os
from src.paths import paths
import random
#============= local library imports  ==========================


class Detector(object):
    name = None
    mass = None
    signal = None
    def __init__(self, name, mass, signal):
        self.name = name
        self.mass = mass
        self.signal = signal

from traits.api import HasTraits, Button, Dict
from traitsui.api import View
class AutomatedRun(HasTraits):
    test = Button
    traits_view = View('test')
    signals = Dict
    def _test_fired(self):
        m = MeasurementPyScript(root=os.path.join(paths.scripts_dir, 'measurement'),
                            name='measureTest.py',
                            automated_run=self
                            )
        m.bootstrap()
    #    print m._text
        m.execute()

    def do_sniff(self, ncounts, *args, **kw):
        keys = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
        for i in range(ncounts):
            vals = [random.random() for _ in range(len(keys))]
            self.signals = dict(zip(keys, vals))
            time.sleep(0.1)

    def set_spectrometer_parameter(self, *args, **kw):
        pass
    def set_magnet_position(self, *args, **kw):
        pass
    def activate_detectors(self, *args, **kw):
        pass
    def do_data_collection(self, *args, **kw):
        pass

class MeasurementPyScript(PyScript):
    automated_run = Any
    _time_zero = None

    _series_count = 0
    _regress_id = 0

    _detectors = None
    def __init__(self, *args, **kw):
        super(MeasurementPyScript, self).__init__(*args, **kw)
        self._detectors = dict([(k, Detector(k, m, 0)) for k, m in
                              zip(['H2', 'H1', 'AX', 'L1', 'L2', 'CDD'],
                                  [40, 39, 38, 37, 36, 35])
                              ])

    def _get_detectors(self):
        return self._detectors
    detector = property(fget=_get_detectors)

    def get_script_commands(self):
        cmds = ['baselines', 'position', 'set_time_zero', 'peak_center',
                 'activate_detectors', 'collect', 'regress', 'sniff',

                 'set_ysymmetry', 'set_zsymmetry', 'set_zfocus',
                 'set_extraction_lens', 'set_deflection'

                 ]
        return cmds

    def get_variables(self):
        return ['detector']

    @on_trait_change('automated_run:signals')
    def update_signals(self, obj, name, old, new):
        try:
            det = self.detector
            for k, v in new.iteritems():
                det[k].signal = v
        except AttributeError:
            pass
#===============================================================================
# commands
#===============================================================================
    @verbose_skip
    def sniff(self, ncounts=0):
        if self.automated_run is None:
            return

        self.automated_run.do_sniff(ncounts,
                           self._time_zero,
                           series=self._series_count,

                           )
        self._series_count += 1

    @verbose_skip
    def regress(self, kind='linear'):
        if self.automated_run is None:
            return

        self.automated_run.regress(kind, series=self._regress_id)
        self._series_count += 3

    @verbose_skip
    def set_time_zero(self):
        self._time_zero = time.time()

    @verbose_skip
    def collect(self, ncounts=200, integration_time=1):
        if self.automated_run is None:
            return

#         print 'cooooll', ncounts, self._time_zero, integration_time
        self.automated_run.do_data_collection(ncounts, self._time_zero,
                      series=self._series_count,
                      #update_x=True
                      )
        self._regress_id = self._series_count
        self._series_count += 1

    @verbose_skip
    def activate_detectors(self, *dets):
        if self.automated_run is None:
            return

        if dets:
            self.automated_run.activate_detectors(list(dets))

    @verbose_skip
    def baselines(self, ncounts, position=None, detector=None):
        '''
            if detector is not none then it is peak hopped
        '''
        if self.automated_run is None:
            return

        self.automated_run.do_baselines(ncounts, self._time_zero,
                               position=position,
                               detector=detector,
                               series=self._series_count
                              )
        self._series_count += 1

    @verbose_skip
    def peak_center(self):
        if self.automated_run is None:
            return

        self.automated_run.do_peak_center()

    @verbose_skip
    def position(self, pos, detector='AX'):
        if self.automated_run is None:
            return

        func = self.automated_run.set_magnet_position
        if isinstance(pos, str):
            dac = None
        else:
            dac = pos

        func(pos, detector=detector, dac=dac)

    @verbose_skip
    def set_ysymmetry(self, v):
        if self.automated_run is None:
            return

        self.automated_run.set_spectrometer_parameter('SetYSymmetry', v)

    @verbose_skip
    def set_zsymmetry(self, v):
        if self.automated_run is None:
            return

        self.automated_run.set_spectrometer_parameter('SetZSymmetry', v)

    @verbose_skip
    def set_zfocus(self, v):
        if self.automated_run is None:
            return

        self.automated_run.set_spectrometer_parameter('SetZFocus', v)

    @verbose_skip
    def set_extraction_lens(self, v):
        if self.automated_run is None:
            return

        self.automated_run.set_spectrometer_parameter('SetExtractionLens', v)

    @verbose_skip
    def set_deflection(self, detname, v):
        if self.automated_run is None:
            return

        v = '{},{}'.format(detname, v)
        self.automated_run.set_spectrometer_parameter('SetDeflection', v)

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_test')
    logging_setup('m_pyscript')

    d = AutomatedRun()
    d.configure_traits()

#============= EOF =============================================