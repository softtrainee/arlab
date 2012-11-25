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

    description = 'Measure baselines'
    example = '''1. baselines(counts=50, mass=40.5)
2. baselines(counts=5, cycles=5, mass=0.5, detector='CDD')

Example 1. multicollects baselines at mass 40.5 for 50 counts. 
    Only activated detectors are records (see. activate_detectors)

Example 2. peak hops activated isotopes on the CDD. In this case <mass> is relative.
    <counts> is the number of integrates per cycle
    <cycles> is the total number of peak jumps 
'''
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
    description = 'Alter magnetic field to position beams'
    example = '''1. position(39.962)
2. position('Ar40', detector="H1")
3. position(5.89813, dac=True)

Example 1. moves the mass 39.962 to AX detector

Example 2. moves 'Ar40' to H1 detector. 
          'Ar40' is converted to a mass using the MolecularWeightsTable
          
Example 3. positions the magnet in DAC space. 
         
         !!Remember to set dac=True otherwise the position will be 
           interpreted as a mass
    
'''

    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetTimeZero(Command):
    description = 'Set Time Zero'
    example = u'''set_time_zero()
    
set_time_zero allows fine grained control of the t\u2080.    
'''

    def _get_view(self):
        pass

    def to_string(self):
        return 'set_time_zero()'


class PeakCenter(Command):
    description = 'Scan the magnet to locate the center of a peak'
    example = '''1. peak_center()
2. peak_center(detector='H1', isotope='Ar39')

Example 1. Scan Ar40 over the AX detector

Example 2. Scan Ar39 over the H1 detector
'''
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class ActivateDetectors(Command):
    detectors = List
    toggle = Event
    toggle_label = Property(depends_on='_toggled')
    _toggled = Bool(False)

    description = 'Define list of detector to record'
    example = '''activate_detectors('H1','AX','CDD')
'''
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


class Multicollect(Command):
    ncounts = Int(1)
    integration_time = Float

    description = 'Simultaneously record data from all activated detectors'
    example = '''1. multicollect(ncounts=200)
2. multicollect(ncounts=200, integration_time=2.097152)

!!setting the integration_time is currently not available because of a bug in Qtegra/RCS!!
    .
'''
    def _get_view(self):
        return VGroup(Item('ncounts'), Item('integration_time'))

    def _to_string(self):
        words = [('ncounts', self.ncounts, True),
               ('integration_time', self.integration_time, True)
               ]
        return self._keywords(words)


class Regress(Command):
    kind = Enum('linear', 'parabolic', 'cubic')

    description = 'Set the default peak-time regression fits'
    example = '''1. regress('parabolic')
2. activate_detectors('AX','CDD')
   regress('parabolic','linear')
   
Example 1. set all activated detectors to use a 'parabolic' fit
Example 2. set AX to parabolic and CDD to linear

!!call 'regress' only after detectors have been activated!!
    
'''

    def _get_view(self):
        return Item('kind', show_label=False)

    def _to_string(self):
        return self._keyword('kind', self.kind)


class Sniff(Command):
    ncounts = Int(1)

    description = '''Record activated detectors, but do not use in peak-time regression. 
Useful for measuring signals during equilibration'''

    example = '''sniff(ncounts=20)'''

    def _get_view(self):
        return Item('ncounts')

    def _to_string(self):
        return self._keyword('ncounts', self.ncounts, True)


class PeakHop(Command):
    description = 'Peak hop a mass on a detector'
    example = '''1. peak_hop(detector='CDD', isotopes=['Ar40','Ar39'])
2. peak_hop(detector='CDD', isotopes=['Ar40','Ar39'], cycles=10, integrations=10)
    
    peak hops isotopes Ar40, Ar39 on the CDD.
    <counts> is the number of integrates per cycle --default=5
    <cycles> is the total number of peak jumps --default=5'''
    def _get_view(self):
        pass

    def _to_string(self):
        pass

class Coincidence(Command):
    description = '''A coincidence scan is similar to a peak_center 
however all peak centers for all activated detectors are determined'''
    example = 'coincidence()'
    def _get_view(self):
        pass

    def _to_string(self):
        pass

class SetYsymmetry(Command):
    description = 'Set y-symmetry'
    example = 'set_y_symmetry(10.1)'
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetZsymmetry(Command):
    description = 'Set z-symmetry'
    example = 'set_z_symmetry(10.1)'
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetZFocus(Command):
    description = 'Set z-focus'
    example = 'set_z_focus(10.1)'
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetExtactionLens(Command):
    description = 'Set extraction lens'
    example = 'set_extraction_lens(10.1)'
    def _get_view(self):
        pass

    def _to_string(self):
        pass


class SetDeflection(Command):
    description = 'Set deflection of a detector'
    example = 'set_deflection("AX", 100)'
    def _get_view(self):
        pass

    def _to_string(self):
        pass

#============= EOF =============================================
