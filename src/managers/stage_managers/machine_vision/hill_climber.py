#=============enthought library imports=======================
from traits.api import HasTraits, Any, Float, Instance, Button, on_trait_change, Range
from traitsui.api import View, Item, HGroup
from src.managers.stage_managers.stage_component_editor import LaserComponentEditor
from pyface.timer.timer import Timer

#============= standard library imports ========================
import math
import copy
from numpy import linspace, meshgrid, random
#============= local library imports  ==========================
from threading import Thread

from src.canvas.canvas2D.markup.markup_canvas import MarkupCanvas
from src.canvas.canvas2D.markup.markup_items import Triangle, Dot

class HillClimber(HasTraits):
    counter = 0
    
    parent = Any
    test = Button
    
    leg_length = Range(1, 5)
    
    dwell_time = Float(250)
    
    timer = Any
    
    canvas = Instance(MarkupCanvas)
    
    center_x = Range(-25, 25)
    center_y = Range(-25, 25)
    #xscalar = Range(0.025, 1)
    #yscalar = Range(0.025, 1)
    randomize = Range(0, 20)
    prev2_popped = None
    prev_popped = None
    
    @on_trait_change('center_x,center_y,randomize')
    def _update_test_point(self):
        try:
            self.canvas.markupcontainer['xxtest_indicator'].x = self.center_x
            self.canvas.markupcontainer['xxtest_indicator'].y = self.center_y       
        except (KeyError, AttributeError):
            pass
        
        self.cmap_data.set_data('cmapdata', self.data_gen())
        self.canvas.invalidate_and_redraw()
        
    def point_gen(self, nx, ny):
        a = 10 - 0.1 * (nx - self.center_x) ** 2 + 10 - 0.1 * (ny - self.center_y) ** 2
        r = 0
        if self.randomize:
            if isinstance(nx, (float, int)):
                r = random.random() * self.randomize
            else:
                r = random.random(nx.shape) * self.randomize
        return a + r
    
    def data_gen(self):
        
        d = linspace(-25, 25, 100)
        x, y = meshgrid(d, d)
        
        return self.point_gen(
                              x, y
                              )
        
    def _canvas_default(self):
        c = MarkupCanvas(show_grids=False)

        zdata = self.data_gen()
        self.cmap_data = c.cmap_plot(zdata)
        
        #make canvas non editable
        c.tool_state = 'noteditable'
        return c
    
    def kill(self):
        if self.timer:
            self.timer.Stop()
            
    def move(self, pos):
        canvas = self.canvas
        
        dx, dy = canvas.map_data(pos[:2])
#        print pos[:2], dx, dy
        #move to the position
#        self.parent.linear_move_to(xaxis=dx, yaxis=dy)
        
    def get_value(self, x, y):
        #provider = self.parent.power_meter
        
        return self.point_gen(x, y)
#        if provider.simulation:
#           return point_calc(x, y)
#        else:
#            
#            return provider.get_power()
#            
    def search(self, ox, oy):
        
        
        #load the contour underlay
        
        
        
        leg = self.leg_length
        canvas = self.canvas
#        self.R = math.sqrt(leg ** 2 - (leg / 2.0) ** 2)
        r = math.sqrt(leg ** 2 - (leg / 2.0) ** 2)
        
#        pts = [(ox, oy, 1), (ox + leg, oy , 5), (ox + leg / 2.0, oy + self.R, 2.0)]
        pts = [(ox, oy, 1), (ox + leg, oy , 5), (ox + leg / 2.0, oy + r, 2.0)]
        pts = [(x, y, self.get_value(x, y)) for x, y, v in pts]
        
        self.start_pts = pts
        
        t = Triangle(canvas=self.canvas,
                     state=True
                     )
        self.test_triangle = t
        self.triangle_count = 1
        self.popped_counter = 0
        canvas.markupcontainer['tri0'] = t
        #xx will prevent indicator from being popped when the markupcontainer fills up
        canvas.markupcontainer[('xxtest_indicator', 0)] = Dot(self.center_x, self.center_y, canvas=canvas)
#        canvas.triangles.append(t)
        canvas.request_redraw()
        
        self.timer = Timer(self.dwell_time, self.step)
        
    def step(self):
        '''
            if the search gets stuck switching between two points reset the values for the nodes in the current 
            triangle
            
            
        '''
        canvas = self.canvas
        new_test_pt, popped = self.get_new_point(self.test_triangle.points)

        ppt = None
        if popped is not None:
            
            t = Triangle(canvas=canvas,
                         state=False)
            t.points = copy.copy(self.test_triangle.points)

            canvas.markupcontainer[('tri{:05n}'.format(self.triangle_count), 0)] = t
            
            self.triangle_count += 1
            if self.triangle_count > 500:
                self.triangle_count = 1
                
            ppt = self.test_triangle.points.pop(popped)
            if self.prev2_popped is not None:
                func = lambda a, b: ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 < 0.1
                if func(self.prev2_popped, ppt):
                    self.popped_counter += 1
            
            if self.popped_counter > 1:
                self.start_pts = [(x, y, self.point_gen(x, y)) for x, y, v in self.test_triangle.points + [self.prev2_popped]]
                self.test_triangle.points = []
                self.popped_counter = 0

        self.test_triangle.points.append(new_test_pt)
        self.prev2_popped = self.prev_popped
        self.prev_popped = ppt
        

        canvas.request_redraw()
        
    def get_new_point(self, pts, tolerance=0.01):

        if len(pts) < 3:
            point, popped = self.start_pts[len(pts)], None
        
        else:
            
            vals = [(pt[2], i) for i, pt in enumerate(pts)]
            vals.sort()
            popped = vals[0][1]
            
            x1 = pts[vals[0][1]][0]
            y1 = pts[vals[0][1]][1]
        
            xa = pts[vals[1][1]][0];ya = pts[vals[1][1]][1]
            xb = pts[vals[2][1]][0];yb = pts[vals[2][1]][1]
            
            dx = (xa - xb) / 2.0
            dy = (ya - yb) / 2.0
            xaa = min(xa, xb)
            yaa = min(ya, yb)
            
            xc = xaa + abs(dx)
            yc = yaa + abs(dy)
            dist = math.sqrt(dx ** 2 + dy ** 2)
                
            dx /= dist
            dy /= dist
            
            if abs(dy) < 1e-14:
                dy = 0.0
                
            r = math.sqrt(self.leg_length ** 2 - (self.leg_length / 2.) ** 2)
            _dir = True
            if dy < 0:
                _dir = False
#                nx = xc - self.R * dy
                nx = xc - r * dy
#                ny = yc + self.R * dx
                ny = yc + r * dx
            elif dy > 0:
                _dir = True
#                nx = xc + self.R * dy
#                ny = yc - self.R * dx
                nx = xc + r * dy
                ny = yc - r * dx
              
            elif dy == 0:
                nx = xc
#                ny = yc - self.R
                ny = yc - r
                if abs(ny - y1) < 0.0001:
#                    ny = yc + self.R
                    ny = yc + r
            
            if abs(nx - x1) < tolerance and abs(ny - y1) < tolerance:
                #we calculated a point already in the triangle
                if _dir:
#                    nx = xc - self.R * dy
#                    ny = yc + self.R * dx
                    nx = xc - r * dy
                    ny = yc + r * dx
                else:
#                    nx = xc + self.R * dy
#                    ny = yc - self.R * dx
                    nx = xc + r * dy
                    ny = yc - r * dx
            
            
            point = (nx, ny, self.get_value(nx, ny))
            
        self.move(point)
        
        return point, popped
    
    def _test_fired(self):
        t = Thread(target=self.search, args=(0, 0))
        t.start()
        
    def canvas_view(self):
        v = View(Item('test', show_label=False),
                 
                 HGroup(Item('center_x'), Item('center_y')),
                 
                 HGroup(Item('randomize'), Item('leg_length')),
                 Item('canvas', style='custom', show_label=False,
                       editor=LaserComponentEditor(width=640, height=480))
                 )
        return v
    
    def traits_view(self):
        return View(Item('dwell_time'),
                    Item('leg_length'),
                    
                    resizable=True,
                    title='Configure Searcher',
                    buttons=['OK', 'Cancel', 'Revert'],
                    
                    
                    )
if __name__ == '__main__':
    d = HillClimber()
    d.configure_traits(view='canvas_view')
#============= EOF =====================================
