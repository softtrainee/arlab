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
from traits.api import  Str, Any, Bool, List, Float, Int, DelegatesTo, Property
from traitsui.api import View, HGroup, Item, VGroup
#============= standard library imports ========================

#============= local library imports  ==========================
from state_machine.valve_FSM_sm import Valve_sm
from src.loggable import Loggable


class HardwareValve(Loggable):
    '''
    '''
    name = Str
    display_name = Str

    address = Str
    actuator = Any

    success = Bool(False)
    interlocks = List
    state = Bool(False)
    display_state = Property(depends_on='state')
    display_software_lock = Property(depends_on='software_lock')
    debug = False
    error = None
    software_lock = False

    cycle_period = Float(1)
    cycle_n = Int(3)
    sample_period = Float(1)

    actuator_name = DelegatesTo('actuator', prefix='name')

    canvas_valve = Any
    position = Property
    shaft_low = Property
    shaft_high = Property

    query_state = Bool(True)

    def _get_shaft_low(self):
        return self.canvas_valve.low_side.orientation

    def _get_shaft_high(self):
        return self.canvas_valve.high_side.orientation

    def _get_position(self):
        return ','.join(map(str, self.canvas_valve.translate))

    def __init__(self, name, *args, **kw):
        '''
     
        '''
        self.display_name = name
        kw['name'] = 'VALVE-{}'.format(name)

        super(HardwareValve, self).__init__(*args, **kw)
        self._fsm = Valve_sm(self)

    def is_name(self, name):
        if len(name) == 1:
            name = 'VALVE-{}'.format(name)
        return name == self.name


    def get_hardware_state(self):
        '''
        '''
        result = None
        if self.actuator is not None:
            result = self.actuator.get_channel_state(self)
            if result is not None:
                self.state = result

                if result:
                    self._fsm.ROpen()
                else:
                    self._fsm.RClose()

        return result

    def get_hard_lock(self):
        '''
        '''
        if self.actuator is not None:
            r = self.actuator.get_hard_lock_indicator_state(self)
        else:
            r = False

        return r

    def get_hard_lock_indicator_state(self):
        '''
        '''

        s = self.get_hardware_state()
        r = self.get_hard_lock()

        if r:
            if s:
                self._fsm.HardLockOpen()
            else:
                self._fsm.HardLockClose()
        else:
            self._fsm.HardUnLock()
        #print self.auto
        return r

    def open(self, mode='normal'):
        '''

        '''
        self._state_change = False
        self.info('%s open' % mode)
        self.debug = mode == 'debug'

        self._fsm.Open()

#        if mode in ['auto', 'manual', 'debug', 'remote']:
#            self._fsm.Open()

        result = self.success
        if self.error is not None:
            result = self.error
            self.error = None

        return result, self._state_change

    def close(self, mode='normal'):
        '''

        '''
        self._state_change = False
        self.info('%s close' % mode)

        self.debug = mode == 'debug'
#        if mode in ['auto', 'manual', 'debug', 'remote']:
#            self._fsm.Close()
        self._fsm.Close()

        result = self.success
        if self.error is not None:
            result = self.error
            self.error = None

        return result, self._state_change

#    def acquire_critical_section(self):
#        self._critical_section = True
#    
#    def release_system_lock(self):
#        self._critical_section = False
#    
#    def isCritical(self):
#        return self._critical_section

    def lock(self):
        if self.state:
            self._fsm.LockOpen()
        else:
            self._fsm.LockClose()
        self.software_lock = True

    def unlock(self):
        '''
        '''
        self.software_lock = False
        self._fsm.Unlock()

    def _error_(self, message):
        self.error = message
        self.warning(message)

    def _open_(self, *args, **kw):
        '''

        '''
        r = False
        if self.actuator is not None:
            if self.debug or self.actuator.simulation:
                r = True
            else:
                r = True if self.actuator.open_channel(self) else False

        self.success = r
        if self.success:
            self.state = True
            self._state_change = True
#        print 'open', self.success, self.state

    def _close_(self, *args, **kw):
        '''

        '''
        r = False
        if self.actuator is not None:
            if self.debug or self.actuator.simulation:
                r = True
            else:
                r = True if self.actuator.close_channel(self) else False

        self.success = r

        if self.success:
            self.state = False
            self._state_change = True
#        print 'close', self.success, self.state

    def _get_display_state(self):
        return 'Open' if self.state else 'Close'

    def _get_display_software_lock(self):
        return 'Yes' if self.software_lock else 'No'

    def traits_view(self):
        info = VGroup(
                    Item('display_name', label='Name', style='readonly'),
                    Item('display_software_lock', label='Locked', style='readonly'),
                    Item('address', style='readonly'),
                    Item('actuator_name', style='readonly'),
                    Item('display_state', style='readonly'),
                    show_border=True,
                    label='Info'
                    )
        sample = VGroup(
                       Item('sample_period', label='Period (s)'),
                       label='Sample',
                       show_border=True
                       )
        cycle = VGroup(
                   Item('cycle_n', label='N'),
                   Item('sample_period', label='Period (s)'),
                   label='Cycle',
                   show_border=True
                   )
        geometry = VGroup(
                          Item('position', style='readonly'),
                          Item('shaft_low', style='readonly'),
                          Item('shaft_high', style='readonly'),
                          label='Geometry',
                          show_border=True
                          )
        return View(
                    VGroup(info, sample, cycle, geometry),

                    buttons=['OK', 'Cancel'],
                    title='{} Properties'.format(self.name)
                    )
#    def warning(self, msg):
#        '''
#            @type msg: C{str}
#            @param msg:
#        '''
##        super(HardwareValve, self).warning(msg)
#        Loggable.warning(self, msg)
#        self.success = False

#============= EOF ====================================
