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
from traits.api import HasTraits, Any, Str, Button, Bool, Instance, \
    DelegatesTo, List
from traitsui.api import View, Item, HGroup, VGroup, ListStrEditor, \
     TableEditor, InstanceEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.bench.workspace import Workspace
from src.bench.workspace_file import WorkspaceFile
import os
from src.managers.data_managers.h5_data_manager import H5DataManager
import random

class BenchManager(HasTraits):
    current_workspace = Any
    def traits_view(self):
        v = View(
                 Item('current_workspace',
                      editor=InstanceEditor(),
                      style='custom', show_label=False),
                 width=700,
                 height=500,
                 resizable=True
                 )
        return v

    def new_workspace(self, root):
        if not os.path.exists(root):
            os.mkdir(root)

        self.current_workspace = ws = Workspace()

#        ws.init_repository(root)
        ws.load_repository(root)
        ws.load_branches()

        ws.switch_branch('master')
#        ws.create_branch('test2')
#        ws.switch_branch('test2')
#        ws.switch_branch('test')

#        dm = H5DataManager()
##        dm.new_frame()
#        p = os.path.join(ws._repo_path, 'scan014.hdf5')
#        p = dm.open_data(p, mode='a')
##
#        fn = dm.get_current_path()
#        table = dm.get_table('foo', '/')
##        table = dm.new_table('/', 'foo')
#        row = table.row
#        for i in range(100):
#            row['time'] = i
#            row['value'] = random.random()
#            row.append()
####
#        dm.close()
#        ws.commit_file(fn)

#        ws.add_file(fn)
#
##    def load_workspace(self, root):


#        ws.load_repository(root)

#        p = '/Users/ross/Sandbox/foo.dat'
#
#        write = lambda ff, m: ff.write(m + '\n')
#        with open(p, 'w') as f:
#            write(f, 'foodat')
#            write(f, 'pluse moodatae')

#        np = ws.add_file(p)
#        if np:
#            ws.current_file = WorkspaceFile(np)

#        np = '/Users/ross/Sandbox/testrepo/foo.dat'
#        ws.current_file = WorkspaceFile(np)
#        ws.current_file.on_trait_change(ws.update_dirty, 'dirty')

if __name__ == '__main__':
    bm = BenchManager()
    root = '/Users/ross/Sandbox/testrepo'

    bm.new_workspace(root)

    bm.configure_traits()
#============= EOF =============================================
