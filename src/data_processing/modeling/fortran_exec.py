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
#=============enthought library imports=======================
from threading import Thread
import subprocess
import os
#============= standard library imports ========================

#============= local library imports  ==========================
class FortranExec(Thread):
    _process = None
    def __init__(self, name, root, queue=None):
        Thread.__init__(self)
        self.name = name
        self.root = root
        ps = os.environ['PATH'].split(':')
        if not root in ps:
            os.environ['PATH'] += ':{}'.format(root)
        
        self.queue = queue
    
    def run(self):
        try:
            p = subprocess.Popen([self.name],
                                  shell=False,
                                  bufsize=1024,
                                  stdout=subprocess.PIPE
                                  )
            self._process = p
            while p.poll() == None:
                if self.queue:
                    self.queue.put(p.stdout.readline())
        
        except OSError, e:
            print e
        
    def get_remaining_stdout(self):
        if self._process:
            return self._process.communicate()[0]
            
if __name__ == '__main__':
    import Queue

    q = Queue.Queue()
    f = FortranExec('hello_world2', '/usr/local/clovera', q)
    
    f.start()
    while f.isAlive() or not q.empty():
        l = q.get().rstrip()
        print l
        
    print f.get_remaining_stdout()
#============= EOF =====================================

