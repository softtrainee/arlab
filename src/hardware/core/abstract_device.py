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
from traits.api import Any, Property, implements, DelegatesTo, Instance
from traitsui.api import View, Item

#=============standard library imports ========================
#=============local library imports  ==========================
#from src.config_loadable import ConfigLoadable
from src.hardware.core.i_core_device import ICoreDevice
#from viewable_device import ViewableDevice
from src.has_communicator import HasCommunicator
from src.rpc.rpcable import RPCable
from src.hardware.core.scanable_device import ScanableDevice
from src.hardware.core.core_device import CoreDevice


class AbstractDevice(RPCable, HasCommunicator):
    '''
    '''
    implements(ICoreDevice)

    _cdevice = Instance(CoreDevice)
    _communicator = DelegatesTo('_cdevice')

    dev_klass = Property(depends_on='_cdevice')
    simulation = Property(depends_on='_cdevice')
#    com_class = Property(depends_on='_cdevice')

#    last_command = Property(depends_on='_cdevice.last_command')
#    last_response = Property(depends_on='_cdevice.last_response')
#    
#    scan_units = DelegatesTo('_cdevice')
#    scan_func = DelegatesTo('_cdevice')
#    scan_period = DelegatesTo('_cdevice')
    scan_button = DelegatesTo('_cdevice')
    scan_label = DelegatesTo('_cdevice')
#    scan_path = DelegatesTo('_cdevice')
#    last_command = DelegatesTo('_cdevice')
#    last_response = DelegatesTo('_cdevice')
##    simulation = DelegatesTo('_cdevice')
#    com_class = DelegatesTo('_cdevice')
#    is_scanable = DelegatesTo('_cdevice')
#    dm_kind = DelegatesTo('_cdevice')
    graph = DelegatesTo('_cdevice')

    def __getattr__(self, attr):
        try:
            return getattr(self._cdevice, attr)
        except AttributeError:
            pass

    def _get_dev_klass(self):
        return self._cdevice.__class__.__name__

    def get_factory(self, package, klass):
        try:
            module = __import__(package, fromlist=[klass])
            factory = getattr(module, klass)
            return factory
        except ImportError, e:
            self.warning(e)

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
                self._cdevice.load()
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
                 Item('dev_klass', style='readonly', label='Dev. Class'),
                 Item('connected', style='readonly'),
                 Item('com_class', style='readonly', label='Com. Class'),
                 Item('config_short_path', style='readonly'),
                 Item('loaded', style='readonly'),

               )
        return v
#============= EOF =====================================
