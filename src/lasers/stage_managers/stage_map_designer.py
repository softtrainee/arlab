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
from traits.api import  Instance, File, Float, Button
from traitsui.api import View, Item, HGroup, VGroup
from enable.component_editor import ComponentEditor
#============= standard library imports ========================
import wx
#============= local library imports  ==========================
from src.canvas.canvas2D.map_canvas import MapCanvas
from src.lasers.stage_managers.stage_map import StageMap
from src.managers.manager import Manager
WIDTH = 1050
PX_PER_CM = 23.2
PADDING = 0


class StageMapDesigner(Manager):
    canvas = Instance(MapCanvas)
    export = Button
    px_per_mm = Float(232)
    path = File('/Users/Ross/Pychrondata_beta/setupfiles/tray_maps/221-hole.txt')
    def _px_per_mm_changed(self):
        w, h = self._get_wh()
        self.canvas.set_mapper_limits('x', (-w, w))
        self.canvas.set_mapper_limits('y', (-h, h))

    def _get_wh(self):
        pxp = self.px_per_mm / 10.0
        w = WIDTH / pxp / 2.0
        h = 0.75 * w
        return w, h

    def _path_changed(self):
        if self.path is not None:
            self.canvas.set_map(StageMap(file_path=self.path))
#            self.canvas.invalidate_and_redraw()
            self.canvas.smart_move()

    def _canvas_default(self):
        #path = '/Users/Ross/Pychrondata_beta/setupfiles/tray_maps/221-hole.txt'
        sm = StageMap(file_path=self.path)

        w, h = self._get_wh()

        c = MapCanvas(map=sm,
                      padding=PADDING,
                      view_x_range=[-w, w],
                      view_y_range=[-h, h],
                      use_valid_holes=False,
                      show_indicators=False
                      )

        c.new_calibration_item(0, 0)
        return c
#============= views ===================================

    def _export_fired(self):
        self.save_bitmap(self.canvas)

    def save_bitmap(self, canvas):
        p = '/Users/Ross/Pychrondata_beta/setupfiles/tray_maps/map2.png'
        dc = wx.ClientDC(canvas._window.control)
        rect = wx.Rect(canvas.x , canvas.y,

                       canvas.width, canvas.height)
        bitmap = dc.GetAsBitmap(rect)
        bitmap.SaveFile(p, wx.BITMAP_TYPE_PNG)

    def traits_view(self):
        w = WIDTH
        h = w * 0.75
        v = View(
                 HGroup(
                        VGroup(

                               Item('path', show_label=False),
                               Item('export', show_label=False),
                               Item('px_per_mm')
                               ),
                        Item('canvas', show_label=False,
                             editor=ComponentEditor(width=w + 2 * PADDING, height=h + 2 * PADDING)
                             )
                        ),
#                 resizable = True
                 )
        return v


if __name__ == '__main__':
    s = StageMapDesigner()
    s.configure_traits()
#============= EOF ====================================
