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
        self.parent.tell('0' * 40, is_hex=True)

        addr = self.address
        commands = [(addr, '2101FF', 50, 'setting module 1 address'),
                  (addr, '2102FF', 50, 'setting module 2 address'),
                  (addr, '2103FF', 50, 'setting module 3 address'),

                  ]
        self._execute_hex_commands(commands)
        return True
