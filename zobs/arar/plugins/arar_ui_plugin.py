# @PydevCodeAnalysisIgnore
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
from traits.api import  on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin

class ArArUIPlugin(CoreUIPlugin):
    '''
    '''
    id = 'pychron.arar'

    def _preferences_pages_default(self):
        from arar_preferences_page import ArArPreferencesPage
        return [ArArPreferencesPage]

    def _action_sets_default(self):
        from arar_action_set import ArArActionSet
        return [ArArActionSet]

    def _perspectives_default(self):
        from arar_perspective import ArArPerspective
        p = [ArArPerspective]
        return p

    def _get_manager(self):
        return self.application.get_service('src.arar.arar_manager.ArArManager')

    def _get_db(self):
        return self.application.get_service('src.database.adapters.massspec_database_adapter.MassSpecDatabaseAdapter')

#============= views ===================================
    def _views_default(self):
        '''
        '''
        rv = [
#              self._create_data_directory_view,
              self._create_notes_view,
              self._create_info_view,
              self._create_engine_view,
#              self._create_engine_configure_view,
              self._create_database_view
              ]
        return rv

    def _create_database_view(self, **kw):
        man = self._get_db()
        man.connect()

        man.selector_factory()
        args = dict(
                  id='pychron.arar.database',
                  name='Database',
                  obj=man.selector
                  )
        return self.traitsuiview_factory(args, kw)

    def _create_engine_view(self, **kw):
        man = self._get_manager()
        args = dict(
                  id='pychron.arar.engine',
                  name='Engine',
                  obj=man
                  )
        return self.traitsuiview_factory(args, kw)

    def _create_engine_configure_view(self, **kw):
        man = self._get_manager()
        args = dict(
                  id='pychron.arar.engine.configure',
                  name='Configure Engine',
                  obj=man.engine,
                  view='configure_view'
                  )
        return self.traitsuiview_factory(args, kw)


    def _create_notes_view(self, **kw):
        from notes_view import NotesView
        obj = NotesView()
        manager = self._get_manager()
        if manager is not None:
            manager.on_trait_change(obj.selected_update, 'selected')

        args = dict(id='pychron.arar.notes_view',
                  name='Notes',
                  obj=obj
                  )
        return self.traitsuiview_factory(args, kw)

    def _create_info_view(self, **kw):
        from info_view import InfoView
        obj = InfoView()
        manager = self._get_manager()
        if manager is not None:
            manager.on_trait_change(obj.selected_update, 'selected')

        args = dict(id='pychron.arar.info',
                  name='Info',
                  obj=obj
                  )
        return self.traitsuiview_factory(args, kw)

#    def _create_data_directory_view(self, **kw):
#        modeler_manager = self._get_manager()
#
#        args = dict(
#                    id='pychron.modeler.data_directory',
#                  name='Data',
#                  view='data_select_view',
#                  obj=modeler_manager#.modeler,
#                  )
#        return self.traitsuiview_factory(args, kw)

    @on_trait_change('application.gui:started')
    def _started(self, obj, name, old, new):
        '''

        '''
        if new  is True:
            app = self.application
            manager = app.get_service('src.arar.arar_manager.ArArManager')
#            manager.open_default()
            manager.demo_open()
#============= EOF ====================================
