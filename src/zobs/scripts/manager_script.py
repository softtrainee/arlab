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



'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Property, Any, Button, Event, Bool, String
from traitsui.api import Item, HGroup, \
    ButtonEditor
#from enable.savage.trait_defs.ui.svg_button import SVGButton

#=============standard library imports ========================
from thread import start_new_thread
import time
#=============local library imports  ==========================

from src.managers.data_managers.data_manager import DataManager

from src.loggable import Loggable
from src.managers.data_managers.csv_data_manager import CSVDataManager


class ManagerScript(Loggable):
    '''
        G{classtree}
    '''
    data_manager = None
    manager = Any
    start_button = Event
    start_label = Property(depends_on='_alive')
    _alive = Bool(False)

    notes_button = Button('Notes')
    notes = String
    notes_enabled = Bool(False)
    default_save = Bool(True)
    '''
    '''
    #stop_button = SVGButton(label = 'Stop',
    #               filename = os.path.join(os.getcwd(), 'resources', 'stop.svg'))

    user_cancel = False
    condition = None
    def __init__(self, *args, **kw):
        '''
            @type manager: C{str}
            @param manager:
        '''

        self.name = self.__class__.__name__
        super(ManagerScript, self).__init__(*args, **kw)
        self.start_args = ()

        self.data_manager = self._data_manager_factory()

    def _get_start_label(self):
        '''
        '''
        return 'Start' if not self._alive else 'Stop'


    def isAlive(self):
        '''
        '''
        if self.manager is None:
            a = self._alive
        else:
            if hasattr(self.manager, '_enabled'):
                a = self._alive and self.manager._enabled# or self.manager.simulation)
            else:
                a = self._alive

            if not a and self.manager.failure_reason is None:
                self.user_cancel = True

        return a


    def set_data_frame(self):
        '''
        '''

        dm = self.data_manager

        if not self.default_save:
            p = dm.save_file_dialog()

            if p is not None:

                dm.new_frame(p)
#                self.notes_enabled = True
                return True

        else:

            dm.new_frame(None, directory=self.name[:-6].lower(), base_frame_name='run')
#            self.notes_enabled = True
            return True



    def run(self, *args):
        '''
            @type *args: C{str}
            @param *args:
        '''
        if self.condition is not None:
            self.condition.acquire()
        self._alive = True
        self._run_()
        self._end_run_()

    def _end_run_(self):
        '''
        '''
        #self.trait_set(start_label='Start')
        #print self.start_label
        #self.start_label = 'Start'
        self.kill_script()
        self.info('%s finished' % self.name)
        #print 

    def start(self):
        '''
        '''
        start_new_thread(self.run, self.start_args)

    def kill_script(self):
        '''
        '''
        self._alive = False
        if self.condition is not None:
            self.condition.notify()
            self.condition.release()

    def _notes_button_fired(self):
        '''
        '''
        self.add_note()

    def add_note(self):
        '''
        '''
        self.data_manager.add_note()


    def _start_fired(self):
        '''
        '''
        return True

    def _start_button_fired(self):
        '''
        '''
        if not self._alive:
            if self._start_fired():
                self._alive = True
                #self.start_label = 'Stop'
        else:
            self.kill_script()

    def _button_group_factory(self):
        '''
        '''
        return HGroup(Item('start_button',
                           #style='custom',
                           editor=ButtonEditor(label_value='start_label')),
                      Item('notes_button', enabled_when='notes_enabled'),
                           show_labels=False)

    def _data_manager_factory(self):
        '''
        '''
        return CSVDataManager()

    def wait(self, dur):
        st = time.time()
        while time.time() - st < dur:
            if not self.isAlive():
                break
            time.sleep(0.01)
#=========== EOF ================
    #def _data_manager_default(self):
    #    return DataManager()
#    def traits_view(self):
#        return View(HGroup('start_button','stop_button',show_labels=False))#Item('stop', show_label = False))
