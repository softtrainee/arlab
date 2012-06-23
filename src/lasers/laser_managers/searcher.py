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



##=============enthought library imports=======================
#from traits.api import HasTraits, Float, Any
#from traitsui.api import View, Item
#from pyface.timer.api import Timer
#
##=============standard library imports ========================
#import math, copy
#
##=============local library imports  ==========================
#
#def point_calc(nx, ny):
#    '''
#        @type ny: C{str}
#        @param ny:
#    '''
#    return 500 - 0.005 * (nx - 150) ** 2 + 500 - 0.005 * (ny - 350) ** 2#+random.randint(0,2)
#
#class Triangle(object):
#    def __init__(self):
#        '''
#        '''
#        self.points = []
#        self.draw_text = False
#
#    def render(self, gc, color = (0, 1, 0)):
#        '''
#            @type gc: C{str}
#            @param gc:
#
#            @type color: C{str}
#            @param color:
#
#            @type 1: C{str}
#            @param 1:
#
#            @type 0): C{str}
#            @param 0):
#        '''
#        points = self.points
#        gc.save_state()
#
#        if points:
#            gc.set_stroke_color(color)
#            gc.begin_path()
#            gc.move_to(*points[0][:2])
#            for p in points[1:]:
#                gc.line_to(*p[:2])
#
#            if len(points) == 3:
#                gc.line_to(*points[0][:2])
#
#            gc.stroke_path()
#
#            if self.draw_text:
#                gc.set_font_size(9)
#                for x, y, v in points:
#                    gc.set_text_position(x, y)
#                    gc.show_text('%0.1f' % v)
#
#        gc.restore_state()
#class Searcher(HasTraits):
#    '''
#        G{classtree}
#    '''
#    counter = 0
#    visited_queue = None
#    parent = Any
#    provider = Any
#    id = 0
#
#    leg_length = Float(10)
#    dwell_time = Float(150)
#
#    timer = Any
#    def __init__(self, *args, **kw):
#        '''
#            @type *args: C{str}
#            @param *args:
#
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        super(Searcher, self).__init__(*args, **kw)
#        self.visited_queue = []
#    def kill(self):
#        '''
#        '''
#        if self.timer:
#            self.timer.Stop()
#
#    def move(self, pos):
#        '''
#            @type pos: C{str}
#            @param pos:
#        '''
#
#
#        dx, dy = self.parent.canvas.map_data(pos[:2])
#
#        #move to the position
#        self.parent.linear_move_to(xaxis = dx, yaxis = dy)
#
#    def get_value(self, x, y):
#        '''
#            @type x: C{str}
#            @param x:
#
#            @type y: C{str}
#            @param y:
#        '''
#        provider = self.provider
#
#
#        if provider.simulation:
#           return point_calc(x, y)
#        else:
#
#            return provider.get_power()
#
#    def search(self, ox, oy):
#        '''
#            @type ox: C{str}
#            @param ox:
#
#            @type oy: C{str}
#            @param oy:
#        '''
#
#        leg = self.leg_length
#
#        canvas = self.parent.canvas
#        self.R = math.sqrt(leg ** 2 - (leg / 2.0) ** 2)
#
#        pts = [(ox, oy, 1), (ox + leg, oy, 5), (ox + leg / 2.0, oy + self.R, 2.0)]
#        pts = [(x, y, self.get_value(x, y)) for x, y, v in pts]
#
#        self.start_pts = pts
#
#        t = Triangle()
#        self.test_triangle = t
#
#        canvas.triangles.append(t)
#        canvas.request_redraw()
#
#        self.timer = Timer(self.dwell_time, self.step)
#
#    def step(self):
#        '''
#        '''
#        canvas = self.parent.canvas
#        new_test_pt, popped = self.get_new_point(self.test_triangle.points)
#
#        if not self.found(new_test_pt):
#
#            #canvas.search_current_points[self.id]=new_test_pt
#            #canvas.current_point=new_test_pt
#
#            if popped is not None:
#                t = Triangle()
#                t.points = copy.copy(self.test_triangle.points)
#               # canvas.triangles.append(t)\
#                canvas.triangles_group[self.id][1].append(t)
#                self.test_triangle.points.pop(popped)
#
#            self.test_triangle.points.append(new_test_pt)
#
#            canvas.request_redraw()
#        else:
#            self.parent.search_label = 'Search'
#            self.parent.searching = False
#            self.parent.add_output('found max value %0.3f at %0.3f, %0.3f' % (new_test_pt[2],
#                                                                           new_test_pt[0],
#                                                                           new_test_pt[1]))
#            self.kill()
#
#    def found(self, pt, r = 5):
#        '''
#            @type pt: C{str}
#            @param pt:
#
#            @type r: C{str}
#            @param r:
#        '''
#        #see how many times pt occurs int the visited_queue
#        tol = 1e-5
#
#        vq = self.visited_queue
#        c = 0
#        n = sum([1 for v in vq if abs(pt[0] - v[0]) < tol and abs(pt[1] - v[1]) < tol])
#        if n > r:
#            return True
#        else:
#            self.visited_queue.append(pt)
#
#
#
#
#    def get_new_point(self, pts, tolerance = 1e-5):
#        '''
#            @type pts: C{str}
#            @param pts:
#
#            @type tolerance: C{str}
#            @param tolerance:
#        '''
#        if len(pts) < 3:
#            point, popped = self.start_pts[len(pts)], None
#
#        else:
#
#            vals = [(pt[2], i) for i, pt in enumerate(pts)]
#            vals.sort()
#            popped = vals[0][1]
#
#            x1 = pts[vals[0][1]][0]
#            y1 = pts[vals[0][1]][1]
#
#            xa = pts[vals[1][1]][0];ya = pts[vals[1][1]][1]
#            xb = pts[vals[2][1]][0];yb = pts[vals[2][1]][1]
#
#            dx = (xa - xb) / 2.0
#            dy = (ya - yb) / 2.0
#            xaa = min(xa, xb)
#            yaa = min(ya, yb)
#
#            xc = xaa + abs(dx)
#            yc = yaa + abs(dy)
#            dist = math.sqrt(dx ** 2 + dy ** 2)
#            dx /= dist
#            dy /= dist
#
#            if abs(dy) < 1e-14:
#                dy = 0.0
#
#            if dy < 0:
#                dir = False
#                nx = xc - self.R * dy
#                ny = yc + self.R * dx
#            elif dy > 0:
#                dir = True
#                nx = xc + self.R * dy
#                ny = yc - self.R * dx
#
#            elif dy == 0:
#                nx = xc
#                ny = yc - self.R
#                if abs(ny - y1) < 0.0001:
#                    ny = yc + self.R
#
#            if abs(nx - x1) < tolerance and abs(ny - y1) < tolerance:
#                #we calculated a point already in the triangle
#                if dir:
#                    nx = xc - self.R * dy
#                    ny = yc + self.R * dx
#                else:
#                    nx = xc + self.R * dy
#                    ny = yc - self.R * dx
#
#
#            point = (nx, ny, self.get_value(nx, ny))
#
#        self.move(point)
#
#        return point, popped
#
#    def traits_view(self):
#        '''
#        '''
#        return View(Item('dwell_time'),
#                    Item('leg_length'),
#
#                    resizable = True,
#                    title = 'Configure Searcher',
#                    buttons = ['OK', 'Cancel', 'Revert'],
#
#
#                    )
