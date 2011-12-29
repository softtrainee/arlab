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
from traits.api import Int, Any
import apptools.sweet_pickle as pickle
#============= standard library imports ========================`

#============= local library imports  ==========================
from src.canvas.canvas2D.markup.markup_canvas import MarkupCanvas
from src.canvas.designer.valve import Valve
W = 2
H = 2
class ExtractionLineCanvas2D(MarkupCanvas):
    '''
    '''
    items = None
    active_item = Int(-1)
    selected_id = Int(-1)
    show_axes = False
    show_grids = False
    use_zoom = False
    padding_left = 0
    padding_right = 0
    padding_bottom = 0
    padding_top = 0
    manager = Any
    def __init__(self, *args, **kw):
        '''
        '''
        super(ExtractionLineCanvas2D, self).__init__(*args, **kw)
        self.items = []
    def toggle_item_identify(self, name):
        v = self._get_valve_by_name(name)
        if v is not None:
            v.identify = not v.identify

        self.request_redraw()

    def update_valve_state(self, name, nstate, mode=None):
        '''
        '''
        valve = self._get_valve_by_name(name)
        if valve is not None:
            valve.state = nstate
        self.invalidate_and_redraw()

    def _get_valve_by_name(self, name):
        '''
        
        '''

        return next((i for i in self.items if i.__class__.__name__ == 'Valve' and i.name == name), None)
#        for i in self.items:
#            if i.__class__.__name__ == 'Valve':
#                if i.name == name:
#                    return i
    def _get_object_by_name(self, name):
        return next((i for i in self.items if i.name == name), None)


    def _bootstrap(self, path):
        ''' 
        '''
        self.items = []
        items = None
        try:
            f = open(path, 'r')
            items = pickle.load(f)
            f.close()
        except:
            pass
        return items

    def bootstrap(self, path):
        '''

        '''
        items = self._bootstrap(path)
        if items:
            self.items = items
        self.invalidate_and_redraw()

    def _over_item(self, event):
        x = event.x
        y = event.y
        for k, item in enumerate(self.items):
            if item.__class__.__name__ == 'Valve':

                mx, my = self.map_screen([item.pos])[0]

                w, h = self._get_wh(W, H)
                mx += w / 2.0
                my += h / 2.0
                if abs(mx - x) < w and abs(my - y) < h:
                    return k, item

        return None, None

    def normal_left_down(self, event):
        pass

    def normal_mouse_move(self, event):
        '''

        '''

        k, item = self._over_item(event)
        if item is not None:
            self.active_item = k
            self.event_state = 'select'
            event.window.set_pointer(self.select_pointer)
            self.manager.set_selected_explanation_item(item)
        else:
            self.active_item = -1
            self.event_state = 'normal'
            event.window.set_pointer(self.normal_pointer)
        event.handled = True
        self.invalidate_and_redraw()

    def select_mouse_move(self, event):
        '''
         :
        '''
        self.normal_mouse_move(event)

    def select_right_down(self, event):
        item = self.items[self.active_item]
        item.soft_lock = lock = not item.soft_lock
        self.manager.set_software_lock(item.name, lock)
        event.handled = True
        self.invalidate_and_redraw()

    def select_left_down(self, event):
        '''
    
        '''
        item = self.items[self.active_item]


        state = item.state
        state = not state

        ok = False
        if self.manager is not None:
            if state:
#                if self.manager.open_valve(item.name, mode = 'manual'):
                if self.manager.open_valve(item.name, mode='manual'):
                    ok = True
            else:
#                if self.manager.close_valve(item.name, mode = 'manual'):
                if self.manager.close_valve(item.name, mode='manual'):
                    ok = True
        else:
            ok = True

        if ok and not item.soft_lock:
            item.state = state
        self.invalidate_and_redraw()

    def _draw_hook(self, gc, *args, **kw):
        '''

        '''
#        MarkupCanvas._draw_hook(self, gc, *args, **kw)
        super(ExtractionLineCanvas2D, self)._draw_hook(gc, *args, **kw)
        self._draw_items(gc)

    def _draw_items(self, gc):
        '''
        '''
        gc.save_state()
        for item in self.items:
            if isinstance(item, Valve):
#            if item.__class__.__name__ == 'Valve':
                if item.pos:
                    pos = tuple(self.map_screen([item.pos])[0])
                    w, h = self._get_wh(W, H)
                    args = pos + (w, h)

                    if item.state:
                        gc.set_fill_color((0, 1, 0))
                    else:
                        if item.selected:
                            gc.set_fill_color((1, 1, 0))
                        else:
                            gc.set_fill_color((1, 0, 0))

                    gc.rect(*args)
                    gc.draw_path()

                    #print item.name, item.soft_lock
                    if item.soft_lock:
                        gc.save_state()
                        gc.set_fill_color((0, 0, 0, 0))
                        gc.set_stroke_color((0, 0.75, 1))
                        gc.set_line_width(3)
                        gc.rect(pos[0] - 2, pos[1] - 2, w + 4, h + 4)
                        gc.draw_path()
                        gc.restore_state()

                    if not item.identify:
                        gc.set_fill_color((0, 0, 0))
#                        if item.state:
#                        else:
#                            gc.set_fill_color((0, 1, 0))

                        try:
                            gc.set_text_position(pos[0] + w / 4.0, pos[1] + h / 4.0)
                            gc.show_text(str(item.name))
                        except RuntimeError, e:
                            print e
                        finally:
                            gc.draw_path()

        gc.restore_state()

#============= views ===================================
#============= EOF ====================================


#=============enthought library imports=======================
#from enable.api import Component, Pointer

#=============standard library imports ========================

#import os
#import math
#=============local library imports  ==========================

#from map_canvas import MapCanvas
#from map import ExtractionLineMap, Valve2D
#from src.color_generators import colors1f as colors

#class ExtractionLineCanvas2D(MapCanvas):
#    '''
#        G{classtree}
#    '''
#    valve_manager = None
#    pump_manager = None
#
#    interactor_state = 'manual'
#
#    def __init__(self, valve_manager, *args, **kw):
#        '''
#            @type valve_manager: C{str}
#            @param valve_manager:
#
#        '''
#
#        kw['view_x_range'] = [0, 800]
#        kw['view_y_range'] = [0, 800]
#        super(ExtractionLineCanvas2D, self).__init__(*args, **kw)
#
#
#        self.text = {}
#
#
#        self.valve_manager = valve_manager
#
#
#        self.map = ExtractionLineMap(self,
#                                     self.valve_manager,
#                                     configuration_dir_path = self.configuration_dir)
#        self.component_groups = [self.map]
#
#    def draw(self, gc, view_bounds = None, mode = 'default'):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type view_bounds: C{str}
#            @param view_bounds:
#
#            @type mode: C{str}
#            @param mode:
#        '''
#        super(ExtractionLineCanvas2D, self).draw(gc, view_bounds = view_bounds, mode = mode)
#        gc.save_state()
#        try:
#            self._draw_components(gc, view_bounds)
#        finally:
#            gc.restore_state()
#
##    def _draw_map(self, gc):
##        gc.save_state()
###        if not self.map==None:
###            v = self.valve_manager.components
###            if v['N'].state or v['M'].state:
###                if not v['M'].state:
###                    gc.draw_image(self.map.get_image(2))
###                else:
###                    gc.draw_image(self.map.get_image(1))
###                if v['D'].state:
###                    gc.draw_image(self.map.get_image(3))
###            #p = self.pump_manager.components
###            if p['PA'].state:
###                gc.draw_image(self.map.get_image(4))
###                #gc.draw_image(self.map.get_image(2))
###            else:
###                gc.draw_image(self.map.get_image(0))
##        gc.draw_image(self.map.get_image(0))
##        gc.restore_state()
#    def _draw_pressures(self, gc, view_bounds):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type view_bounds: C{str}
#            @param view_bounds:
#        '''
#        w = 80
#        h = 30
#        gc.save_state()
#        xx = 0.05
#        yy = 0.25
#        x, y = self._pos_to_screen(xx, yy, view_bounds)
#        self._draw_pressure_box(gc, x, y, w, h, view_bounds)
#        args = [x, y, w, h]
#        self._draw_pressure_text(gc, 'A', args)
##===================================================         
#        xx = 0.79
#        yy = 0.25
#        x, y = self._pos_to_screen(xx, yy, view_bounds)
#        self._draw_pressure_box(gc, x, y, w, h, view_bounds)
#        args = [x, y, w, h]
#        self._draw_pressure_text(gc, 'B', args)
##===================================================
#        xx = 0.414
#        yy = 0.2
#        x, y = self._pos_to_screen(xx, yy, view_bounds)
#        self._draw_pressure_box(gc, x, y, w, h, view_bounds)
#        args = [x, y, w, h]
#        self._draw_pressure_text(gc, 'C', args)
#        gc.restore_state()
#    def _draw_pressure_box(self, gc, x, y, w, h, view_bounds):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type x: C{str}
#            @param x:
#
#            @type y: C{str}
#            @param y:
#
#            @type w: C{str}
#            @param w:
#
#            @type h: C{str}
#            @param h:
#
#            @type view_bounds: C{str}
#            @param view_bounds:
#        '''
#        gc.save_state()
#        gc.set_line_width(5)
#        gc.set_fill_color((1, 1, 1))
#        gc.rect(x, y, w, h)
#        gc.draw_path()
#        gc.restore_state()
#
#    def _draw_pressure_text(self, gc, key, args):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type key: C{str}
#            @param key:
#
#            @type args: C{str}
#            @param args:
#        '''
#        gc.save_state()
#        x = args[0]
#        y = args[1]
#        h = args[3]
#        text = self.text[key]
#
#        gc.set_fill_color((0, 0, 0))
#        fontsize = 14
#        gc.set_font_size(fontsize)
#
#        superscript = True
#        if superscript:
#            if len(text) > 1:
#                text, stext = self._do_super_script(text)
#                gc.set_text_position(x + 5, y + h / 2 - fontsize / 4)
#                gc.show_text(text)
#                gc.set_font_size(10)
#                gc.set_text_position(x + 5 + fontsize * len(text) / 2, y + h - fontsize)
#                gc.show_text(stext)
#        else:
#            gc.set_text_position(x + 5, y + h / 2 - fontsize / 4)
#            gc.show_text(text)
#        gc.restore_state()
#
#    def set_pressure(self, s, k):
#        '''
#            @type s: C{str}
#            @param s:
#
#            @type k: C{str}
#            @param k:
#        '''
#        self.text[k] = s
#
#    def _draw_components(self, gc, view_bounds = None):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type view_bounds: C{str}
#            @param view_bounds:
#        '''
#        dict = self.map.explanable_items
#        for c in dict:
#            self._draw_valve(gc, dict[c])
##        v = self.valve_manager.components
##        for vi in v:
##            self._draw_valve(gc,v[vi],view_bounds)
###         
##        p = self.pump_manager.components
##        for pi in p:
##            self._draw_pump(gc,p[pi],view_bounds)
##    def _draw_pump(self, gc, p, view_bounds):
##        gc.save_state()
##        if p.state:
##            gc.set_fill_color(self.OPENCOLOR)
##        else:
##            gc.set_fill_color(self.CLOSECOLOR)
##        x, y = self._pos_to_screen(p.canvas_x, p.canvas_y, view_bounds)
##        w, h = self._size_to_screen(p.width, p.height, view_bounds)
##        gc.rect(x, y, w, h)
##        gc.draw_path()
##        gc.restore_state()
##
##        gc.save_state()
##        gc.set_font_size(15)
##        gc.set_text_position(x + 5, y + 5)
##        gc.show_text(p.name)
##        gc.restore_state()
#
#    def _draw_valve(self, gc, v):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type v: C{str}
#            @param v:
#
#            @type view_bounds: C{str}
#            @param view_bounds:
#        '''
#
#        x, y = self.map_screen([(v.x, v.y)])[0]
#        #x=v.x
#        #y=v.y
#        o, wh = self.map_screen([(0, 0), (v.width, v.height)])
#
#        w = abs(o[0] - wh[0])
##        h=abs(o[1]-wh[1])
#
#        r = w / 2.0
#
#        sf = lambda x, r, a: x + r * (1 - math.sin(math.radians(a)))
#        cf = lambda x, r, a: x + r * (1 - math.cos(math.radians(a)))
#
#        gc.save_state()
#        gc.set_line_width(2)
#
#        if v.soft_lock:
#            gc.set_stroke_color(colors['deepskyblue'])
#        else:
#            if v.state:
#                gc.set_stroke_color(colors['green'])
#            else:
#                gc.set_stroke_color(colors['red'])
#
#        xo = x + r
#        yo = y + r
#        if not v.state:
#            for xx, yy, x2, y2 in [[sf(x, r, 45), cf(y, r, 45),
#                                 sf(x + 2 * r, -r, 45), cf(y + 2 * r, -r, 45)],
#                              [sf(x + 2 * r, -r, 45), cf(y, r, 45),
#                               sf(x, r, 45), cf(y + 2 * r, -r, 45)]]:
#
#                gc.move_to(xx, yy)
#                gc.line_to(x2, y2)
#                gc.stroke_path()
#
#        gc.arc(xo , yo, r, 0, 360)
#        gc.stroke_path()
#
#        gc.restore_state()
#
#        draw_text = False
#        if draw_text:
#            gc.save_state()
#            gc.set_font_size(15)
#            gc.set_text_position(x + 5, y + 5)
#            gc.show_text(v.name)
#            gc.restore_state()
#
#
#    def _get_object_by_name(self, name):
#        '''
#            @type name: C{str}
#            @param name:
#        '''
#        if self.map.explanable_items.has_key(name):
#            return self.map.explanable_items[name]
##    def set_map(self):
##        self.map = 
#    def lock_valve(self, name):
#        v = self._get_object_by_name(name)
#        if isinstance(v, Valve2D):
#            v.soft_lock = True
#    def unlock_valve(self, name):
#        v = self._get_object_by_name(name)
#        if isinstance(v, Valve2D):
#            v.soft_lock = False
#    def set_valve_state(self, name, state):
#        '''
#            @type name: C{str}
#            @param name:
#
#            @type state: C{str}
#            @param state:
#        '''
#        v = self._get_object_by_name(name)
#        if isinstance(v, Valve2D):
#            v.state = state
#            self.request_redraw()
#
##        for comps in self.map.explanable_items:
##            v = self.map.explanable_items[comps]
##            if isinstance(v, Valve2D) and v.name == name:
##                v.state = state
##                self.request_redraw()
##                break
##            
#
##    def set_valve_manual_state(self, name, state):
##        '''
##            @type name: C{str}
##            @param name:
##
##            @type state: C{str}
##            @param state:
##        '''
##        for comps in self.map.explanable_items:
##            v = self.map.explanable_items[comps]
##            if isinstance(v, Valve2D) and v.name == name:
##                v.manual_state = state
##                self.request_redraw()
##                break
##            
##            
#    def select_left_down(self, event):
#        '''
#            @type event: C{str}
#            @param event:
#        '''
#        def _actuate_(valve, mode):
#            #valve.state = not valve.state
#            name = valve.name
#            if not valve.state:
#                if self.valve_manager.open_by_name(name, mode = mode):
#                    valve.state = True
#            else:
#                if self.valve_manager.close_by_name(name, mode = mode):
#                    valve.state = False
#        c = super(ExtractionLineCanvas2D, self).select_left_down(event)
#        if c is not None:
#            i_state = self.interactor_state
#
#            if isinstance(c, Valve2D):
#                if i_state == 'manual':
#                    #c.manual_state = True
#                    _actuate_(c, i_state)
#                elif i_state == 'locking_manual':
#                    c.soft_lock = True
#                    _actuate_(c, i_state)
#                elif i_state == 'unlock':
#                    #c.manual_state = False
#                    c.soft_lock = False
#
#
#
#                self.parent.update_canvas(c, 'canvas3D', i_state)
#
#        self.request_redraw()
#        event.handled = True
#    def _do_super_script(self, t):
#        '''
#            @type t: C{str}
#            @param t:
#        '''
#        #assume only 2 sigfigs
#        exp = t[-3:] #strip of the e+-XX
#        #text = t[:-4] #get digits
#        rtext = '%s x10' % t[:-4]
#
#
#        return rtext, exp
#
#
#
#
