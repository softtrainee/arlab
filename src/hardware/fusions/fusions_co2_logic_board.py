#=============enthought library imports=======================
from traits.api import Float, Property
#=============standard library imports ========================

#=============local library imports  ==========================
from fusions_logic_board import FusionsLogicBoard

class FusionsCO2LogicBoard(FusionsLogicBoard):
    '''
    '''

    request_power = Property(Float(enter_set = True, auto_set = False),
                            depends_on = '_request_power')
    _request_power = Float
    request_powermin = Float(0)
    request_powermax = Float(100)

    def _get_request_power(self):
        '''
        '''
        return self._request_power

    def _set_request_power(self, v):
        '''
        '''

        self._set_laser_power_(v)

#    def _request_power_changed(self):
#        
#        self._set_laser_power_(self.request_power)

    def load_additional_args(self, config):
        '''
        '''

        self.set_attribute(config, 'request_powermin', 'General', 'power min', cast = 'float')
        self.set_attribute(config, 'request_powermax', 'General', 'power max', cast = 'float')

        return FusionsLogicBoard.load_additional_args(self, config)
#        return super(FusionsCO2LogicBoard, self).load_additional_args(config)

    def _disable_laser_(self):
        '''
        '''
        cmd = '%s%s' % (self.prefix, 'PDC 0.00')
        self._request_power = 0.0
        self.ask(cmd)
        return FusionsLogicBoard._disable_laser_(self)

    def _enable_laser_(self):
        '''
        '''
        self.ask(self.prefix + 'PWE 1')
        return FusionsLogicBoard._enable_laser_(self)


    def _set_laser_power_(self, request_pwr):
        '''
            
            see Photon Machines Logic Board Command Set Reference
            version 0.96
            
            this version uses PDC instead of PWW and PWE (pwm mode) to set the laser power
            
            request power valid range 0 100 with 0.02 resolution
            
            PDC sets the laser Duty Cycle
        '''
        self._request_power = request_pwr

        cmd = 'PDC'
        cmd = ''.join([self.prefix, cmd, ' %0.2f' % request_pwr])

        #cmd=self.prefix + 'PWW %s' % request_pwr
        self.ask(cmd)
#====================== EOF ===========================================

