'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================
#=============standard library imports ========================
from pylab import get_cmap, zeros
#=============local library imports  ==========================
from base_canvas import BaseCanvas

class RasterCanvas(BaseCanvas):
    '''
    '''
    ok_to_draw = False
    centerx = 280
    centery = 280
    max_value = 0
    bgcolor = (0.6, 0.6, 0.6)

    def set_parameters(self, x, y):
        '''
        '''
        self.ok_to_draw = True
        self.xstepper = x
        self.ystepper = y

        self.clear_cells()

    def clear_cells(self):
        '''
        '''
        self.max_value = 0
        self.cells = self.cell_factory()
        self.request_redraw()

    def cell_factory(self, x=None, y=None):
        '''
        '''
        if x is None:
            x = len(self.xstepper)
        if y is None:
            y = len(self.ystepper)

        return zeros((x, y))

    def draw(self, gc, *args, **kw):
        '''
        '''
        super(RasterCanvas, self).draw(gc, *args, **kw)
        gc.save_state()
        try:
            if self.ok_to_draw:
                self._draw_grid(gc)

                self._draw_colorbar(gc)
        finally:
            gc.restore_state()

    def set_cell_value(self, x, y, value, refresh=True):
        '''
        '''

        #apply a rotation around diag 
        m = len(self.xstepper) - 1
        n = len(self.ystepper) - 1

        self.cells[m - x][n - y] = value
        if value > self.max_value:
            self.max_value = value

        if refresh:
            self.request_redraw()

    def _colormap(self, mag, cmin=0, cmax=1):
        '''
        '''
        if cmax <= 0:
            cmax = 1
        x = float(mag - cmin) / float(cmax - cmin)

        map = 'hot'
        maf = get_cmap(map)
        return maf(x)


    def _color_cell(self, gc, x, y, color, height=20, width=20, border=False):
        '''
        '''
        gc.save_state()
        if not border:
            gc.set_stroke_color(color)
        gc.set_fill_color(color)
        gc.rect(x, y, width, height)
        gc.draw_path()
        gc.restore_state()

    def _draw_center(self, gc):
        '''
        '''

        gc.save_state()
        gc.set_fill_color((1, 0, 0))
        gc.begin_path()
        gc.arc(self.centerx, self.centery, 10, 0, 360)
        gc.draw_path()
        gc.restore_state()

    def _draw_colorbar(self, gc):
        '''
        '''
        gc.save_state()
        ncolorsteps = 50
        x = 15
        y = 50
        height = 5
        width = 10
        for ci in range(ncolorsteps):
            color = self._colormap(ci, cmax=ncolorsteps - 1)

            self._color_cell(gc, x, y + ci * height, color, width=width, height=height, border=False)

        fmt = '{:0.2f}'
        xx = x + width + 5
        for x, y, t in [(xx, y, fmt.format(0.0)),
                      (xx, y + ncolorsteps * height / 2.0, fmt.format(self.max_value / 2.0)),
                      (xx, y + ncolorsteps * height, fmt.format(self.max_value)),
                      ]:
            gc.set_text_position(x, y)
            gc.show_text(t)

        gc.restore_state()

    def _draw_grid(self, gc):
        '''
        '''
        gc.save_state()

#        xstep = ystep = int((self.width - 100) / len(self.xstepper))
        xstep = ystep = int(450 / len(self.xstepper))

        for i, xi in enumerate(self.xstepper):
            xi = xi * xstep + self.centerx
            for j, yi in enumerate(self.ystepper):
                yi = yi * ystep + self.centery
                if j < len(self.ystepper) and i < len(self.xstepper):
                    #get the cells value and colormap it
                    color = self._colormap(self.cells[i][j], cmax=self.max_value)
                    self._color_cell(gc, xi, yi, color, width=xstep, height=ystep)

        gc.restore_state()
