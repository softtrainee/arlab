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

#=============enthought library imports=======================
#=============standard library imports ========================
import time
#=============local library imports  ==========================
from src.scripts.file_script import FileScript
class CalibrationScript(FileScript):
    '''
        G{classtree}
    '''
    def load_file(self):
        '''
        '''
        self.step_interval = int(self._file_contents_[0])
        sp, ep, stp = [int(i) for i in self._file_contents_[1].split(',')]
        self.power_steps = xrange(sp, ep + 1, stp)

    def kill_script(self):
        '''
        '''
        super(CalibrationScript, self).kill_script()

        m = self.manager
        m.disable_laser()
        m.stream_manager.stop_streams()

    def _run_(self):
        '''
        '''

        sm = self.manager.stream_manager

        for name in sm.streamids:
            self.data_manager.add_group(name)
            table = 'stream'
            self.data_manager.add_table(table, parent = 'root.%s' % name)
            sm.set_stream_tableid(name, 'root.%s.%s' % (name, table))


        self.progress.add_text('Starting streams')
        sm.start_streams()

        time.sleep(2)

        self.progress.add_text('Firing laser')
        self.manager.enable_laser()


        for pi in self.power_steps:
            self.progress.add_text('Set laser power %0.2f' % pi)
            self.manager.set_laser_power(pi, 'open')
            time.sleep(self.step_interval)

        self.manager.disable_laser()

        cd = 10
        self.progress.add_text('Cooling down for %i (secs)' % cd)
        time.sleep(cd)

        sm.stop_streams()
        #sm.edit_traits()


