#=============enthought library imports=======================
from traits.api import HasTraits, Instance, Float, Button, Any
from traitsui.api import View, Item
from pyface.timer.timer import Timer

#============= standard library imports ========================
import time
#============= local library imports  ==========================
from src.graph.graph import Graph
from src.graph.stream_graph import StreamGraph

SETPOINT = 10
DELAY = 250



class PIDController(HasTraits):
    graph = Instance(Graph)
    setpoint = Float(SETPOINT)
    Kp = Float(0.25)
    Ki = Float(0)
    Kd = Float(0)

    _prev_time = 0
    _integral_err = 0
    _prev_err = Float(0)
    _output = Float(0)
    cnt = 0

    def traits_view(self):
        v = View(Item('graph', show_label=False, style='custom'))
        return v

    def get_output(self, inp):
        v = 0
        dt = time.time() - self._prev_time
        err = self.setpoint - v
        self._input = v
        return self._iteration(err, self.Kp, self.Ki, self.Kd, dt)

    def _iteration(self, error, Kp, Ki, Kd, dt):

        self._integral_err += (error * dt)
        derivative = (error - self._prev_err) / dt
        output = (Kp * error) + (Ki * self._integral_err) + (Kd * derivative)
        self._prev_err = error
        self._output = output

        self.dev.setpoint = output
        return output

    def __prev_err_changed(self):
        self.graph.record_multiple((self._prev_err, self._output, self._input))

    def _graph_default(self):
        g = StreamGraph()
        g.new_plot(padding=20, data_limit=60,
                   scan_delay=DELAY / 1000.0
                   )
        g.new_series()
        g.new_series()
        g.new_series()
        return g


class Demo(HasTraits):
    test = Button
    pidcontroller = Instance(PIDController, ())
    timer = Any

    def traits_view(self):
        v = View(Item('test', show_label=False),
               Item('pidcontroller', show_label=False, style='custom'),
               width=600,
               height=600
               )
        return v

    def _test_fired(self):
        if not self.timer:
            self.timer = Timer(DELAY, self.ontimer)
        else:
            self.timer.Stop()
            self.timer = None

    def ontimer(self):
        self.pidcontroller.get_output(None)

if __name__ == '__main__':
    d = Demo()

    d.configure_traits()
#============= EOF =====================================
