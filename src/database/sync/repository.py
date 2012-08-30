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
from traits.api import HasTraits, Property, Any, Str, List, Button
from traitsui.api import View, Item, TabularEditor
#============= standard library imports ========================
import os
import datetime
from traitsui.tabular_adapter import TabularAdapter
from src.loggable import Loggable
#============= local library imports  ==========================
os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = '/usr/local/git/bin/git'
from git import Repo

def make_file(root, name, txt):
    with open(os.path.join(root, name), 'w') as f:
        f.write(txt)


class GitRefLog(HasTraits):
    _ref = Any

    action = Property
    message = Property
    time = Property
    user = Property

    def _get_message(self):
        return ':'.join(self._ref.message.split(':')[1:])

    def _get_time(self):
        t, _tz = self._ref.time
        return datetime.datetime.fromtimestamp(t)

    def _get_action(self):
        return self._ref.message.split(':')[0]

    def _get_user(self):
        return self._ref.actor.name

class GitCommit(GitRefLog):
    def _get_action(self):
        return 'commit'

    def _get_message(self):
        return self._ref.message
    def _get_user(self):
        return self._ref.author
    def _get_time(self):
        return datetime.datetime.fromtimestamp(self._ref.committed_date)

class GitRefLogAdapter(TabularAdapter):
    columns = [('Time', 'time'), ('Action', 'action'),
               ('Message', 'message'), ('User', 'user')]

#class GitCommitAdapter(TabularAdapter):
#    columns = [('Time', 'time'), ('Action', 'action'),
#               ('Message', 'message'), ('User', 'user')]

class Repository(Loggable):
    git_repo = Any
    root = Str
    remote = Property(depends_on='git_repo')

    push_button = Button('Push')
    pull_button = Button('Pull')

    local_changes = List
    commits = List

    def __init__(self, root):
        self.root = root
        if os.path.isdir(root):
            self.git_repo = Repo(root)

            repo = self.git_repo
            master = repo.head.reference

            local_changes = self.local_changes
            for ch in master.log():

                local_changes.append(GitRefLog(_ref=ch))

            commits = self.commits
            for ci in repo.iter_commits('master'):
                commits.append(GitCommit(_ref=ci))

#===============================================================================
# git interface
#===============================================================================
    def ignore_file(self, name):
        p = os.path.join(self.git_repo.working_dir, '.gitignore')
        if os.path.isfile(p):
            mode = 'a'
        else:
            mode = 'w'

        with open(p, mode) as f:
            f.write('{}\n'.format(name))

    def clone(self, url):
        remote_repo = Repo(url)
        self.git_repo = remote_repo.clone(self.root)

    def add(self, name):
        index = self.git_repo.index
        index.add([name])

    def commit(self, msg):
        index = self.git_repo.index
        index.commit(msg)
        self.info('commit: {}'.format(msg))

    def pull(self):
        self.git_repo.remotes.origin.pull()
        self.info('pulled changes from remote')

    def push(self, branch='master', pull=True):
        repo = self.git_repo
        if pull:
            try:
                self.pull()
            except AssertionError:
                pass

        self.info('pulled changes to {}'.format(branch))
        repo.remotes.origin.push(branch)

    def create_branch(self, name):
        self.info('creating branch {}'.format(name))
        repo = self.git_repo
        return repo.create_head(name)

    def switch_branch(self, name):
        self.info('switching to branch {}'.format(name))
        repo = self.repo
        try:
            br = getattr(repo.heads, name)
            br.checkout()
        except AttributeError:
            pass

#===============================================================================
# handler
#===============================================================================
    def _push_button_fired(self):
        root = self.root
        name = 'analysis001.txt'
        txt = 'this is an altered file'
        make_file(root, name, txt)
        self.add(name)
        self.commit('alter analysis001.txt')

        self.push()

    def _pull_button_fired(self):
        self.pull()
#===============================================================================
# propert get/set    
#===============================================================================
    def _get_remote(self):
        return self.git_repo.remotes.origin.url
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(

                 Item('root', label='local'),
                 Item('remote', label='remote'),

                 Item('push_button', show_label=False),
                 Item('pull_button', show_label=False),


                 Item('local_changes', show_label=False, editor=TabularEditor(
                                                                              adapter=GitRefLogAdapter(),
                                                                              editable=False,
                                                                              )),
                 Item('commits', show_label=False, editor=TabularEditor(
                                                                              adapter=GitRefLogAdapter(),
                                                                              editable=False,
                                                                              ))

                 )
        return v
#============= EOF =============================================
