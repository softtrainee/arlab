#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.managers.graph_manager import GraphManager
class GraphPlugin(CorePlugin):
    def _service_offers_default(self):
        so = self.service_offer_factory(protocol = GraphManager,
                                        factory = GraphManager)
        return [so]

#============= EOF =============================================
