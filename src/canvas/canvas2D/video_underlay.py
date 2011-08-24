#============= enthought library imports =======================
from traits.api import Instance
from chaco.api import AbstractOverlay

#============= standard library imports ========================
#import wx

#============= local library imports  ==========================
from src.image.video import Video
class VideoUnderlay(AbstractOverlay):
    '''
    '''
    video = Instance(Video)
    swap_rb = True
    mirror = False
#    visible = True
    def overlay(self, component, gc, *args, **kw):
        '''

        '''
        try:
            gc.save_state()
            dc = component._window.dc

            bitmap = self.video.get_bitmap(
                                           flip = True,
                                         swap_rb = self.swap_rb,
                                         mirror = self.mirror
                                         )
            if bitmap:
                x = component.x
                y = component.y

                dc.DrawBitmap(bitmap, x, y, False)

        except (AttributeError, UnboundLocalError), e:
            print e
        finally:
            gc.restore_state()




#============= EOF ====================================
