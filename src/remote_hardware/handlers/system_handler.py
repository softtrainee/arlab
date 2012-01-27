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
from threading import Thread
#============= local library imports  ==========================
from src.remote_hardware.errors.system_errors import DeviceConnectionErrorCode, \
    InvalidArgumentsErrorCode, InvalidValveErrorCode, InvalidIPAddressErrorCode, InvalidValveGroupErrorCode
from base_remote_hardware_handler import BaseRemoteHardwareHandler
from dummies import DummyELM, DummyDevice

EL_PROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
TM_PROTOCOL = 'src.social.twitter_manager.TwitterManager'
RHM_PROTOCOL = 'src.remote_hardware.remote_hardware_manager.RemoteHardwareManager'


class SystemHandler(BaseRemoteHardwareHandler):
    extraction_line_manager = None
    manager_name = 'extraction_line_manager'

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
            if dev is None:
                #possible we are trying to get a flag
                m = self.get_manager()
                dev = m.get_flag(name)

        else:
            dev = DummyDevice()
        return dev

    def Set(self, manager, dname, value, *args):
        d = self.get_device(dname)
        if d is not None:
            result = d.set(value)
        else:
            result = DeviceConnectionErrorCode(dname, logger=self)

        return result

    def Read(self, manager, dname, *args):
        d = self.get_device(dname)
        if d is not None:
            result = d.get()
        else:
            result = DeviceConnectionErrorCode(dname, logger=self)
        return result

    def Open(self, manager, vname, sender_address, *args):
        result = manager.open_valve(vname, sender_address=sender_address)
        if result == True:
            result = 'OK'
        elif result is None:
            result = InvalidArgumentsErrorCode('Open', vname, logger=self)

        return result

    def Close(self, manager, vname, sender_address, *args):
        result = manager.close_valve(vname, sender_address=sender_address)
        if result == True:
            result = 'OK'
        elif result is None:
            result = InvalidArgumentsErrorCode('Close', vname, logger=self)
        return result

    def GetValveState(self, manager, vname, *args):
        result = manager.get_valve_state(vname)
        if result is None:
            result = InvalidValveErrorCode(vname)
        return result

    def GetValveStates(self, manager, *args):

        result = manager.get_valve_states()
        if result is None:
            result = 'ERROR'
        return result

    def GetManualState(self, manager, vname, *args):
        lstate = manager.get_software_lock(vname)
        if lstate is None:
            result = 'ERROR: {} name available'.format(vname)
            result = False
        else:
            result = lstate

        return result

    def StartRun(self, manager, *args):
        '''
            data is a str in form:
            
            RID,Sample,Power/Temp 
        '''
        data = ' '.join(args[:-1])
        if manager.multruns_report_manager is not None:
            manager.multruns_report_manager.start_run(data)

        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                tm.post('Run {} started'.format(data))

        return 'OK'

    def CompleteRun(self, manager, *args):
        '''
            complete run should report age
        '''

        data = ' '.join(args[:-1])
        if manager.multruns_report_manager is not None:
            manager.multruns_report_manager.complete_run()
        if self.application is not None:
            tm = self.application.get_service(TM_PROTOCOL)
            if tm is not None:
                if 'cancel' in data.lower():
                    tm.post('Run {}'.format(data))
                else:
                    tm.post('Run {} completed'.format(data))

        return 'OK'

    def StartMultRuns(self, manager, *args):
        '''
            data should be str of form:
            
            NSamples,
        '''
        sender_addr = args[-1]
        data = ' '.join(args[:-1])
        if self.application is not None:

            rhm = self.application.get_service(RHM_PROTOCOL)
            if rhm.lock_by_address(sender_addr, lock=True):

                if manager.multruns_report_manager is not None:
                    manager.multruns_report_manager.start_new_report(data)

                tm = self.application.get_service(TM_PROTOCOL)
                if tm is not None:
                    tm.post('Mult runs start {}'.format(data))
            else:
                return InvalidIPAddressErrorCode(sender_addr)
        return 'OK'

    def CompleteMultRuns(self, manager, *args):

        sender_addr = args[-1]
        data = ' '.join(args[:-1])

        if self.application is not None:

            rhm = self.application.get_service(RHM_PROTOCOL)
            if rhm.lock_by_address(sender_addr, lock=False):
                if manager.multruns_report_manager is not None:
                    t = Thread(target=manager.multruns_report_manager.complete_report)
                    t.start()

                tm = self.application.get_service(TM_PROTOCOL)
                if tm is not None:
                    tm.post('Mult runs completed {}'.format(data))
            else:
                return InvalidIPAddressErrorCode(sender_addr)

        return 'OK'

    def SystemLock(self, manager, name, onoff, sender_addr, *args):

        cp = manager.remote_hardware_manager.command_processor
        rhm = self.application.get_service(RHM_PROTOCOL)
        if rhm.validate_address(sender_addr):
            cp.system_lock = onoff in ['On', 'on', 'ON']
            if onoff:
                cp.system_lock_address = sender_addr
        else:
            return InvalidIPAddressErrorCode(sender_addr)

        return 'OK'

    def ClaimGroup(self, manager, grp, sender_addr, *args):
        rhm = self.application.get_service(RHM_PROTOCOL)
        if rhm.validate_address(sender_addr):
            err = manager.claim_section(grp, sender_addr)
            if err is True:
                return InvalidValveGroupErrorCode(grp)
        else:
            return InvalidIPAddressErrorCode(sender_addr)

        return 'OK'

    def ReleaseGroup(self, manager, grp, sender_addr, *args):
        rhm = self.application.get_service(RHM_PROTOCOL)
        if rhm.validate_address(sender_addr):
            err = manager.release_section(grp)
            if err:
                return InvalidValveGroupErrorCode(grp)
        else:
            return InvalidIPAddressErrorCode(sender_addr)

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
