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
from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager

#============= standard library imports ========================

#============= local library imports  ==========================
SPECTROMETER_PROTOCOL = 'src.spectrometer.spectrometer_manager.SpectrometerManager'
ION_OPTICS_PROTOCOL = 'src.spectrometer.ion_optics_manager.IonOpticsManager'
SCAN_PROTOCOL = 'src.spectrometer.scan_manager.ScanManager'
def get_manager(event, protocol):
    app = event.window.application
    manager = app.get_service(protocol)
    return manager

class OpenIonOpticsAction(Action):
    def perform(self, event):
        man = get_manager(event, ION_OPTICS_PROTOCOL)
        open_manager(event.window.application, man)

class OpenScanManagerAction(Action):
    accelerator = 'Ctrl+D'
    def perform(self, event):
        man = get_manager(event, SCAN_PROTOCOL)
        open_manager(event.window.application, man)

#class MagFieldCalibrationAction(Action):
#    description = 'Update the magnetic field calibration table'
#    def perform(self, event):
#        app = event.window.application
#
#        manager = app.get_service(SPECTROMETER_PROTOCOL)
#        manager.peak_center(update_mftable=True)
#
class PeakCenterAction(Action):
    description = 'Calculate peak center'

    def __init__(self, *args, **kw):
        super(PeakCenterAction, self).__init__(*args, **kw)
        man = self.window.workbench.application.get_service(ION_OPTICS_PROTOCOL)
        man.on_trait_change(self._update_enabled, 'alive')
        self.enabled = True

    def _update_enabled(self, new):
        self.enabled = not self.enabled

    def perform(self, event):
        man = get_manager(event, ION_OPTICS_PROTOCOL)
        man.do_peak_center(confirm_save=True)
#        man.open_peak_center()

class RelativePositionsAction(Action):
    def perform(self, event):
        man = get_manager(event, SPECTROMETER_PROTOCOL)
        obj = man.relative_detector_positions_task_factory()
        open_manager(event.window.application, obj)
#============= EOF ====================================
