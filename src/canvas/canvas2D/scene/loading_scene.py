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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.canvas.canvas2D.scene.scene import Scene
import os
from src.paths import paths
from src.lasers.stage_managers.stage_map import StageMap
from src.canvas.canvas2D.scene.primitives.primitives import Circle
from numpy import Inf
#============= standard library imports ========================
#============= local library imports  ==========================

class LoadingScene(Scene):
    def load(self, t):
        self.reset_layers()

        p = os.path.join(paths.map_dir, t)
        sm = StageMap(file_path=p)
        xmi, ymi, xma, yma = Inf, Inf, -Inf, -Inf
        for hi in sm.sample_holes:
            xmi = min(xmi, hi.x)
            ymi = min(ymi, hi.y)
            xma = max(xma, hi.x)
            yma = max(yma, hi.y)

            v = Circle(
                       x=hi.x,
                       y=hi.y,
                       radius=sm.g_dimension / 2.0,
                       identifier=hi.id,
                       name=hi.id,
                       font='modern 10'
                       )
            self.add_item(v)

        w = xma - xmi
        h = yma - ymi
        w *= 1.1 / 2.0
        h *= 1.1 / 2.0
        self._xrange = -w, w
        self._yrange = -h, h

    def get_xrange(self):
        return self._xrange
    def get_yrange(self):
        return self._yrange


#============= EOF =============================================
