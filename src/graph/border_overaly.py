#============= enthought library imports =======================
from chaco.api import AbstractOverlay

#============= standard library imports ========================

#============= local library imports  ==========================
class BorderOverlay(AbstractOverlay):
    def overlay(self, component, gc, view_bounds = None, mode = 'normal'):
        '''
            @type component: C{str}
            @param component:

            @type gc: C{str}
            @param gc:

            @type view_bounds: C{str}
            @param view_bounds:

            @type mode: C{str}
            @param mode:
        '''
        print component.outer_bounds, component.outer_position
        gc.set_stroke_color((0, 1, 0))
        x, y = component.outer_position
        w, h = component.outer_bounds
        gc.rect(x - 3, y - 3, w + 6, h + 6)

        gc.stroke_path()
#============= views ===================================
#============= EOF ====================================
