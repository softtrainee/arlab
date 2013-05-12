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
from traitsui.api import View
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#============= local library imports  ==========================
from src.machine_vision.machine_vision_manager import MachineVisionManager
from src.machine_vision.detectors.brightness_detector import BrightnessDetector
from threading import Thread


class BrightnessManager(MachineVisionManager):

    def _test_fired(self):
        t = Thread(target=self._test)
        t.start()
#        do_later(self._test)
    def _test(self):
        det = self.detector
        do_later(det.edit_traits)

        import time
        time.sleep(1)
        det.collect_baseline()

        while 1:
            do_later(det.get_value, verbose=False)
            time.sleep(0.25)

    def traits_view(self):
        return View('test')

#===============================================================================
# persistence
#===============================================================================
    def dump_detector(self):
        self._dump_detector('brightness_detector', self.detector)

    def load_detector(self):
        return self._load_detector('brightness_detector', BrightnessDetector)

    def collect_baseline(self, **kw):
        return self.detector.collect_baseline(**kw)

    def get_value(self, **kw):
        return self.detector.get_value(**kw)

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

#    from src.globals import globalv
#    globalv._test = False
    logging_setup('bm')
    b = BrightnessManager()
    b.configure_traits()

#============= EOF =============================================
