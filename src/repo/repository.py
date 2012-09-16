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
from traits.api import HasTraits, Str, Password
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import os
import hashlib
import random
from ftplib import FTP
import StringIO

#============= local library imports  ==========================
class Repository(HasTraits):
    root = Str
#    def __init__(self, root, *args, **kw):
#        self.root = root
#        super(Repository, self).__init__(*args, **kw)

class FTPRepository(Repository):
    host = Str
    username = Str
    password = Password
    remote = Str
#    def __init__(self, *args, **kw):
#        self.remote = remote
#        super(FTPRepository, self).__init__(*args, **kw)

    def _get_client(self):
        h = self.host
        u = self.username
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

    def get_file_path(self, cp):
        return os.path.join(self.remote, cp)

    def retrieveFile(self, p, out):
        cb = lambda ftp:self._retreive_binary(ftp, p, out)
        self._execute(cb)

    def add_file(self, p):
        cb = lambda ftp:self._add_binary(ftp, p)
        return self._execute(cb)

    def isfile(self, cp):
        p = self.get_file_path(cp)

        cb = lambda ftp:self._isfile(ftp, cp)
        return self._execute(cb)

    def _isfile(self, ftp, cp):
#        ftp.cwd(self.remote)
        return cp in ftp.nlst()

    def _retreive_binary(self, ftp, p, op):
#        ftp.cwd(self.remote)

        cb = open(op, 'wb').write
        ftp.retrbinary('RETR {}'.format(p), cb)

    def _add_binary(self, ftp, p, dst=None):
#        ftp.cwd(self.remote)
        if dst is None:
            dst = os.path.basename(p)
        with open(p, 'rb') as fp:
            ftp.storbinary('STOR {}'.format(dst), fp)

    def _add_ascii(self, ftp, p, dst=None):
#        ftp.cwd(self.remote)
        if dst is None:
            dst = os.path.basename(p)
        with open(p, 'r') as fp:
            ftp.storascii('STOR {}'.format(dst), fp)

    def _execute(self, cb):
        ftp, err = self._get_client()
        if ftp is not None:
            ftp.cwd(self.remote)
            return cb(ftp)
        else:
            print err


if __name__ == '__main__':
    c = FTPRepository(
                      remote='Sandbox/ftp/data',
#                      root='/',
                      user='ross',
                      password='jir812'
                      )

    p = '/Users/ross/Sandbox/download.h5'
    c.add_file(p)

#============= EOF =============================================
