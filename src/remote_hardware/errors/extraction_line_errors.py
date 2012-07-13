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
from error import ErrorCode, code_generator, get_code_decorator

code_gen = code_generator(0, start=1)

def generate_code(*args):
    return get_code_decorator(code_gen)(*args)


@generate_code
class PyScriptErrorCode(ErrorCode):
    msg = 'invalid pyscript {} does not exist'

    def __init__(self, path, *args, **kw):
        self.msg = self.msg.format(path)
        super(PyScriptErrorCode, self).__init__(*args, **kw)


#===== debug errors =====
@generate_code
class FuncCallErrorCode(ErrorCode):
    msg = 'func call problem: err= {} args= {}'
    def __init__(self, err, data, *args, **kw):
        self.msg = self.msg.format(err, data)
        super(FuncCallErrorCode, self).__init__(*args, **kw)

@generate_code
class InvalidCommandErrorCode(ErrorCode):
    msg = 'invalid command: {}'

    def __init__(self, command, *args, **kw):
        self.msg = self.msg.format(command)
        super(InvalidCommandErrorCode, self).__init__(*args, **kw)


@generate_code
class InvalidArgumentsErrorCode(ErrorCode):
    msg = 'invalid arguments: {} {}'

    def __init__(self, command, err, *args, **kw):
        self.msg = self.msg.format(command, err)
        super(InvalidArgumentsErrorCode, self).__init__(*args, **kw)


@generate_code
class InvalidValveErrorCode(ErrorCode):
    msg = '{} is not a registered valve name'

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(InvalidValveErrorCode, self).__init__(*args, **kw)


@generate_code
class InvalidValveGroupErrorCode(ErrorCode):
    msg = 'Invalid valve group - {}'

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(InvalidValveGroupErrorCode, self).__init__(*args, **kw)


#====== initialization problems with pychron    
@generate_code
class ManagerUnavaliableErrorCode(ErrorCode):
    msg = 'manager unavaliable: {}'

    def __init__(self, manager, *args, **kw):
        self.msg = self.msg.format(manager)
        super(ManagerUnavaliableErrorCode, self).__init__(*args, **kw)


@generate_code
class DeviceConnectionErrorCode(ErrorCode):
    msg = 'device {} not connected'

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(DeviceConnectionErrorCode, self).__init__(*args, **kw)


@generate_code
class InvalidIPAddressErrorCode(ErrorCode):
    msg = '{} is not a registered ip address'

    def __init__(self, ip, *args, **kw):
        self.msg = self.msg.format(ip)
        super(InvalidIPAddressErrorCode, self).__init__(*args, **kw)


#===== comm errors =====        
@generate_code
class NoResponseErrorCode(ErrorCode):
    msg = 'no response from device'


@generate_code
class PychronCommErrorCode(ErrorCode):
    msg = 'could not communicate with pychron through {}. socket.error = {}'

    def __init__(self, path, err, *args, **kw):
        self.msg = self.msg.format(path, err)
        super(PychronCommErrorCode, self).__init__(*args, **kw)

#===== security =====
@generate_code
class SystemLockErrorCode(ErrorCode):
    msg = 'Access restricted to {} ({}). You are {}'

    def __init__(self, name, locker, sender, *args, **kw):
        self.msg = self.msg.format(name, locker, sender)
        super(SystemLockErrorCode, self).__init__(*args, **kw)

@generate_code
class SecurityErrorCode(ErrorCode):
    msg = 'Not an approved ip address {}'

    def __init__(self, addr, *args, **kw):
        self.msg = self.msg.format(addr)
        super(SecurityErrorCode, self).__init__(*args, **kw)

#======= runtime errors ------
@generate_code
class ValveSoftwareLockErrorCode(ErrorCode):
    msg = 'Valve {} is software locked'

    def __init__(self, name, *args, **kw):
        self.msg = self.msg.format(name)
        super(ValveSoftwareLockErrorCode, self).__init__(*args, **kw)

@generate_code
class ValveActuationErrorCode(ErrorCode):
    msg = 'Valve {} failed to actuate {}'

    def __init__(self, name, action, *args, **kw):
        self.msg = self.msg.format(name, action)
        super(ValveActuationErrorCode, self).__init__(*args, **kw)

#@generate_code
#class HMACSecurityErrorCode(ErrorCode):
#    msg = 'Computer {} was not authenticated. Invalid HMAC certificate'
#    code = 000
#    def __init__(self, addr, *args, **kw):
#        self.msg = self.msg.format(addr)
#        super(HMACSecurityErrorCode, self).__init__(*args, **kw)
#============= EOF =====================================
