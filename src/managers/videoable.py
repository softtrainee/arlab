#============= enthought library imports =======================
from traits.api import HasTraits, Instance, Property
#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.manager import Manager
try:
    from src.managers.video_manager import VideoManager
except ImportError, e:
    print e
    VideoManager = Manager

class Videoable(HasTraits):

    video_manager = Instance(VideoManager)
    video = Property
    def _get_video(self):
        return self.video_manager.video

    def _video_manager_default(self):
        '''
        '''

        if VideoManager is not None:
            return VideoManager()


#============= EOF =============================================
