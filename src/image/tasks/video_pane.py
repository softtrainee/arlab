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
from traits.api import HasTraits, Any, File, String, Int, Enum, Instance, Dict
from traitsui.api import View, Item, UItem, InstanceEditor, EnumEditor
from pyface.tasks.traits_task_pane import TraitsTaskPane
from enable.component_editor import ComponentEditor
from src.canvas.canvas2D.video_canvas import VideoCanvas
from src.ui.stage_component_editor import VideoComponentEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
#============= standard library imports ========================
#============= local library imports  ==========================
class Source(HasTraits):
    def url(self):
        return

class LocalSource(Source):
    path = File
    def traits_view(self):
        return View(UItem('path'))

    def url(self):
        return 'file://{}'.format(self.path)

class RemoteSource(Source):
    host = String('localhost')
    port = Int(1084)
    def traits_view(self):
        return View(
                    Item('host'),
                    Item('port'),

                    )

    def url(self):
        return 'pvs://{}:{}'.format(self.host, self.port)

class SourcePane(TraitsDockPane):
    name = 'source'
    id = 'pychron.video.source'
    kind = Enum('Remote', 'Local')
    source = Instance(Source)
    connections = Dict
    selected_connection = Any


    def traits_view(self):
        v = View(
                 UItem('kind'),
                 UItem('source',
                       style='custom'),
                 UItem('selected_connection',
                       editor=EnumEditor(name='connections'),
                       style='custom'
                       )
                 )
        return v

    def _kind_changed(self):
        if self.kind == 'Local':
            self.source = LocalSource()
        else:
            self.source = RemoteSource()

    def _source_default(self):
        return RemoteSource()

class VideoPane(TraitsTaskPane):
    component = Any
    video = Any

    def _video_changed(self):
        self.component.video = self.video

    def _component_default(self):
        c = VideoCanvas(video=self.video)
        return c

    def traits_view(self):
        v = View(
                 UItem('component',
                       style='custom',
                        editor=VideoComponentEditor()
                       )
                 )
        return v
#============= EOF =============================================
