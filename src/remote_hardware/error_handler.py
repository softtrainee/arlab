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
#=============enthought library imports========================
from traits.api import HasTraits
from traitsui.api import View, Item
#============= standard library imports =======================
#============= local library imports  =========================
class ErrorCode:
    msg = None
    code = None
    def __repr__(self):
        return '{} : {}'.format(self.code, self.msg)

class InvalidCommandErrorCode(ErrorCode):
    msg = 'invalid command: {}'
    code = 1
    def __init__(self, command):
        self.msg = self.msg.format(command)
    
class ManagerUnavaliableErrorCode(ErrorCode):
    msg = 'manager unavaliable: {}'
    code = 2
    def __init__(self, manager):
        self.msg = self.msg.format(manager)
    
class InvalidArgumentsErrorCode(ErrorCode):
    msg = 'invalid arguments: {} {}'
    code = 3
    def __init__(self, command, err):
        self.msg = self.msg.format(command, err)
        
class DeviceCommErrorCode(ErrorCode):
    msg = 'no response from device'
    code = 6
class DeviceConnectionErrorCode(ErrorCode):
    msg = 'device {} not connected'
    code = 7
    def __init__(self, name):
        self.msg = self.msg.format(name)
    
class ErrorHandler:
    def check_manager(self, manager, name):
        if manager is None:
            return ManagerUnavaliableErrorCode(name) 
            
    def check_command(self, handler, args):
        if args:
            command_func = handler.get_func(args[0])
            if command_func is None:
                return InvalidCommandErrorCode(args[0]), None
            else:
                return None, command_func
        else:
            return InvalidCommandErrorCode(), None
        
    def check_response(self, func, manager, args):
        '''
            performs the requested command and checks for errors
             
        '''
        result = None
        err = None
        try:
            result = func(manager, *args)
            if result is None:
                err = DeviceCommErrorCode()
            elif result in ['DeviceConnectionErrorCode', 'InvalidArgumentsErrorCode']:
                err = globals()[result](args[0])
                
        except TypeError, e:
            err = InvalidArgumentsErrorCode(args, e)
            
        return err, str(result)
        
if __name__ == '__main__':
    ec = ErrorHandler()
    
#============= EOF ============================================
