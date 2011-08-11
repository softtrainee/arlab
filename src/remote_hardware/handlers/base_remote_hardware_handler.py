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

