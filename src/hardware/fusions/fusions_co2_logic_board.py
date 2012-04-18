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
from traits.api import Float, Property
#=============standard library imports ========================

#=============local library imports  ==========================
from fusions_logic_board import FusionsLogicBoard


class FusionsCO2LogicBoard(FusionsLogicBoard):
    '''
    '''
    request_power = Property(Float(enter_set=True, auto_set=False),
                            depends_on='_request_power')
    _request_power = Float
    request_powermin = Float(0)
    request_powermax = Float(100)

    def load_additional_args(self, config):
        '''
        '''
        self.set_attribute(config, 'request_powermin', 'General',
                           'power min', cast='float')
        self.set_attribute(config, 'request_powermax', 'General',
                            'power max', cast='float')

        return super(FusionsCO2LogicBoard, self).load_additional_args(config)

    def read_power_meter(self, verbose=False):
        '''
        '''
        cmd = self._build_command('ADC1')
        r = self._parse_response(self.ask(cmd, verbose=verbose))

        if r is not None:
            try:
                r = float(r)
            except:
                self.warning('*Bad response from ADC ==> %s' % r)
                r = None

        return r

    def _disable_laser_(self):
        '''
        '''
#        cmd = self._build_command('PDC', '0.00')
        cmd = ('PDC', '0.00')
        self._request_power = 0.0

#        callback = lambda :self._parse_response(self.ask(cmd))
        resp = self.repeat_command(cmd, check_val='OK')
        if resp is not None:
            return FusionsLogicBoard._disable_laser_(self)
        else:
            msg = 'failed to disable co2 laser'
            self.warning(msg)
            return msg

    def _enable_laser_(self):
        '''
        '''
        cmd = self._build_command('PWE', '1')

#        callback = lambda :self._parse_response(self.ask(cmd))
        resp = self.repeat_command(cmd, check_val='OK')
        if resp is not None:

            return FusionsLogicBoard._enable_laser_(self)
        else:
            msg = 'failed to enable co2 laser'
            self.warning(msg)
            return msg

    def _set_laser_power_(self, request_pwr):
        '''
            
            see Photon Machines Logic Board Command Set Reference
            version 0.96
            
            this version uses PDC instead of PWW and PWE (pwm mode) to set the laser power
            
            request power valid range 0 100 with 0.02 resolution
            
            PDC sets the laser Duty Cycle
        '''
        self._request_power = request_pwr

        cmd = self._build_command('PDC', '{:0.2f}'.format(request_pwr))

        self.ask(cmd)

    def _get_request_power(self):
        '''
        '''
        return self._request_power

    def _set_request_power(self, v):
        '''
        '''
        self._set_laser_power_(v)

#====================== EOF ===========================================

