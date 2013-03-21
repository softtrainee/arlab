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
# from traits.api import Instance, DelegatesTo
from traits.api import HasTraits, Any, Int, Instance
#============= standard library imports ========================
# import os
#============= local library imports  ==========================
from fusions_logic_board import FusionsLogicBoard
from threading import Timer, Event
# from src.hardware.kerr.kerr_motor import KerrMotor

class NitrogenFlower(HasTraits):
    delay = Int(30)
    timeout = Int(6000)
    controller = Any
    channel = Int
    _ready_signal = None
    _timeout_timer = None

    def start(self):
        if self._ready_signal is None or \
            not self._ready_signal.is_set():
            self._start_delay_timer()

        self._start_timeout_timer()

    def _start_delay_timer(self):
        self.controller.set_channel(self.channel, True)
        self._ready_signal = Event()
        self._ready_signal.clear()
        t = Timer(self.delay, self.set_ready, args=(True,))
        t.start()

    def _start_timeout_timer(self):
        if self._timeout_timer:
            self._timeout_timer.cancel()

        self._timeout_timer = Timer(self.timeout, self.set_ready, args=(False,))
        self._timeout_timer.start()

    def set_ready(self, onoff):
        if onoff:
            self._ready_signal.set()
        else:
            self.controller.set_channel(self.channel, False)
            self._ready_signal.clear()

    def is_ready(self):
        return self._ready_signal.is_set()


class FusionsUVLogicBoard(FusionsLogicBoard):
    '''
    '''
    has_pointer = False
    _test_comms = False  # dont test comms on startup. UV doesn't really have logic board only kerr motor controllers

    nitrogen_flower = Instance(NitrogenFlower)
    def _nitrogen_flower_default(self):
        return NitrogenFlower(controller=self)

    def _enable_laser(self):
        '''
        '''
        return True

    def _disable_laser(self):
        '''
        '''
        return True

    def prepare(self):
        self.flower.start()


    def is_ready(self):

        pass


#    attenuator_motor = Instance(KerrMotor, ())
#    attenuation = DelegatesTo('attenuator_motor', prefix='data_position')
#    attenuationmin = DelegatesTo('attenuator_motor', prefix='min')
#    attenuationmax = DelegatesTo('attenuator_motor', prefix='max')
#    update_attenuation = DelegatesTo('attenuator_motor', prefix='update_position')

    def load_additional_args(self, config):
        super(FusionsUVLogicBoard, self).load_additional_args(config)
        # load nitrogen flower

        nf = self.nitrogen_flower
        section = 'Flow'
        if config.has_section(section):
            nf.delay = self.config_get(config, section, 'delay', cast='int', default=30)
            nf.timeout = self.config_get(config, section, 'timeout', cast='int', default=6000)
            nf.channel = self.config_get(config, section, 'channel', default='1')
#
#    def _attenuator_motor_default(self):
#        '''
#        '''
#        return KerrMotor(name='attenuator', parent=self)
#============= views ===================================

#============= EOF ====================================
