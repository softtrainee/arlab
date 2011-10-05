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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.remote_hardware.errors.error import ErrorCode
class InvalidCommandErrorCode(ErrorCode):
    msg = 'invalid command: {}'
    code = 1
    def __init__(self, command, *args, **kw):
        self.msg = self.msg.format(command)
        super(InvalidCommandErrorCode, self).__init__(*args, **kw)
    
class ManagerUnavaliableErrorCode(ErrorCode):
    msg = 'manager unavaliable: {}'
    code = 2
    def __init__(self, manager, *args, **kw):
        self.msg = self.msg.format(manager)
        super(ManagerUnavaliableErrorCode, self).__init__(*args, **kw)
    
class InvalidArgumentsErrorCode(ErrorCode):
    msg = 'invalid arguments: {} {}'
    code = 3
    def __init__(self, command, err, *args, **kw):
        self.msg = self.msg.format(command, err)
        super(InvalidArgumentsErrorCode, self).__init__(*args, **kw)
        
class DeviceCommErrorCode(ErrorCode):
    msg = 'no response from device'
    code = 4
    
class DeviceConnectionErrorCode(ErrorCode):
    msg = 'device {} not connected'
    code = 5
    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(DeviceConnectionErrorCode, self).__init__(*args, **kw)

class SystemLockErrorCode(ErrorCode):
    msg = 'Access Denied by {}. you are {}'
    code = 6
    def __init__(self, locker, sender, *args, **kw):
        self.msg = self.msg.format(locker, sender)
        super(SystemLockErrorCode, self).__init__(*args, **kw)

class PychronCommunicationErrorCode(ErrorCode):
    msg = 'could not communication with pychron through {}. socket.error = {}'
    code = 6
    def __init__(self, path, err, *args, **kw):
        self.msg = self.msg.format(path, err)
        super(PychronCommunicationErrorCode, self).__init__(*args, **kw)
        
class InvalidValveErrorCode(ErrorCode):
    msg = '{} is not a register valve name'
    code = 7
    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(InvalidValveErrorCode, self).__init__(*args, **kw)
#============= EOF =====================================
