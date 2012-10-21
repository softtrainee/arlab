#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Str, Instance
from traitsui.api import View, Item
#============= standard library imports ========================
import os
#============= local library imports  ==========================
#from src.managers.manager import Manager
from src.repo.repository import FTPRepository, Repository

#from src.experiment.processing.ideogram import Ideogram
#from src.experiment.processing.spectrum import Spectrum
#from src.experiment.processing.inverse_isochron import InverseIsochron
#from src.database.core.database_adapter import DatabaseAdapter
from src.experiment.processing.figures.figure import Figure
from src.experiment.processing.database_manager import DatabaseManager
from src.paths import paths
from apptools.preferences.preference_binding import bind_preference
#from src.experiment.processing.processing_selector import ProcessingSelector
#from src.experiment.processing.figure import Figure
class ProcessingRepository(Repository):
    pass

class ProcessingManager(DatabaseManager):
    workspace_root = paths.workspace_root_dir
    workspace = None
    new_name = Str
    repo_kind = Str('Local')
    repo = None
    username = Str

    def __init__(self, *args, **kw):
        super(ProcessingManager, self).__init__(*args, **kw)
        self.bind_preferences()

    def bind_preferences(self):
        try:
            bind_preference(self, 'username', 'envisage.ui.workbench.username')
        except AttributeError:
            pass

    def connect_repo(self):
        host = 'localhost'
        usr = 'ross'
        pwd = 'jir812'
#        kind = 'local'
        if self.repo_kind == 'FTP':
            repo = FTPRepository(host=host, username=usr,
                                  password=pwd,
                             remote=paths.isotope_dir
                             )
        else:
            repo = Repository(root=paths.isotope_dir)
        self.repo = repo

    def open_workspace(self, name=None):
        if name is None:
            name = self.open_directory_dialog(default_path=self.workspace_root)
        else:
            name = os.path.join(self.workspace_root, name)

        if name:
            self.workspace = ProcessingRepository(root=name)

    def new_workspace(self, name=None):
        if name is None:
            info = self.edit_traits(view='new_workspace_view', kind='livemodal')
            if info.result:
                name = self.new_name

        while 1:
            ws = self._workspace_factory(name)
            if ws is not None:
                self.workspace = ws
                break
            else:
                #get another name
                info = self.edit_traits(view='new_workspace_view', kind='livemodal')
                if info.result:
                    name = self.new_name
                else:
                    break

    def new_figure(self):


        self.connect_repo()


#        self.workspace_root = '/Users/ross/Sandbox/workspace'
#        self.new_workspace('foo2')

        if self.workspace is None:
            self.information_dialog('Set a workspace')
        else:
            db = self.db
            db.selector.set_data_manager(kind=self.repo_kind,
                                         repository=self.repo,
                                         workspace_root=self.workspace.root
                                         )


            usr = self.username
            return self._figure_factory(username=usr)

#===============================================================================
# factories
#===============================================================================
    def _figure_factory(self, **kw):
        fc = Figure(
                    db=self.db,
                    **kw
                    )
        return fc

    def _workspace_factory(self, name):
        self.info('creating new workspace {} at {}'.format(name, self.workspace_root))
        p = os.path.join(self.workspace_root, name)

        if os.path.isdir(p):
            self.warning_dialog('{} is already taken choosen another name'.format(name))
            return
        else:
            os.mkdir(p)

        return ProcessingRepository(root=p)

    def _db_factory(self):
        db = super(ProcessingManager, self)._db_factory()
        if self.workspace:
            db.selector.set_data_manager(kind=self.repo_kind,
                                          repository=self.repo,
                                          workspace_root=self.workspace.root
                                          )
        return db
#===============================================================================
# views
#===============================================================================
    def new_workspace_view(self):
        return View(Item('new_name', label='Name',),
                    buttons=['OK', 'Cancel']
                    )

    def traits_view(self):
        return View('test')

if __name__ == '__main__':
    from globals import globalv
    globalv.show_infos = False
    globalv.show_warnings = False
    from launchers.helpers import build_version
    build_version('_experiment')
    from src.helpers.logger_setup import logging_setup
    logging_setup('processing')

    pm = ProcessingManager()
    pm.connect_repo()
#    pm.workspace_root = '/Users/ross/Sandbox/workspace'
    pm.username = 'bar'
    pm.open_workspace('mobat')

#    sl = pm.db.selector_factory()
#    sl.configure_traits()
#    pm.configure_traits()
    fc = pm._figure_factory()
    fc.configure_traits()
#============= EOF =============================================
