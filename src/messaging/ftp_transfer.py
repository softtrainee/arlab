from __future__ import with_statement
#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change,Str,Int,Float,Button
#from traitsui.api import View,Item,Group,HGroup,VGroup

#============= standard library imports ========================
import ftplib
import os

#============= local library imports  ==========================
class FTPTranfer(object):
    '''
        G{classtree}
    '''
    _ftp = None
    def __init__(self, host, *args, **kw):
        '''
            @type host: C{str}
            @param host:

            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        self._connect(host)

    def transfer(self, path, name = None):
        '''
            @type path: C{str}
            @param path:

            @type name: C{str}
            @param name:
        '''
        if name is None:
            name = os.path.basename(path)
        if self._ftp is not None:
            self._ftp.cwd('argusVI_one_data')
            with open(path, 'r') as f:
                self._ftp.storlines('STOR %s' % name, f,
                                callback = self._transfer_line,
                                )

    def _transfer_line(self, args):
        '''
            @type args: C{str}
            @param args:
        '''
        print 'transfering %s' % args

    def _connect(self, host):
        '''
            @type host: C{str}
            @param host:
        '''
        self._ftp = f = ftplib.FTP(host)
        f.login(user = 'ross', passwd = 'jir812')

if __name__ == '__main__':
    f = FTPTranfer('localhost')
#    f._ftp.mkd('argusVI_one_data')
    p = '/Users/Ross/Desktop/airshot_script.txt'
    f.transfer(p)
#============= EOF ====================================
