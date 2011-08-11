#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.hardware.core.core_device import CoreDevice

class GPActuator(CoreDevice):
    def get_channel_state(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        raise NotImplementedError
    def open_channel(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        raise NotImplementedError
    def close_channel(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        raise NotImplementedError
#============= views ===================================
#============= EOF ====================================
