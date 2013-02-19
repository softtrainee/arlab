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
from traits.api import Any, Instance, Str
from traitsui.api import View, Item, HGroup
from src.managers.manager import Manager
from src.hardware.core.core_device import CoreDevice


class MultiplexerManager(Manager):
    controller=Instance(CoreDevice)
    hname=Str('Name')
    haddress=Str('Address')
    hvalue=Str('Value')
    hprocessvalue=Str('ProcessValue')
    title='Multiplexer'
    window_width=500
    window_height=500
    def opened(self):
        self.controller.start_scan()
        
    def closed(self, isok):
        self.controller.stop_scan()
        return isok
        
    def finish_loading(self):
        if self.devices:
            self.controller=self.devices[0]

    def traits_view(self):
        v=self.view_factory(
               HGroup(
                      Item('hname', show_label=False, style='readonly',width=200), 
                      Item('haddress', show_label=False, style='readonly',width=75),
                      Item('hvalue', show_label=False, style='readonly',width=100),
                      Item('hprocessvalue', show_label=False, style='readonly',width=100)
                      ),
               Item('controller', style='custom', show_label=False),
               )
        
        return v