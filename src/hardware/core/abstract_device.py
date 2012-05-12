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



#=============enthought library imports=======================
from traits.api import Any, Property, implements, DelegatesTo
from traitsui.api import View, Item

#=============standard library imports ========================
#=============local library imports  ==========================
#from src.config_loadable import ConfigLoadable
from src.hardware.core.i_core_device import ICoreDevice
from viewable_device import ViewableDevice


class AbstractDevice(ViewableDevice):
    '''
    '''
    implements(ICoreDevice)

    _cdevice = Any

    simulation = Property(depends_on='_cdevice')
#    com_class = Property(depends_on='_cdevice')

#    last_command = Property(depends_on='_cdevice.last_command')
#    last_response = Property(depends_on='_cdevice.last_response')
#    
    scan_units = DelegatesTo('_cdevice')
    scan_func = DelegatesTo('_cdevice')
    scan_period = DelegatesTo('_cdevice')
    scan_button = DelegatesTo('_cdevice')
    scan_path = DelegatesTo('_cdevice')
    last_command = DelegatesTo('_cdevice')
    last_response = DelegatesTo('_cdevice')
#    simulation = DelegatesTo('_cdevice')
    com_class = DelegatesTo('_cdevice')
    is_scanable = DelegatesTo('_cdevice')


    def ask(self, cmd, **kw):
        '''
        '''
        if self._cdevice is not None:
            return self._cdevice.ask(cmd)

    def initialize(self, *args, **kw):
        '''
        '''
        if self._cdevice is not None:
            return self._cdevice.initialize(*args, **kw)

    def post_initialize(self, *args, **kw):
        pass

    def open(self, **kw):
        '''
        '''
        if self._cdevice is not None:
            return self._cdevice.open(**kw)

    def setup_scan(self, *args, **kw):
        if self._cdevice is not None:
            return self._cdevice.setup_scan(*args, **kw)

    def load(self, *args, **kw):
        '''
        '''
        config = self.get_configuration()
        if config:

            if self.load_additional_args(config):
                self._loaded = True
                return True

#===============================================================================
# viewable device protocol
#===============================================================================
#    def _get_last_command(self):
#        return self._cdevice.last_command
#    def _get_last_response(self):
#        return self._cdevice.last_response

#    def _get_com_class(self):
#        if self._cdevice is not None:
#            return self._cdevice.com_class
#
    def _get_simulation(self):
        '''
        '''
        r = True
        if self._cdevice is not None:
            r = self._cdevice.simulation
        return r

    def traits_view(self):
        v = View(Item('name', style='readonly'),
                 Item('klass', style='readonly', label='Class'),
                 Item('_type', style='readonly', label='Type'),
                 Item('connected', style='readonly'),
                 Item('com_class', style='readonly', label='Com. Class'),
                 Item('config_short_path', style='readonly'),
                 Item('loaded', style='readonly'),

               )
        return v
#============= EOF =====================================
