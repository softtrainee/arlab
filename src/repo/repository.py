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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import os
import hashlib
import random
from ftplib import FTP

#============= local library imports  ==========================
class Repository(HasTraits):
    root = None
    current_path = None
#    def __init__(self, root, *args, **kw):
#        self.root = root
#        super(Repository, self).__init__(*args, **kw)

class FTPRepository(Repository):
    host = None
    user = None
    password = None
    remote = None
#    def __init__(self, *args, **kw):
#        self.remote = remote
#        super(FTPRepository, self).__init__(*args, **kw)

    def _get_client(self):
        h = self.host
        u = self.user
        p = self.password
        if h is None:
            h = 'localhost'
        ftp = None
        e = None
        try:
            ftp = FTP(h, user=u, passwd=p)
        except Exception, e:
            pass
        return ftp, e

    def commit(self):
        ftp, err = self._get_client()
        if ftp is not None:
            ftp.cwd(self.remote)

            p = self.current_path
            name = os.path.basename(p)
            fp = open(p, 'rb')
            cmd = 'STOR {}'.format(name)
            ftp.storbinary(cmd, fp)
        else:
            print err

if __name__ == '__main__':
    c = FTPRepository(
                      remote='Sandbox/ftp/data',
#                      root='/',
                      user='ross',
                      password='jir812'
                      )

    c.current_path = '/Users/ross/Sandbox/ftpdownload.h5'
    print 'isfile', os.path.isfile(c.current_path)
    c.commit()

#============= EOF =============================================
