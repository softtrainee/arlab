d = os.path.dirname(os.getcwd())
sys.path.append(d)

from src.ui import set_toolkit

set_toolkit('qt4')

from numpy import *

from src.graph.graph import Graph
from src.graph.tools.limits_tool import LimitsTool, LimitOverlay


xs = linspace(0, pi * 2)
ys = cos(xs)

g = Graph()
p = g.new_plot()
g.new_series(xs, ys)

t = LimitsTool(component=p)
o = LimitOverlay(component=p, tool=t)
p.tools.append(t)
p.overlays.append(o)

t = LimitsTool(component=p, orientation='y')
o = LimitOverlay(component=p, tool=t)
p.tools.append(t)
p.overlays.append(o)

g.configure_traits()