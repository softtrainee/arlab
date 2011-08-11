#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin
class SpectrometerUIPlugin(CoreUIPlugin):
    def _action_sets_default(self):

        from src.spectrometer.plugins.spectrometer_action_set import SpectrometerActionSet
        return [SpectrometerActionSet]
#============= EOF =============================================
