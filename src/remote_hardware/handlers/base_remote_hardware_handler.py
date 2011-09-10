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
from traits.api import Any
from src.loggable import Loggable

#============= standard library imports ========================
import shlex
import os
from src.remote_hardware.error_handler import ErrorHandler
#============= local library imports  ==========================

class BaseRemoteHardwareHandler(Loggable):
    application = Any

    def __init__(self):
        self.error_handler=ErrorHandler()
        
    #@staticmethod
    def _make_keys(self,name):
        return [name, name.upper(), name.capitalize(), name.lower()]

    def parse(self, data):
        args = data.split(' ')
        return args[0], ' '.join(args[1:])

    def handle(self, data):
        eh=self.error_handler
        manager=self.get_manager()
        err=eh.check_manager(manager)
        if err is None:
            args=self.split_data(data)
            err, func=eh.check_command(self,args)
            if err is None:
                err, response=eh.check_response(func,manager,args)
                if err is None:
                    return response
        return err

    def get_manager(self):
        return
    
    #@staticmethod
    def split_data(self,data):
        return [a.strip() for a in shlex.split(data)]

    def _get_func(self, fstr):
        try:
            return getattr(self, fstr)
        except AttributeError:
            self.warning('Invalid command {}, {:n}'.format(fstr, len(fstr)))





#============= EOF ====================================

