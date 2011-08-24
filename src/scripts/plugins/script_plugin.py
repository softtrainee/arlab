#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.scripts.core.scripts_manager import ScriptsManager

class ScriptPlugin(CorePlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.script'
    name = 'Script'
    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(protocol = 'src.scripts.core.scripts_manager.ScriptsManager',
                          factory = self._factory
                          )

        return [so]

    def _factory(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        return ScriptsManager()

#    def start(self):
#        a = self.application.get_service('src.scripts.scripts_manager.ScriptsManager')
#        a.window = self.application.workbench.window
#        a.start()
#============= EOF ====================================
