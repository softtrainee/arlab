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
from traits.api import Str, Password, Property, cached_property, Event
#============= standard library imports ========================
import os
import ftplib as ftp
#============= local library imports  ==========================
from src.loggable import Loggable


class Repository(Loggable):
    root = Str

    @property
    def name(self):
        return os.path.basename(self.root)

    @property
    def url(self):
        return self.root

    def connect(self):
        return True

    def add_file(self, p):
        pass
#        src = p
#        dst = self.get_file_path(p)
#        shutil.copyfile(src, dst)

    def get_file_path(self, p):
        dst = os.path.join(self.root, os.path.basename(p))
        return dst
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
#    client = Property(depends_on='host, username, password')
    reset=Event
    client = Property(depends_on='host, username, password, reset')
    _server_root = None
    @property
    def url(self):
        return '{}@{}/{}'.format(self.username,
                                 self.host,
                                 self.remote
                                 )
    def connect(self):
        c, _ = self.client
        return c is not None

    def _get_client(self):
        h = self.host
        u = self.username
        p = self.password
        if h is None:
            h = 'localhost'
        fc = None
        e = None

        try:
            fc = ftp.FTP(h, user=u, passwd=p, timeout=2)
        except Exception, e:
            pass
        return fc, e

    def get_file_path(self, cp):
        return os.path.join(self.remote, cp)

    def retrieveFile(self, p, out):
        cb = lambda ftp:self._retreive_binary(ftp, p, out)
        self._execute(cb)

    def add_file(self, p):
        cb = lambda ftp:self._add_binary(ftp, p)
        return self._execute(cb)

    def isfile(self, cp):
#        cp = self.get_file_path(cp)
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
        i = 0
        ntries = 3
        while i < ntries:
            i += 1
            ftp, err = self._get_client()
            if ftp is not None:
                try:
                    if self._server_root is None:
                        self._server_root = ftp.pwd()
                    if not ftp.pwd() == os.path.join(self._server_root, self.remote):
                        ftp.cwd(self.remote)
                    return cb(ftp)
                except Exception, e:
                    '''
                        clears the client property cache
                    '''
                    self.reset=True
                    self.warning('execute exception {}'.format(e))
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
