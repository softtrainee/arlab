#=============enthought library imports=======================
from traits.api import Any, Property, implements
from traitsui.api import View, Item

#=============standard library imports ========================
#=============local library imports  ==========================
#from src.config_loadable import ConfigLoadable
from src.hardware.core.i_core_device import ICoreDevice
from viewable_device import ViewableDevice

class AbstractDevice(ViewableDevice):
    '''
        G{classtree}
    '''
    implements(ICoreDevice)

    _cdevice = Any

    simulation = Property(depends_on = '_cdevice')
    com_class = Property(depends_on = '_cdevice')

    last_command = Property(depends_on = '_cdevice.last_command')
    last_response = Property(depends_on = '_cdevice.last_response')
    def _get_last_command(self):
        return self._cdevice.last_command
    def _get_last_response(self):
        return self._cdevice.last_response
    def start(self):
        '''
        '''
        self.load()
        self.open()
        self.initialize()

    def ask(self, cmd, **kw):
        '''
        '''
        if self._cdevice is not None:
            return self._cdevice.ask(cmd)

    def initialize(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        if self._cdevice is not None:
            return self._cdevice.initialize(*args, **kw)

    def open(self, **kw):
        '''
        '''
        if self._cdevice is not None:
            return self._cdevice.open(**kw)

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

    def _get_com_class(self):
        if self._cdevice is not None:
            return self._cdevice.com_class

    def _get_simulation(self):
        '''
        '''
        r = True
        if self._cdevice is not None:
            r = self._cdevice.simulation
        return r


    def traits_view(self):
        v = View(Item('name', style = 'readonly'),
                 Item('klass', style = 'readonly', label = 'Class'),
                 Item('_type', style = 'readonly', label = 'Type'),
                 Item('connected', style = 'readonly'),
                 Item('com_class', style = 'readonly', label = 'Com. Class'),
                 Item('config_short_path', style = 'readonly'),
                 Item('loaded', style = 'readonly'),

               )
        return v
