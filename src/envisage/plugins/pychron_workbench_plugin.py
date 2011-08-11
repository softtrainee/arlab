#============= enthought library imports =======================
#from traits.api import on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.experiments.process_view import ProcessView
from src.helpers.gdisplays import gWarningDisplay, gLoggerDisplay


class PychronWorkbenchPlugin(CorePlugin):
    id = 'pychron.workbench'
    def _service_offers_default(self):
        so = self.service_offer_factory(protocol = 'src.experiments.process_view.ProcessView',
                                        factory = self._factory
                                        )
        return [so]
    def _factory(self):
        return ProcessView()

    def stop(self):
        gWarningDisplay.close()
        gLoggerDisplay.close()
#    @on_trait_change('application:gui:stopped')
#    def _gui_start(self, obj, trait_name, old, new):
#        window = self.application.workbench.active_window
#        gLoggerDisplay.close()
#        if gLoggerDisplay.ok_to_open:
#            gLoggerDisplay.close()
#            gLoggerDisplay.edit_traits(parent = window.control)
#            gLoggerDisplay.ok_to_open = False
#============= views ===================================
#============= EOF ====================================
