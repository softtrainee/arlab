#============= enthought library imports =======================
from traits.api import Instance
from chaco.api import AbstractOverlay

#============= standard library imports ========================

#============= local library imports  ==========================
from src.image.image import Image

class ImageUnderlay(AbstractOverlay):
    '''
    '''
    image = Instance(Image)
    swap_rb = True

    def overlay(self, component, gc, *args, **kw):
        '''

        '''
        try:
            gc.save_state()
            dc = component._window.dc
            bitmap = self.image.get_bitmap(flip = True,
                                         swap_rb = self.swap_rb
                                         )
            if bitmap:
                x = component.x
                y = component.y

                dc.DrawBitmap(bitmap, x, y, False)

        except AttributeError, UnboundLocalError:
            pass
        finally:
            gc.restore_state()




#============= EOF ====================================
