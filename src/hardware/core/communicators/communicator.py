#============= enthought library imports =======================
from traits.api import Str, Bool

#============= standard library imports ========================
import time
from threading import Lock

#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable
class Communicator(ConfigLoadable):
    '''
      
    '''
    _lock = Lock
    name = Str
    simulation = Bool
    _terminator = chr(13) #'\r'
    def __init__(self, *args, **kw):
        '''
        '''
        super(Communicator, self).__init__(*args, **kw)
        self._lock = Lock()

    def delay(self, ms):
        '''
          
        '''
        time.sleep(ms / 1000.0)

    def ask(self, cmd, *args, **kw):
        pass
    def tell(self, cmd, *args, **kw):
        pass

    def write(self, *args, **kw):
        pass

    def read(self, *args, **kw):
        pass

    def process_response(self, re, replace = None, remove_eol = True):
        '''
        '''
        if remove_eol:
            re = self._remove_eol(re)

        #substitute replace[0] for replace[1]
        if isinstance(replace, tuple):
            ree = ''
            for ri in re:
                rii = ri
                if ri == replace[0]:
                    rii = replace[1]
                ree += rii
            re = ree
        return re

    def _prep_str(self, s):
        '''
        '''
        ns = ''
        for c in s:
            oc = ord(c)
            if not 0x20 <= oc <= 0x7E:
                c = '[%02i]' % ord(c)
            ns += c
        return ns

    def log_tell(self, cmd, info = None):
        '''
        '''
        cmd = self._remove_eol(cmd)
        ncmd = self._prep_str(cmd)

        if ncmd:
            cmd = ncmd


        if info is not None:
            msg = '%s    %s' % (info, cmd)
        else:
            msg = cmd

        self.info(msg)

    def log_response(self, cmd, re, info = None):
        '''
        '''
        cmd = self._remove_eol(cmd)

        ncmd = self._prep_str(cmd)
        if ncmd:
            cmd = ncmd

        if info and info != '':
            msg = '%s    %s ===>> %s' % (info, cmd, re)
        else:
            msg = '%s ===>> %s' % (cmd, re)

        self.info(msg, decorate = False)


    def _remove_eol(self, re):
        '''
        '''

        if re is not None:
            return str(re).rstrip()
#============= EOF ====================================
