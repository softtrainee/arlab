'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from shm_user import SharedMemoryUser

class SHMClient(SharedMemoryUser):
    def __del__(self):
        print 'asdf'
        if self.mapfile is not None:
            self.mapfile.close()

        if self.semaphore is not None:
            self.semaphore.close()

    def open(self):
        name = '/tmp/shm5/hardware'
        memory = self._memory_factory(name)
        self.semaphore = self._semaphore_factory(name)
        self.mapfile = self._mapfile_factory(memory)

        memory.close_fd()
        return True

    def send_command(self, cmd):
        sema = self.semaphore

        sema.acquire()
        self._write_(cmd)

        result = self._read_()

        while result == cmd:
            sema.release()
            sema.acquire()
            result = self._read_()

        sema.release()
        return result
#        sema.acquire()
#        s = self._read_()
s = None
def main():
    global s
    s.send_command('System|Read bakeout1')

if __name__ == '__main__':
#    from pylab import hist, show
#    from timeit import Timer
#    t = Timer('main()', 'from __main__ import main')
#    n = 1000
#    times = t.repeat(n, number = 1)
#    print min(times) * 1000, max(times) * 1000
#    hist(times, n / 3.0)
#    show()
    s = SHMClient()
    s.open()

    from testclient import benchmark

    benchmark('main()', 'from __main__ import main',
              'benchmark_shm_only.npz'
              )
#============= EOF ====================================
