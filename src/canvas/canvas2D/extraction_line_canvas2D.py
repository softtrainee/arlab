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
from traits.api import Any, Str
#============= standard library imports ========================`

#============= local library imports  ==========================
from src.canvas.canvas2D.markup.markup_canvas import MarkupCanvas
#from src.canvas.designer.valve import Valve
from src.canvas.canvas2D.markup.markup_items import Rectangle, Valve, Line, \
    Label, RoughValve, BaseValve, RoundedRectangle
from pyface.wx.dialog import confirmation

W = 2
H = 2


class ExtractionLineCanvas2D(MarkupCanvas):
    '''
    '''
    valves = None
    active_item = Any
    selected_id = Str
    show_axes = False
    show_grids = False
    use_zoom = False
    padding_left = 0
    padding_right = 0
    padding_bottom = 0
    padding_top = 0
    manager = Any

    aspect_ratio = 4 / 3.

    y_range = (-10, 25)

    def __init__(self, *args, **kw):
        '''
        '''
        super(ExtractionLineCanvas2D, self).__init__(*args, **kw)
        self.valves = dict()

    def toggle_item_identify(self, name):
        v = self._get_valve_by_name(name)
        if v is not None:
            try:
                v.identify = not v.identify
            except AttributeError:
                pass

        self.request_redraw()

    def update_valve_state(self, name, nstate, mode=None):
        '''
        '''
        valve = self._get_valve_by_name(name)
        if valve is not None:
            valve.state = nstate

        self.invalidate_and_redraw()

    def update_valve_lock_state(self, name, lockstate):
        valve = self._get_valve_by_name(name)
        if valve is not None:
            valve.soft_lock = lockstate

        self.invalidate_and_redraw()


    def _get_valve_by_name(self, name):
        '''
        
        '''
        return next((i for i in self.valves.itervalues()
                    if isinstance(i, BaseValve) and i.name == name), None)
#        for i in self.valves:
#            if i.__class__.__name__ == 'Valve':
#                if i.name == name:
#                    return i
    def _get_object_by_name(self, name):
        return next((i for i in self.valves.itervalues() if i.name == name), None)

#    def _bootstrap(self, path):
#        ''' 
#        '''
#        self.valves = []
#        valves = None
#        try:
#            f = open(path, 'r')
#            valves = pickle.load(f)
#            f.close()
#        except:
#            pass
#        return valves
#
#    def bootstrap(self, path):
#        '''
#
#        '''
#        valves = self._bootstrap(path)
#        if valves:
#            self.valves = valves

    @staticmethod
    def _get_canvas_parser(p):
        from src.helpers.parsers.canvas_parser import CanvasParser
        cp = CanvasParser(p)
        return cp

    @staticmethod
    def get_canvas_view_range(p):
        xv = (-25, 25)
        yv = (-25, 25)
        cp = ExtractionLineCanvas2D._get_canvas_parser(p)
        elm = cp._tree.find('xview')
        if elm is not None:
            xv = map(float, elm.text.split(','))

        elm = cp._tree.find('yview')
        if elm is not None:
            yv = map(float, elm.text.split(','))

        return xv, yv

    def load_canvas_file(self, p):
        cp = self._get_canvas_parser(p)
#        def get_translation(elem):
#            return map(float, elem.find('translation').text.split(','))
#
#        def get_dimensions(elem):
#            return 

        def get_floats(elem, name):
            return map(float, elem.find(name).text.split(','))

        def new_rectangle(elem, c, bw=3):
            key = elem.text.strip()
            x, y = get_floats(elem, 'translation')
            w, h = get_floats(elem, 'dimension')
#            self.markupcontainer[key] = Rectangle(x + ox, y + oy, width=w, height=h,
            self.markupcontainer[key] = RoundedRectangle(x + ox, y + oy, width=w, height=h,
                                                canvas=self,
                                                name=key,
#                                                line_width=lw,
                                                border_width=bw,
                                                default_color=c)
        color_dict = dict()
        #get default colors
        for c in cp._tree.findall('color'):
            t = c.text.strip()
            k = c.get('tag')
            co = map(float, t.split(',')) if ',' in t else t

            if k == 'bgcolor':
                self.bgcolor = co
            else:
                color_dict[k] = co

        #get an origin offset
        ox = 0
        oy = 0

        o = cp._tree.find('origin')
        if o is not None:
            ox, oy = map(float, o.text.split(','))

        self.markupcontainer.clear()
        ndict = dict()
        for v in cp.get_elements('valve'):
            key = v.text.strip()
            x, y = get_floats(v, 'translation')
            v = Valve(x + ox, y + oy, name=key,
                                    canvas=self,
                                    border_width=3
                                    )
            #sync the states
            if key in self.valves:
                vv = self.valves[key]
                v.state = vv.state
                v.soft_lock = vv.soft_lock

            self.markupcontainer[key] = v
            ndict[key] = v

        for rv in cp.get_elements('rough_valve'):
            key = rv.text.strip()
            x, y = get_floats(rv, 'translation')
            v = RoughValve(x + ox, y + oy, name=key,
                                    canvas=self)
            self.markupcontainer[key] = v
            ndict[key] = v

        self.valves = ndict

        for b in cp.get_elements('stage'):
            if 'stage' in color_dict:
                c = color_dict['stage']
            else:
                c = (0.8, 0.8, 0.8)
            new_rectangle(b, c, bw=5)

        for s in cp.get_elements('spectrometer'):
            if 'spectrometer' in color_dict:
                c = color_dict['spectrometer']
            else:
                c = (0, 0.8, 0.8)
            new_rectangle(s, c, bw=5)

        for t in cp.get_elements('turbo'):
            if 'turbo' in color_dict:
                c = color_dict['turbo']
            else:
                c = (0, 0.5, 0.8)
            new_rectangle(t, c)
#            key = t.text.strip()

        for i, l in enumerate(cp.get_elements('label')):
            x, y = map(float, l.find('translation').text.split(','))
            l = Label(x + ox, y + oy,
                      text=l.text.strip(),
                      canvas=self,

                      )
            self.markupcontainer['{:03}'.format(i)] = l

        for g in cp.get_elements('getter'):
            v = self.markupcontainer[g.get('valve')]
            w, h = 5, 2
            key = g.text.strip()
            self.markupcontainer[key] = Rectangle(v.x, v.y + 2.5, width=w, height=h,
                                                canvas=self,
                                                name=key,
                                                line_width=2,
                                                default_color=(0, 0.5, 0))
        for g in cp.get_elements('gauge'):
            if 'gauge' in color_dict:
                c = color_dict['gauge']
            else:
                c = (0.8, 0.8, 0.8)
            new_rectangle(g, c)

        for i, c in enumerate(cp.get_elements('connection')):
            start = c.find('start')
            end = c.find('end')
            skey = start.text.strip()
            ekey = end.text.strip()
            try:
                orient = c.get('orientation')
            except:
                orient = None

            x = self.markupcontainer[skey].x
            y = self.markupcontainer[skey].y
            try:
                ox, oy = map(float, start.get('offset').split(','))
            except:
                ox = 1
                oy = 1
            x += ox
            y += oy

            x1 = self.markupcontainer[ekey].x
            y1 = self.markupcontainer[ekey].y
#            ox, oy = map(float, end.get('offset').split(','))

            try:
                ox, oy = map(float, end.get('offset').split(','))
            except:
                ox = 1
                oy = 1

            x1 += ox
            y1 += oy
            if orient == 'vertical':
                x1 = x
            elif orient == 'horizontal':
                y1 = y

            l = Line((x, y), (x1, y1), default_color=(0, 0, 0),
                     canvas=self, width=10)
            self.markupcontainer[('con{:03}'.format(i), 0)] = l

        self.invalidate_and_redraw()

    def _over_item(self, event):
        x = event.x
        y = event.y
#        for k, item in enumerate(self.valves):
        for k, item in self.valves.iteritems():
#            print k
            if hasattr(item, 'is_in'):
                if item.is_in(x, y):
                    return k, item
#            if item.__class__.__name__ == 'Valve':
#            if isinstance(item, Valve):
#                if item.is_in(x, y):
#                    return k, item
#                mx, my = self.map_screen([item.])[0]
#                mx, my = item.get_xy()
#                w, h = item.get_wh()
#                if mx <= x <= (mx + w) and my <= y <= (my + h):
#                    return k, item
#                mx += w / 2.0
#                my += h / 2.0
#                print mx, my, w, h
#                if abs(mx - x) < w and abs(my - y) < h:
#                    return k, item

        return None, None

    def normal_left_down(self, event):
        pass

    def normal_mouse_move(self, event):
        '''

        '''

        k, item = self._over_item(event)
        if item is not None:
            self.active_item = item
            self.event_state = 'select'
            event.window.set_pointer(self.select_pointer)
            self.manager.set_selected_explanation_item(item)
        else:
            self.active_item = None
            self.event_state = 'normal'
            event.window.set_pointer(self.normal_pointer)
        event.handled = True
        self.invalidate_and_redraw()

    def select_mouse_move(self, event):
        '''
         :
        '''
        self.normal_mouse_move(event)

    def OnLock(self, event):
        item = self.active_item
        if item:
            item.soft_lock = lock = not item.soft_lock
            self.manager.set_software_lock(item.name, lock)

    def OnSample(self, event):
        pass
    def OnCycle(self, event):
        pass
    def OnProperties(self, event):
        pass
#    def OnSample(self, event):
#        self.manager.sample(self.active_item.name, mode='normal')
#
#    def OnCycle(self, event):
#        self.manager.cycle(self.active_item.name, mode='normal')

#
#    def OnProperties(self, event):
#        self.manager.show_valve_properties(self.active_item.name)

    def _show_menu(self, event, obj):
        enabled = True
        import wx

#        n = self.active_item.name
#        obj = self.manager.get_valve_by_name()
        if obj is None:
            enabled = False

#        self._selected = obj
        self._popup_menu = wx.Menu()

        panel = event.window.control#GetEventObject()
        if self.manager.mode != 'client':
            t = 'Lock'
            lfunc = self.OnLock
            if obj.soft_lock:
                t = 'Unlock'

            item = self._popup_menu.Append(-1, t)
            item.Enable(enabled)
            panel.Bind(wx.EVT_MENU, lfunc, item)

        en = not obj.state
        try:
            en = en and not obj.soft_lock
        except AttributeError:
            pass

        for t, enable in [('Sample', en),
                           ('Cycle', en),
                           ('Properties...', True)]:
            item = self._popup_menu.Append(-1, t)
            item.Enable(enable and enabled)
            if t.endswith('...'):
                t = t[:-3]

            panel.Bind(wx.EVT_MENU, getattr(self, 'On{}'.format(t)), item)

        pos = event.x, panel.Size[1] - event.y

        panel.PopupMenu(self._popup_menu, pos)
        self._popup_menu.Destroy()
        self.invalidate_and_redraw()

    def select_right_down(self, event):
        item = self.active_item

        if item is not None and\
             isinstance(item, BaseValve):
            self._show_menu(event, item)

#        item = self.valves[self.active_item]
#        item.soft_lock = lock = not item.soft_lock
#        self.manager.set_software_lock(item.name, lock)
#        event.handled = True
        self.invalidate_and_redraw()

    def select_left_down(self, event):
        '''
    
        '''
#        item = self.valves[self.active_item]
        item = self.active_item
        if item is None:
            return

        if item.soft_lock:
            return

        state = item.state
        if isinstance(item, RoughValve) and not state:
            event.handled = True
            result = confirmation(None, 'Are you sure you want to open {}'.format(item.name))
            if result == 5104:
                return

        state = not state

        ok = False
        if self.manager is not None:
            if state:
#                if self.manager.open_valve(item.name, mode = 'manual'):
                if self.manager.open_valve(item.name, mode='normal'):
                    ok = True
            else:
#                if self.manager.close_valve(item.name, mode = 'manual'):
                if self.manager.close_valve(item.name, mode='normal'):
                    ok = True
        else:
            ok = True

#        ok = True
        if ok and not item.soft_lock:
            item.state = state

        self.invalidate_and_redraw()

#============= EOF ====================================
