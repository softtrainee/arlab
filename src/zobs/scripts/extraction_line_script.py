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
from traits.api import Enum
from pyface.timer.api import do_later

#============= standard library imports ========================
from threading import Condition
import time
import os
#============= local library imports  ==========================
from src.scripts.core.core_script import CoreScript
from src.helpers.filetools import parse_file
from src.helpers.datetime_tools import generate_datetimestamp
from wait_dialog import WaitDialog
from extraction_line_script_parser import ExtractionLineScriptParser
#from src.scripts.analysis.analysis_script import AnalysisScript
from src.scripts.measurement.measurement_script import MeasurementScript

class Sniffer:
    def sniff(self):
        nsniff = 6
        #record a block of spectrometer data
        data = []
        for i in range(nsniff):
            data.append(i)

        #analysis the data
        action = self.analyze_data(data)

        #return the sniff action
        return action

    def analyze_data(self, data):

        action = 'continue'
        #action = 'signal too high'
        #action = 'signal too low'
        return action


class ExtractionLineScript(CoreScript):
    parser_klass = ExtractionLineScriptParser
    getter_time = 0
    temp_or_power = 0
    heat_duration = 0
    hole = 0
    kind = Enum('analysis', 'blank')
    debug = False
    eq_time = 15

    @classmethod
    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText
        return ''



    #===========================================================================
    # statements
    #===========================================================================
    def sniff_statement(self, *args):
#        bootstrap a new sniffer
        ss = Sniffer(
                    )
#        ss.path = '/Users/Ross/Desktop/sniff.rs'
        action = ss.sniff()
        if action == 'signal too low':
            self._ok_to_run = False
            self.warning(action)

        #daughter threads are joined just before the script is killed
        #so that the script will wait for the daughter before finishing 
        #self.daughter_threads.append(t)

#    def extraction_analysis_statement(self, *args):
#        #bootstrap an analysis script
#        an = MeasurementScript(
#                            source_dir=os.path.join(scripts_dir, 'analysis'),
#                            file_name='test.rs'
#
#                            )
#        an.bootstrap()
#        self.stoppable_scripts.append(an)

    def define_statement(self, define_dict):
        for key in define_dict:
            value = define_dict[key]
            setattr(self.script, key, value)

    def set_time_zero_statement(self):

        msg = 'time zero %s' % generate_datetimestamp()
        self.time_zero = time.time()

        self.log_statement(msg)

    def get_time_zero(self, eqtime):
        return self.time_zero + eqtime * 2 / 3.0

    def wait_statement(self, wtime, N=5):
        '''

        '''

        start_time = time.time()
        if self.debug:
            time.sleep(1)

        else:
            if isinstance(wtime, str):
                wtime = float(self._get_interpolation_value(wtime))

            if wtime > N:
                c = Condition()
                c.acquire()
                wd = WaitDialog(wtime=wtime,
                                    condition=c,
                                    parent=self)
                do_later(wd.edit_traits, kind='livemodal')
                c.wait()
                c.release()
                do_later(wd.close)
            else:
                time.sleep(wtime)

        msg = 'actual wait time %0.3f s' % (time.time() - start_time)
        self.log_statement(msg)

    def if_statement(self, condition, tout, fout):
        '''
        '''
        if eval(condition):
            self._run_command(-1, tout)
        elif fout is not None:
            self._run_command(-1, fout)

    def log_statement(self, msg):
        '''
        '''
        if msg.startswith("'"):
            msg = msg[1:]

        if msg.endswith("'"):
            msg = msg[:-1]

        self.logger.info('====== %s ======' % msg)

    def for_statement(self, start, lim, step, command):
        '''

        '''
        for i in range(start, lim, step):
            for c in command:
                for op in ['+', '-', '*', '^', '/']:
                    if op in c and '---' not in c:
                        com, args = c.split(' ')
                        args = args.split(op)

                        if args[0] == 'i':
                            a = i
                            b = int(args[1])
                        else:
                            a = int(args[0])
                            b = i

                        if op == '+':
                            c = com + ' %s' % (a + b)
                        elif op == '-' :
                            c = com + ' %s' % (a - b)
                        elif op == '/':
                            c = com + ' %s' % (a / b)
                        elif op == '*':
                            c = com + ' %s' % (a * b)
                        elif op == '^':
                            c = com + ' %s' % (a ** b)
                        break

                if '---' in c and '%i' in c:
                    c = c % i
                self.run_command(c, infor=True)

    def valve_statement(self, valve_name, open_close):
        '''
        execute a valve statement
        send control to manager ie extractionlinemanager
        @type valve_name: C{str}
        @param valve_name: id of the valve
        @type open_close: boolean
        @param open_close: True to open, False to close valve
        '''
        if self.manager is not None:
            if open_close:
                fname = 'open_valve'
#                self.manager.do('open_valve', valve_name)
            else:
                fname = 'close_valve'
#                self.manager.do('close_valve', valve_name)
            kw = dict()
            if self.debug:
                kw['mode'] = 'debug'

            resp = getattr(self.manager, fname)(valve_name, **kw)
            if resp:
                time.sleep(1)

    def sub_statement(self, subpath):
        '''
            @type subpath: C{str}
            @param subpath:
        '''
        #c = self.cond
        for i, cmd in enumerate(parse_file(subpath)):
            self._run_command(i, cmd)
            #ri = ExtractionLineScriptItem(self, c, cmd, self.logger)
            #ri.start()

    def warning_statement(self, statement):
        '''
            @type statement: C{str}
            @param statement:
        '''
        #warning(None, statement)
        self.logger.warning('****** %s ******' % statement)

    def close_stage_manager_statement(self):
        self.device_statement(self.laser_manager_id, 'close_stage_manager', None, None)

    def move_to_hole_statement(self, hole, kw):
        self.device_statement(self.laser_manager_id, 'move_to_hole', hole, kw)

    def enable_laser_statement(self):
        self.device_statement(self.laser_manager_id, 'enable_laser', None, None)

    def disable_laser_statement(self):
        self.device_statement(self.laser_manager_id, 'disable_laser', None, None)

    def set_laser_power_statement(self, power, kw):
        self.device_statement(self.laser_manager_id, 'set_laser_power', power, kw)

    def set_beam_diameter_statement(self, diameter, kw):
        self.device_statement(self.laser_manager_id, 'set_beam_diameter', diameter, kw)

    def device_statement(self, device, func, args, kw):
        '''
            @type device: C{str}
            @param device:

            @type func: C{str}
            @param func:
        '''
        if self.debug:
            msg = 'debug device statement %s %s %s %s' % (device, func, args, kw)
            self.log_statement(msg)
        else:
            if args is not None:
                if isinstance(args, (str, int, float)):
                    args = [args]
                #check for interpolation keys
                for i, a in enumerate(args):
                    if isinstance(a, str):
                        if a[0] == '%':
                            args[i] = self._get_interpolation_value(a)
            if self.manager is not None:
                try:
                    dev = getattr(self.manager, device)
                    try:

                        f = getattr(dev, func)

                        if args:

                            if kw:
                                r = f(*args, **kw)
                            else:
                                r = f(*args)
                        elif kw:
                            r = f(**kw)
                        else:
                            r = f()

                        self.current_temp = r
                    except AttributeError, e:
                        self.logger.warning('****** %s not available %s******' % (func, e))
                except AttributeError:
                    self.logger.warning('****** %s not available******' % device)
            else:
                self.logger.warning('****** No Extraction Line Manager ******')


#============= views ===================================
#============= EOF ====================================

#
##============= enthought library imports =======================
#from traits.api import Button, Float, Enum, Int
#from traitsui.api import Item
##============= standard library imports ========================
#from threading import Condition
##============= local library imports  ==========================
##import time
##st=time.time()
#from file_script import FileScript
##print 'file script load time %0.5f'%(time.time()-st)
#
#from extraction_line_script_item import ExtractionLineScriptItem
#from src.scripts.core.script_validator import ScriptValidator
#
#
#class ExtractionLineScript(FileScript):
#    '''
#        G{classtree}
#    '''
#    edit = Button
#
#    getter_time = Float
#    power = Float
#    time_at_temp = Float
#    hole = Int
#    kind = Enum('analysis', 'blank')
#    debug = False
#    def _edit_fired(self):
#        '''
#
##        from src.scripts.script_writer import ScriptWriter
##        s = ScriptWriter()
##
##        f = self.file_name
##        if f is None:
##            f = self.available_scripts[0]
##
##        p = os.path.join(self.source_dir, f)
##        s.add_script(p)
##        s.edit_traits()
#        '''
#        pass
#    def load_file(self):
#        '''
#        _file_contents_ is now loaded
#        
#        
#        '''
#        #the script loaded into _file_contents may not be valid
#
#        #use a scriptvalidator to validate the script and recursively
#        # validate any subroutines
#
#        sv = ScriptValidator()
#
#        errors = sv.validate(self._file_contents_)
#
#        if errors:
#            return True
#
#    def _button_group_factory(self):
#        '''
#        '''
#        grp = super(ExtractionLineScript, self)._button_group_factory()
#        grp.content.append(Item('edit', show_label = False))
#        return grp
#
#    def _run_(self):
#        '''
#        '''
#        print 'asdfasdf'
#        self.info('%s started' % self.file_name)
#
#        c = Condition()
#        c.acquire()
#        for line in self._file_contents_:
#            if self.isAlive():
#                ri = ExtractionLineScriptItem(self, c, line, self.logger)
#                ri.start()
#                c.wait()
#
#        c.release()
#
#        self.info('%s finished' % self.file_name)

#============= EOF ====================================
