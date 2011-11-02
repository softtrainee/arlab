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
from traits.api import Str, Float, Any, Button, Int, List, Bool
from traitsui.api import  Item, HGroup, VGroup, Handler, \
    RangeEditor, ButtonEditor, ScrubberEditor, Label, spring
from traitsui.menu import Action, Menu, MenuBar
from pyface.api import FileDialog, OK, warning
from pyface.timer.do_later import do_after
#=============standard library imports ========================
import os
#=============local library imports  ==========================
from src.config_loadable import ConfigLoadable
from src.hardware import HW_PACKAGE_MAP
from threading import Thread
import time

class ManagerHandler(Handler):
    '''
        
    '''
    def init(self, info):
        info.object.ui = info.ui
        info.object.opened()

    def close(self, info, is_ok):
        return info.object.close(is_ok)

    def closed(self, info, is_ok):
        '''
        '''

        info.object.kill()
        return True

class Manager(ConfigLoadable):
    '''
    '''

    test = Button

    macro = None
    parent = Any

    title = Str
    window_x = Float(0.1)
    window_y = Float(0.1)
    window_width = Float(0.75)
    window_height = Float(0.75)
    simulation = False

    _killed = False
    failure_reason = None
    enable_close_after = Bool
    close_after_minutes = Int #in minutes

    ui = Any

    handler_klass = ManagerHandler
    application = Any
    
    devices = List

    def __init__(self, *args, **kw):
        '''

        '''
        if self.name is None:
            self.name = self.__class__.__name__
        super(Manager, self).__init__(*args, **kw)


    def finish_loading(self):
        '''
        '''
        pass


    def opened(self):
        def _loop():
            start = time.time()
            self.info('Window set to close after {} min'.format(self.close_after_minutes))
            
            now = time.time()
            while  now - start < (self.close_after_minutes * 60) and not self._killed:
                time.sleep(1)
                now = time.time()

            self.close_ui()

        if self.enable_close_after and self.close_after_minutes:
            t = Thread(target=_loop)
            t.start()

        self._killed = False
        for _k, man in self.get_managers():
            man._killed = False


    def close_ui(self):
        if self.ui is not None:
            #disposes 50 ms from now
            do_after(1, self.ui.dispose)
            #sleep a little so everything has time to update
            #time.sleep(0.05)

    def close(self, is_ok):
#        print self.name, 'close', is_ok
        return True
    
    def _kill_hook(self):
        pass
    
    def kill(self, **kw):
        '''

        '''

        if not self._killed:
            self.info('killing')
            self._kill_hook()
            
            self._killed = True

            for _k, man in self.get_managers():
                if man is not None:
                    man.kill()

        return not self._killed

    def warning_dialog(self, msg):
        '''
        '''
        warning(None, msg)

    def open_file_dialog(self, **kw):
        '''
        '''
        return self._file_dialog_('open', **kw)

    def save_file_dialog(self, **kw):
        '''
        '''
        return self._file_dialog_('save as', **kw)

    def get_managers(self):

        return [(ma, getattr(self, ma)) for ma in self.traits()
                    if ma.endswith('_manager')
                        and getattr(self, ma) is not None]

    def get_device(self, device_name):
        '''
        '''
        dev = None
        if hasattr(self, device_name):
            dev = getattr(self, device_name)
        elif hasattr(self.parent, device_name):
            dev = getattr(self.parent, device_name)
        else:

            for man in self.get_managers():
                if hasattr(man, device_name):
                    dev = getattr(man, device_name)
                    break

            if dev is None:
                self.warning('Invalid device {}'.format(device_name))

        return dev


    def get_default_managers(self):
        return []
    def get_manager_factory(self, package, klass):
#        print package, klass
        class_factory = None
        try:
            m = __import__(package, globals(), locals(), [klass], -1)
            class_factory = getattr(m, klass)
        except ImportError:
            self.warning(' Invalid manager class {}'.format(klass))
        except:
            self.warning('Problem with manager class {} source'.format(klass))
        return class_factory

    def create_device(self, device_name, gdict=None, dev_class=None, prefix=None):
        '''
        '''
        device = None

        if dev_class is not None:
            klass = dev_class
        else:
            klass = self.convert_config_name(device_name)

        if gdict is not None and klass in gdict:
            class_factory = gdict[klass]

        else:
            try:
                package = HW_PACKAGE_MAP[klass]
                m = __import__(package, globals(), locals(), [klass], -1)
                class_factory = getattr(m, klass)

            except ImportError:
                self.warning('Invalid device class {}'.format(klass))
                return

        device = class_factory(name=device_name)

        if device is not None:
            if prefix:
                device_name = ''.join((prefix, device_name))

            
            if device_name in self.traits():
                self.trait_set(**{device_name:device})
            else:
                self.add_trait(device_name, device)

        return device

    def get_file_list(self, p, extension=None):

        if os.path.isdir(p):

            ps = os.listdir(p)
            if extension is not None:
                ps = [pi for pi in ps if pi.endswith(extension)]

            return ps

    def _file_dialog_(self, action, **kw):
        '''
        '''
        dlg = FileDialog(action=action, **kw)
        if dlg.open() == OK:
            return dlg.path

    def _led_editor_factory(self, window, editor):
        '''
        '''
        import wx

        p = wx.Panel(window, -1)
        p.Add()
        return p

    def _led_factory(self, name, color='green'):
        '''

        '''
        i = Item(name, show_label=False)
        return i

    def _switch_factory(self, name, label=False, enabled=None):
        '''
        '''
        if label == True:
            label = '{}_label'.format(name)

        v = VGroup(HGroup(spring, Label(name.upper()), spring),
                 HGroup(spring, self._led_factory('{}_led'.format(name)), spring),
                 self._button_factory(name, label, enabled)
                 )
        return v

    def _switch_group_factory(self, switches, orientation='h', **kw):
        '''

        '''
        if orientation == 'h':
            g = HGroup(**kw)
        else:
            g = VGroup(**kw)

        for s, label, enabled in switches:
            sw = self._switch_factory(s, label=label, enabled=enabled)
            g.content.append(sw)
        return g

    def _scrubber_factory(self, name, range_dict):
        '''
        
        '''
        return Item(name, editor=ScrubberEditor(**range_dict))

    def _scrubber_group_factory(self, scrubbers, **kw):
        '''
        
            
        '''
        vg = VGroup(**kw)
        for name, prefix in scrubbers:
            range_dict = dict(low=getattr(self, '%smin' % prefix), high=getattr(self, '%smax' % prefix))
            vg.content.append(self._scrubber_factory(name, range_dict))
        return vg

    def _readonly_slider_factory(self, *args, **kw):
        '''
        
        '''
        return self._slider_factory(
                                    enabled_when='0',
                                    *args, **kw)
    def _slider_factory(self, name, prefix, mode='slider', ** kw):
        '''
        

        '''
        return Item(name, editor=RangeEditor(mode=mode,
                                            low_name='%smin' % prefix,
                                            high_name='%smax' % prefix,

                                            format='%0.2f'
                                            ),

                                            **kw)

    def _update_slider_factory(self, name, prefix, **kw):
        '''
    
        '''
        vg = VGroup()

        r = self._slider_factory(name, prefix, **kw)
        vg.content.append(r)

        ur = self._slider_factory('update_%s' % name, name, **dict(show_label=False, enabled_when='0'))

        vg.content.append(ur)

        return vg

    def _update_slider_group_factory(self, sliders, **kw):
        '''
            
        '''
        vg = VGroup(**kw)

        for si, prefix, options in sliders:
            if not options:
                options = {}
            vg.content.append(self._update_slider_factory(si, prefix, **options))
        return vg

    def _slider_group_factory(self, sliders, **kw):
        '''
      
        '''
        vg = VGroup(**kw)
        for si, prefix, options in sliders:
            if not options:
                options = {}
            vg.content.append(self._slider_factory(si, prefix, **options))
        return vg

    def _button_factory(self, name, label, enabled=None, align=None, **kw):
        '''
            
        '''
        b = Item(name, show_label=False, **kw)
        if label is not None:
            b.editor = ButtonEditor(label_value=label)

        if enabled is not None:
            b.enabled_when = enabled




        if align is not None:
            if align == 'right':
                b = HGroup(spring, b)
            elif align == 'center':
                b = HGroup(spring, b, spring)
            else:
                b = HGroup(b, spring)



        return b

    def _button_group_factory(self, buttons, orientation='v'):
        '''
        '''
        vg = VGroup() if orientation == 'v' else HGroup()

        for name, label, enabled in buttons:
            vg.content.append(HGroup(self._button_factory(name, label, enabled), springy=False))
        return vg

    def get_menus(self):
        '''
        '''
        pass

    def _menu_factory(self, name, actions):
        '''
        '''
        a = [Action(**a) for a in actions]
        return Menu(name=name, *a)

    def menus_factory(self):
        '''
        '''
        menus = self.get_menus()
        if menus:
            return [self._menu_factory(m, actions) for m, actions in menus ]

    def _menubar_factory(self):
        '''
        '''

        menus = self.menus_factory()
        return MenuBar(*menus)

#=================== EOF =================================================
