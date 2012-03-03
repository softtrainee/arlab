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

#=============standard library imports ========================

#=============local library imports  ==========================
import wx

from canvases.interaction_canvas3D import InteractionCanvas3D
from loaders.scene_loader import SceneLoader
from elements.components import Valve

def url_generator():
    i = 1

    base = 'http://www.mademan.com/chickipedia-hot-100-gallery/'
    while 1:
        if i == 1:
            yield base
        else:
            yield base + str(i)
        i += 1
        if i == 21:
            i = 1
url_gen = url_generator()

class ExtractionLineCanvas3D(InteractionCanvas3D):
    '''
    '''
    control_canvas = None
    manager = None

    interactor_state = 'manual'
    hit = None

    _popup_menu = None
    _selected = None
    _current = None
    def __init__(self, panel, manager):
        '''
        '''
        super(ExtractionLineCanvas3D, self).__init__(panel)
        self.manager = manager

        if manager.valve_manager is not None:
            manager.valve_manager.canvas3D = self

#    def setup(self, setupdir=None, setupfile=None):
    def setup(self):
        '''
        '''
        self.scene_graph = self.scene_graph_factory()
        sl = SceneLoader(self.scene_graph)
        sl.load_scene_graph(self.manager.valve_manager,
                            self)

    def update_popup(self, obj):
        self.popup.text.SetLabel('''Name: {}
State: {}
Locked: {}'''.format(obj.name,
                'Open' if obj.state else 'Closed',
                 'Yes' if obj.soft_lock else 'No'
                 )
                                )

    def OnLock(self, event):
        self._selected.toggle_lock()

    def OnSample(self, event):
        self.manager.sample(self._selected.name, mode='normal')

    def OnCycle(self, event):
        self.manager.cycle(self._selected.name, mode='normal')

    def OnCycleConfigure(self, event):
        pass

    def OnSampleConfigure(self, event):
        pass

    def OnProperties(self, event):
        self.manager.show_valve_properties(self._selected.name)

    def show_menu(self, event, obj):
        if isinstance(obj, Valve):
            valve = self.manager.get_valve_by_name(obj.name)
            enabled = True
            if valve is None:
                enabled = False
            self._selected = obj
            self._popup_menu = wx.Menu()
            panel = event.GetEventObject()

            t = 'Lock'
            lfunc = self.OnLock
            if obj.soft_lock:
                t = 'Unlock'
            item = self._popup_menu.Append(-1, t)
            item.Enable(enabled)
            panel.Bind(wx.EVT_MENU, lfunc, item)

            for t, enable in [('Sample', not self._selected.state),
                               ('Cycle', not self._selected.state),
                               ('Properties...', True)]:
                item = self._popup_menu.Append(-1, t)
                item.Enable(enable and enabled)
                if t.endswith('...'):
                    t = t[:-3]

                panel.Bind(wx.EVT_MENU, getattr(self, 'On{}'.format(t)), item)

            pos = event.GetPosition()
            panel.PopupMenu(self._popup_menu, pos)
            self._popup_menu.Destroy()

            #obj.toggle_lock()
            #self.update_popup(obj)

            self.Refresh()


    def OnAltSelect(self, event):
        '''
        '''
        a = InteractionCanvas3D.OnAltSelect(self, event)
        if a is not None:
            obj = self.scene_graph.get_object_by_id(a)
            self.show_menu(event, obj)

    def OnMotion(self, event):
        hit = InteractionCanvas3D.OnMotion(self, event)

        obj = self.scene_graph.get_object_by_id(hit)
        if isinstance(obj, Valve):
#            self.update_popup(obj)
            self._current = obj
            self.manager.set_selected_explanation_item(obj)
        else:
            self._current = None


    def OnSelect(self, event):
        '''

        '''
        a = InteractionCanvas3D.OnSelect(self, event)
        if a is not None:
            obj = self.scene_graph.get_object_by_id(a)
            if isinstance(obj, Valve):
                istate = self.interactor_state

                if istate == 'manual':
#                    obj.toggle_state(mode = istate)
                    obj.toggle_state()

                elif istate == 'sample':
                    obj.sample_valve()

                self.manager.update_canvas2D(obj.name, obj.state, istate)
#                self.update_popup(obj)

            self.Refresh()

    def _get_object_by_name(self, name):
        '''
        '''
        r = self.scene_graph.get_object_by_name(name)
        return r

#    def _popup_hook(self, hit):
#        obj = self.scene_graph.get_object_by_id(hit)
#        self.manager.set_selected_explanation_item(obj)

    def _on_key_hook(self, event, charcode):
        if event.MetaDown() and charcode == 76:
            if self._current is not None:
                self._current.toggle_lock()

        elif event.MetaDown() and charcode == 66:
            import webbrowser
            webbrowser.open(url_gen.next())



#============= EOF ============================================

#    def update_pumping_duration(self, name, val):
#        '''
#        '''
#        if 'analytical' in name.lower():
#            textp = self._get_object_by_name('Analytical_info_panel')
#        if textp is not None:
#            textp.fields[3] = (val, True, 'pumping_dur')
#        self.Refresh()
#
#    def update_idle_duration(self, name, val):
#        '''
#        '''
#        if 'analytical' in name.lower():
#            textp = self._get_object_by_name('Analytical_info_panel')
#        if textp is not None:
#            textp.fields[4] = (val, True, 'idle_dur')
#        self.Refresh()
#    def update_pressure(self, name, val, state):
#        '''
#            
#        '''
#
#        id = int(name[-1:])
#        if id in [0, 1, 2]:
#            textp = self._get_object_by_name('Analytical_info_panel')
#        else:
#            id -= 3
#            textp = self._get_object_by_name('Roughing_info_panel')
#
#        if textp is not None:
#            textp.fields[id] = (val, state, 'pressure')
#
#        self.Refresh()

        #self.Refresh()

#    def toggle_laser(self,name):
#        l=self._get_object_by_name(name)
#        if l is not None:
#            l.toggle_state()

#    def _load_valve_states(self):
#        '''
#        '''
#        for v in self.valve_manager.components:
#            if v.state:
#                self.set_valve_state(v.name,True)
#            else:
#                self.set_valve_state(v.name,False)


#
#    def open_valve(self, name, remote = False):
#        '''
#            @type name: C{str}
#            @param name:
#
#            @type remote: C{str}
#            @param remote:
#        '''
#        self.set_valve_state(name, True, remote = remote)
#
#    def close_valve(self, name, remote = False):
#        '''
#            @type name: C{str}
#            @param name:
#
#            @type remote: C{str}
#            @param remote:
#        '''
#        self.set_valve_state(name, False, remote = remote)
#    def set_valve_auto(self,name,auto):
#        v = self._get_object_by_name(name)
#        print v
#        if v is not None:
#            v.set_auto_indicator(auto)
#
#    def set_laser_state(self, name, state):
#        '''
#            @type name: C{str}
#            @param name:
#
#            @type state: C{str}
#            @param state:
#        '''
#        l = self._get_object_by_name(name)
#        if l is not None:
#            #l.state=state
#            if state:
#                l.on()
#            else:
#                l.off()
