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
#@PydevCodeAnalysisIgnore

#============= enthought library imports =======================

#============= standard library imports ========================
from threading import Thread
#============= local library imports  ==========================
from shm_user import SharedMemoryUser
class SHMServer(SharedMemoryUser):
    mapfile = None
    semaphore = None
    memory = None
    _listen = True
    def __del__(self):
        if self.mapfile is not None:
            self.mapfile.close()

        if self.semaphore is not None:
            self.semaphore.close()
            self.semaphore.unlink()

        if self.memory is not None:
            self.memory.unlink()

    def close(self):
        self._listen = False

    def open(self):
        name = '/tmp/shm5/hardware'
        memory = self._memory_factory(name, o_crex = True, size = 1024)
        self.semaphore = self._semaphore_factory(name, o_crex = True)

        self.mapfile = self._mapfile_factory(memory)

        #done with memory object 
        memory.close_fd()

        #start server forever thread

        t = Thread(target = self.serve)
        t.start()

        return True

    def serve(self):
        semaphore = self.semaphore
        i = 0
        j = 0
        curdata = ''
        while self._listen:# and i < 3:
            semaphore.release()

            semaphore.acquire()


            data = self._read_()
            if data != curdata:
#                self.say('%s, %s, %s, %s' % (data, curdata, len(data), len(curdata)))
                r = self._handle(data)
#                self.say('result %s' % r)
                i += 1

                self._write_(r)
                curdata = r

    def _handle(self, r):
        return 'r_%s' % r

#============= views ===================================
#============= EOF ====================================



if __name__ == '__main__':
    s = SHMServer()
    s.open()