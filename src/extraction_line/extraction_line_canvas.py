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
from traits.api import HasTraits, Instance, Any, Property, Float, Enum
from traitsui.api import View, Item
#from enable.component_editor import ComponentEditor
#============= standard library imports ========================
import os
#============= local library imports  ==========================
#from canvas.canvas3D.extraction_line_canvas3D import ExtractionLineCanvas3D
from src.canvas.canvas3D.canvas3D_editor import Canvas3DEditor

from src.helpers import paths
class ExtractionLineCanvas3DDummy(HasTraits):
    '''
    '''
    canvas = Any
    scene_graph = Property(depends_on='canvas')
    user_views = Property(depends_on='canvas')
    interactor_state = Property(depends_on='canvas')

    manager = None

    def setup(self, *args, **kw):
        '''
        '''
        if self.canvas is not None:
            self.canvas.setup(*args, **kw)
            self.load_valve_states()

    def _canvas_changed(self):
        self.load_valve_states()

    def load_valve_states(self):
        '''
        '''
        vm = self.manager.valve_manager
        if vm is not None:
            for v in vm.explanable_items:
                self.update_valve_state(v.name, v.state)

    def toggle_item_identify(self, name):
        '''
        '''
        v = self._get_object_by_name(name)
        if v is not None:
            v.toggle_identify()

        #self.canvas.Refresh()
    def lock_valve(self, name):
        '''
        '''
        va = self._get_object_by_name(name)
        if va is not None:
            va.soft_lock = True

    def unlock_valve(self, name):
        '''
        '''
        va = self._get_object_by_name(name)
        if va is not None:
            va.unlock()

    def update_valve_state(self, name, state):
        '''
        '''

        va = self._get_object_by_name(name)
        if va is not None:
            if state:

                va._finish_state_change(True)

            else:
                va._finish_state_change(False)
            self.Refresh()

    def _get_object_by_name(self, name):
        '''
        '''
        if self.canvas:
            return self.canvas._get_object_by_name(name)

    def _get_scene_graph(self):
        '''
        '''
        if hasattr(self.canvas, 'scene_graph'):
            return self.canvas.scene_graph

    def _set_user_views(self, v):
        '''
        '''
        if hasattr(self.canvas, 'user_views'):
            self.canvas.user_views = v

    def _set_user_view(self, v):
        if hasattr(self.canvas, 'user_views'):
            self.canvas._set_view(v)

#    def _get_interactor_state(self):
#        '''
#        '''
#        return self.canvas.interactor_state
#
#    def _set_interactor_state(self, s):
#        '''
#        '''
#        self.canvas.interactor_state = s
#
#    def update_pressure(self, *args, **kw):
#        '''
#        '''
#        if self.canvas is not None:
#            self.canvas.update_pressure(*args, **kw)
#
#    def update_pumping_duration(self, *args, **kw):
#        '''
#        '''
#        if self.canvas is not None:
#            self.canvas.update_pumping_duration(*args, **kw)
#
#    def update_idle_duration(self, *args, **kw):
#        '''
#        '''
#        if self.canvas is not None:
#            self.canvas.update_idle_duration(*args, **kw)

    def Refresh(self):
        '''
        '''
        if self.canvas:
            self.canvas.Refresh()

    def Update(self):
        '''
        '''
        if self.canvas:
            self.canvas.Update()
#    
class ExtractionLineCanvas(HasTraits):
    '''
    '''
    canvas2D = Any#Instance(ExtractionLineCanvas2D)
    canvas3D = Any#Instance(ExtractionLineCanvas3DDummy)
    manager = Any
    style = Enum('2D', '3D')
    width = Float(700)
    height = Float(700)

    def __init__(self, *args, **kw):
        '''
        '''
        super(ExtractionLineCanvas, self).__init__(*args, **kw)

        for c in self.manager.explanation.explanable_items:
            c.canvas = self

    def toggle_item_identify(self, name):
        '''
        '''
        if self.canvas2D is not None:
            self.canvas2D.toggle_item_identify(name)
        if self.canvas3D is not None:
            self.canvas3D.toggle_item_identify(name)

    def Refresh(self):
        '''
        '''
        if self.canvas3D:
            self.canvas3D.Refresh()
        if self.canvas2D:
            self.canvas2D.request_redraw()

    def Update(self):
        '''
        '''
        if self.canvas3D:
            self.canvas3D.Update()

#    def set_interactor_state(self, state):
#        '''
#        
#        '''
#
#        for c in [self.canvas2D, self.canvas3D]:
#            if c is not None:
#                c.interactor_state = state
    def get_object(self, name):
        if self.style == '2D':
            obj = self.canvas2D._get_object_by_name(name)
        else:
            obj = self.canvas3D._get_object_by_name(name)
        return obj

    def load_canvas_file(self, path):
        '''
        '''
        if self.canvas2D:
            self.canvas2D.load_canvas_file(path)

    def update_valve_state(self, name, state, *args, **kw):
        '''
            do the specific canvas action
        '''
        if self.canvas2D:
            self.canvas2D.update_valve_state(name, state)

        if self.canvas3D:
            self.canvas3D.update_valve_state(name, state)

    def _canvas2D_default(self):
        '''
        '''
        from src.canvas.canvas2D.extraction_line_canvas2D import ExtractionLineCanvas2D

        e = ExtractionLineCanvas2D(
                                   manager=self.manager
                                   )
        p = os.path.join(paths.canvas2D_dir, 'canvas.xml')
        e.load_canvas_file(p)
        return e
#     
    def _canvas3D_default(self):
        '''
        '''
        e = ExtractionLineCanvas3DDummy(manager=self.manager)
        return e

    def _get_canvas_size(self):
        '''
        '''

        w = self.width
        h = self.height
        return w, h

    def _canvas2D_group(self):
        '''
        '''

        from enable.component_editor import ComponentEditor
        w, h = self._get_canvas_size()

        g = Item('canvas2D',
                    style='custom',
                    #visible_when='twod_canvas',
                    show_label=False,
                    editor=ComponentEditor(width=w,
                                           height=h
                                            ),
                label='2D'
                )
        return g

    def _canvas3D_group(self):
        '''
        '''
        w, h = self._get_canvas_size()
        g = Item('canvas3D',
                    style='custom',
                    show_label=False,
                    #visible_when = 'not twod_canvas',
                    editor=Canvas3DEditor(),
                    width=w,
                    height=h,
                    label='3D'
                    )

        return g

    def traits_view(self):
        '''
        '''
        if self.style == '2D':
            c = self._canvas2D_group()
        else:
            c = self._canvas3D_group()
        v = View(c)
        return v
#============= EOF ====================================
