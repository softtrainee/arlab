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
#============= local library imports  ==========================

class BaseRemoteHardwareHandler(Loggable):
    application = Any

    @staticmethod
    def _make_keys(name):
        return [name, name.upper(), name.capitalize(), name.lower()]

    def parse(self, data):
        args = data.split(' ')
        return args[0], ' '.join(args[1:])

    def handle(self, data):
        pass

    @staticmethod
    def split_data(data):
        return [a.strip() for a in shlex.split(data)]

    def _get_func(self, fstr):
        try:
            return getattr(self, fstr)
        except AttributeError:
            self.warning('Invalid command {}, {:n}'.format(fstr, len(fstr)))





#============= EOF ====================================

