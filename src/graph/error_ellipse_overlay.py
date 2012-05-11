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
from chaco.api import AbstractOverlay

#============= standard library imports ========================
from numpy import linspace, hstack, sqrt, power, corrcoef
from numpy.linalg import eig
import math

#============= local library imports  ==========================


class ErrorEllipseOverlay(AbstractOverlay):
    def overlay(self, component, gc, view_bounds=None, mode='normal'):
        '''
            
        '''
#        gc.save_state()     
        gc.clip_to_rect(component.x, component.y, component.width, component.height)

        x = component.index.get_data()
        y = component.value.get_data()
        xer = component.xerror.get_data()
        yer = component.yerror.get_data()

#        er39 = 0.00001
#        er40 = 0.0001
#        er36 = 0.001
#        a = (er39 ** 2 + er40 ** 2) ** 0.5
#        b = (er36 ** 2 + er40 ** 2) ** 0.5
#        a = 0.001
#        b = 0.00002

        pxy = corrcoef(x, y)[0][1]

        for cx, cy, ox, oy in zip(x, y, xer, yer):
            a, b, rot = self.calculate_ellipse(component, cx, cy, ox, oy, pxy)
            gc.save_state()
            self._draw_ellipse(gc, component, cx, cy, a, b, rot)
            gc.restore_state()

    def calculate_ellipse(self, component, x, y, ox, oy, pxy,):

        covar = ox * oy * pxy
        covmat = [[ox * ox, covar],
                       [covar, oy * oy]
                       ]
        w, _v = eig(covmat)

        if ox > oy:
            a = (max(w)) ** 0.5
            b = (min(w)) ** 0.5
        else:
            a = (min(w)) ** 0.5
            b = (max(w)) ** 0.5
        dx = abs(component.index_mapper.range.low -
                 component.index_mapper.range.high)
        dy = abs(component.value_mapper.range.low -
                 component.value_mapper.range.high)

        height = component.height
        width = component.width

        aspectratio = (dy / height) / (dx / width)
#        print aspectratio, dx, dy, width, height
        rotation = 0.5 * math.atan(1 / aspectratio * (2 * covar) / (ox ** 2 - oy ** 2))
        return a, b, rotation

    def _draw_ellipse(self, gc, component, cx, cy, a, b, rot):

        scx, scy = component.map_screen([(cx, cy)])[0]
        ox, oy = component.map_screen([(0, 0)])[0]
#        gc.translate_ctm(-scx, -scy)
        #gc.rotate_ctm(45)
        x1 = linspace(-a, a)
        y1 = sqrt(power(b, 2) * (1 - power(x1, 2) / power(a, 2)))

        x2 = x1[::-1]

        y2 = -sqrt(power(b, 2) * (1 - power(x2, 2) / power(a, 2)))

        x = hstack((x1, x2))
        y = hstack((y1, y2))
        pts = component.map_screen(zip(x, y))

        gc.translate_ctm(scx, scy)
        gc.rotate_ctm(rot)
        gc.translate_ctm(-scx, -scy)

        gc.translate_ctm(scx - ox, scy - oy)

        gc.begin_path()

        gc.lines(pts)

        gc.stroke_path()

if __name__ == '__main__':
    x = [1, 2, 3, 4, 4.1]
    y = [1, 2, 3, 4, 5.5]
    xer = [0.1, 0.1, 0.1, 0.1, 0.1]
    yer = [0.1, 0.1, 0.1, 0.1, 0.1]

    ox = 0.1
    oy = 0.1

    pxy = corrcoef(x, y)[0][1]

    covar = ox * oy * pxy
    covmat = [[ox * ox, covar],
                   [covar, oy * oy]
                   ]
    w, _v = eig(covmat)

    if ox > oy:
        a = (max(w)) ** 0.5
        b = (min(w)) ** 0.5
    else:
        a = (min(w)) ** 0.5
        b = (max(w)) ** 0.5

    dx = 1
    dy = 1
    height = 1
    width = 1
    aspectratio = (dy / height) / (dx / width)
    rotation = math.degrees(0.5 * math.atan(1 / aspectratio * (2 * covar) / (ox ** 2 - oy ** 2)))


#        
##        gc.begin_path()
##        pts = component.map_screen(zip(x, ny))
#        gc.lines(pts)
#        gc.stroke_path()    

#        gc.restore_state()
