#===============================================================================
# Copyright 2013 Jake Ross
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
from pyface.action.action import Action
from pyface.tasks.action.task_action import TaskAction
from traits.api import HasTraits
from traitsui.api import View, Item

#============= standard library imports ========================
#============= local library imports  ==========================


class UpdateDatabaseAction(Action):
    name = 'Update Database'

    def perform(self, event):
        app = event.task.window.application
        man = app.get_service('src.database.isotope_database_manager.IsotopeDatabaseManager')

        url = man.db.url

        repo = 'isotopedb'
        from src.database.migrate.manage_database import manage_database

        progress = man.open_progress()
        manage_database(url, repo,
                        logger=man.logger,
                        progress=progress
        )

        man.populate_default_tables()

    #============= EOF =============================================
