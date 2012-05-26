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
from traits.api import on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin

VIEW = 'src.database.plugins.views.%s_view'
CLASS = '%sView'

class DatabaseUIPlugin(CoreUIPlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.database.ui'

    def _preferences_pages_default(self):
        from database_preferences_page import DatabasePreferencesPage
        return [DatabasePreferencesPage]

    def _perspectives_default(self):
        '''
        '''
        from database_perspective import DatabasePerspective
        p = [DatabasePerspective]
        return p

    def _views_default(self):
        '''
        '''
        rv = []

        views = ['user', 'project', 'sample', 'irradiation',
                 'irradiation_production_ratios']
        for v in views:
            rv.append(getattr(self, '_create_%s_view' % v))
        return rv

    def _create_irradiation_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        return self.__create_view('irradiation', **kw)

    def _create_user_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        return self.__create_view('user', **kw)

    def _create_project_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        return self.__create_view('project', **kw)

    def _create_sample_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        return self.__create_view('sample', **kw)

    def _create_irradiation_production_ratios_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        return self.__create_view('irradiation_production_ratios', **kw)

    def __create_view(self, id, **kw):
        '''
            @type id: C{str}
            @param id:

            @type **kw: C{str}
            @param **kw:
        '''
        view = VIEW % id

        nc = ''
        cap_next = False
        for c in id:
            if c == '_':
                cap_next = True
                continue

            if cap_next:
                cap_next = False
                c = c.capitalize()
            nc += c

        name = nc[0].upper() + nc[1:]
        __class__ = CLASS % name
        module = __import__(view, fromlist=[__class__])
        klass = getattr(module, __class__)

        database = self._get_database()
        if database is not None:
            args = dict(
                      id='db.%s' % id,
                      name=name,
                      category='Database',
                      obj=klass(database=database),
                     )
            return self.traitsuiview_factory(args, kw)


    def _get_database(self):
        '''
        '''
        from src.database.pychron_database_adapter import PychronDatabaseAdapter
        return self.application.get_service(PychronDatabaseAdapter)

    @on_trait_change('application.gui:started')
    def _started(self, obj, name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if new  is True:
            app = self.application
            window = app.workbench.active_window
            db = self._get_database()
            db.window = window

#============= views ===================================
#============= EOF ====================================
