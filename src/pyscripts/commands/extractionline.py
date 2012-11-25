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
from traits.api import Str, Dict, Int, Float
from traitsui.api import Item, EnumEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.pyscripts.commands.core import Command
from src.helpers.parsers.valve_parser import ValveParser
import os
from src.paths import paths

class ValveCommand(Command):
    items = Dict
    item = Str

    def __init__(self):
        path = os.path.join(paths.extraction_line_dir, 'valves.xml')
        parser = ValveParser(path)

        valves = []
        for vg in parser.get_groups() + [None]:
            valves += [(ve.text.strip(),
                 ve.find('description').text.strip()
                 ) for ve in parser.get_valves(group=vg)]
        self.items = dict(valves)
        self.item = self.items.keys()[0]

    def _get_view(self):
        return Item('item', editor=EnumEditor(name='items'))

    def _to_string(self):
        return self._keywords([('name', self.item),
                               ('description', self.items[self.item])
                               ])

#        return 'name{}, description={}'.format(self._quote(self.item),
#                                           self._quote(self.items[self.item]))

class Open(ValveCommand):
    description = 'Open a valve'
    example = '''1. open("V")
2. open(description="Bone to Turbo")
'''

class Close(ValveCommand):
    description = 'Close a valve'
    example = '''1. open("V")
2. close(description="Bone to Turbo")
'''

class IsOpen(ValveCommand):
    description = 'Check if a valve is Open'
    example = '''1. is_open("V")
2. is_open(description="Bone to Turbo")
'''

class IsClosed(ValveCommand):
    description = 'Check if a valve is Closed'
    example = '''1. is_closed("V")
2. is_closed(description="Bone to Turbo")
'''



class Release(Command):
    name = Str
    def _get_view(self):
        return Item('name', width=300)

    def _to_string(self):
        return self._keyword('name', self.name)
#        return self._quote(self.name)

class Acquire(Command):
    name = Str
    def _get_view(self):
        return Item('name', width=300)

    def _to_string(self):
        return self._quote(self.name)


class MoveToPosition(Command):
    position = Int
    def _get_view(self):
        return Item('position')

    def _to_string(self):
        return '{}'.format(self.position)


class HeatSample(Command):
    value = Float
    def _get_view(self):
        return Item('value')

    def _to_string(self):
        return '{}'.format(self.value)

#============= EOF =============================================
