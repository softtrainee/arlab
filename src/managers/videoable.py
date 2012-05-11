#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



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
