#===============================================================================
# Copyright 2012 Jake Ross
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
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import numpy as np
#============= local library imports  ==========================
from src.loggable import Loggable

class StageLearner(Loggable):
    laser_manager = None
    machine_vision = None
    def teach_learner(self):
        '''
            traverse a set of learning holes
            for a set of light values
        '''
        lm = self.laser_manager
#        sm = lm.stage_manager
#        st = sm.stage_controller
        mv = self.machine_vision
        lvalues = [50, 75, 80, 100]
        holeset = [1, 2, 3]
        results = []
        targets = []
        for lv in lvalues[:1]:
#            lm.fiber_light.intensity = lv
            for h in map(str, holeset[:1]):
                #move to the hole
                #do and autocenter
#                sm.linear_move(h.x, h.y, block=True)

#                x = st.x
#                y = st.y
                x = 0
                y = 0

                r = mv.locate_target(x, y, h, do_all=True)
                #record autocenter results
                klass, result = self._record_result(lv, r, x, y, h)
                targets += klass
                results += result
#                print result
#                results.append(result)

        results = np.array(results)
        targets = np.array(targets)

        from sklearn import svm
        clf = svm.SVC()
#        print targets[:-1]
#        print results[:-1]
        clf.fit(results[:-1], targets[:-1])

        print clf.predict(results[-1])
        print targets[-1]


    def _record_result(self, lv, rlist, kx, ky, holenum):

        keys = ['region', 'edge', 'threshold']
        KINDDICT = dict(zip(keys, range(len(keys))))

        fmt = '{:<14s}'
        ffmt = fmt.format
        join = ' | '.join

        pprint = lambda x: join(map(ffmt, map(str, x)))

#        print join(map(ffmt, ['seg', 'smooth', 'contrast', 'sharpen']))
        print pprint(['klass', 'light', 'hole', 'seg', 'tlow', 'thigh', 'time',
                       'npos', 'dev', 'sdev', 'smooth', 'contrast', 'sharpen'])

        training_data = []
        klasses = []
        tappend = training_data.append


        xs = []
        ys = []
        xsappend = xs.append
        ysappend = ys.append
        for r in rlist:
            for seg in r[1]:
                ss = seg[0]
                if ss:
                    xsappend(ss[0])
                    ysappend(ss[1])

        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)

        ptformat = lambda x:','.join(map('{:0.3f}'.format, x)) if x else ''
#        pteformat = lambda x:','.join(map('{:0.1e}'.format, x)) if x else ''
        rows = []
        pprintrows = rows.append
        for r in rlist:
#            print r[1]
            for seg in r[1]:
                x = seg[0][0] if seg[0] else None
                y = seg[0][1] if seg[0] else None
                dx = x - kx if x else None
                dy = y - ky if y else None
                sdx = (mx - dx) ** 2 if x else None
                sdy = (my - dy) ** 2 if y else None

                klass = 1 if x and y else 0
                klasses.append(klass)


                kind = KINDDICT[seg[1]]
                tl = seg[2]
                th = seg[3]
                smooth = int(r[0][0])
                contrast = int(r[0][1])
                sharpen = int(r[0][2])
                rdata = [lv, holenum, kind, tl, th, x, y, dx, dy, sdx, sdy,
                       smooth, contrast, sharpen
                       ]

#                rdata = list((lv, holenum) + tuple(seg[1:]) +
#                             (x, y, dx, dy, sdx, sdy) + r[0])
                tappend(rdata)

                pprintrows([klass, lv,
                              holenum] +
                              list(seg[1:-1]) +
                            [
                            '{:0.3f}'.format(seg[-1]),
                            ptformat(seg[0]),
                            ptformat((dx, dy)) if dx else '',
                            ptformat((sdx, sdy)) if sdx else '',

#                            ','.join(map('{:0.3f}'.format, seg[0])) if seg[0] else '',
#                            ','.join(map('{:0.3f}'.format, (dx, dy))) if seg[0] else '',
#                            ','.join(map('{:0.3f}'.format, (dx, dy))) if seg[0] else '',

                            ] + map(str, r[0])
                             )

        rows = sorted(zip(training_data, rows), key=lambda k: k[0][10])

        for td, ri in rows:
            print pprint(ri)


        return klasses, training_data
#                print rdata











#============= EOF =============================================
