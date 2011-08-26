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
#============= enthought library imports =======================
#============= standard library imports ========================

from numpy import linspace
import math
#============= local library imports  ==========================
#============= views ===================================

def line_jogger(cx, cy, R, ns, p, ss, direction = 'out'):

    stepfunc = lambda i: 2 * i + ss
    rfunc = lambda i, j :R * (1 + (i + j / 360.) * p)
    if direction == 'in':
        stepfunc = lambda i: 2 * (ns - i) + ss
        rfunc = lambda i, j :R * (1 + ((ns - i - 1) + (360 - j) / 360.) * p)

    for ni in xrange(ns):
        nstep = stepfunc(ni)
        for t in linspace(0, 360, nstep):
            if t == 360 and ni != ns - 1:
                continue

            r = rfunc(ni, t)
            theta = math.radians(t)
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)

            yield x, y

def square_jogger(cx, cy, R, ns, p, direction = 'out', ox = 0, oy = 0):

    rfunc = lambda i: R * (1 + (i) * p)
    ns = 4 * ns + 1
    steps = xrange(ns)
    funclist = [lambda x, y, r:(x + r, y),
                lambda x, y, r:(x, y + r),
                lambda x, y, r:(x - r, y),
                lambda x, y, r:(x, y - r)]

    if direction == 'in':
        rfunc = lambda i:R * (1 + (ns - i) * p)
        funclist = funclist[1:] + funclist[:1]

    x = cx
    y = cy

    for i in steps:
        r = rfunc(i)
        if direction == 'in' and i == 0:
            yield x, y
        rem = i % 4
        func = funclist[rem]

        x, y = func(x, y, r)

        yield x, y
#============= EOF ====================================
