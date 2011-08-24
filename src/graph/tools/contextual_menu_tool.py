#============= enthought library imports =======================
from traits.api import Any
from enable.api import Interactor

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
        def display_menu(parent, event):
            window = event.window.control
            _w, h = window.GetSize()
            x = event.x
            y = h - event.y

            parent._control = window

            menu = parent.get_contextual_menu()
            wxmenu = menu.create_menu(window, None)

            window.PopupMenu(wxmenu, (x, y))
            wxmenu.Destroy()

        comps = self.component.components_at(event.x, event.y)

        if comps:
            plot = comps[0]
            self.parent.selected_plot = plot
            display_menu(self.parent, event)
        else:
            display_menu(self.parent, event)
            #if hasattr(self.parent, 'explanable_items'):
    #            self.parent.selected_plotid = self.parent.plotcontainer.explanable_items.index(plot)

        event.handled = True
#============= EOF ====================================
