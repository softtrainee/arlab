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
#from traits.api import Button, Bool, Event, String
##from traitsui.api import View, Item, Group, VGroup, HGroup, spring
##from enable.component_editor import ComponentEditor
##from pyface.timer.api import Timer
#
##=============standard library imports ========================
##=============local library imports  ==========================
#from stage_manager import StageManager
#from managers.laser_managers.searcher import Searcher
#from canvas.canvas2D.search_laser_canvas import SearchLaserCanvas
#class SearchStageManager(StageManager):
#    '''
#        G{classtree}
#    '''
#
#    search = Event
#    searching = Bool(False)
#    search_label = String('Search')
#    searcher = None
#    clear = Button
#    directory = None
#    configure_search = Button
#
#    def __init__(self, *args, **kw):
#        '''
#            @type *args: C{str}
#            @param *args:
#
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        super(SearchStageManager, self).__init__(*args, **kw)
#        self.buttons += [
#                         ('search', 'search_label', None),
#                         ('configure_search', None, None),
#                         ('clear', None, 'not searching')
#                        ]
#
#    def kill(self):
#        '''
#        '''
#        if self.searcher:
#            self.searcher.kill()
#
#    def _clear_fired(self):
#        '''
#        '''
#        self.canvas.clear()
#
#    def _configure_search_fired(self):
#        '''
#        '''
#        self.searcher = s = Searcher(parent = self)
#        s.edit_traits()
#
#    def _search_fired(self):
#        '''
#        '''
#        if self.searching:
#            self.kill()
#            self.search_label = 'Search'
#            self.add_output('stopping search')
#        else:
#            self.add_output('starting search')
#
#            pts = (self.center_x, self.center_y)
#            pts = self.canvas.map_screen([pts])[0]
#            if not self.searcher:
#                self.searcher = Searcher(parent = self)
#
#            #self.canvas.current_point=pts
#
#            self.searcher.id = self.canvas.add_triangles_group()
#            self.canvas.request_redraw()
#            self.searcher.provider = self.parent.analog_power_meter
#
#            self.searcher.search(*pts)
#
#            self.search_label = 'Stop'
#
#
#
#        self.searching = not self.searching
#
#
#    def _canvas_factory(self):
#        '''
#        '''
#
#        sc = SearchLaserCanvas(parent = self,
#                        padding = 30,
#                        #directory = self.get_canvas_dir()
#                        map = self.stage_map
#                        )
#
#        return sc
##    
##def point_calc(nx,ny):
##    return 500-0.005*(nx-150)**2+500-0.005*(ny-350)**2#+random.randint(0,2)
##import math,copy
##class Triangle(object):
##    def __init__(self):
##        self.points=[]
##        self.draw_text=False
##        
##    def render(self,gc,color=(0,1,0)):
##        points=self.points
##        gc.save_state()
##        
##        if points:
##            gc.set_stroke_color(color)
##            gc.begin_path()
##            gc.move_to(*points[0][:2])
##            for p in points[1:]:
##                gc.line_to(*p[:2])
##                  
##            if len(points)==3:
##                gc.line_to(*points[0][:2])
##            
##            gc.stroke_path()
##            
##            if self.draw_text:
##                gc.set_font_size(9)
##                for x,y,v in points:
##                    gc.set_text_position(x,y)
##                    gc.show_text('%0.1f'%v)
##
##        gc.restore_state()
##class Searcher(HasTraits):
##    counter=0
##    
##    parent=Any
##    
##    id=0
##    
##    leg_length=Float(10)
##    dwell_time=Float(150)
##    
##    timer=Any
##    def kill(self):
##        if self.timer:
##            self.timer.Stop()
##            
##    def move(self,pos):
##        canvas=self.parent.canvas
##        
##        dx,dy=canvas.map_data(pos[:2])
##        
##        #move to the position
##        self.parent.linear_move_to(xaxis=dx,yaxis=dy)
##        
##    def get_value(self,x,y):
##        provider=self.parent.power_meter
##        
##        
##        if provider.simulation:
##           return point_calc(x,y)
##        else:
##            
##            return provider.get_power()
##            
##    def search(self,ox,oy):
##        
##        leg=self.leg_length
##        
##        canvas=self.parent.canvas
##        self.R=math.sqrt(leg**2-(leg/2.0)**2)
##        
##        pts=[(ox,oy,1),(ox+leg,oy,5),(ox+leg/2.0,oy+self.R,2.0)]
##        pts=[(x,y,self.get_value(x,y)) for x,y,v in pts]
##        
##        self.start_pts=pts
##        
##        t=Triangle()
##        self.test_triangle=t
##        
##        canvas.triangles.append(t)
##        canvas.request_redraw()
##        
##        self.timer=Timer(self.dwell_time,self.step)
##        
##    def step(self):
##        canvas=self.parent.canvas
##        new_test_pt,popped=self.get_new_point(self.test_triangle.points)
##    
##        #canvas.search_current_points[self.id]=new_test_pt
##        #canvas.current_point=new_test_pt
##        
##        if popped is not None:
##            t=Triangle()
##            t.points=copy.copy(self.test_triangle.points)
##            canvas.triangles.append(t)
##            
##            self.test_triangle.points.pop(popped)
##        
##        self.test_triangle.points.append(new_test_pt)
##
##        canvas.request_redraw()
##        
##    def get_new_point(self,pts, tolerance=1e-5):
##        if len(pts)<3:
##            point,popped= self.start_pts[len(pts)],None
##        
##        else:
##            
##            vals=[(pt[2],i) for i,pt in enumerate(pts)]
##            vals.sort()
##            popped=vals[0][1]
##            
##            x1=pts[vals[0][1]][0]
##            y1=pts[vals[0][1]][1]
##        
##            xa=pts[vals[1][1]][0];ya=pts[vals[1][1]][1]
##            xb=pts[vals[2][1]][0];yb=pts[vals[2][1]][1]
##            
##            dx=(xa-xb)/2.0
##            dy=(ya-yb)/2.0
##            xaa=min(xa,xb)
##            yaa=min(ya,yb)
##            
##            xc=xaa+abs(dx)
##            yc=yaa+abs(dy)
##            dist=math.sqrt(dx**2+dy**2)
##            dx/=dist
##            dy/=dist
##            
##            if abs(dy)<1e-14:
##                dy=0.0
##            
##            if dy<0:
##                dir=False
##                nx=xc-self.R*dy
##                ny=yc+self.R*dx
##            elif dy>0:
##                dir=True
##                nx=xc+self.R*dy
##                ny=yc-self.R*dx
##              
##            elif dy==0:
##                nx=xc
##                ny=yc-self.R
##                if abs(ny-y1)<0.0001:
##                    ny=yc+self.R
##                    
##            if abs(nx-x1)<tolerance and abs(ny-y1)<tolerance:
##                #we calculated a point already in the triangle
##                if dir:
##                    nx=xc-self.R*dy
##                    ny=yc+self.R*dx
##                else:
##                    nx=xc+self.R*dy
##                    ny=yc-self.R*dx
##            
##            
##            point=(nx,ny,self.get_value(nx,ny))
##            
##        self.move(point)
##        
##        return point,popped
##    
##    def traits_view(self):
##        return View(Item('dwell_time'),
##                    Item('leg_length'),
##                    
##                    resizable=True,
##                    title='Configure Searcher',
##                    buttons=['OK','Cancel','Revert'],
##                    
##                    
##                    )
