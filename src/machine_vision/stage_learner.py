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

                results = mv.locate_target(x, y, h, do_all=True)
                #record autocenter results
                self._record_result(lv, results, x, y, h)

    def _record_result(self, lv, rlist, kx, ky, holenum):
        fmt = '{:<12s}'
        ffmt = fmt.format
        join = ' | '.join

        pprint = lambda x: join(map(ffmt, map(str, x)))

#        print join(map(ffmt, ['seg', 'smooth', 'contrast', 'sharpen']))
        print pprint(['light', 'hole', 'seg', 'tlow', 'thigh', 'time',
                       'npos', 'dev', 'smooth', 'contrast', 'sharpen'])

        for r in rlist:
#            print r[1]
            for seg in r[1]:
                x = seg[0][0] if seg[0] else None
                y = seg[0][1] if seg[0] else None
                dx = x - kx if x else None
                dy = y - ky if y else None

                rdata = (lv, holenum) + tuple(seg[1:]) + (x, y, dx, dy) + r[0]

                print pprint([lv,
                              holenum] +
                              list(seg[1:-1]) +
                            [
                            '{:0.3f}'.format(seg[-1]),
                            ','.join(map('{:0.3f}'.format, seg[0])) if seg[0] else '',
                            ','.join(map('{:0.3f}'.format, (dx, dy))) if seg[0] else '',
                            ] + map(str, r[0])
                             )
#                print rdata











#============= EOF =============================================
