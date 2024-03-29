#!/usr/bin/python
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
from traits.api import Any
#============= standard library imports ========================
import time
from wx import DisplaySize
#============= local library imports  ==========================
from src.paths import paths
from src.hardware.core.i_core_device import ICoreDevice
from src.helpers.parsers.initialization_parser import InitializationParser
from loggable import Loggable
from src.progress_dialog import MProgressDialog
import os
from globals import globalv


class Initializer(Loggable):

    '''
    '''

    pd = None
    name = 'Initializer'
    application = Any
    device_prefs = Any

    def __init__(self, *args, **kw):
        '''
        '''

        super(Initializer, self).__init__(*args, **kw)
        self.clear()
        self.cnt = 0
        self.parser = InitializationParser()

    def clear(self):
        self.init_list = []
        self.application = None

    def add_initialization(self, a):
        '''

        '''

        ilist = self.init_list
        ilist.append(a)
#        add = True
#        for (i, il) in enumerate(ilist):
#            if il['name'] == a['name']:
#                ilist[i] = a
#                add = False
#                break
#
#        if add:
#            ilist.append(a)

    def run(self, application=None):
        '''
        '''

        self.application = application

        ok = True
        self.info('Running Initializer')
        nsteps = 1
        for idict in self.init_list:
            nsteps += self.get_nsteps(**idict)

        self.load_progress(nsteps)

        for idict in self.init_list:
            ok = self._run_(**idict)
            if not ok:
                break

        msg = ('Complete' if ok else 'Failed')
        self.info('Initialization {}'.format(msg))

        if self.pd is not None:
            self.pd.update(self.pd.max)
            self.pd.close()
        return ok

    def info(self, msg, **kw):

        pd = self.pd
        if pd is not None:

            offset = pd.progress_bar.control.GetValue()
            pd.change_message(msg)

            if offset == pd.max - 1:
                pd.max += 1
            pd.update(offset + 1)
#            (cont, skip) = pd.update(offset + 1)
#            if not cont or skip:
#                return

            # time.sleep(0.1)

        super(Initializer, self).info(msg, **kw)

    def get_nsteps(self, name=None, manager=None, plugin_name=None):
        parser = self.parser
        if plugin_name is None:
            # remove manager from name
            idx = name.find('_manager')
            if idx is not -1:
                name = name[:idx]
            mp = parser.get_plugin(name)
        else:
            mp = parser.get_manager(name, plugin_name)

        if mp is None:
            mp = parser.get_root().find('plugins/{}'.format(name))

        ns = 0
        if mp is not None:
            ns += (2 * (len(parser.get_managers(mp)) + 1))
            ns += (3 * (len(parser.get_devices(mp)) + 1))
            ns += (len(parser.get_flags(mp)) + 1)
            ns += (len(parser.get_timed_flags(mp)) + 1)

        return ns

    def _run_(
        self,
        name=None,
        device_dir=None,
        manager=None,
        plugin_name=None,
        ):
        '''
        '''

        if device_dir is None:
            device_dir = paths.device_dir

        parser = self.parser
        if manager is not None:
            self.info('loading {}'.format(name))
            manager.application = self.application
            manager.load()

        else:
            return False

        managers = []
        devices = []
        flags = []
        timed_flags = []

        if plugin_name is None:

            # remove manager from name

            idx = name.find('_manager')
            if idx is not -1:
                name = name[:idx]
            mp = parser.get_plugin(name)
        else:
            mp = parser.get_manager(name, plugin_name)

        if mp is None:
            mp = parser.get_root().find('plugins/{}'.format(name))

        if mp is not None:
            if not globalv.ignore_required:
                if not self._check_required(mp):
                    return False

            managers = parser.get_managers(mp)
            devices = parser.get_devices(mp)
            flags = parser.get_flags(mp)
            timed_flags = parser.get_timed_flags(mp)

            # set rpc server
            mode, _, port = parser.get_rpc_params(mp)
            if port and mode != 'client':
                manager.load_rpc_server(port)


        if managers:
            self.info('loading managers - {}'.format(', '.join(managers)))
            manager.name = name
            self.load_managers(manager, managers, device_dir)

        if devices:
            self.info('loading devices - {}'.format(', '.join(devices)))
            self.load_devices(manager, name, devices, plugin_name)

        if flags:
            self.info('loading flags - {}'.format(', '.join(flags)))
            self.load_flags(manager, flags)

        if timed_flags:
            self.info('loading timed flags - {}'.format(','.join(timed_flags)))
            self.load_timed_flags(manager, timed_flags)

        if manager is not None:
            self.info('finish {} loading'.format(name))
            manager.finish_loading()

        return True

    def load_flags(self, manager, flags):
        for f in flags:
            self.info('loading {}'.format(f))
            manager.add_flag(f)

    def load_timed_flags(self, manager, flags):
        for f in flags:
            self.info('loading {}'.format(f))
            manager.add_timed_flag(f)

    def load_managers(
        self,
        manager,
        managers,
        device_dir,
        ):
        '''
        '''

        for mi in managers:
            man = None
            if mi == '':
                continue
            self.info('load {}'.format(mi))
            mode, host, port = self.parser.get_rpc_params((mi, manager.name))
            remote = mode == 'client'
            try:
                man = getattr(manager, mi)
                if man is None:
                    man = manager.create_manager(mi, host=host,
                                                 port=port, remote=remote)
            except AttributeError:
#                self.warning(e)
                try:
                    man = manager.create_manager(mi,
                                                 host=host,
                                                 port=port, remote=remote)
                except Exception:
                    import traceback
                    traceback.print_exc()

            if man is None:
                self.debug('trouble creating manager {}'.format(mi))
                break




            if self.application is not None:

                # register this manager as a service
                man.application = self.application
                self.application.register_service(type(man), man)

            d = dict(name=mi, device_dir=device_dir, manager=man,
                     plugin_name=manager.name)

            self.add_initialization(d)

    def _check_required(self, subtree):
        # check the subtree has all required devices enabled
        devs = self.parser.get_devices(subtree, all=True, element=True)
        for di in devs:
            required = True
            req = self.parser.get_parameter(di, 'required')
            if req:
                required = req.strip().lower() == 'true'

            enabled = di.get('enabled').lower() == 'true'

#            print enabled, di.text.strip(), required
            if required and not enabled:
                name = di.text.strip().upper()
                msg = '''Device {} is REQUIRED but is not ENABLED.
                
Do you want to quit to enable {} in the Initialization File?'''.format(name, name)
                result = self.confirmation_dialog(msg, title='Quit Pychron')
                if result:
                    os._exit(0)

        return True

    def load_devices(
        self,
        manager,
        name,
        devices,
        plugin_name,
        ):
        '''
        '''

        opened = []
        devs = []
        if manager is None:
            return

        for device in devices:

            if device == '':
                continue

            dev = None
            pdev = self.parser.get_device(name, device, plugin_name,
                    element=True)

            dev_class = pdev.find('klass')
            if dev_class is not None:
                dev_class = dev_class.text.strip()

            try:

                dev = getattr(manager, device)
                if dev is None:
                    dev = manager.create_device(device,
                            dev_class=dev_class)
            except AttributeError:
                dev = manager.create_device(device, dev_class=dev_class)

            if dev is None:
                self.warning('No device for {}'.format(device))
                break

            self.info('loading {}'.format(dev.name))

            if dev.load():

                # register the device

                if self.application is not None:

                    # display with the HardwareManager

                    self.application.register_service(ICoreDevice, dev,
                            {'display': True})

                devs.append(dev)
                self.info('opening {}'.format(dev.name))
                if not dev.open(prefs=self.device_prefs):
                    self.info('failed connecting to {}'.format(dev.name))
                else:
                    opened.append(dev)
            else:
                self.info('failed loading {}'.format(dev.name))

#        for od in opened:

        for od in devs:
            self.info('Initializing {}'.format(od.name))
            result = od.initialize(progress=self.pd)
            if result is not True:
                self.warning('Failed setting up communications to {}'.format(od.name))
                if od._communicator:
                    od._communicator.simulation = True

            elif result is None:
                raise NotImplementedError

            od.application = self.application
            od.post_initialize()

            manager.devices.append(od)



#            if od.simulation:
#                time.sleep(0.25)

    def load_progress(self, n):
        '''
        '''
        pd = MProgressDialog(max=n, size=(550, 15))

        pd.open()
        pd.center()
        self.pd = pd


# ========================= EOF ===================================

#    def _get_option_list(self, config, section, option):
#        '''
#
#        '''
#        rlist = []
#        if config.has_option(section, option):
#            rlist = [d.strip() for d in config.get(section, option).split(',') if not d.strip().startswith('_')]
#        return rlist
