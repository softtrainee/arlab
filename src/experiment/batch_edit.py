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
from traits.api import HasTraits, Bool, Float, Str, List, Int, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup, EnumEditor, spring
#============= standard library imports ========================
#============= local library imports  ==========================

class BatchEdit(HasTraits):
    batch = Bool(False)

    measurement_scripts = List
    measurement_script = Str
    orig_measurement_script = Str
    apply_measurement_script = Bool


    extraction_scripts = List
    extraction_script = Str
    orig_extraction_script = Str
    apply_extraction_script = Bool

    power = Float
    apply_power = Bool
    orig_power = Float

    duration = Float
    apply_duration = Bool
    orig_duration = Float

    position = Int
    apply_position = Bool
    orig_position = Int
    auto_increment_position = Bool
    auto_increment_step = Int(1)

    def apply_edits(self, runs):
        for i, ri in enumerate(runs):
            for name in ['extraction', 'measurement']:
                sname = '{}_script'.format(name)
                if getattr(self, 'apply_{}'.format(sname)):
                    pi = ri.configuration[sname]
                    ni = globals()['{}_path'.format(name)](getattr(self, sname))
                    if pi != ni:
                        ri.configuration[sname] = ni
                        setattr(ri, '{}_dirty'.format(sname), True)

            for attr, name in [('temp_or_power', 'power'),
                               ('duration', 'duration'),
                               ]:
                if getattr(self, 'apply_{}'.format(name)):
                    setattr(ri, attr, getattr(self, name))

            if self.apply_position:
                if self.auto_increment_position:
                    pos = i * self.auto_increment_step + self.position
                    ri.position = pos
                else:
                    ri.position = self.position

    @on_trait_change('measurement_script,extraction_script,power,duration,position')
    def _changed(self, obj, name, old, new):
        ap = getattr(self, name) != getattr(self, 'orig_{}'.format(name))
        setattr(self, 'apply_{}'.format(name), ap)

    def reset(self):
        #disable all the apply_
        for k in ['measurement_script',
                   'extraction_script',
                   'power',
                   'duration',
                   'position'
                   ]:
            setattr(self, 'apply_{}'.format(k), False)

    def traits_view(self):

        fgroup = lambda n: HGroup(Item('apply_{}'.format(n), show_label=False),
                                spring,
                                Item(n)
                                )

        sgroup = lambda n: HGroup(Item('apply_{}_script'.format(n), show_label=False),
                                  spring,
                                  Item('{}_script'.format(n),
                                       label=n.capitalize(),
                                       editor=EnumEditor(name='{}_scripts'.format(n)))
                                  )

        return View(
                    VGroup(
                           sgroup('extraction'),
                           sgroup('measurement'),
                           fgroup('power'),
                           fgroup('duration'),
                           VGroup(
                                  fgroup('position'),
                                  HGroup(spring,
                                         Item('auto_increment_position'),
                                         Item('auto_increment_step', label='Step'),
                                         enabled_when='batch'
                                         )
                                  )
                           ),
                    title='Batch Edit',
                    kind='livemodal',
                    buttons=['OK', 'Cancel']
                    )
#============= EOF =============================================
