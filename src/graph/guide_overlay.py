#=============enthought library imports=======================
from traits.api import Enum, Float, Tuple
from chaco.api import AbstractOverlay

#=============standard library imports ========================

#=============local library imports  ==========================
class GuideOverlay(AbstractOverlay):
    '''
        G{classtree}
    '''
    orientation = Enum('h', 'v')
    value = Float
    color = Tuple(1, 0, 0)
    def overlay(self, component, gc, view_bounds = None, mode = 'normal'):
        '''

        '''
        gc.save_state()
        gc.clip_to_rect(self.component.x, self.component.y, self.component.width, self.component.height)
        gc.set_line_dash([5, 2.5])
        gc.set_stroke_color(self.color)
        gc.begin_path()

        if self.orientation == 'h':
            x1 = self.component.x
            x2 = self.component.x2
            y1 = y2 = self.component.value_mapper.map_screen(self.value)

        else:
            y1 = self.component.y
            y2 = self.component.y2
            x1 = x2 = self.component.index_mapper.map_screen(self.value)

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.stroke_path()
        gc.restore_state()
