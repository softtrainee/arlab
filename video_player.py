#============= enthought library imports =======================
from traits.api import DelegatesTo, Instance
from traitsui.api import View, Item, HGroup, spring

#============= standard library imports ========================
import sys
import os
#============= local library imports  ==========================
#add src to the path
root = os.path.basename(os.path.dirname(__file__))
if 'pychron_beta' not in root:
    root = 'pychron_beta'
src = os.path.join(os.path.expanduser('~'),
                   'Programming',
                   root
                   )
sys.path.append(src)


from src.managers.stage_managers.video_component_editor import VideoComponentEditor
from src.managers.videoable import Videoable
from src.canvas.canvas2D.video_laser_tray_canvas import VideoLaserTrayCanvas

class VideoDisplayCanvas(VideoLaserTrayCanvas):

    show_grids = False
    show_axes = False
    use_camera = False

class VideoPlayer(Videoable):

    canvas = Instance(VideoDisplayCanvas)
    crosshairs_kind = DelegatesTo('canvas')
    crosshairs_color = DelegatesTo('canvas')

    def _canvas_default(self):
        self.video.open(user = 'underlay')
        return VideoDisplayCanvas(padding = 30,
                                  video = self.video_manager.video)

    def traits_view(self):
        vc = Item('canvas',
                  style = 'custom',
                  editor = VideoComponentEditor(width = 640, height = 480),
                  show_label = False,
                  resizable = False,

                  )
        v = View(

                 HGroup(spring, Item('crosshairs_kind'), Item('crosshairs_color')),
                 vc,
#                 width = 800,
                 height = 530,
                 title = 'Video Display'
                 )
        return v
if __name__ == '__main__':
    v = VideoPlayer()
    v.configure_traits()
#============= EOF ====================================
