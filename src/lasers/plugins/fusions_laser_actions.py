#============= enthought library imports =======================
from pyface.action.api import Action
from src.lasers.plugins.laser_actions import get_manager, open_manager
#from traits.api import on_trait_change

#============= standard library imports ========================

#============= local library imports  ==========================
class OpenCalibrationManagerAction(Action):
    def perform(self, event):
        manager = get_manager(event)
        if manager is not None:
            man = manager.stage_manager.calibration_manager
            open_manager(man)
#============= EOF ====================================
