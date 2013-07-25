#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Any, Array, Str, Event
from traitsui.api import View, Item, UItem
from src.ui.image_editor import ImageEditor
from numpy import asarray, array
from src.viewable import Viewable
from scipy.ndimage.interpolation import zoom
# from traitsui.editors.image_editor import ImageEditor
# from pyface.ui.qt4.image_resource import ImageResource
# from pyface.image_resource import ImageResource
#============= standard library imports ========================
#============= local library imports  ==========================
class StandAloneImage(Viewable):
# class StandAloneImage(HasTraits):
    image = Any
    source_frame = Array
    refresh = Event
    def traits_view(self):
        v = View(
                 UItem('source_frame',
                       editor=ImageEditor(refresh='refresh')),
                width=300,
                height=300,
#                  handler=self.handler_klass,
#                 resizable=True
                 )
        return v

    def load(self, frame, swap_rb=False):
        self.source_frame = array(frame)

    def set_frame(self, frame):
        self.source_frame = asarray(frame)
#============= EOF =============================================
