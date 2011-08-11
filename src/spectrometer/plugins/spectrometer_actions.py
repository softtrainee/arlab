#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================
SPECTROMETER_PROTOCOL = 'src.managers.spectrometer_manager.SpectrometerManager'
class MagFieldCalibrationAction(Action):
    description = 'Update the magnetic field calibration table'
    def perform(self, event):
        app = event.window.application

        manager = app.get_service(SPECTROMETER_PROTOCOL)
        manager.peak_center(update_mftable = True)

class PeakCenterAction(Action):
    description = 'Calculate peak center'
    def perform(self, event):
        app = event.window.application

        manager = app.get_service(SPECTROMETER_PROTOCOL)
        manager.peak_center()
#============= EOF ====================================
