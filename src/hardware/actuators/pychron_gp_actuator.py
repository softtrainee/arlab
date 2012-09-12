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

#========== standard library imports ==========

#========== local library imports =============
from gp_actuator import GPActuator


class PychronGPActuator(GPActuator):
    '''
        
    '''
#    id_query = '*TST?'

#    def id_response(self, response):
#        if response.strip() == '0':
#            return True

#    def initialize(self, *args, **kw):
#        '''
#        '''
#        self._communicator._terminator = chr(10)
#
#        #clear and record any accumulated errors
#        errs = self._get_errors()
#        if errs:
#            self.warning('\n'.join(errs))
#        return True

#    def _get_errors(self):
#        #maximum of 10 errors so no reason to use a while loop
#
#        errors = []
#        for _i in range(10):
#            error = self._get_error()
#            if error is None:
#                break
#            else:
#                errors.append(error)
#        return errors
#
#    def _get_error(self):
#        error = None
#        cmd = 'SYST:ERR?'
#        if not self.simulation:
#            s = self.ask(cmd)
#            if s is not None:
#                if s != '+0,"No error"':
#                    error = s
#
#        return error

    def _get_valve_name(self, obj):
        if isinstance(obj, (str, int)):
            addr = obj
        else:
            addr = obj.name.split('-')[1]
        return addr

    def get_channel_state(self, obj):
        '''
        Query the hardware for the channel state
         
        '''

        # returns one if channel close  0 for open
        boolfunc = lambda x:True if x in ['True', 'true', 'T', 't'] else False
        cmd = 'GetValveState {}'.format(self._get_valve_name(obj))
        resp = self.ask(cmd)
        if resp is not None:
            resp = boolfunc(resp.strip())

        return resp

    def close_channel(self, obj, excl=False):
        '''
        Close the channel
      
        '''
        cmd = 'Close {}'.format(self._get_valve_name(obj))
        resp = self.ask(cmd)
        if resp:
            if resp.lower().strip() == 'ok':
                resp = self.get_channel_state(obj) == True
        return resp

    def open_channel(self, obj):
        '''
        Close the channel
        
   
        '''
        cmd = 'Open {}'.format(self._get_valve_name(obj))
        resp = self.ask(cmd)
        if resp:
            if resp.lower().strip() == 'ok':
                resp = self.get_channel_state(obj) == True
#        cmd = 'ROUT:OPEN (@{})'.format(self._get_valve_name(obj))
#        self.tell(cmd)
#        if self.simulation:
#            return True
        return resp

#============= EOF =====================================
