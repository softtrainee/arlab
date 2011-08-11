#=============enthought library imports========================
#from traits.api import Any
#=============standard library imports ========================

#=============local library imports  ==========================
from base_data_canvas import BaseDataCanvas
class InteractionCanvas(BaseDataCanvas):
    '''
        G{classtree}
    '''
    def __init__(self, *args, **kw):
        '''
            
        '''
        super(InteractionCanvas, self).__init__(*args, **kw)
        self.component_groups = []
        self.cur_pos = [0, 0]


    def normal_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.cur_pos = [event.x, event.y]

        for compdict in self.component_groups:

            if self._over_components(event, compdict):
                self.event_state = 'select'
                event.window.set_pointer(self.select_pointer)

                break
            else:
                self.draw_info = False
                self.event_state = 'normal'
                event.window.set_pointer(self.normal_pointer)
        self.request_redraw()
        event.handled = True

    def select_mouse_move(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        self.normal_mouse_move(event)

    def select_left_down(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        event.handled = True
        for compdict in self.component_groups:
            c = self._over_components(event, compdict)
            if not c == None:
                return c

    def _over_components(self, event, compdict):
        '''
            @type event: C{str}
            @param event:

            @type compdict: C{str}
            @param compdict:
        '''
        x = event.x
        y = event.y
        for ck in compdict.explanable_items:
            c = compdict.explanable_items[ck]

            dx, dy, = self.map_screen([(c.x, c.y)])[0]
            oo, wh = self.map_screen([(0, 0), (c.width, c.height)])

            w = abs(oo[0] - wh[0])
            h = abs(oo[1] - wh[1])

            dx += w / 2.0
            dy += h / 2.0

            if abs(dx - x) < w and abs(dy - y) < h:

                return c

        return