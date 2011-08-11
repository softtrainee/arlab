#============= enthought library imports =======================
from traits.api import Str, Float
from chaco.api import AbstractOverlay

#============= standard library imports ========================
import wx
import os
#============= local library imports  ==========================
import math
class BitmapUnderlay(AbstractOverlay):
    '''
    '''

#    data_origin = None
    path = Str
    scale = Float(1)
    sdx = Float
    sdy = Float
    bitmap = None
    canvas_scaling = Float(1)
    def _path_changed(self):

        p = self.path
        if p is not None and os.path.isfile(p):
            image = wx.Image(p)
            image = image.Mirror(horizontally = False)
            self.bitmap = wx.BitmapFromImage(image)

    def overlay(self, component, gc, *args, **kw):
        '''

        '''
        try:
            gc.save_state()
            dc = component._window.dc

            ca = component.calibration_item
            if  self.bitmap and ca is not None:


                gc.clip_to_rect(component.x, component.y,
                                component.width, component.height)


                cx, cy = component.map_screen([ca.get_center_position()])[0]

                rx = cx + 1
                ry = cy + 1
                #do rotation around center
                gc.translate_ctm(rx, ry)
                gc.rotate_ctm(math.radians(ca.get_rotation()))
                gc.translate_ctm(-rx, -ry)

                #correct for padding and delta size
                dx = ((self.bitmap.GetWidth() - self.component.width -
                      self.component.padding_left - self.component.padding_right
                      ) / 2.0)
                dy = ((self.bitmap.GetHeight() - self.component.height -
                      self.component.padding_top - self.component.padding_bottom
                      ) / 2.0)

                dx = (self.bitmap.GetWidth() - self.component.width) / 2.0 - self.component.padding_left
                dy = (self.bitmap.GetHeight() - self.component.height) / 2.0 - self.component.padding_bottom
                gc.translate_ctm(-dx, -dy)

                #correct for center
                ox, oy = component.map_screen([(0, 0)])[0]
                tpos = (cx - ox, cy - oy)
                gc.translate_ctm(tpos[0], tpos[1])

                #correct for scaling
                scale = self.scale * self.canvas_scaling

                sdx = self.bitmap.GetWidth() / 2.0 * (scale - 1)
                sdy = self.bitmap.GetHeight() / 2.0 * (scale - 1)
                gc.translate_ctm(-sdx , -sdy)

                #scale
                gc.scale_ctm(scale, scale)

                da = self.component.map_data((0, 0))
                da[0] -= self.component.parent.stage_controller.x
                da[1] -= self.component.parent.stage_controller.y
                x, y = self.component.map_screen([da])[0]
                dc.DrawBitmap(self.bitmap, x, y, False)

        except (AttributeError, UnboundLocalError), e:
            print 'bitmap', e
        finally:
            gc.restore_state()




#============= EOF ====================================
