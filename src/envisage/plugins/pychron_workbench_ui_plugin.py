#============= enthought library imports =======================
#============= standard library imports ========================

#============= local library imports  ==========================

from src.envisage.core.core_ui_plugin import CoreUIPlugin

class PychronWorkbenchUIPlugin(CoreUIPlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.workbench.ui'
    name = 'Pychron Workbench'

    def _action_sets_default(self):
        '''
        '''
        from pychron_workbench_action_set import PychronWorkbenchActionSet
        return [PychronWorkbenchActionSet]

    def _perspectives_default(self):
        '''
        '''
        return []

    def _preferences_pages_default(self):
        '''
        '''
        from pychron_workbench_preferences_page import PychronWorkbenchPreferencesPage
        return [PychronWorkbenchPreferencesPage]

    def _views_default(self):
        '''
        '''
        return []#self._create_process_view]

    def _create_process_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        app = self.application
        obj = app.get_service('src.experiments.process_view.ProcessView')
        manager = app.get_service('src.experiments.experiments_manager.ExperimentsManager')
        smanager = app.get_service('src.scripts.scripts_manager.ScriptsManager')

        #obj.experiment = manager.selected
        if manager is not None:
            manager.on_trait_change(obj.selected_update, 'selected')
        if smanager is not None:
            smanager.on_trait_change(obj.selected_update, 'selected')

        args = dict(id = 'pychron.process_view',
                         name = 'Process',
                         obj = obj
                       )
        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
