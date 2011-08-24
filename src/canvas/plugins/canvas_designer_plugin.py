#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.canvas.designer.canvas_manager import CanvasManager
from src.envisage.core.core_plugin import CorePlugin

class CanvasDesignerPlugin(CorePlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.canvas_designer'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = CanvasManager,
                          #protocol = 'src.canvas.designer.canvas_manager.CanvasManager',
                          factory = self._factory
                          )
        return [so]
    def _factory(self):
        '''
        '''
        return CanvasManager()

#============= EOF ====================================
