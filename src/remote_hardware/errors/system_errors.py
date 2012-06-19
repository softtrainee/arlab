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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.remote_hardware.errors.error import ErrorCode
class PyScriptErrorCode(ErrorCode):
    msg = 'invalid pyscript {} does not exist'
    code = 14

    def __init__(self, path, *args, **kw):
        self.msg = self.msg.format(path)
        super(PyScriptErrorCode, self).__init__(*args, **kw)


#===== debug errors =====
class FuncCallErrorCode(ErrorCode):
    msg='func call problem: err= {} args= {}'
    def __init__(self, err,data, *args, **kw):
        self.msg = self.msg.format(err,data)
        super(FuncCallErrorCode, self).__init__(*args, **kw)


class InvalidCommandErrorCode(ErrorCode):
    msg = 'invalid command: {}'
    code = 1

    def __init__(self, command, *args, **kw):
        self.msg = self.msg.format(command)
        super(InvalidCommandErrorCode, self).__init__(*args, **kw)


class InvalidArgumentsErrorCode(ErrorCode):
    msg = 'invalid arguments: {} {}'
    code = 2

    def __init__(self, command, err, *args, **kw):
        self.msg = self.msg.format(command, err)
        super(InvalidArgumentsErrorCode, self).__init__(*args, **kw)


class InvalidValveErrorCode(ErrorCode):
    msg = '{} is not a registered valve name'
    code = 3

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(InvalidValveErrorCode, self).__init__(*args, **kw)


class InvalidValveGroupErrorCode(ErrorCode):
    msg = 'Invalid valve group - {}'
    code = 14

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(InvalidValveGroupErrorCode, self).__init__(*args, **kw)


#====== initialization problems with pychron    
class ManagerUnavaliableErrorCode(ErrorCode):
    msg = 'manager unavaliable: {}'
    code = 4

    def __init__(self, manager, *args, **kw):
        self.msg = self.msg.format(manager)
        super(ManagerUnavaliableErrorCode, self).__init__(*args, **kw)


class DeviceConnectionErrorCode(ErrorCode):
    msg = 'device {} not connected'
    code = 5

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(DeviceConnectionErrorCode, self).__init__(*args, **kw)


class InvalidIPAddressErrorCode(ErrorCode):
    msg = '{} is not a registered ip address'
    code = 6

    def __init__(self, ip, *args, **kw):
        self.msg = self.msg.format(ip)
        super(InvalidIPAddressErrorCode, self).__init__(*args, **kw)


#===== comm errors =====        
class NoResponseErrorCode(ErrorCode):
    msg = 'no response from device'
    code = 11


class PychronCommErrorCode(ErrorCode):
    msg = 'could not communicate with pychron through {}. socket.error = {}'
    code = 12

    def __init__(self, path, err, *args, **kw):
        self.msg = self.msg.format(path, err)
        super(PychronCommErrorCode, self).__init__(*args, **kw)


class SystemLockErrorCode(ErrorCode):
    msg = 'Access restricted to {} ({}). You are {}'
    code = 13

    def __init__(self, name, locker, sender, *args, **kw):
        self.msg = self.msg.format(name, locker, sender)
        super(SystemLockErrorCode, self).__init__(*args, **kw)

class SecurityErrorCode(ErrorCode):
    msg = 'Not an approved ip address {}'
    code = 14
    def __init__(self, addr, *args, **kw):
        self.msg = self.msg.format(addr)
        super(SecurityErrorCode, self).__init__(*args, **kw)

#======= runtime errors ------
class ValveSoftwareLockErrorCode(ErrorCode):
    msg = 'Valve {} is software locked'
    code = 14

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(ValveSoftwareLockErrorCode, self).__init__(*args, **kw)


class ValveActuationErrorCode(ErrorCode):
    msg = 'Valve {} failed to actuate {}'
    code = 14

    def __init__(self, name, action, *args, **kw):
        self.msg = self.msg.format(name, action)
        super(ValveActuationErrorCode, self).__init__(*args, **kw)

#============= EOF =====================================
