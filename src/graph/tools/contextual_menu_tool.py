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
from traits.api import Any
from enable.api import Interactor
# from chaco.base_plot_container import BasePlotContainer
from chaco.plot import Plot

#============= standard library imports ========================

#============= local library imports  ==========================


class ContextualMenuTool(Interactor):
    '''
    '''
    parent = Any

    def normal_mouse_move(self, event):
        '''
        '''
        if self.parent.plots:
            comps = self.component.components_at(event.x, event.y)

            if comps and hasattr(comps[0], 'plots') and comps[0].plots:
                xmapper = comps[0].x_mapper
                ymapper = comps[0].y_mapper

                p = self.component.padding
                xoffset = abs(p[0] - p[1])
                yoffset = abs(p[2] - p[3])
                x = xmapper.map_data(event.x - xoffset)
                y = ymapper.map_data(event.y - yoffset)

                self.parent.status_text = 'x:%0.2f y:%0.2f' % (x, y)

    def normal_mouse_enter(self, event):
        '''
        '''
        self.parent.status_text = ''

    def normal_mouse_leave(self, event):
        '''
        '''
        self.parent.status_text = ''

    def normal_right_down(self, event):
        '''
        '''
        def display_menu(plot):
            parent = self.parent

            if not parent.use_context_menu:
                return
            control = event.window.control
            ex, ey = event.x, event.y
            size = control.size()
            h = size.height()
            ey = h - ey
            pw = control
            offsetx = 0
            offsety = 0
            while 1:
                pw = pw.parentWidget()
                if not pw:
                    break
                x, y = pw.pos().toTuple()
                if x and y:
                    break
                offsetx += x
                offsety += y

            menu_manager = parent.get_contextual_menu()
            menu = menu_manager.create_menu(control, None)
            x += ex + offsetx
            y += ey + offsety + menu.height()

            menu.show(x, y)
            menu_manager.destroy()

        comps = self.component.components_at(event.x, event.y)
        if comps:
            plot = comps[0]
            while not isinstance(plot, Plot):
                plots = plot.components_at(event.x, event.y)
#                print plots
                if plots:
                    plot = plots[0]
                else:
                    break

            self.parent.selected_plot = plot
            self.parent.close_popup()

            display_menu(plot)

        else:
            self.parent.selected_plot = None


        event.handled = True
#============= EOF ====================================
