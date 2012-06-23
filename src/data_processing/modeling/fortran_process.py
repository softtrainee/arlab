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



#=============enthought library imports=======================
from threading import Thread
import subprocess
import os
from pyface.message_dialog import warning
import sys
from src.initializer import MProgressDialog
from pyface.timer.do_later import do_later
import time
#============= standard library imports ========================

#============= local library imports  ==========================
class FortranProcess(Thread):
    _process = None
    def __init__(self, name, root, queue=None):
        Thread.__init__(self)
        self.name = name
        self.root = root
        self.success = False
        delimiter = ':'
        if sys.platform != 'darwin':
            delimiter = ';'

        ps = os.environ['PATH'].split(delimiter)
        if not root in ps:
            os.environ['PATH'] += '{}{}'.format(delimiter, root)

        self.queue = queue

    def run(self):
        n = 5
        if not os.path.exists(os.path.join(self.root, self.name)):
            warning(None, 'Invalid Clovera path {}'.format(self.root))
            return

        pd = MProgressDialog(max=n, size=(550, 15))
        do_later(pd.open)
        do_later(pd.change_message, '{} process started'.format(self.name))
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
                time.sleep(1e-6)

            self.success = True
            do_later(pd.change_message, '{} process complete'.format(self.name))

            return True

        except OSError, e:
            #warning(None, '{} - {}'.format(e, self.name))
            do_later(pd.change_message, '{} process did not finish properly'.format(self.name))



    def get_remaining_stdout(self):
        if self._process:
            try:
                txt = self._process.communicate()[0]
                if txt:
                    return txt.split('\n')
            except Exception, e:
                pass
                #print 'get remaining stdout',e
        return []

if __name__ == '__main__':
    import Queue
    import time
    q = Queue.Queue()
    d = '/Users/Ross/Desktop'
    f = FortranProcess('hello_world', d, q)
    print os.getcwd()
    os.chdir(d)
    f.start()
    time.clock()
    while f.isAlive() or not q.empty():
        l = q.get().rstrip()
        #print l

    #print f.get_remaining_stdout()
    print time.clock()
#============= EOF =====================================

