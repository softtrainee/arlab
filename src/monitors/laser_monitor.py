#============= enthought library imports =======================
from traits.api import Float

#============= standard library imports ========================
import time
#============= local library imports  ==========================
from monitor import Monitor

NFAILURES = 3
NTRIES = 3
class LaserMonitor(Monitor):
    '''
        G{classtree}
    '''
    #manager = None
    max_duration = Float(60) # in minutes

    max_coolant_temp = Float(25)

    gntries = 0
    def load_additional_args(self, config):
        '''
        '''

        self.set_attribute(config, 'max_duration',
                           'General', 'max_duration', cast = 'float', optional = True)



        return True


    def __check_duration(self):
        '''
        '''
        #check max duration
        manager = self.manager
        #self.info('Check duration')

        #max duration in mins convert to secs for comparison
        if time.time() - self.start_time > self.max_duration * 60.0:
            self.warning('Max duration %s (min) exceeded' % self.max_duration)
            manager.emergency_shutoff(reason = 'Max duration exceeded')


#============= EOF ====================================
