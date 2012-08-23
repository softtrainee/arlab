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
from traits.api import HasTraits, Instance, Any, Str, Button, \
    DelegatesTo, List
from traitsui.api import View, Item, VGroup, HGroup, ListStrEditor
#============= standard library imports ========================
import os
import shutil
#============= local library imports  ==========================
from src.bench.workspace_file import WorkspaceFile
from src.bench.commit_dialog import CommitDialog
import sys
from src.loggable import Loggable

os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = '/usr/local/git/bin/git'
from git import Repo

class Workspace(Loggable):
    name = Str
#    repo_root = Directory
    _repo = None
    _repo_path = None
    current_file = Instance(WorkspaceFile)
    commit_button = Button('Commit')
    dirty = DelegatesTo('current_file')

    branches = List
    selected = Any
    prev_selected = Any
#    def update_dirty(self, obj, name, old, new):
#        print obj, name, old, new
#        self.dirty = new


#===============================================================================
# public
#===============================================================================
    def load_repository(self, name):
        self._repo = Repo(name)
        self._repo_path = name

        np = '/Users/ross/Sandbox/testrepo/foo.dat'
        self.current_file = WorkspaceFile(np)

    def init_repository(self, name):
        self.info('initializing repository {}'.format(name))
        self._repo = repo = Repo.init(name)
        self._repo_path = name
#        repo.create_head('master')
#        print repo.heads

        p = os.path.join(name, 'foo.dat')
        with open(p, 'w') as f:
            f.write('foo\n')
            f.write('moofff\n')
#
#        #stage the new file
        ind = self._repo.index
        ind.add([p])
        #commit the current stage
        self._do_commit()

    def load_branches(self):
        self.branches = [b.name for b in self._repo.heads]

    def create_branch(self, name):
        self.info('creating branch {}'.format(name))
        repo = self._repo
        if not repo:
            return
        repo.create_head(name)

    def switch_branch(self, name):
        self.info('switching to branch {}'.format(name))
        repo = self._repo
        try:
            br = getattr(repo.heads, name)
            br.checkout()
        except AttributeError:
            pass

    def add_file(self, src):
        self.info('adding file {}'.format(src))
        root = self._repo_path
        name = os.path.basename(src)
        dst = os.path.join(root, name)
        _, ext = os.path.splitext(dst)
        if ext in ['.hdf5', '.h5']:
            from tables import copyFile
            func = copyFile
        else:
            func = shutil.copyfile
        func(src, dst)

        self.commit_file(dst)

    def commit_file(self, dst):
        repo = self._repo
        ind = repo.index
        ind.add([dst])

        self._do_commit()

#    def test_modify(self):
#        repo = self._repo
#        repo.heads.test.checkout()
#
#        p = os.path.join(self._repo_path, 'foo.dat')
#        with open(p, 'w') as f:
#            f.write('foofffddf\n')
#            f.write('moofffasdfsdfd\n')
#
#        #stage the new file
#        ind = repo.index
#        ind.add([p])
##        #commit the current stage
#        self._do_commit()

#    def compare(self):
#        repo = self._repo
#        mcommit = repo.heads.master.commit
#        tcommit = repo.heads.test.commit
#        diffobj = mcommit.diff(tcommit)
#        print diffobj


#===============================================================================
# 
#===============================================================================

    def _selected_changed(self):
        if self.selected:
            self.switch_branch(self.selected)
            self.current_file.reload()

#    def _commit_button_fired(self):
#        cf = self.current_file
#        print cf.text
#        cf.dump()
#
#        self._repo.stage([os.path.basename(cf.path)])

#    def _(self):
#        commit_args = self.pre_commit()
#        if commit_args:
#            cid = self.commit(*commit_args)
#            print cid


#    def _load_revision_history(self):
#        for i in self._repo.revision_history(self._repo.head()):
#            s = self._parse_revision_history(i)
#            self.branches.append(s)
#
#    def _parse_revision_history(self, r):
#        args = r.as_pretty_string().split('\n')
##        for a in args:
##            print a
##        print str(r.sha().hexdigest())
#
#        return args[-1]
#
#    def add_file(self, srcpath):
#
#        name = os.path.basename(srcpath)
#        np = os.path.join(self._repo_path, name)
#        shutil.copyfile(srcpath,
#                        np)
#
#        self._repo.stage([name])
#
#        commit_args = self.pre_commit()
#        if commit_args:
#            cid = self.commit(*commit_args)
#            return np
    def _do_commit(self):
        args = self._get_commit_args()
        if args:
            msg, _ = args
            index = self._repo.index
            index.commit(msg)

    def _get_commit_args(self):
        cd = CommitDialog()
        info = cd.edit_traits()
        if info.result:
            return cd.message, cd.committer

#    def commit(self, message, committer):
#        return self._repo.do_commit(message, committer)

    def traits_view(self):
        toolbar = HGroup(Item('commit_button',
                              enabled_when='dirty',
                               show_label=False))
        v = View(toolbar,
                Item('branches', editor=ListStrEditor(editable=False,
                                                       operations=[],
                                                       selected='selected'),
                     show_label=False),
                Item('current_file', style='custom',
                      show_label=False),
                 )
        return v
#============= EOF =============================================
