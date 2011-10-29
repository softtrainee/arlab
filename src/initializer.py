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
#=============enthought library imports=======================
from traits.api import Any
from pyface.api import ProgressDialog
#=============standard library imports ========================
import time
import os

from wx import DEFAULT_FRAME_STYLE, FRAME_NO_WINDOW_MENU, CLIP_CHILDREN, VERTICAL, \
     Frame, BoxSizer, NullColor, Size, DisplaySize
#=============local library imports  ==========================
from src.helpers import paths
from src.hardware.core.i_core_device import ICoreDevice
from src.helpers.paths import setup_dir
from src.helpers.initialization_parser import InitializationParser
from loggable import Loggable

class MProgressDialog(ProgressDialog):
    def _create_control(self, parent):
        '''
        '''
        style = DEFAULT_FRAME_STYLE | FRAME_NO_WINDOW_MENU | CLIP_CHILDREN

        dialog = Frame(parent, -1, self.title, style=style,
                          #size = self.size,
                          #pos = self.position
                          )

        sizer = BoxSizer(VERTICAL)
        dialog.SetSizer(sizer)
        dialog.SetAutoLayout(True)
        dialog.SetBackgroundColour(NullColor)

        self.dialog_size = Size(*self.size)

        # The 'guts' of the dialog.
        self._create_message(dialog, sizer)
        self._create_gauge(dialog, sizer)
        self._create_percent(dialog, sizer)
        self._create_timer(dialog, sizer)
        self._create_buttons(dialog, sizer)

        dialog.SetClientSize(self.dialog_size)

        #dialog.CentreOnParent()

        return dialog

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
        self.parser = InitializationParser(os.path.join(setup_dir, 'initialization.xml'))

    def clear(self):
        self.init_list = []
        self.application = None

    def add_initialization(self, a):
        '''

        '''
        ilist = self.init_list
        add = True
        for i, il in enumerate(ilist):
            if il['name'] == a['name']:
                ilist[i] = a
                add = False
                break

        if add:
            ilist.append(a)

    def run(self, application=None):
        '''
        '''
        self.application = application

        ok = True
        self.info('Running Initializer')
        for idict in self.init_list:
            ok = self._run_(**idict)
            if not ok:
                break

        msg = 'Complete' if ok else 'Failed'
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

            cont, skip = pd.update(offset + 1)
            if not cont or skip:
                return
            time.sleep(0.1)

        super(Initializer, self).info(msg, **kw)

#    def _run_(self, name=None , device_dir=None, initialization_dir=None, manager=None, plugin_name=None):
    def _run_(self, name=None , device_dir=None, manager=None, plugin_name=None):
        '''
        '''
        if device_dir is None:
            device_dir = paths.device_dir
#        if initialization_dir is None:
#            initialization_dir = paths.initialization_dir

        if manager is not None:
            self.info('loading {}'.format(name))
            manager.application = self.application
            manager.load()
        else:
            return False

        managers = []
        devices = []
        parser = self.parser
        if plugin_name is None:

            #remove manager from name
            idx = name.find('_manager')
            if idx is not - 1:
                name = name[:idx]
            mp = parser.get_plugin(name)
        else:
            mp = parser.get_manager(name, plugin_name)

        if mp is not None:
            managers = parser.get_managers(mp)
            devices = parser.get_devices(mp)

        pdmax = 35
        if self.pd is None or self.pd.progress_bar is None:
            self.load_progress(pdmax)

        if managers:
            self.info('loading managers - {}'.format(','.join(managers)))
#            self.load_managers(manager, managers, device_dir, initialization_dir)
            self.load_managers(manager, managers, device_dir)

        if devices:
            self.info('loading devices - {}'.format(','.join(devices)))
            self.load_devices(manager, name, devices, plugin_name)

        if manager is not None:
            self.info('finish {} loading'.format(name))
            manager.finish_loading()

        return True

    def load_managers(self, manager, managers, device_dir):
        '''
        '''

        for mi in managers:
            self.info('load {}'.format(mi))

            man = None
            if mi == '':
                continue

            try:
                man = getattr(manager, mi)
                if man is None:
                    man = manager.create_manager(mi)
            except AttributeError, e:
                self.warning(e)
                man = manager.create_manager(mi)

            if man is None:
                break

            if self.application is not None:
                #register this manager as a service
                man.application = self.application
                self.application.register_service(type(man), man)

#
#            #HACK
#            MAP = dict(diode = 'FusionsDiode',
#                     co2 = 'FusionsCO2'
#                     )

            d = dict(name=mi, device_dir=device_dir, manager=man, plugin_name=manager.name)
            self.add_initialization(d)

    def load_devices(self, manager, name, devices, plugin_name):
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
            pdev = self.parser.get_device(name, device, plugin_name, element=True)
            dev_class = pdev.get('klass')
            try:

                dev = getattr(manager, device)
                if dev is None:
                    dev = manager.create_device(device, dev_class=dev_class)

            except AttributeError:
                dev = manager.create_device(device, dev_class=dev_class)

            if dev is None:
                self.warning('No device for %s' % device)
                break

            self.info('loading {}'.format(dev.name))

            if dev.load():
                #register the device
                if self.application is not None:
                    self.application.register_service(ICoreDevice, dev)
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
                od._communicator.simulation = True
            elif result is None:
                raise NotImplementedError
        
            od.post_initialize()
                
            manager.devices.append(od)
            od.application = self.application
                
            if od.simulation:
                time.sleep(0.25)

    def load_progress(self, n):
        '''
        '''
        pd = MProgressDialog(max=n,
                             size=(550, 15))

        pd.open()
        w, h = DisplaySize()
        ww, _hh = pd.control.GetSize()

        pd.control.MoveXY(w / 2 - ww + 275, h / 2 + 150)

        self.pd = pd
#========================= EOF ===================================

#    def _get_option_list(self, config, section, option):
#        '''
#
#        '''
#        rlist = []
#        if config.has_option(section, option):
#            rlist = [d.strip() for d in config.get(section, option).split(',') if not d.strip().startswith('_')]
#        return rlist
