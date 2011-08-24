#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from laser_tray_canvas import LaserTrayCanvas
def color_generator():
    '''
    '''
    i = 0
    colors = [(1, 0, 0), (0, 1, 0), (1, 0, 1),
            (1, 1, 0), (0, 1, 1), (0, 0, 1)
            ]
    while 1 :
        yield colors[i]
        i += 1
        if i >= len(colors):
            i = 0

color_gen = color_generator()
class SearchLaserCanvas(LaserTrayCanvas):
    '''
        G{classtree}
    '''
    triangles_group = None
    resizable = ''
    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        super(SearchLaserCanvas, self).__init__(*args, **kw)
        self.clear()

    def clear(self):
        '''
        '''
        self.color_gen = color_generator()
        self.triangles_group = []
        self.request_redraw()

    def add_triangles_group(self):
        '''
        '''

        self.triangles_group.append((self.color_gen.next(), []))
        return len(self.triangles_group) - 1

    def _draw(self, gc, *args, **kw):
        '''
            @type gc: C{str}
            @param gc:

            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        #super(LaserTrayCanvas, self)._draw(gc, *args, **kw)
        LaserTrayCanvas._draw(self, gc, *args, **kw)
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        self._draw_map(gc)
        self._draw_triangles(gc)
        self._draw_inspectors(gc)


        #self._draw_scale(gc)

    def _draw_triangles(self, gc):
        '''
            @type gc: C{str}
            @param gc:
        '''
        if self.triangles_group:

            for color, g in self.triangles_group:
                for t in g:
                    t.render(gc, color = color)