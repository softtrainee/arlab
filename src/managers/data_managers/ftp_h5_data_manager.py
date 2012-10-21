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
import os
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.repo.repository import FTPRepository


class FTPH5DataManager(H5DataManager):
    repository = None
    workspace_root = None
    def connect(self, host, usr, pwd, remote):
        self.repository = FTPRepository(host=host, username=usr, password=pwd, remote=remote)

    def open_data(self, p, **kw):
        out = os.path.join(self.workspace_root, p)
        self.repository.retrieveFile(p, out)
        return super(FTPH5DataManager, self).open_data(out, **kw)

    def isfile(self, path):
        return self.repository.isfile(path)

#============= EOF =============================================
