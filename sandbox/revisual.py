from pylab import *

import hglib

p = '/Users/ross/Programming/mercurial/pychron_dev/'
repo = hglib.open(p)
x, y = [], []
for l in repo.log():
    i, rev, _, br, name, note, t = l
    x.append(t)
    y.append(i)

plot(x, y)
show()





