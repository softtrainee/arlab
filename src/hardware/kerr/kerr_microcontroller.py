#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from kerr_device import KerrDevice
class KerrMicrocontroller(KerrDevice):
    '''
        Provides access to a `Kerr Controller board <http://www.jrkerr.com/boards.html>`_. 
        Used for controlling stepper motors and servos. 
    '''
    address = '00'
    def initialize(self, *args, **kw):
        '''
        '''
        progress = kw['progress'] if 'progress' in kw else None
        if progress is not None:
            progress.change_message('Initialize Microcontroller')

        #clear the buffers
        self.info('init microcontroller')
        self.parent.tell('0' * 40, hex = True)

        addr = self.address
        commands = [(addr, '2101FF', 50, 'setting module 1 address'),
                  (addr, '2102FF', 50, 'setting module 2 address'),
                  (addr, '2103FF', 50, 'setting module 3 address'),

                  ]
        self._execute_hex_commands(commands)
        return True
