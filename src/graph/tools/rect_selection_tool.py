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



'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Any, Int, Str
from chaco.api import AbstractOverlay
#=============standard library imports ========================
from numpy import vstack
#=============local library imports  ==========================


class RectSelectionTool(AbstractOverlay):
    '''
    '''
    #update_flag = Bool
    parent = Any
    plotid = Int
    threshold = 5
    hover_metadata_name = Str('hover')
    persistent_hover = False
    selection_metadata_name = Str('selections')

    def normal_mouse_move(self, event):

        control = event.window.control
        self.parent.current_pos = control.ClientToScreenXY(event.x, event.y)

        plot = self.component
        index = plot.map_index((event.x, event.y), threshold=self.threshold)
        if index is not None:
            if event.control_down:
                plot.index.metadata[self.hover_metadata_name] = [index]
                if hasattr(plot, "value"):
                    plot.value.metadata[self.hover_metadata_name] = [index]

        elif not self.persistent_hover:
            plot.index.metadata.pop(self.hover_metadata_name, None)
            if hasattr(plot, "value"):
                plot.value.metadata.pop(self.hover_metadata_name, None)
        return

    def overlay(self, component, gc, *args, **kw):
        '''
   
        '''

        if self.event_state == 'select' and not self.others_active():
            self._overlay_box(gc)

    def _overlay_box(self, gc):
        '''

        '''
        if self._start_pos and self._end_pos:
            gc.save_state()
            try:
                x, y = self._start_pos
                x2, y2 = self._end_pos
                rect = (x, y, x2 - x + 1, y2 - y + 1)
                gc.set_fill_color([1, 0, 0, 0.5])
                gc.set_stroke_color([1, 0, 0, 0.5])
                gc.rect(*rect)
                gc.draw_path()
            finally:
                gc.restore_state()

    def _get_selection_token(self, event):
        '''

        '''
        return self.component.map_index((event.x, event.y), threshold=self.threshold)

    def _already_selected(self, token):
        '''
        '''
        already = False
        plot = self.component
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if md is None or self.selection_metadata_name not in md:
                continue
            if token in md[self.selection_metadata_name]:
                already = True
        return already

    def normal_left_down(self, event):
        '''

        '''

        if not self.others_active():
            self.parent.selected_plotid = self.plotid

            token = self._get_selection_token(event)
            if not token:
                self._start_select(event)
            else:
                if self._already_selected(token):
                    self._deselect_token(token)
                else:
                    self._select_token(token)

    def _deselect_token(self, token):
        '''

        '''
        plot = self.component
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            if not self.selection_metadata_name in md:
                pass
            elif token in md[self.selection_metadata_name]:
                new = md[self.selection_metadata_name][:]
                new.remove(token)
                md[self.selection_metadata_name] = new
                getattr(plot, name).metadata_changed = True

    def _select_token(self, token, append=True):
        '''
        '''
        plot = self.component
        for name in ('index', 'value'):
            if not hasattr(plot, name):
                continue
            md = getattr(plot, name).metadata
            selection = md.get(self.selection_metadata_name, None)
            if selection is None:
                md[self.selection_metadata_name] = [token]
            else:
                if append:
                    if token not in md[self.selection_metadata_name]:
                        new = md[self.selection_metadata_name] + [token]
                        md[self.selection_metadata_name] = new

                        getattr(plot, name).metadata_changed = True
#            print md
#            plot.request_redraw()

    def others_active(self):
        '''
        '''
        # a bit of a hack to prevent selection when we are in the panning
        for plot in self.parent.plots:
            for tool in plot.tools:
                if hasattr(tool, 'state'):
                    if tool.state:
                        return True
        else:
            return False

    def select_left_up(self, event):
        '''

        '''

        self._update_selection()

        self._end_select(event)
        event.handled = True

    def select_mouse_move(self, event):
        '''

        '''
        self._end_pos = (event.x, event.y)
        self.component.request_redraw()
        event.handled = True

    def _update_selection(self):
        '''
        '''
        if self._start_pos and self._end_pos:
            x, y = self._start_pos
            x2, y2 = self._end_pos
            dx, dy = self.component.map_data([x, y])
            dx2, dy2 = self.component.map_data([x2, y2])
            ind = []

            datax = self.component.index.get_data()
            datay = self.component.value.get_data()

            data = vstack([datax, datay]).transpose()
            for i, args in enumerate(data):
                if dx <= args[0] <= dx2 and dy >= args[1] >= dy2:
                    ind.append(i)
            selection = self.component.index.metadata['selections']
            for i in ind:
                if i in selection:
                    selection.pop(selection.index(i))
                else:
                    selection.append(i)
            self.component.index.metadata['selections'] = selection
            self.component.index.metadata_changed = True

    def _end_select(self, event):
        '''
 
        '''
        self.component.request_redraw()
        self.event_state = 'normal'
        event.window.set_pointer('arrow')
        self._end_pos = None

    def _start_select(self, event):
        '''
 
        '''
        self._start_pos = (event.x, event.y)
        self._end_pos = None
        self.event_state = 'select'
        event.window.set_pointer('cross')
#============= EOF =====================================
