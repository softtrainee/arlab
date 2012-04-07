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
from traits.api import Instance, Directory, Str, Bool, String, Enum, \
    Int, Event
from traitsui.api import View, Item
#=============standard library imports ========================
from threading import Thread
import time
import os
#=============local library imports  ==========================

from src.loggable import Loggable
from src.managers.data_managers.csv_data_manager import CSVDataManager
from src.helpers.filetools import parse_file
from core_script_parser import CoreScriptParser
from src.graph.graph import Graph


class CoreScript(Loggable):
    '''
    '''
    graph = Instance(Graph, ())
    _thread = None
    _file_contents_ = None
    source_dir = Directory
    file_name = Str

    #user_cancel = False
    condition = None

    data_manager = Instance(CSVDataManager)

    parser = Instance(CoreScriptParser)
    parser_klass = None

    manager = None

    _alive = Bool(False)
    _display_msg = String
    #_ok_to_run = False
#    record_data = Bool(False)

    base_frame_name = None
    daughter_threads = None
    stoppable_scripts = None
    threaded = True

    progress_state = Enum('notrun', 'stopped', 'finished', 'inprogress')
    active_line = Int
    update = Event

    def __init__(self, *args, **kw):
        '''
            
        '''

        self.name = self.__class__.__name__
        super(CoreScript, self).__init__(*args, **kw)
        self.daughter_threads = []
        self.stoppable_scripts = []

    def get_documentation(self):
        return ''

    def info(self, msg, **kw):
        super(CoreScript, self).info(msg, **kw)
        self._display_msg = msg

    def join(self):
        self._thread.join()

    def bootstrap(self, new_thread=True):

        #load the file 
        p = os.path.join(self.source_dir, self.file_name)
        ok = False

        if os.path.isfile(p):
            self.file_path = p
            self._file_contents_ = parse_file(p)
            if self.load():
                #if self.set_data_frame():
                self.set_graph()
                self._alive = True
                ok = self.start(new_thread)
#                ok = True

        if not ok:
            self._alive = False

        return ok

    def load(self):
#        sv = ScriptValidator()
#
#        errors = sv.validate(self._file_contents_)
#
#        if not errors:
#            return True
        return True

    def kill_script(self, failure_reason=None, force=False, user_cancel=False):
        if self.isAlive() or force:
            self._kill_script()

            for s in self.stoppable_scripts:
                s.kill_script()

            fr = self.manager.failure_reason if self.manager is not None else failure_reason


            if user_cancel:
                self.info('run canceled by user')

            elif fr is not None:
                self.info(fr)


            self.info('{} finished'.format(self.file_name))
            #self._ok_to_run = False
        self._alive = False

    def _kill_script(self):
        '''
            hook for subclasses to implement
        '''
        pass

    def isAlive(self):
        '''
        
            this is way too confusing should be simplified
        '''
        r = self._alive

        if not self._alive:
            return False

        if self._thread is not None:
            r = self._thread.isAlive()


        if hasattr(self.manager, 'enabled'):
            r = self.manager.enabled and r

#        if not r and self.manager.failure_reason is None:
#            self.user_cancel = True

        #r = r and self._ok_to_run
        #self._alive = r
        #print 'isAlive', self._thread.isAlive(), self.manager.enabled, r
        return r

    def graph_view(self, **kw):
        return View(Item('graph', show_label=False, style='custom'), resizable=True)
    def set_graph(self):
        pass

    def set_data_frame(self, base_frame_name=None):
        '''
        '''
        dm = self.data_manager
#
#        if not self.default_save:
#            p = dm.save_file_dialog()
#
#            if p is not None:
#
#                dm.new_frame(p)
##                self.notes_enabled = True
#                return True
#
#        else:

        #if self.record_data:
        dm.new_frame(directory=self.name[:-6].lower(),
                     base_frame_name=base_frame_name)

        h = self.get_frame_header()
        for line in h:
            dm.write_to_frame(line)
#            self.notes_enabled = True
        return True

    def get_frame_header(self):
        return []

    def start(self, new_thread):
        #new_thread = True
        if new_thread:
            self._thread = Thread(target=self.run)
            self._thread.start()
            return True
        else:
            return self.run()

    def run(self):

        self.info('parsing {}'.format(self.file_name))

        errors = self.parser.parse(self._file_contents_, check_header=False)
#        print errors
        error = False

        for e in errors:
            if e[2] is not None:
                error = True
                self.warning('Line: {} - {}'.format(e[1], e[2]))

        if not error:
            #self._ok_to_run = True
            self.info('{} started'.format(self.file_name))
            if self._pre_run_():
                self._alive = True

                for i, line in enumerate(self._file_contents_):
                    self.info('setting progress to {}'.format('inpr'))
                    self.active_line = i
                    self.progress_state = 'inprogress'
                    if self.isAlive():
                        self._run_command(i, line)
                        self.progress_state = 'finished'
                    else:
                        self.progress_state = 'stopped'
                else:
                    self.progress_state = 'finished'

        else:
            self.warning('parsing unsuccessful')
            return

        #join any daughter threads before finishing
        for d in self.daughter_threads:
            d.join()

        if self._post_run():
            self.kill_script()

        return True

    def _progress_state_changed(self):
        self.update = True

    def _execute_script(self):
        raise NotImplementedError

    def _post_run(self):
        return True

    def _pre_run_(self):
        return self._file_contents_ is not None

    def _run_command(self, linenum, cmd, infor=False):
        '''
       
        '''
        cmd = cmd.strip()

        self.parser.set_lexer(cmd)
        token = self.parser.get_command_token()

        if token is None:
            token = 'raw'

        if not token.lower() == 'log':
            self.info(cmd)#

        # get a statement method 
        func = getattr(self, '{}_statement'.format(token.lower()))

        # get a parser method
        # all parsers should return a tuple
        #print token
        parser = getattr(self.parser, '_{}_parse'.format(token.lower()))

        func(*parser(0, line=cmd)[1:])

    def raw_statement(self, a):
        pass

    def config_statement(self, config_dict):
        for key in config_dict:
            if hasattr(self, key):
                value = config_dict[key]
                setattr(self, key, value)

    def wait(self, dur):
        st = time.time()
        cnt = 0
        while time.time() - st < dur:
            if not self.isAlive():
                cnt += 1
            else:
                cnt = 0

            if cnt > 3:
                break
            time.sleep(0.1)

        self.info('WAITING OVER')

    def _data_manager_factory(self):
        '''
        '''
        return CSVDataManager()

    def _data_manager_default(self):
        return self._data_manager_factory()

    def _parser_factory(self):
        if self.parser_klass is not None:
            return self.parser_klass()

    def _parser_default(self):
        return self._parser_factory()
#============= views ===================================
#============= EOF ====================================
