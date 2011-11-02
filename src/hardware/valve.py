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
from traits.api import  Str, Any, Bool, List

#============= standard library imports ========================

#============= local library imports  ==========================
from state_machine.valve_FSM_sm import Valve_sm
from src.loggable import Loggable
class HardwareValve(Loggable):
    '''
    '''
    name = Str

    address = Str
    actuator = Any

    success = Bool(False)
    interlocks = List
    state = Bool(False)
    debug = False
    error = None
    software_lock = False

    def __init__(self, *args, **kw):
        '''
     
        '''
        if 'name' in kw:
            kw['name'] = 'VALVE-{}'.format(kw['name'])

        super(HardwareValve, self).__init__(*args, **kw)
        self._fsm = Valve_sm(self)

    def get_hardware_state(self):
        '''
        '''
        if self.actuator is not None:
            r = self.actuator.get_channel_state(self)
            if r is None:
                r = False
        else:
            r = False

        self.state = r
        if r:
            self._fsm.ROpen()
        else:
            self._fsm.RClose()

        return r

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
        self.info('%s open' % mode)
        self.debug = mode == 'debug'

        self._fsm.Open()
#        if mode in ['auto', 'manual', 'debug', 'remote']:
#            self._fsm.Open()

        result = self.success
        if self.error is not None:
            result = self.error
            self.error = None

        return result

    def close(self, mode='normal'):
        '''

        '''
        self.info('%s close' % mode)

        self.debug = mode == 'debug'
#        if mode in ['auto', 'manual', 'debug', 'remote']:
#            self._fsm.Close()
        self._fsm.Close()

        result = self.success
        if self.error is not None:
            result = self.error
            self.error = None

        return result

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
            if self.debug:
                r = True
            else:
                r = True if self.actuator.open_channel(self) else False

        self.success = r
        if self.success:
            self.state = True


    def _close_(self, *args, **kw):
        '''

        '''

        r = False
        if self.actuator is not None:
            if self.debug:
                r = True
            else:
                r = True if self.actuator.close_channel(self) else False

        self.success = r

        if self.success:
            self.state = False

#    def warning(self, msg):
#        '''
#            @type msg: C{str}
#            @param msg:
#        '''
##        super(HardwareValve, self).warning(msg)
#        Loggable.warning(self, msg)
#        self.success = False


#============= EOF ====================================
