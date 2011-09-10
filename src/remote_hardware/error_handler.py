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
    msg=None
    code=None
    def __repr__(self):
        return '{} : {}'.format(self.code,self.msg)

class InvalidCommandErrorCode(ErrorCode):
    msg='invalid command: {}'
    code=1
    def __init__(self,command):
        self.msg=self.msg.format(command)
    
class ManagerUnavaliableErrorCode(ErrorCode):
    msg='manager unavaliable {}'
    code=2

class InvalidArgumentsErrorCode(ErrorCode):
    msg='invalid arguments: {}'
    code=3
    def __init__(self,command):
        self.msg=self.msg.format(command)
        
class DeviceCommErrorCode(ErrorCode):
    msg='no response from device'
    code=6
    
class ErrorHandler:
    def check_manager(self,manager):
        if manager is None:
            return ManagerUnavaliableErrorCode() 
            
    def check_command(self,handler,args):
        if args:
            command_func=self._get_func(args[0])
            if command_func is None:
                return InvalidCommandErrorCode(), None
            else:
                return None, command_func
        else:
            return InvalidCommandErrorCode(), None
        
    def check_response(self,func, manager, args):
        try:
            result = func(manager,*args)
            
            if result is None:
                err=DeviceCommErrorCode()
            
        except TypeError:
            err=InvalidArgumentsErrorCode(args)
            
        return err, result
        
if __name__ == '__main__':
    ec=ErrorHandler()
    
#============= EOF ============================================
