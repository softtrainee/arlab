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
from src.managers.manager import Manager
from src.repo.repository import FTPRepository, Repository

#from src.experiment.processing.ideogram import Ideogram
#from src.experiment.processing.spectrum import Spectrum
#from src.experiment.processing.inverse_isochron import InverseIsochron
from src.database.core.database_adapter import DatabaseAdapter
from src.experiment.processing.figures.figure import Figure
from src.experiment.processing.database_manager import DatabaseManager
from src.paths import paths
#from src.experiment.processing.processing_selector import ProcessingSelector
#from src.experiment.processing.figure import Figure
class ProcessingRepository(Repository):
    pass

class ProcessingManager(DatabaseManager):
    workspace_root = None
    workspace = None
    new_name = Str

    def connect_repo(self):
        host = 'localhost'
        usr = 'ross'
        pwd = 'jir812'
        kind = 'local'
        if kind == 'local':
            repo = Repository(root=paths.isotope_dir)
        else:
            repo = FTPRepository(host=host, username=usr,
                                  password=pwd,
                             remote='Sandbox/ftp/data'
                             )
#        self.repo = repo
        self.repo = repo

#    def open_plot(self):
#        kind = 'spectrum'
#
#        #get get data
#        names = self.get_names()
#        if names:
#            self.get_remote_files(names)
#            func = getattr(self, 'plot_{}'.format(kind))
#            func(names)
#
#    def get_names(self):
#        return ['B-92.h5', 'B-91.h5',
#                  'B-90.h5',
#                  'B-89.h5',
#                  'B-88.h5',
#                  ]

    def get_remote_file(self, name, force=False):
        out = os.path.join(self.workspace.root, name)
        if not os.path.isfile(out) or force:
            self.repo.retrieveFile(name, out)

    def get_remote_files(self, names, **kw):
        for n in names:
            self.get_remote_file(n, **kw)

    def open_workspace(self, name):
        self.workspace = ProcessingRepository(root=os.path.join(self.workspace_root, name))

    def new_workspace(self, name):
        while 1:
            if self._workspace_factory(name):
                #get another name
                info = self.edit_traits(view='new_workspace_view', kind='livemodal')
                if info.result:
                    name = self.new_name
                else:
                    break
            else:
                break

    def _figure_factory(self):
        fc = Figure(db=self.db,
                    repo=self.repo,
                    workspace=self.workspace)
        return fc

    def _workspace_factory(self, name):
        self.info('creating new workspace {}'.format(name))
        p = os.path.join(self.workspace_root, name)
        if os.path.isdir(p):
            self.warning_dialog('{} is already taken choosen another name'.format(name))
            return True
        else:
            os.mkdir(p)

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
    pm.workspace_root = '/Users/ross/Sandbox/workspace'
    pm.open_workspace('foo1')

#    sl = pm.db.selector_factory()
#    sl.configure_traits()
#    pm.configure_traits()
    fc = pm._figure_factory()
    fc.configure_traits()
#============= EOF =============================================
