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

TIMEDICT = dict(s=1, m=60.0, h=60.0 * 60.0)

class BakeoutScript(CoreScript):
    '''
    '''

    parser_klass = BakeoutScriptParser
    heat_ramp = 0
    cool_ramp = 0
    scale = 'h'
    maintain_time = 1
    controller = None

    kind = None
    current_setpoint = 0

    @classmethod
    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText
        doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')
        doc.add_heading('Bakeout Documentation', heading=2, color='red')
        doc.add_heading('Parameters', heading=3)
        doc.add_text('Setpoint (C), Duration (min)')
        doc.add_list(['Setpoint (C) -- Bakeout Controller Setpoint',
                      'Duration (hrs) -- Heating duration'
                      ])
        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])

        r2 = HTMLText('150,360', face='courier', size='2')
        table.add_row([r2])

        return str(doc)

    def ramp_statement(self, args):
        c = self.controller

        if c is not None:
            if not c.isAlive():
                return

            setpoint = float(args[0])
            ramp_rate = float(args[1])
            try:
                unit_name = args[2]
                unit = TIMEDICT[unit_name]
            except (IndexError, KeyError):
                unit_name = 's'
                unit = 1

            try:
                n_update = float(args[3])
            except IndexError:
                n_update = 1

            s_start = c.closed_loop_setpoint
            s_end = setpoint
            self.info('ramping from {} to {}, rate= {} C/{}'.format(s_start,
                                                                    s_end,
                                                                    ramp_rate,
                                                                    unit_name
                                                                    ))

            ramp_rate_hrs = (ramp_rate / unit) * 3600.
            dt = s_end - s_start
            c.duration = abs(dt / ramp_rate_hrs)
            step = int(ramp_rate / n_update)
            for si in xrange(int(s_start), int(s_end) + step, step):
                if not c.isAlive():
                    break

                self.set_setpoint(si)
                time.sleep(unit / n_update)

    def set_setpoint(self, sp):
        if self.controller.setpoint == sp:
            if self.controller.isAlive():
                self.controller.set_closed_loop_setpoint(sp)
        else:
            self.controller.setpoint = sp



    def raw_statement(self, args):

        #change the setpoint temp
        if self.controller is not None:
            sp = float(args[0])
            self.set_setpoint(sp)
            self.controller.duration = float(args[1])
        #wait for dur 
        self.wait(float(args[1]) * TIMEDICT[self.scale])

    def kill_script(self):
        if self.controller is not None:
            self.controller.end(script_kill=True)
        super(BakeoutScript, self).kill_script()

    def maintain_statement(self, mt):
        '''
        '''
        if self.controller is not None:
            self.controller.led.state = 2

        self.info('Maintaining setpoint for {} {}'.format(mt, self.scale))
        mt *= TIMEDICT[self.scale]

        st = time.time()
        self.controller.duration = mt / 3600.
        cnt = 1
        sleep_time = 5
        while time.time() - st < mt and self.isAlive():
            time.sleep(sleep_time)
            self.controller._duration = self.controller._oduration - cnt * sleep_time / 3600.
            #print 'f', cnt, self.controller._duration, self.controller._oduration
            cnt += 1

    def goto_statement(self, setpoint):
        '''

        '''
        controller = self.controller

        if setpoint > self.current_setpoint:
            name = 'heat'
        else:
            name = 'cool'

        ramp = float(getattr(self, '{}_ramp'.format(name)))
        #sp = getattr(self, '{}_setpoint'.format(name))

        if controller is not None:
            controller.led.state = -1
            controller.ramp_to_setpoint(ramp, setpoint, self.scale)

        #wait until setpoint reached or ramping timed out
        kw = dict()
        if name == 'cool':
            kw['mean_check'] = False
            kw['std_check'] = True
            kw['std_tolerance'] = 5
            kw['timeout'] = 60
        self._wait_for_setpoint(setpoint, **kw)

    def _wait_for_setpoint(self, sp, mean_check=True, std_check=False,
                            mean_tolerance=5, std_tolerance=1, timeout=15):
        '''

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
