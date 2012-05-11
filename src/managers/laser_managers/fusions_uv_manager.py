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



#============= enthought library imports =======================
from traits.api import Instance, Enum, Bool, Button, Str, DelegatesTo, Event, Property
from traitsui.api import View, Item, Group, HGroup, VGroup, Label, \
    EnumEditor

#============= standard library imports ========================
from fusions_laser_manager import FusionsLaserManager
from src.hardware.fusions.fusions_uv_logic_board import FusionsUVLogicBoard
from src.hardware.fusions.atl_laser_control_unit import ATLLaserControlUnit
from src.managers.laser_managers.laser_shot_history import LaserShotHistory

#============= local library imports  ==========================

class FusionsUVManager(FusionsLaserManager):
    '''
        G{classtree}
    '''
    _video_stage = False
    attenuation = DelegatesTo('logic_board')
    attenuationmin = DelegatesTo('logic_board')
    attenuationmax = DelegatesTo('logic_board')
    update_attenuation = DelegatesTo('logic_board')

    controller = Instance(ATLLaserControlUnit)

    single_shot = Button('Single Shot')
    laser_status = Str
    laseronoff = Event
    laseronoff_label = Property(depends_on='_enabled')
    _enabled = DelegatesTo('controller')
    fire_label = Property(depends_on='triggered')
    triggered = DelegatesTo('controller')

    energy = DelegatesTo('controller')
    energymin = DelegatesTo('controller')
    energymax = DelegatesTo('controller')
    update_energy = DelegatesTo('controller')

    hv = DelegatesTo('controller')
    hvmin = DelegatesTo('controller')
    hvmax = DelegatesTo('controller')
    update_hv = DelegatesTo('controller')

    reprate = DelegatesTo('controller')
    repratemin = DelegatesTo('controller')
    repratemax = DelegatesTo('controller')
    update_reprate = DelegatesTo('controller')

    trigger_modes = DelegatesTo('controller')
    trigger_mode = DelegatesTo('controller')#Str('External I')

    stablization_modes = DelegatesTo('controller')
    stablization_mode = DelegatesTo('controller')#Str('High Voltage')
    stop_at_low_e = DelegatesTo('controller')

    cathode = DelegatesTo('controller')
    reservoir = DelegatesTo('controller')
    missing_pulses = DelegatesTo('controller')
    halogen_filter = DelegatesTo('controller')

    laser_head = DelegatesTo('controller')
    laser_headmin = DelegatesTo('controller')
    laser_headmax = DelegatesTo('controller')

    burst = DelegatesTo('controller')
    nburst = DelegatesTo('controller')
    cburst = DelegatesTo('controller')

    shot_history = Instance(LaserShotHistory)

    auto = Event
    auto_label = Property(depends_on='gas_handling_state')
    auto_led = Bool

    mirror = Event
    mirror_label = Property(depends_on='gas_handling_state')
    mirror_led = Bool

    gas_handling_state = Enum('none', 'auto', 'mirror')

    def _auto_fired(self):
        '''
        '''
        if self.gas_handling_state == 'none':
            self.gas_handling_state = 'auto'
            self.auto_led = True
        else:
            self.auto_led = False
            self.gas_handling_state = 'none'

    def _mirror_fired(self):
        '''
        '''
        if self.gas_handling_state == 'none':
            self.gas_handling_state = 'mirror'
            self.mirror_led = True
        else:
            self.mirror_led = False
            self.gas_handling_state = 'none'


    def _get_auto_label(self):
        '''
        '''
        return 'OFF' if self.gas_handling_state == 'auto' else 'ON'

    def _get_mirror_label(self):
        '''
        '''
        return 'OFF' if self.gas_handling_state == 'mirror' else 'ON'


    def _get_laseronoff_label(self):
        '''
        '''
        return 'OFF' if self._enabled else 'ON'

    def _get_fire_label(self):
        '''
        '''
        return 'STOP' if self.triggered else 'RUN'

    def _laseronoff_fired(self):
        '''
        '''
        if not self._enabled:
            self.controller.laser_on()
            self.laser_status = 'Laser ON'
        else:
            self.controller.laser_off()
            self.laser_status = 'Laser OFF'

    def _fire_fired(self):
        '''
        '''
        if not self.triggered:
            self.controller.trigger_laser()
            self.laser_status = 'Laser Triggered'
            self.shot_history.add_shot()
        else:
            self.controller.stop_triggering_laser()
            self.laser_status = ''

    def show_control_view(self):
        '''
        '''
        self.edit_traits(view='control_view')

    def get_control_buttons(self):
        '''
        '''
        return []
    def get_menus(self):
        '''
        '''
        m = super(FusionsUVManager, self).get_menus()

        m.append(('Laser', [dict(name='Control',
                               action='show_control_view')]))
        return m
    def get_control_sliders(self):
        '''
        '''
        s = super(FusionsUVManager, self).get_control_sliders()
        s.pop(len(s) - 1)
        s.append(('attenuation', 'attenuation', {}))
        return s

#============= views ===================================

    def _get_gas_contents(self):
        '''
        '''
        hg = self._readonly_slider_factory('laser_head', 'laser_head')
        sg = self._switch_group_factory([('auto', True, 'gas_handling_state in ["none","auto"]'),
                                       ('mirror', True, 'gas_handling_state in ["none","mirror"]')])
        return [hg,
                sg
                ]
    def _get_control_contents(self):
        '''
        '''

        stg = VGroup(#Label('Stab. Mode'),
                    Item('stablization_mode', style='custom',
                         show_label=False,
                         editor=EnumEditor(values=self.stablization_modes,
                                           cols=1),
                         ),
                    HGroup(Item('stop_at_low_e', show_label=False), Label('Stop at Low Energy')),
                    label='STAB. MODE',
                    show_border=True
                    )
        tbg = self._button_group_factory([('fire', 'fire_label', 'on'),
                                               ('single_shot', '', 'on')
                                               ], orientation='v')
        bg = HGroup(VGroup(
                         HGroup(Item('burst', show_label=False),
                                Label('BURST'))
                         ),
                  Item('nburst', show_label=False),
                  Item('cburst', show_label=False, enabled_when='0')
                  )
        tg = HGroup(VGroup(Label('TRIGGER MODE'),
                         Item('trigger_mode', style='custom',
                            show_label=False,
                               editor=EnumEditor(values=self.trigger_modes,
                                                        cols=1)),
                         bg
                         ),
                    tbg
                 )
        tg.label = 'TRIGGER'
        tg.show_border = True

        lg = Group(self._button_factory('laseronoff', 'laseronoff_label', None))
        lg.label = 'LASER'
        lg.show_border = True
        cg = HGroup(
                    stg,
                  lg,
                  tg,
                  )

        sliders = [('energy', 'energy', None),
                 ('hv', 'hv', None),
                 ('reprate', 'reprate', None),
                 ]

        sg = self._update_slider_group_factory(sliders)
        sg.content.append(self._readonly_slider_factory('laser_head', 'laser_head'))
        sg.show_border = True

        vg = VGroup(Item('cathode', enabled_when='0'),
                  Item('reservoir', enabled_when='0'),
                  Item('missing_pulses', enabled_when='0'),
                  Item('halogen_filter', enabled_when='0'))

        pg = HGroup(sg, vg)

        hg = HGroup(Item('shot_history', show_label=False, style='custom')
                  )
        return [
                cg,
                pg,
                hg,
                HGroup(Item('laser_status', style='readonly'))
                ]
    def control_view(self):
        '''
        '''
        control_contents = self._get_control_contents()
        v = View(
               resizable=True,
               title='UV Laser Control'
               )
        for c in control_contents:

            v.content.append(c)
        return v
    def gas_view(self):
        '''
        '''
        contents = self._get_gas_contents()

        v = View(
               )
        for c in contents:
            v.content.append(c)
        return v

    def __test__group__(self):
        '''
        '''
        vg = VGroup()
        for c in self._get_gas_contents():
            vg.content.append(c)
        return vg
#============= defaults ===================================
    def _stage_manager_default(self):
        '''
        '''
        args = dict(name='uvstage',
                            configuration_dir_name='uv',
                             parent=self,
                             stage_controller_class='Aerotech'
                             )

        if self.video_manager.__class__.__name__ == 'VideoManager' and self._video_stage:
            from src.managers.stage_managers.video_stage_manager import VideoStageManager
            factory = VideoStageManager
            args['video_manager'] = self.video_manager
        else:
            from src.managers.stage_managers.stage_manager import StageManager
            factory = StageManager

        return factory(**args)

    def _logic_board_default(self):
        '''
        '''
        return FusionsUVLogicBoard(name='uvlogicboard',
                                   configuration_dir_name='uv')

    def _controller_default(self):
        '''
        '''
        return ATLLaserControlUnit(name='atl_laser_control',
                                   configuration_dir_name='uv',
                                   )
    def _shot_history_default(self):
        '''
        '''
        return LaserShotHistory(view_mode='simple')
#============= EOF ====================================
