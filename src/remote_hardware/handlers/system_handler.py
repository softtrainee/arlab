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

#============= standard library imports ========================
#============= local library imports  ==========================
from base_remote_hardware_handler import BaseRemoteHardwareHandler
from src.remote_hardware.errors.system_errors import DeviceConnectionErrorCode, \
    InvalidArgumentsErrorCode, ManagerUnavaliableErrorCode

#============= views ===================================
EL_PROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
TM_PROTOCOL = 'src.social.twitter_manager.TwitterManager'
class DummyDevice(object):
    def get(self):
        return 0.1
    def set(self, v):
        return 'OK'

alphas = [chr(i) for i in range(65, 65 + 26, 1)]

class DummyELM(object):
    def open_valve(self, v):
        if len(v) == 1 and v in alphas:
            return True
        
    def close_valve(self, v):
        if len(v) == 1:
            return True
    
    def get_valve_state(self, v):
        return True
    def get_valve_states(self):
        return ','.join(map(str, [True, True, False]))
    def get_manual_state(self, v):
        return True
    def get_device(self, n):
        
        d = DummyDevice()
        d = None
        return d
        
    def get_software_lock(self, n):
        return False

class SystemHandler(BaseRemoteHardwareHandler):
    extraction_line_manager = None
    manager_name = 'extraction_line_manager'
#    def get_extraction_line_manager(self):
    def get_manager(self):

        if self.extraction_line_manager is None:
            if self.application is not None:
                elm = self.application.get_service(EL_PROTOCOL)
            else:
                elm = DummyELM()
            self.extraction_line_manager = elm
        else:
            elm = self.extraction_line_manager

        return elm

    def get_device(self, name, protocol=None):
        if self.application is not None:
            if protocol is None:
                protocol = 'src.hardware.core.i_core_device.ICoreDevice'
            dev = self.application.get_service(protocol, 'name=="{}"'.format(name))
        else:
            dev = DummyDevice()
        return dev

    def Set(self, manager, dname, value):
        d = self.get_device(dname)
        if d is not None:
            result = d.set(value)
        else:
            result = DeviceConnectionErrorCode(dname, logger=self)
        
        return result

    def Read(self, manager, dname):
        d = self.get_device(dname)
        if d is not None:
            result = d.get()
        else:
            result = DeviceConnectionErrorCode(dname, logger=self)
        return result

    def Open(self, manager, vname):
        result = manager.open_valve(vname)
        if result == True:
            result = 'OK'
        elif result is None:
            result = InvalidArgumentsErrorCode('Open', vname, logger=self)
        
        return result

    def Close(self, manager, vname):
        result = manager.close_valve(vname)
        if result == True:
            result = 'OK'
        elif result is None:
            result = InvalidArgumentsErrorCode('Close', vname, logger=self)
        return result

    def GetValveState(self, manager, vname):
        return manager.get_valve_state(vname)

    def GetValveStates(self, manager, *args):
        result = manager.get_valve_states()
        if result is None:
            result = 'ERROR'
        return result

    def GetManualState(self, manager, vname):
        lstate = manager.get_software_lock(vname)
        if lstate is None:
            result = 'ERROR: {} name available'.format(vname)
            result = False
        else:
            result = lstate
            
        return result

    
    def StartRun(self, manager, *args):
        
        data = ' '.join(args)
        manager.multruns_report_manager.start_run(data)
        
        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                tm.post('Run {} started'.format(data))
#            else:
##                return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#                ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#
#        else:
##            return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#            ManagerUnavaliableErrorCode('TwitterManager', logger=self)
        return 'OK'

    def CompleteRun(self, manager, *args):
        data = ' '.join(args)
        manager.multruns_report_manager.complete_run()
        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                if 'cancel' in data.lower():
                    tm.post('Run {}'.format(data))
                else:     
                    tm.post('Run {} completed'.format(data))
#
#            else:
#                ManagerUnavaliableErrorCode('TwitterManager', logger=self)
##                return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#        else:
#            ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#            return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
        return 'OK'
                    
    def StartMultRuns(self, manager, *args):
        data = ' '.join(args)
        
        manager.multruns_report_manager.start_new_report(data)
        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                tm.post('Mult runs start {}'.format(data))
#            else:
#                ManagerUnavaliableErrorCode('TwitterManager', logger=self)
##                return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#        else:
#            ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#            return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
        return 'OK'
            
    def CompleteMultRuns(self, manager, *args):
        data = ' '.join(args)
        
        manager.multruns_report_manager.complete_report()
        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                tm.post('Mult runs completed {}'.format(data))
#            else:
#                ManagerUnavaliableErrorCode('TwitterManager', logger=self)
##                return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#        else:
#            ManagerUnavaliableErrorCode('TwitterManager', logger=self)
#            return ManagerUnavaliableErrorCode('TwitterManager', logger=self)
        return 'OK'
            
#    def RemoteLaunch(self, manager, *args):
#        #launch pychron
#        p = '/Users/Ross/Programming/pychron/Pychron.app'
#        result = 'OK'
#        try:
#            subprocess.Popen(['open', p])
#        except OSError:
#            result = 'ERROR: failed to launch Pychron'
#
#        return result   
        
#    def handle(self, data):
#        elm = self.get_extraction_line_manager()
#        result = 'ERROR'
#        if elm is None:
#            self.warning('Extraction Line Manager not available')
#        else:
#            args = self.split_data(data)
#            if args:
#                action = args[0]
#
#                func = self._get_func(action)
#                if func is not None:
#                    try:
#                        result = func(*args[1:])
#                    except TypeError:
#                        result = 'Invalid arguments passed {}'.format(args[1:])
#            else:
#                result = 'No command passed'
#        return str(result)
    
if __name__ == '__main__':
    v = SystemHandler()
    v.RemoteLaunch()
#============= EOF ====================================
            #if action in self._make_keys('set'):
#                dname = args[1]
#                d = self.get_device(dname)
#                if d is not None:
#                    result = d.set(args[2])

#            elif action in self._make_keys('read'):
#                dname = args[1]
#                d = self.get_device(dname)
#                if d is not None:
#                    result = d.get()

#            elif action in self._make_keys('open'):
#                result = elm.open_valve(args[1])
#                if result == True:
#                    result = 'OK'
#
#            elif action in self._make_keys('close'):
#                result = elm.close_valve(args[1])
#                if result == True:
#                    result = 'OK'

#            elif action == 'GetValveState':
#                result = elm.get_valve_state(args[1])

#            elif action == 'GetValveStates':
#                result = elm.get_valve_states()
#                if result is None:
#                    result = 'ERROR'

#            elif action == 'GetManualState':
#                result = elm.get_manual_state(args[1])
#                if result is None:
#                    result = 'ERROR'
#            else:
#                self.warning('Invalid command %s, %i' % (data, len(data)))

#        return str(result)
#            if '.' in data:
#                obj, func = data.split('.')
#
#                t = elm.get_device(obj)
#                if t is not None:
#                    if hasattr(t, func):
#                        result = getattr(t, func)()
#                    else:
#                        self.warning('Invalid func %s' % func)
#            else:
#                self.warning('Invalid command %s' % data)
