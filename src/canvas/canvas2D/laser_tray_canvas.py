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
from traits.api import  Color, Property, Tuple, Float, Any, Bool, Range, on_trait_change, Enum
from traitsui.api import View, Item
#=============standard library imports ========================
#=============local library imports  ==========================
from src.canvas.canvas2D.markup.markup_canvas import MarkupCanvas
from src.canvas.canvas2D.map_canvas import MapCanvas
import math
from src.canvas.canvas2D.markup.markup_items import PointIndicator

class LaserTrayCanvas(MapCanvas):
    '''
    '''
    markup = Bool(False)
    configuration_dir = None

    stage_position = Property(depends_on='_stage_position')
    _stage_position = Tuple(Float, Float)

    desired_position = Property(depends_on='_desired_position')
    _desired_position = Any

#    map = StageMap
    show_axes = True
    current_position = Property(depends_on='cur_pos')
    cur_pos = Tuple(Float(0), Float(0))

    tool_state = None
    prev_x_val = 0
    prev_y_val = 0

    parent = Any

    show_desired_position = Bool(True)

    desired_position_color = Color(0x008000)
    show_laser_position = Bool(True)


    use_zoom = False

    beam_radius = 1
    crosshairs_kind = Enum(1, 2, 3, 4)
    crosshairs_color = Color('maroon')
    crosshairs_offset_color = Color('blue')

    crosshairs_radius = Range(0.0, 4.0, 1.0)
    crosshairs_offset = Tuple(0, 0)
#    _jog_moving = False
    def point_exists(self, x, y, tol=1e-5):
        for p in self.markupdict.itervalues():
            if isinstance(p, PointIndicator):
                if abs(p.x - x) < tol and abs(p.y - y) < tol:
                    #point already in the markup dict
                    return p
        
        
    def new_point(self):
        if self.point_exists(*self._stage_position):
            return
        
        id = 'point{}'.format(self.point_counter)
        p = PointIndicator(*self._stage_position, id=id, canvas=self)
        self.markupdict[id] = p 
        self.point_counter += 1
        self.request_redraw()
        return p
    
    def clear_points(self):
        popkeys = []
        self.point_counter = 0
        for k, v in self.markupdict.iteritems():
            if isinstance(v, PointIndicator):
                popkeys.append(k)
        for p in popkeys:
            self.markupdict.pop(p)
        self.request_redraw()
        
    def load_points_file(self, p):
        self.point_counter = 0
        with open(p, 'r') as f:
            for line in f:
                id, x, y = line.split(',')
                pt = self.point_exists(float(x), float(y))
                if pt is not None:
                    self.markupdict.pop(pt.id)
                
                self.markupdict[id] = PointIndicator(float(x), float(y), id=id, canvas=self)
                self.point_counter += 1
                
        self.request_redraw()
             
    def save_points(self, p):
        lines = []
        for _k, v in self.markupdict.iteritems(): 
            if isinstance(v, PointIndicator):
                lines.append(','.join(map(str, (v.id, v.x, v.y))))
        
        with open(p, 'w') as f:
            f.write('\n'.join(lines))
                
        
    def config_view(self):
        v = View(
               Item('render_map'),
               Item('show_bitmap'),
               Item('show_grids'),
               Item('show_desired_position'),
               Item('desired_position_color', show_label=False, enabled_when='show_desired_position'),
               Item('show_laser_position'),
               Item('crosshairs_kind', enabled_when='show_laser_position'),
               Item('crosshairs_color', show_label=False, enabled_when='show_laser_position'),
               Item('crosshairs_radius', enabled_when='show_laser_position and object.crosshairs_kind==4'),
               Item('crosshairs_offset'),
               Item('crosshairs_offset_color', show_label=False, enabled_when='object.crosshairs_offset!=(0,0)'),
               )
        return v

    def end_key(self, event):
        pass
#        c = event.GetKeyCode()
#        if c == 314: #left
#            self.parent.stop(ax_key = 'x')
#        elif c == 315: #up
#            self.parent.stop(ax_key = 'y')
#        elif c == 316: #right
#            self.parent.stop(ax_key = 'x')
#        elif c == 317: #down
#            self.parent.stop(ax_key = 'y')
#
#        self._jog_moving = False

    def normal_key_pressed(self, event):
#        if not self._jog_moving:
#            c = event.character
#            if c in ['Left', 'Right', 'Up', 'Down']:
#                    event.handled = True
#                    controller = self.parent.stage_controller
#                    controller.jog_move(c)
#                    self._jog_moving = True


        c = event.character
        if c in ['Left', 'Right', 'Up', 'Down']:
            event.handled = True
            self.parent.stage_controller.relative_move(c)
#            self.parent.canvas.set_stage_position(x, y)

        super(LaserTrayCanvas, self).normal_key_pressed(event)

    def _get_current_position(self):

        md = self.map_data(self.cur_pos)
        return  self.cur_pos[0], md[0], self.cur_pos[1], md[1]

    @on_trait_change('''render_map,show_laser_position, show_desired_position,
                         desired_position_color,
                         crosshairs_kind, crosshairs_color,crosshairs_radius,
                         crosshairs_offset,crosshairs_offset_color
                         ''')
    def change_indicator_visibility(self):
        self.request_redraw()

    @on_trait_change('parent:parent:beam')
    def set_beam_radius(self, obj, name, old, new):
        if new:
            self.radius = new / 2.0
            self.request_redraw()

    def valid_position(self, x, y):
        '''
        '''
        if self.x < x <= self.x2 and self.y < y <= self.y2:
            if self.parent is not None:
                p = self.parent.stage_controller
                x, y = self.map_data((x, y))

                if 'x' in p.axes and 'y' in p.axes:
                    if p.xaxes_min < x <= p.xaxes_max and p.yaxes_min < y <= p.yaxes_max:
                        return x, y

    def normal_left_down(self, event):
        '''
        '''
        if self.calibrate or self.markup:
            super(LaserTrayCanvas, self).normal_left_down(event)

        else:

            pos = self.valid_position(event.x, event.y)
            if pos:
                self.parent.linear_move(*pos, calibrated_space=False)
                event.handled = True

    def normal_mouse_wheel(self, event):
        enable_mouse_wheel_zoom = False
        if enable_mouse_wheel_zoom:
            inc = event.mouse_wheel

            self.parent.parent.logic_board.set_zoom(inc, relative=True)
            event.handled = True

#    def normal_key_pressed(self, event):
#        '''
#
#        '''
#        char = event.character
#        if self.tool_state == 'center_point':
#            if char == 'a':
#                self.parent.set_center_point()
#        elif self.tool_state == 'end_point':
#            if char == 'a':
#                self.parent.set_end_point()
#        event.handled = True

    def normal_mouse_move(self, event):
        '''
        '''
        self.cur_pos = (event.x, event.y)
        if self.calibrate or self.markup:
            super(LaserTrayCanvas, self).normal_mouse_move(event)
#
#            #both the markup and map canvas can handle this event
#            MarkupCanvas.normal_mouse_move(self, event)
#            if not event.handled:
#                MapCanvas.normal_mouse_move(self, event)
        else:
            if self.valid_position(event.x, event.y):
                event.window.set_pointer(self.cross_pointer)
            else:
                event.window.set_pointer(self.normal_pointer)

            event.handled = True
        self.request_redraw()

    def normal_mouse_enter(self, event):
        '''
        '''
        event.window.set_pointer(self.cross_pointer)
        event.handled = True

    def normal_mouse_leave(self, event):
        '''
        '''
        event.window.set_pointer(self.normal_pointer)
        self.request_redraw()
        event.handled = True

    def _get_stage_position(self):
        '''
        '''
        return self.map_screen([self._stage_position])[0]

    def set_stage_position(self, x, y):
        '''
        '''
        if x is not None and y is not None:
            self._stage_position = (x, y)
            self.request_redraw()

    def _get_desired_position(self):
        '''
        '''

        if not self._desired_position is None:
            x, y = self.map_screen([self._desired_position])[0]
            return x, y

    def set_desired_position(self, x, y):
        '''
        '''
        self._desired_position = (x, y)
        self.request_redraw()

    def adjust_limits(self, mapper, val, delta=None):
        '''
        '''
        if val is None:
            return

        if delta is None:

            vrange = getattr(self, '{}_mapper'.format(mapper)).range

            vmi = vrange.low
            vma = vrange.high
            pname = 'prev_{}_val'.format(mapper)

            d = val - getattr(self, pname)
            setattr(self, pname, val)

            nmi = vmi + d
            nma = vma + d
        else:
            delta /= 2.0
            nmi = val - delta
            nma = val + delta


        self.set_mapper_limits(mapper, (nmi, nma))

    def _draw_hook(self, gc, *args, **kw):
        '''
        '''

        if self.render_map:
            self._draw_map(gc)

        if self.show_desired_position and self.desired_position is not None:
            #draw the place you want the laser to be
            self._draw_crosshairs(gc, self.desired_position, color=self.desired_position_color, kind=2)

        if self.show_laser_position:
            #draw where the laser is
            #laser indicator is always the center of the screen
            pos = (self.x + (self.x2 - self.x) / 2.0  , self.y + (self.y2 - self.y) / 2.0)

            #add the offset
            if self.crosshairs_offset is not (0, 0):
                pos_off = pos[0] + self.crosshairs_offset[0], pos[1] + self.crosshairs_offset[1]
                self._draw_crosshairs(gc, pos_off, color=self.crosshairs_offset_color, kind=5)
                
                
#            self._draw_crosshairs(gc, pos, color = colors1f[self.crosshairs_color])
            self._draw_crosshairs(gc, pos, color=self.crosshairs_color)

        MarkupCanvas._draw_hook(self, gc, *args, **kw)

    def _draw_crosshairs(self, gc, xy, color=(1, 0, 0), kind=None):
        '''
        '''
        mx = xy[0] + 1
        my = xy[1] + 1

#===============================================================================
#             
#           1 |
#             |
#        0---- m,m  -----2
#             |
#             |3
#        kind 0 none
#        kind 1 with circle
#        kind 2 with out circle
#        kind 3 +
#===============================================================================
        if kind is None:
            kind = self.crosshairs_kind
        radius = 0
        if kind in [1, 5]:
#            args = self.map_screen([(0, 0), (0, self.beam_radius + 0.5),
#                                    (0, 0), (self.beam_radius + 0.5, 0)
#                                    ])
#            radius = abs(args[0][1] - args[1][1])
            radius = self._get_wh(self.beam_radius, 0)[0]

        elif kind == 2:
            radius = 10
        elif kind == 3:
            radius = 0
        elif kind == 4:
            radius = self._get_wh(self.crosshairs_radius, 0)[0]
        else:
            return
        gc.save_state()
        gc.set_stroke_color(color)
    
        if kind is not 5:
            p00 = self.x, my
            p01 = mx - radius, my
    
            p10 = mx, my + radius
            p11 = mx, self.y2
    
            p20 = mx + radius, my
            p21 = self.x2, my
    
            p30 = mx, my - radius
            p31 = mx, self.y
    
            points = [(p00, p01), (p10, p11),
                      (p20, p21), (p30, p31)]
    
    
            
            for p1, p2 in points:
    
                gc.begin_path()
                gc.move_to(*p1)
                gc.line_to(*p2)
                gc.close_path()
                gc.stroke_path()

        if kind in [1, 4, 5]:
            gc.set_fill_color((0, 0, 0, 0))
            if kind == 5:
                step = 20
                for i in range(0, 360, step):
                    gc.arc(mx, my, radius, math.radians(i),
                                           math.radians(i + step / 2.0))        
                    gc.draw_path()
                
            else:
                gc.arc(mx, my, radius, 0, math.radians(360))
            gc.draw_path()

        gc.restore_state()



#========================EOF============================
#    def _draw_current_position(self, gc):
#        gc.save_state()
#
#        gc.set_text_position(self.x + 50, self.y + 18)
#        gc.show_text('{:0.2f},{:0.2f}'.format(*self.cur_pos))
#        gc.restore_state()

#    def _get_desired_position(self):
#        '''
#        '''
#        try:
#            r = self.map_screen([self._desired_position])[0]
#        except:
#            r = None
#        return r


        #self.map = LaserTrayMap(configuration_dir_path = self.configuration_dir)
#        self.component_groups = [self.map]
        #self.cur_pos = (0, 0)
        #self.center_pos = (0, 0)
#        self.old_center_pos = (0, 0)

        #self.next_state_key=KeySpec('Right','Shift')
        #self.previous_state_key=KeySpec('Left','Shift')
        #z=ZoomTool(component=self,always_on=False,)
        #self.overlays.append(z)
        #self.tools.append(PanTool(self))
#    def normal_key_pressed(self,event):
#        
#        self._history_handle_key(event)
#        
#    def set_moving_position(self,x,y):
#        self.moving_position=[x,y]
#        
#    def set_current_position(self, x, y):
#        '''
#            @type x: C{str}
#            @param x:
#
#            @type y: C{str}
#            @param y:
#        '''
#        if x == 'simulation' or y == 'simulation':
#            x = 0.5
#            y = 0.5
#        self.last_data_pos = (x, y)
#    def _draw_targeter(self, gc, xy):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type xy: C{str}
#            @param xy:
#        '''
#        x = xy[0]
#        y = xy[1]
#        gc.save_state()
#        gc.set_stroke_color((1, 0, 0))
#        gc.begin_path()
#        gc.arc(x, y, 5, 0, 360)
#        gc.draw_path()
#
#        gc.restore_state()      
#    def set_desired_position(self, x, y):
#        '''
#            @type x: C{str}
#            @param x:
#
#            @type y: C{str}
#            @param y:
#        '''
#
#        self._desired_position = (x, y)
#        if self.show_desired_position:
#
#
#            #adjust the view range
#            self.adjust_limits('x', x)
#            self.adjust_limits('y', y)
#
#
#            self.request_redraw()
#    def _next_state_pressed(self):
#        '''
#        '''
#        self.update_current_position()
#        x, y = self._current_state()
#        self.parent.linear_move_to(xaxis = x, yaxis = y)
#
#    def _prev_state_pressed(self):
#        '''
#        '''
#        self.update_current_position()
#        x, y = self._current_state()
#        self.parent.linear_move_to(xaxis = x, yaxis = y)
#    def _draw_map(self, gc):
#        '''
#            @type gc: C{str}
#            @param gc:
#        '''
#        comps = self.map.explanable_items
#        shape = self.map.sample_hole_shape
#        size = self.map.sample_hole_size
#        gc.save_state()
#
#
#        #cp=np.matrix([[self.stage_center_position[0]],
#        #              [self.stage_center_position[1]]])
#        #cp_n=np.matrix([[-self.stage_center_position[0]],
#        #              [-self.stage_center_position[1]]])
#
#        #r=np.matrix([[math.cos(a),math.sin(a)],
#        #            [-math.sin(a),math.cos(a)]])
#        for c in comps:
#            c = comps[c]
#
#            #tp=np.matrix([[c.x],[c.y]])
#            #ni=r*tp+cp
#
#            #x=ni.item(0)
#            #y=ni.item(1)
#            x = c.x + self.stage_center_position[0]
#            y = c.y + self.stage_center_position[1]
#
#            x, y = self.map_screen([(x, y)])[0]
#
#            self._draw_sample_hole(gc, x, y, size, shape)
#
#
#        gc.restore_state()
#    def _draw_scale(self, gc, units = 'inches'):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type units: C{str}
#            @param units:
#        '''
#        gc.save_state()
#        gc.set_fill_color((0, 0, 0))
#
#
#        s = 0.5
#        scale_length_px = s / self.map.x_axis_throw * self.width
#
#        ox = self.x
#        oy = self.y
#        gc.rect(ox + 10, oy + 10, scale_length_px, 5)
#        gc.set_text_position(ox + 50, oy + 18)
#
#        #s=scale_length_px/self.view_bounds[2]*self.map.x_axis_throw
#        if units == 'microns':
#            un = u'\u03BC'.join(' m')
#        elif units == 'inches':
#            un = 'in'
#
#        gc.show_text('%0.3f %s' % (s, un))
#        gc.draw_path()
#        gc.restore_state()
