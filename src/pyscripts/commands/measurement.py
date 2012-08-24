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
from traits.api import Int, Str, Bool, List, Event, Property, Enum, Float
from traitsui.api import Item, CheckListEditor, VGroup, HGroup, ButtonEditor, EnumEditor
from src.pyscripts.commands.core import Command
#============= standard library imports ========================
#============= local library imports  ==========================


DETS = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']

class Baselines(Command):
    ncounts = Int(1)
    position = Float

    detector = Str('H1')

    def _get_view(self):
        return VGroup(Item('ncounts'),
                      Item('position'),
                      Item('detector', editor=EnumEditor(values=DETS))
                      )

    def _to_string(self):
        pos = self.position
        if not pos:
            pos = None

        words = [('ncounts', self.ncounts, True),
               ('position', pos, True),
               ('detector', self.detector)
               ]

        return self._keywords(words)


class Position(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetTimeZero(Command):
    def _get_view(self):
        pass

    def to_string(self):
        return 'set_time_zero()'


class PeakCenter(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class ActivateDetectors(Command):
    detectors = List
    toggle = Event
    toggle_label = Property(depends_on='_toggled')
    _toggled = Bool(False)

    def _toggle_fired(self):
        if not self._toggled:
            self.detectors = DETS
        else:
            self.detectors = []
        self._toggled = not self._toggled

    def _get_toggle_label(self):
        return 'None' if self._toggled else 'All'

    def _get_view(self):
        return VGroup(Item('detectors',
                    show_label=False,
                    style='custom',
                    editor=CheckListEditor(values=DETS,
                                           cols=1
                                           )),
                      Item('toggle',
                           show_label=False,
                           editor=ButtonEditor(label_value='toggle_label'))
                      )

    def _to_string(self):
        return ', '.join([self._quote(di) for di in self.detectors])


class Collect(Command):
    ncounts = Int(1)
    integration_time = Float
    def _get_view(self):
        return VGroup(Item('ncounts'), Item('integration_time'))

    def _to_string(self):
        words = [('ncounts', self.ncounts, True),
               ('integration_time', self.integration_time, True)
               ]
        return self._keywords(words)


class Regress(Command):
    kind = Enum('linear', 'parabolic', 'cubic')
    def _get_view(self):
        return Item('kind', show_label=False)

    def _to_string(self):
        return self._keyword('kind', self.kind)


class Sniff(Command):
    ncounts = Int(1)
    def _get_view(self):
        return Item('ncounts')

    def _to_string(self):
        return self._keyword('ncounts', self.ncounts, True)


class SetYsymmetry(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetZsymmetry(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetZFocus(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetExtactionLens(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetDeflection(Command):
    def _get_view(self):
        pass

    def _to_string(self):
        pass

#============= EOF =============================================
