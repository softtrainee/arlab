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



#============= enthought library imports =======================

#============= standard library imports ========================
from threading import Thread
import time
import os
#============= local library imports  ==========================
from src.loggable import Loggable


class FileMonitor(Loggable):
    '''
        G{classtree}
    '''
    kill = False
    watch_dir = None
    first_check = True
    def __init__(self, watch_dir, *args, **kw):
        '''
            @type watch_dir: C{str}
            @param watch_dir:

            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        self.watch_dir = watch_dir
        super(FileMonitor, self).__init__(*args, **kw)

    def start(self):
        '''
        '''
        self.info('Monitoring %s' % self.watch_dir)
        t = Thread(target=self._run_)
        t.start()

    def _run_(self, *args):
        '''
            @type *args: C{str}
            @param *args:
        '''
        while not self.kill:
            self._check()
            time.sleep(0.5)

    def _check(self):
        '''
        '''
        # check algorithm should be more sophisticated
        #now just check to see it the number of files changes
        def get_files():

            files = os.listdir(self.watch_dir)
            files = dict([(f, None) for f in files if f.endswith('.csv')])
            return files

        if self.first_check:
            self.first_check = False
            #self.files = get_files()
            self.before = get_files()
        else:
            self.after = get_files()
            added = [f for f in self.after if not f in self.before]
            removed = [f for f in self.before if not f in self.after]
            self.before = added

            if added:
                print 'added', ', '.join(added)
            if removed:
                print 'removed', ', '.join(removed)

#============= EOF ====================================
#import os, time
#path_to_watch = "."
#before = dict ([(f, None) for f in os.listdir (path_to_watch)])
#while 1:
#  time.sleep (10)
#  after = dict ([(f, None) for f in os.listdir (path_to_watch)])
#  added = [f for f in after if not f in before]
#  removed = [f for f in before if not f in after]
#  if added: print "Added: ", ", ".join (added)
#  if removed: print "Removed: ", ", ".join (removed)
#  before = after
