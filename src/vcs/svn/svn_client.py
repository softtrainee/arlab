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

#============= standard library imports ========================
from threading import Thread
import os
import time
#============= local library imports  ==========================
from src.loggable import Loggable
from pyface.api import information
from src.helpers.paths import src_root, project_home
from pyface.timer.do_later import do_later
HEAD = ''
BASE = ''
try:
    import pysvn
    HEAD = pysvn.Revision(pysvn.opt_revision_kind.head)
    BASE = pysvn.Revision(pysvn.opt_revision_kind.base)
    def revision_factory(n):
        rev = pysvn.Revision(pysvn.opt_revision_kind.number, n)
        return rev
except ImportError:
    pysvn = None


VERSION_PATH = 'version_info.txt'
class SVNClient(Loggable):
    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        self.name = 'SVNClient'
        super(SVNClient, self).__init__(*args, **kw)
        self._client = pysvn.Client() if pysvn is not None else None
        if self._client is not None:
            self._client.callback_ssl_server_trust_prompt
    def _update_(self):
        '''
        '''
        revision = self._client.update(src_root)[0]
        self.info('updated to revision %i' % revision.number)
        msg = 'Restart for updates to take effect'
        self.info(msg)
        information(None, msg)

    def update_to_head(self):
        '''
        '''
        self.info('updating to head')
        t = Thread(target=self._update_)
        t.start()

    def isCurrent(self):
        status = self._client.status(src_root, get_all=False)

        current = True
        for pi in status:
            head, tail = os.path.splitext(pi.path)
            if tail != '.pyc':
                if pi.is_versioned:
                    if str(pi.repos_text_status) != "none":
                        current = False
                        break
        return current

    def get_version_number(self):
        #p='http://arlab.googlecode.com/svn/branches/pychron'
        if self._client:
            entry = self._client.info(src_root)

            return int(entry.revision.number)

    def get_local_version_file(self):
        if self._client:
            p = os.path.join(src_root, VERSION_PATH)

            entry = self._client.info(p)

            return p, entry

    def get_remote_version_file(self, progress=None):
        if self._client:
            p = os.path.join(project_home, VERSION_PATH)
            self._inprogress = True
            if progress is not None:
                tt = Thread(target=self._timer_update, args=(progress,))
                tt.start()
            return self._get_remote_file_info(p)
#        t=Thread(target=self._get_remote_file_info, args=(p,))
#        t.start()

    def _timer_update(self, progress):

        do_later(progress.update, *(0,))
        while self._inprogress:
            time.sleep(0.1)

        progress.reset()

    def _get_remote_file_info(self, p):
        if self._client:
            self._inprogress = True
            name, info = self._client.info2(p,
                                    )[0]

            self._inprogress = False
            return name, info

#    def __getattr__(self, name):
#        '''
#            @type name: C{str}
#            @param name:
#        '''
#        obj = self
#        if hasattr(self._client, name):
#            obj = self._client
#
#        return getattr(obj, name)
#============= EOF ====================================
