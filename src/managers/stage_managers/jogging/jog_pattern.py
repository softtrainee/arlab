#============= enthought library imports =======================
from traits.api import HasTraits, on_trait_change, Float, Range, Bool, Enum, Any
from traitsui.api import View, Item, HGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from jogger import line_jogger, square_jogger
from src.hardware.core.motion.motion_profiler import MotionProfiler


class JogPattern(HasTraits):
    ns = Range(1, 10, 2)
    R = Range(0.01, 0.5, 0.1)
    p = Range(0.01, 5.0, 0.8)
    step_scalar = Range(0, 20, 5)

    show_overlap = Bool(False)
    alpha = Range(0, 1.0, 0.6)
    beam_diam = 1
    cx = Float
    cy = Float
    direction = Enum('in', 'out')
    show_path = Bool(True)

    parent = Any(transient = True)
    transit_time = Float
    mp = MotionProfiler()

#    def __init__(self, *args, **kw):
#        super(JogPattern, self).__init__(*args, **kw)
#        #self.mp = MotionProfiler()

#============= views ===================================
    def traits_view(self):
        v = View(
                 Item('ns', label = 'N revolutions'),
                 Item('R', label = 'Radius'),
                 Item('p', label = '% radius increase'),
                 Item('step_scalar'),

                 HGroup(Item('show_path'), Item('show_overlap'),
                        #Item('alpha', visible_when = 'show_overlap')
                        ),
                 #Item('transit_time'),
                 )
        return v

    @on_trait_change('ns,R,p,show_overlap,show_path,alpha,step_scalar')
    def change(self):
        if self.parent is not None:
            self.parent.replot()

    def do_spiral(self, kind, sx = None, sy = None):

        if self.direction == 'in':
            return getattr(self, 'inner_%s' % kind)(sx, sy)

        else:
            return getattr(self, 'outer_%s' % kind)()

    def outer_square_spiral(self, *args):
        jogger = square_jogger(self.cx, self.cy, self.R, self.ns, self.p)
        x, y = self._spiral_(self.cx, self.cy, jogger, 'purple')
        return x, y

    def inner_square_spiral(self, sx, sy, *args):
        jogger = square_jogger(
                               sx, sy,
                               self.R, self.ns, self.p,
                               direction = 'in'
                               )
        self._spiral_(self.cx, self.cy, jogger, 'green', direction = 'in')

    def outer_line_spiral(self, *args):
        cx = self.cx
        cy = self.cy

        line_jog_gen = line_jogger(cx, cy, self.R, self.ns, self.p, self.step_scalar)
        self._spiral_(cx, cy, line_jog_gen, 'red')

        return self.cx, self.cy

    def inner_line_spiral(self, *args):
        cx = self.cx
        cy = self.cy
        line_jog = line_jogger(cx, cy, self.R, self.ns, self.p, self.step_scalar, direction = 'in')
        self._spiral_(cx, cy, line_jog, 'yellow', direction = 'in')

    def _spiral_(self, cx, cy, jogger, color, direction = 'out'):
        xs = []
        ys = []
        if direction == 'out':
            xs.append(cx)
            ys.append(cy)
        px = cx
        py = cy
        tt = 0

        while 1:
            try:
                x, y = jogger.next()
                xs.append(x)
                ys.append(y)
                ac = 7
                v = 3
                tt += self.mp.calculate_transit((ac, v), px, py, x, y)

                px = x
                py = y

                if self.show_overlap:
                    if self.parent is not None:
                        self.parent.circle(x, y, self.beam_diam / 2.0,
                                    face_color = color, #(1, 0, 0, 0),
                                    alpha = self.alpha,
                                    edge_width = 0,
                                    #   edge_color = 'transparent'
                                 )
            except StopIteration:
                break
        self.transit_time = tt
        if direction == 'in':
            xs.append(cx)
            ys.append(cy)

        if self.show_path:
            if self.parent is not None:
                self.parent.canvas.new_series(xs, ys, color = color, render_style = 'connectedpoints')
                self.parent.canvas.set_x_limits(-1.5 + cx, cx + 1.5)
                self.parent.canvas.set_y_limits(-1.5 + cy, cy + 1.5)

        return x, y


#============= EOF ====================================
