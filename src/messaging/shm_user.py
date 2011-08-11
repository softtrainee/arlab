#============= enthought library imports =======================

#============= standard library imports ========================
try:
    import posix_ipc
except ImportError:
    pass

import mmap
import time
import sys

#============= local library imports  ==========================
from src.config_loadable import ConfigLoadable
class SharedMemoryUser(ConfigLoadable):
    mapfile = None
    semaphore = None
    def _read_(self):
        mf = self.mapfile
        mf.seek(0)
        s = []
        c = mf.read_byte()
        while c != '\0':
            s.append(c)
            c = mf.read_byte()
        s = ''.join(s)

    #    self.say('read %s' % s)
        return s

    def _write_(self, data):
#        self.say('writing %s' % data)
        mf = self.mapfile


        mp = mf.tell()
        mf.seek(0)
        l = len(data)

        mf.write(data)
        while l <= mp:
            mf.write('\0')
            l += 1

    def _memory_factory(self, name, o_crex = False, size = None):

        args = (name,)
        kw = dict()
        if o_crex:
            args += (posix_ipc.O_CREX,)

        if size is not None:
            kw['size'] = size
        try:
            shm = posix_ipc.SharedMemory(*args, **kw)
        except:
            posix_ipc.unlink_shared_memory(name)
            shm = posix_ipc.SharedMemory(*args, **kw)

        return shm

    def _semaphore_factory(self, name, o_crex = False):
        args = (name,)
        if o_crex:
            args += (posix_ipc.O_CREX,)
        try:
            sema = posix_ipc.Semaphore(*args)
        except:
            posix_ipc.unlink_semaphore(name)
            sema = posix_ipc.Semaphore(*args)

        return sema

    def _mapfile_factory(self, mem):
        return mmap.mmap(mem.fd, mem.size)

    def say(self, s):
        """Prints a timestamped, self-identified message"""
        who = sys.argv[0]
        if who.endswith(".py"):
            who = who[:-3]

        s = "%s@%1.6f: %s" % (who, time.time(), s)
        print (s)
#============= views ===================================
#============= EOF ====================================
