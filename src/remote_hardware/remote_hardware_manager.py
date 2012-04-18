'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import Instance, Bool, on_trait_change, List
from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.initialization_parser import InitializationParser
from src.remote_hardware.command_processor import CommandProcessor

'''
#===================================
@todo
    add get_error_status
    add get list of files
    
#===================================
'''


class RemoteHardwareManager(Manager):

    command_processor = Instance(CommandProcessor)
    processors = List
    enable_hardware_server = Bool
    result = None
#    def __init__(self, *args, **kw):
#        super(RemoteHardwareManager, self).__init__(*args, **kw)
    system_lock = Bool(False)

    def _processors_default(self):
        ps = []
#        ip = InitializationParser(os.path.join(setup_dir, 'initialization.xml'))
        ip = InitializationParser()

        for pi in ip.get_processors():
            ps.append(self._command_processor_factory(pi))
        return ps

    def bootstrap(self):
        if self.enable_hardware_server:
            for p in self.processors:
                p.manager = self
                p.bootstrap()
#            self.command_processor.manager = self
#            self.command_processor.bootstrap()

    @on_trait_change('enable_hardware_server')
    def enabled_changed(self):
        if self.enable_hardware_server:
            self.bootstrap()
        else:
            self.stop()
#            for p in self.processors:
#                p.close()
#            self.command_processor.close()

    def stop(self):
        for p in self.processors:
            p.close()
#        self.command_processor.close()

    def _command_processor_factory(self, path):

        name = path.split('-')[-1]
#    def _command_processor_default(self):
        cp = CommandProcessor(application=self.application,
                              path=path,
                              name=name)

        self.bind_preferences(cp)
        return cp

    def bind_preferences(self, cp):
        bind_preference(self, 'system_lock', 'pychron.hardware.enable_system_lock')

        bind_preference(cp, 'system_lock', 'pychron.hardware.enable_system_lock')
        bind_preference(cp, 'system_lock_address', 'pychron.hardware.system_lock_address')
        bind_preference(cp, 'system_lock_name', 'pychron.hardware.system_lock_name')

#        ip = InitializationParser(os.path.join(setup_dir, 'initialization.xml'))
        ip = InitializationParser()
        names = []
        hosts = dict()
        for name, host in ip.get_systems():
            names.append(name)
            hosts[name] = host

        pref = self.application.preferences
        pref.set('pychron.hardware.system_lock_names', names)
        pref.set('pychron.hardware.system_lock_addresses', hosts)

        name = pref.get('pychron.hardware.system_lock_name')

        try:
            if name:
                pref.set('pychron.hardware.system_lock_address',
                          hosts[name.strip("'").lower()])
            else:
                pref.set('pychron.hardware.system_lock_address',
                          hosts[names[0].lower()])
        except Exception, err:
            import traceback
            traceback.print_exc()
            print 'system lock exception', err

        pref.save()

    def validate_address(self, addr):

        if self.system_lock:
            addrs = self.application.preferences.get('pychron.hardware.system_lock_addresses')
            pairs = addrs[1:-1].split(',')

            for p in pairs:
                k, v = p.split(':')
                k = k.strip()
                v = v.strip()
                if v[1:-1] == addr:
                    return k
            self.warning('You are not using an approved ip address {}'.format(addr))
        else:
            return addr


    def lock_by_address(self, addr, lock=True):
        if lock:
            name = self.validate_address(addr)
            if name is not None:
                self.application.preferences.set('pychron.hardware.system_lock_address', addr)
                self.application.preferences.set('pychron.hardware.system_lock_name', name)
                return True

        else:
            self.application.preferences.set('pychron.hardware.enable_system_lock', lock)
            return True

    def get_server_response(self):
        return self.result


#============= EOF ====================================
#    def process_server_request(self, request_type, data):
#        '''
#
#        '''

#        self.debug('Request: {}, {}'.format(request_type, data.strip()))
#        result = 'error handling'
#
#        if not request_type in ['System', 'Diode', 'Synrad', 'CO2', 'test']:
#            self.warning('Invalid request type ' + request_type)
#        elif request_type == 'test':
#            result = data
#        else:
#
#            klass = '{}Handler'.format(request_type.capitalize())
#            pkg = 'src.remote_hardware.handlers.{}_handler'.format(request_type.lower())
#            try:
#                
#                    
#                module = __import__(pkg, globals(), locals(), [klass])
#
#                factory = getattr(module, klass)
#
#                handler = factory(application=self.application)
#                '''
#                    the context filter uses the handler object to 
#                    get the kind and request
#                    if the min period has elapse since last request or the message is triggered
#                    get and return the state from pychron
#                    
#        
#                    pure frequency filtering could be accomplished earlier in the stream in the 
#                    Remote Hardware Server (CommandRepeater.get_response) 
#                '''
#
#
#                result = self.context_filter.get_response(handler, data)
#
#            except ImportError, e:
#                result = 'ImportError klass={} pkg={} error={}'.format(klass, pkg, e)
#
#        self.debug('Result: {}'.format(result))
#        if isinstance(result, ErrorCode):
#            self.result = repr(result)
#        else:
#            self.result = result
#            
#        return result
