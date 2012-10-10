#===============================================================================
# Copyright 2012 Jake Ross
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

#============= enthought library imports =======================
from traits.api import HasTraits, Str, Float
from traitsui.api import View, Item, FileEditor
from traitsui.menu import OKCancelButtons
#============= standard library imports ========================
import os
import re
#============= local library imports  ==========================
from src.paths import paths
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def uncamelcase(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

class Command(HasTraits):
    def to_string(self):
        m = '{}({})'.format(
                          self._get_command(),
                          self._to_string()
                          )
        return self.indent(m)

    def _get_command(self):
        return uncamelcase(self.__class__.__name__)
#        return self.__class__.__name__.lower()

    def _to_string(self):
        pass

    @classmethod
    def _keywords(cls, words):
        return ', '.join([cls._keyword(*args) for args in words])

    @classmethod
    def _keyword(cls, k, v, number=False):
        if not number:
            v = cls._quote(v)
        return '{}={}'.format(k, v)

    @classmethod
    def _quote(cls, m):
        return '"{}"'.format(m)

    @classmethod
    def indent(cls, m, n=1):
        ts = '    ' * n
        return '{}{}'.format(ts, m)

    def traits_view(self):
        v = View(self._get_view(),
                 title=self.__class__.__name__,
                 buttons=OKCancelButtons
                 )
        return v

    def get_text(self):
        info = self.edit_traits(kind='livemodal')
        if info.result:
            return self.to_string()


class Info(Command):
    message = Str
    def _get_view(self):
        return Item('message', width=500)

    def _to_string(self):
        return self._keyword('message', self.message)


class Sleep(Command):
    duration = Float
    def _get_view(self):
        return Item('duration', label='Duration (s)')

    def _to_string(self):
        return self._keyword('duration', self.duration,
                             number=True)


class Gosub(Command):
    path = Str(paths.scripts_dir)
    def _get_view(self):
        return Item('path',
                    editor=FileEditor(filter=['*.py']),
                    width=600,
                    )

    def _to_string(self):
        if os.path.isfile(self.path):
            head, tail = os.path.split(self.path)
            words = [('name', tail),
                     ('root', head),
                     ]
            return self._keywords(words)

class BeginInterval(Command):
    duration = Float
    def _get_view(self):
        return Item('duration', label='Duration (s)')

    def to_string(self):
        m = 'begin_interval(duration={})'.format(self.duration)
        m2 = 'complete_interval()'
        return self.indent(m) + '\n    \n' + self.indent(m2)


class CompleteInterval(Command):
    def get_text(self):
        return self.indent('complete_interval()')


class Exit(Command):
    def get_text(self):
        return self.indent('exit()')
#============= EOF =============================================
