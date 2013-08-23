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
from traits.api import Any
#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.scene.scene_canvas import SceneCanvas
from src.canvas.canvas2D.scene.loading_scene import LoadingScene


class LoadingCanvas(SceneCanvas):
    use_pan = False
    use_zoom = False
    selected = Any
#     fill_padding = True
#     bgcolor = 'red'
    show_axes = False
    show_grids = False

    padding_top = 0
    padding_bottom = 0
    padding_left = 0
    padding_right = 0

    aspect_ratio = 1
    editable = True

    def load_tray_map(self, t, show_hole_numbers):
        scene = LoadingScene()
        scene.load(t, show_hole_numbers=show_hole_numbers)

        self.view_x_range = scene.get_xrange()
        self.view_y_range = scene.get_yrange()

        self.scene = scene

    def normal_left_down(self, event):
        if self.editable:
            self.hittest(event)
            self.request_redraw()
            self.selected = None

    def hittest(self, event):
        for li in self.scene.layers:
            for it in li.components:
                if it.is_in(event):
#                     it.fill = not it.fill
                    self.selected = it

                    return True


#============= EOF =============================================
