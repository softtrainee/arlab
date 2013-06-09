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
from traits.api import HasTraits, Instance, on_trait_change, File, Str, Int, \
    List, Any
from traitsui.api import View, Item
from pyface.tasks.task_layout import PaneItem, TaskLayout
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_task import BaseTask, BaseManagerTask
from src.image.tasks.video_pane import VideoPane, SourcePane
from src.image.video_source import VideoSource, parse_url


class VideoTask(BaseManagerTask):
    id = 'pychron.extraction_line'
    name = 'Video Display'
    video_source = Instance(VideoSource, ())
    source_pane = Instance(SourcePane)
    available_connections = List

    def _default_layout_default(self):
        return TaskLayout(
#                           top=PaneItem('pychron.extraction_line.gauges'),
                        left=PaneItem('pychron.video.source')
#                          width=500,
#                          height=500
                          )

    def prepare_destroy(self):
        pass

    def create_central_pane(self):
        self.video_pane = VideoPane(
                                    video=self.video_source,

                                    )

        self.video_pane.component.fps = 1
        return self.video_pane

    def create_dock_panes(self):
        self.source_pane = SourcePane(
                                      connections=dict(self.available_connections)
                                      )
        self.video_source.set_url(self.source_pane.source.url())
        panes = [
                 self.source_pane
#                  GaugePane(model=self.manager),
#                  ExplanationPane(model=self.manager)
                 ]
        return panes

    @on_trait_change('source_pane:[selected_connection, source:+]')
    def _update_source(self, name, new):
        if name == 'selected_connection':
            islocal, r = parse_url(new)
            if islocal:
                pass
            else:
                self.source_pane.source.host = r[0]
                self.source_pane.source.port = r[1]
        else:
            url = self.source_pane.source.url()

            self.video_source.set_url(url)
#         if name == 'source':
#             self.video_source.image_path = new

#     @on_trait_change('video_source:fps')
#     def _update_fps(self):
#         self.video_pane.set_fps(self.video_source.fps)
#============= EOF =============================================
