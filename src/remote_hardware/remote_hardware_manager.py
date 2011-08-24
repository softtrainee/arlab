#============= enthought library imports =======================
from traits.api import Instance, Bool, on_trait_change
from src.managers.manager import Manager

#from globals import use_shared_memory
#if use_shared_memory:
#    from src.messaging.command_processor import SHMCommandProcessor as CommandProcessor
#else:

from src.messaging.command_processor import CommandProcessor
from src.remote_hardware.context import ContextFilter

#============= standard library imports ========================

#============= local library imports  ==========================

'''
#===================================
@todo
    add get_error_status
    add get list of files
    
#===================================
'''

class RemoteHardwareManager(Manager):
    command_processor = Instance(CommandProcessor, ())
    enable_hardware_server = Bool
    result = None
    def __init__(self, *args, **kw):
        super(RemoteHardwareManager, self).__init__(*args, **kw)
        self.context_filter = ContextFilter()

    def bootstrap(self):
        if self.enable_hardware_server:
            self.command_processor.manager = self
            self.command_processor.bootstrap()

    @on_trait_change('enable_hardware_server')
    def enabled_changed(self):
        if self.enable_hardware_server:
            self.bootstrap()
        else:
            self.command_processor.close()

    def stop(self):
        self.command_processor.close()

    def process_server_request(self, request_type, data):
        '''

        '''

        self.debug('Request: {}, {}'.format(request_type, data.strip()))
        result = 'error handling'

        if not request_type in ['System', 'Diode', 'Synrad', 'CO2', 'test']:
            self.warning('Invalid request type ' + request_type)
        elif request_type == 'test':
            result = data
        else:

            klass = '{}Handler'.format(request_type.capitalize())
            pkg = 'src.remote_hardware.handlers.{}_handler'.format(request_type.lower())
            try:
                
                    
                module = __import__(pkg, globals(), locals(), [klass])

                factory = getattr(module, klass)

                handler = factory(application = self.application)
                '''
                    the context filter uses the handler object to 
                    get the kind and request
                    if the min period has elapse since last request or the message is triggered
                    get and return the state from pychron
                    
        
                    pure frequency filtering could be accomplished earlier in the stream in the 
                    Remote Hardware Server (CommandRepeater.get_response) 
                '''


                result = self.context_filter.get_response(handler, data)

            except ImportError,e:
                result = 'ImportError klass={} pkg={} error={}'.format(klass, pkg,e )

        self.debug('Result: {}'.format(result))
        self.result = result
        return result

    def get_server_response(self):
        return self.result



#============= views ===================================
#============= EOF ====================================
