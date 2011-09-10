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
import time
#============= local library imports  ==========================


from src.scripts.core.script_helper import smart_equilibrate#, equilibrate
from src.scripts.core.core_script import CoreScript
from bakeout_script_parser import BakeoutScriptParser

class BakeoutScript(CoreScript):
    '''
        G{classtree}
    '''

    parser_klass = BakeoutScriptParser
    heat_ramp = 0
    heat_scale = None
    cool_ramp = 0
    cool_scale = None
    maintain_time = 1
    controller = None
    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText
        doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')
        doc.add_heading('Bakeout Documentation', heading=2, color='red')
        doc.add_heading('Parameters', heading=3)
        doc.add_text('Setpoint (C), Duration (min)')
        doc.add_list(['Setpoint (C) -- Bakeout Controller Setpoint',
                      'Duration (min) -- Heating duration'
                      ])
        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])

        r2 = HTMLText('150,360', face='courier', size='2')
        table.add_row([r2])

        return str(doc)

    def raw_statement(self, args):
        #change the setpoint temp
        if self.controller is not None:
            self.controller.setpoint = float(args[0])

        #wait for dur mins
        self.wait(float(args[1]) * 60)

    def kill_script(self):
        if self.controller is not None:
            self.controller.end(script_kill=True)
#        super(BakeoutScript, self).kill_script()
        CoreScript.kill_script(self)

    def wait_for_setpoint(self, sp, mean_check=True, std_check=False, mean_tolerance=5, std_tolerance=1, timeout=15):
        '''
            @type sp: C{str}
            @param sp:

            @type tolerance: C{str}
            @param tolerance:

            @type frequency: C{str}
            @param frequency:
        '''
        self.info('waiting for setpoint equilibration')
        if self.controller is not None:
            if self.controller.simulation:
                time.sleep(3)
            else:
                #equilibrate(sp, frequency = frequency, mean_check = True, mean_tolerance = tolerance)
                smart_equilibrate(self,
                                  self.controller.get_temperature,
                                  sp,
                                  mean_check=mean_check,
                                  std_check=std_check,
                                  mean_tolerance=mean_tolerance,
                                  std_tolerance=std_tolerance,
                                  timeout=timeout
                                  )

    def maintain(self, *args):
        '''
        '''
        if self.controller is not None:
            self.controller.led.state = 2
            if self.controller.simulation:
                mt = 3 / 60.
        else:
            mt = self.maintain_time

        self.info('Maintaining setpoint for %s minutes' % mt)
        mt *= 60
        st = time.time()
        while time.time() - st < mt and self.isAlive():
            time.sleep(1)

    def goto_setpoint(self, name):
        '''
            @type name: C{str}
            @param name:
        '''
        controller = self.controller
        r = getattr(self, '%s_ramp' % name)
        sp = getattr(self, '%s_setpoint' % name)
        s = getattr(self, '%s_scale' % name)

        if controller is not None:
            controller.led.state = -1
            controller.ramp_to_setpoint(r, sp, s)

        #wait until setpoint reached or ramping timed out
        kw = dict()
        if name == 'cool':
            kw['mean_check'] = False
            kw['std_check'] = True
            kw['std_tolerance'] = 5
            kw['timeout'] = 60
        self.wait_for_setpoint(sp, **kw)
#============= EOF ====================================
#    def load_file(self):
#        '''
#        '''
#
#        def set_ramp(a, attr):
#            scale = None
#            if ',' in a:
#                ramp, scale = a.split(',')
#            else:
#                ramp = a
#            setattr(self, '%s_ramp' % attr, float(ramp))
#            if scale is not None:
#                setattr(self, '%s_scale' % attr, float(scale))
#
#        f = self._file_contents_
#        h, t = self.file_name.split('.')
#        if t == 'bo':
#            set_ramp(f[0], 'heat')
#            self.heat_setpoint = float(f[1])
#            self.maintain_time = int(f[2])
#            set_ramp(f[3], 'cool')
#            self.cool_setpoint = float(f[4])
#        else:
#            self.kind = 'step'
#
#        return True
#    def _execute_raw_line(self, line):
#        args = line.split(',')
#        sp = float(args[0])
#        dur = 1
#        if len(args) == 2:
#            dur = float(args[1])
#
#        #change the setpoint temp
##        self.manager.setpoint = sp
#
#        #wait for dur mins
#        self.wait(dur * 60)

#    def _run_(self):
#        '''
#        '''
#        self.manager.led.state = 0
#        if self.kind == 'ramp':
#            for func, args in [(self.goto_setpoint, ('heat',)),
#                               (self.maintain, tuple()),
#                               (self.goto_setpoint, ('cool',)),
#                              # (self.manager.end, tuple())
#                               ]:
#
#                if self.isAlive():
#                    func(*args)
#        else:
#            for i in self._file_contents_:
#
#
#                args = i.split(',')
#                sp = float(args[0])
#                dur = 1
#                if len(args) == 2:
#                    dur = float(args[1])
#
#                self.manager.setpoint = sp
##                if not self.isAlive():
##                    break
#
#                self.wait(dur * 60)
##                st = time.time()
##                while time.time() - st < dur * 60.:
##                    if not self.isAlive():
##                        break
#                    #time.sleep(0.5)
