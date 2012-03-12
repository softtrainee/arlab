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
#============= enthought library imports =======================
from traits.api import Any, Instance
import shlex

#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from error_handler import ErrorHandler
from threading import Lock

from dummies import DummyDevice, DummyLM

DIODE_PROTOCOL = 'src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager'
CO2_PROTOCOL = 'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
SYNRAD_PROTOCOL = 'src.managers.laser_managers.synrad_co2_manager.SynradCO2Manager'

class BaseRemoteHardwareHandler(Loggable):
    application = Any
    error_handler = Instance(ErrorHandler, ())
    manager_name = 'Manager'

    def __init__(self, *args, **kw):
        super(BaseRemoteHardwareHandler, self).__init__(*args, **kw)
        self._manager_lock = Lock()

    def _error_handler_default(self):
        eh = ErrorHandler()
        eh.logger = self
        return eh

    #@staticmethod
    def _make_keys(self, name):
        return [name, name.upper(), name.capitalize(), name.lower()]

    def parse(self, data):
        args = data.split(' ')
        return args[0], ' '.join(args[1:])

    def handle(self, data, sender_addr):
        with self._manager_lock:
            eh = self.error_handler
            manager = self.get_manager()
            err = eh.check_manager(manager, self.manager_name)
            if err is None:
                #str list split by shlex
                #first arg is the command
                args = self.split_data(data)
                #try:
                err, func = eh.check_command(self, args)
                #except InvalidCommandErrorCode, e:
                #    err = e

                if err is None:
                    err, response = eh.check_response(func, manager, args[1:] +
                                                      [sender_addr])

                    if err is None:
                        return response

        return err

    def get_manager(self):
        return

    #@staticmethod
    def split_data(self, data):
        return [a.strip() for a in shlex.split(data)]

    def get_func(self, fstr):
        try:
            return getattr(self, fstr)

        except AttributeError:
            pass

    def get_device(self, name, protocol=None):

        if self.application is not None:
            if protocol is None:
                protocol = 'src.hardware.core.i_core_device.ICoreDevice'
            dev = self.application.get_service(protocol, 'name=="{}"'.format(name))
            if dev is None:
                #possible we are trying to get a flag
                m = self.get_manager()
                if m:
                    dev = m.get_flag(name)
                else:
                    dev = DummyDevice()
        else:
            dev = DummyDevice()
        return dev

    def get_laser_manager(self, name=None):
        if name is None:
            name = self.manager_name

        if self.application is not None:
            protocol = CO2_PROTOCOL
            if name == 'Diode':
                protocol = DIODE_PROTOCOL
            elif name == 'Synrad':
                protocol = SYNRAD_PROTOCOL

            lm = self.application.get_service(protocol)
        else:
            lm = DummyLM()

        return lm

#============= EOF ====================================
