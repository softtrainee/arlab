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
from traits.api import Enum, List, Property
#============= standard library imports ========================

#============= local library imports  ==========================
#from markup_canvas import MarkupCanvas
from extraction_line_canvas2D import ExtractionLineCanvas2D
from src.canvas.designer.canvas_previewer import CanvasPreviewer
from src.canvas.canvas2D.rect_selection_tool import RectSelectionTool


class DesignerCanvas(ExtractionLineCanvas2D):
    '''
    '''
    tool_state = Enum('select', 'line', 'mline', 'valve')
    active = False
    _selected_item = Property(depends_on='selected_id')
    show_axes = True
    show_grids = True
    padding_left = 50
    padding_right = 50
    padding_bottom = 50
    padding_top = 50
    selected_items = List

    def __init__(self, *args, **kw):
        '''

        '''
        super(DesignerCanvas, self).__init__(*args, **kw)

        r = RectSelectionTool(component=self)
        self.overlays.append(r)


    def _get__selected_item(self):
        '''
        '''
        if self.selected_id >= 0:
            return self.items[self.selected_id]

    def _get__active_item(self):
        '''
        '''
        if self.active_item >= 0:
            return self.items[self.active_item]

    def bootstrap(self, path):
        '''
            @type path: C{str}
            @param path:
        '''
        for item in  self._bootstrap(path):
            self.add_item(item, use_editor=False)
        self.invalidate_and_redraw()

    def add_item(self, item_name, args=None, use_editor=True):
        '''
            @type item_name: C{str}
            @param item_name:

            @type args: C{str}
            @param args:

            @type use_editor: C{str}
            @param use_editor:
        '''
        self.selected_items = []
        if isinstance(item_name, str):
            if args is None:
                args = dict()

            item = globals()[item_name.capitalize()](state=False, **args)
        else:
            item = item_name

        item.on_trait_change(self.request_redraw, '_x, _y, identify, name')
        if use_editor:
            info = item.edit_traits(kind='livemodal')
            if info.result:
                self.active_item = len(self.items)
                self.items.append(item)
        else:
            self.active_item = len(self.items)
            self.items.append(item)

    def normal_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.temp_start_pos = (event.x, event.y)
        if self.tool_state == 'valve' and self.active:
            self.event_state = 'vdraw'

        else:
            #super(DesignerCanvas, self).normal_mouse_move(event)
            ExtractionLineCanvas2D.normal_key_pressed(self, event)
    def vdraw_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        id = self.active_item
        item = self.items[id]

        item.pos = tuple(self.map_data((event.x, event.y)))
        self.invalidate_and_redraw()

    def select_left_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''

        self.selected_id = self.active_item
        self.active = True

    def select_left_up(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.active = False
        self.event_state = 'normal'



    def normal_left_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.selected_id = -1
        for i in self.selected_items:
            i.selected = False
        self.selected_items = []
        event.handled = True

    def select_mouse_move(self, event):
        def adjust(ii, adj):
            #get items position in screen space
            pos = self.map_screen([ii.pos])[0]

            #apply adjustment and map to data space
            ii.pos = tuple(self.map_data((pos[0] + adj[0], pos[1] + adj[1])))

        if self.active:

            #calc adjustment in screen space
            adj = self._calc_adjustment(event)
            if self.selected_items:
                for i in self.selected_items:
                    adjust(i, adj)
            else:
                item = self.items[self.active_item]
                adjust(item, adj)


            self.temp_start_pos = (event.x, event.y)
        else:
            self.normal_mouse_move(event)

    def vdraw_left_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.event_state = 'normal'
        self.active = False
        self.invalidate_and_redraw()

        event.handled = True

    def key_set_tool_state(self, event):
        '''

        '''
        try:
            c = event.character
            window = event.window
            if c == 'v':
                self.tool_state = 'valve'
                window.set_pointer(self.cross_pointer)
                self.add_item('valve')
            elif c == 'p':
                e = CanvasPreviewer()
                e.canvas.items = self.items
                e.edit_traits()

            elif c == 'Backspace':
                if self.selected_items:
                    for i in self.selected_items:
                        self.items.remove(i)
                else:
                    self.items.pop(self.selected_id)

            elif c == 'c':
                self.items = []

            else:
                ExtractionLineCanvas2D.key_set_tool_state(event)
                #super(DesignerCanvas, self).key_set_tool_state(event)
        except:
            pass
        self.invalidate_and_redraw()

    def check_collision(self, item, srect):
        '''
            @type item: C{str}
            @param item:

            @type srect: C{str}
            @param srect:
        '''
        x, y = self.map_screen([item.pos])[0]

        ssx, ssy = srect[0]
        sex, sey = srect[1]

        ssx, sex = max((ssx, sex)), min((ssx, sex))
        ssy, sey = max((ssy, sey)), min((ssy, sey))

        print ssx, ssy, '--', sex, sey
        if sex <= x <= ssx and sey <= y <= ssy:
            return True

#============= EOF ====================================
