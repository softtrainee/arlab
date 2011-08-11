#============= enthought library imports =======================
from traits.api import on_trait_change
#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.video_canvas import VideoCanvas
from laser_tray_canvas import LaserTrayCanvas


class VideoLaserTrayCanvas(LaserTrayCanvas, VideoCanvas):
    '''
    '''

    @on_trait_change('parent:parent:zoom')
    def zoom_update(self, obj, name, old, new):
        if new is not None:
            self.camera.set_limits_by_zoom(new)

    @on_trait_change('calibrate')
    def _update_(self, new):
        self.pause = new

    def set_stage_position(self, x, y):
        '''
   
        '''
        super(VideoLaserTrayCanvas, self).set_stage_position(x, y)
        self.adjust_limits('x', x)
        self.adjust_limits('y', y)
        if self.use_camera:
            self.camera.current_position = (x, y)

#============= EOF ====================================
