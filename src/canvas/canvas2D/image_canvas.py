#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.base_data_canvas import BaseDataCanvas

from src.canvas.canvas2D.image_underlay import ImageUnderlay
class ImageCanvas(BaseDataCanvas):
    image = None
    def __init__(self, *args, **kw):
        '''

        '''
        self.padding_top = 0
        super(ImageCanvas, self).__init__(*args, **kw)


        image_underlay = ImageUnderlay(component = self, image = self.image)

        self.underlays.insert(0, image_underlay)

        #self.overlays.pop()

        for key, d in [('x_grid', dict(line_color = (1, 1, 0),
                                     line_width = 1,
                                     line_style = 'dash',
                                     visible = self.show_grids)
                                     ),
                       ('y_grid', dict(line_color = (1, 1, 0),
                                      line_width = 1,
                                      line_style = 'dash',
                                      visible = self.show_grids))]:
            o = getattr(self, key)
            o.trait_set(**d)

#        if self.use_camera:
#            self.camera = Camera(parent = self)
#            p = os.path.join(canvas2D_dir, 'camera.txt')
#            self.camera.load(p)
#            self.camera.current_position = (0, 0)
#
#            self.camera = Camera(parent = self)
#            p = os.path.join(canvas2D_dir, 'camera.txt')
#            self.camera.load(p)
#            self.camera.current_position = (0, 0)
#            self.camera.set_limits_by_zoom(0)
#
#            #swap red blue channels True or False
#            video_underlay.swap_rb = self.camera.swap_rb
#
        if self.image:
            self.on_trait_change(self.image.update_bounds, 'bounds')
#            self.video.open(user = 'underlay')
#============= EOF ====================================
