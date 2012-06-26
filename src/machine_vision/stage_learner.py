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
from traits.api import Event, Property, Bool, Str, Float
from traitsui.api import View, Item, ButtonEditor
#============= standard library imports ========================
import numpy as np
import csv
import math
from threading import Thread
from threading import Event as TEvent
#from os import path
#============= local library imports  ==========================
from src.loggable import Loggable

def pprint(l):
    fmt = '{:<14s}'
    ffmt = fmt.format
    join = ' | '.join
    print join(map(ffmt, map(str, l)))

RDATA_NAMES = ['light', 'hole', 'segkind', 'tl', 'th', 'ex. time',
                            'x', 'y', 'dx', 'dy', 'sdx', 'sdy',
                            'smooth', 'contrast', 'sharpen', 'convextest'
                            ]
class StageLearner(Loggable):
    laser_manager = None
    machine_vision = None

    execute = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool

    current_hole = Str
    light_value = Float
    def _get_execute_label(self):
        return 'Stop' if self._alive else 'Execute'
    def _execute_fired(self):
        if self._alive:
            self._stop_signal.set()
            self._alive = False
        else:
            self._alive = True
            self._stop_signal = sig = TEvent()
            t = Thread(target=self.collect_data, args=(sig,))
            t.start()

    def teach_learner(self):
#        targets, results = self.collect_data()
        results, targets = self.get_data()
        self._learn(results, targets)

    def collect_data(self, signal):
        '''
            traverse a set of learning holes
            for a set of light values
        '''
#        lm = self.laser_manager
#        sm = lm.stage_manager
#        st = sm.stage_controller
        mv = self.machine_vision
        mv.hole_detector.use_all_permutations = True
        lvalues = [50, 75, 80, 100]
        holeset = range(1, 5, 1)[:1]
#        pids = ['pos_err_53001', 'pos_err_54001']
#        pids = ['pos_err_54001'] * len(holeset)
#        results = []
#        targets = []
#        rows = []

        from src.paths import paths
        from os import path
        p = path.join(paths.data_dir, 'stage.csv')

        with open(p, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(RDATA_NAMES)
            for lv in lvalues[:1]:
                if signal.isSet():
                    break
                self.light_value = lv
    #            lm.fiber_light.intensity = lv
#                time.sleep(5)

#                for pid, h in zip(pids, map(str, holeset)):
                for h in holeset:
                    if signal.isSet():
                        break
                    self.current_hole = str(h)
                    #move to the hole
                    #do and autocenter
    #                sm.linear_move(h.x, h.y, block=True)

    #                x = st.x
    #                y = st.y
                    x = 0
                    y = 0

                    r = mv.locate_target(x, y, h)
                    #record autocenter results
                    self._record_result(writer, lv, r, x, y, h)

        if not signal.isSet():
            self.info('{}Data Collection Complete{}'.format('=' * 10, '=' * 10))
        else:
            self.info('{}Data Collection Stopped{}'.format('=' * 10, '=' * 10))
#                    klass, result, row = self._record_result(writer, lv, r, x, y, h)
#                    targets += klass
#                    results += result
#                    rows += row
#
#                    #time.sleep(0.1)
#
#            results = np.array(results, dtype=float)
#            targets = np.array(targets)
#
##            self.print_results(rows, results)
#
#            return results, targets, rows

    def print_results(self, rows, results):
        print len(rows)
        pprint(['klass', 'light', 'hole', 'rank', 'rank val.',
                       'seg', 'tlow', 'thigh', 'time',
                       'npos', 'dev', 'sdev', 'smooth', 'contrast', 'sharpen', 'convextest'])

        rows = sorted(zip(results, rows), key=lambda k: k[1][0])
        for _, ri in rows:
            pprint(ri)


    def _learn(self, results, targets):
        self.svc(results, targets)
        self._pca(results)

    def svc(self, results, targets):
        from sklearn import svm
        clf = svm.SVC()
#        print targets[:-1]
#        print results[:-1]
        clf.fit(results[:-1], targets[:-1])

        print clf.predict(results[-1])
        print targets[-1]

    def _pca(self, results):
#        from sklearn.cluster import KMeans
#        kmeans = KMeans(k=4, n_init=10)
        from sklearn.decomposition.pca import PCA

#        pca = PCA()
#        pca.fit(results)
        pca = PCA(n_components=2)

        reduced_data = pca.fit_transform(results)
        print pca.explained_variance_ratio_
        comps = pca.components_
        print comps

        i0 = np.argmax(comps[0])
        i1 = np.argmax(comps[1])
        print RDATA_NAMES[i0]
        print RDATA_NAMES[i1]
#        kmeans.fit(reduced_data)

                # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = .02     # point in the mesh [x_min, m_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will asign a color to each
        x_min, x_max = reduced_data[:, 0].min() + 1, reduced_data[:, 0].max() - 1
        y_min, y_max = reduced_data[:, 1].min() + 1, reduced_data[:, 1].max() - 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        # Obtain labels for each point in mesh. Use last trained model.
#        Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

        import pylab as pl
        # Put the result into a color plot
#        Z = Z.reshape(xx.shape)
#        pl.figure(1)
#        pl.clf()
#        pl.imshow(Z, interpolation='nearest',
#                  extent=(xx.min(), xx.max(), yy.min(), yy.max()),
#                  cmap=pl.cm.Paired,
#                  aspect='auto', origin='lower')

        pl.plot(reduced_data[:, 0], reduced_data[:, 1], 'ro', markersize=8)
        # Plot the centroids as a white X
#        centroids = kmeans.cluster_centers_
#        pl.scatter(centroids[:, 0], centroids[:, 1],
#                   marker='x', s=169, linewidths=3,
#                   color='w', zorder=10)
        pl.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
                 'Centroids are marked with white cross')
        pl.xlim(x_min, x_max)
        pl.ylim(y_min, y_max)
#        pl.xticks(())
#        pl.yticks(())

        from pyface.timer.do_later import do_later
        do_later(pl.show)


    def _record_result(self, writer, lv, rlist, kx, ky, holenum):


        def calc_devs(seg):
            x = seg[0][0] if seg[0] else None
            y = seg[0][1] if seg[0] else None
            dx = x - kx if x else None
            dy = y - ky if y else None
            sdx = (mx - dx) ** 2 if x else None
            sdy = (my - dy) ** 2 if y else None
            return x, y, dx, dy, sdx, sdy

        keys = ['region', 'edge', 'threshold']
        KINDDICT = dict(zip(keys, range(len(keys))))



#        pprint = lambda x: join(map(ffmt, map(str, x)))

#        print join(map(ffmt, ['seg', 'smooth', 'contrast', 'sharpen']))
#        pprint(['klass', 'light', 'hole', 'rank', 'rank val.',
#                       'seg', 'tlow', 'thigh', 'time',
#                       'npos', 'dev', 'sdev', 'smooth', 'contrast', 'sharpen'])

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

        bins, values = np.histogram(xs, 3)
        mx = values[np.argmax(bins)]

        bins, values = np.histogram(xs, 3)
        my = values[np.argmax(bins)]

        #calculate the rank
        ms = []
        ids = []
        cnt = 0
        for i, r in enumerate(rlist):
            for j, seg in enumerate(r[1]):

                ids.append(cnt)
                cnt += 1
                _, _, _, _, sdx, sdy = calc_devs(seg)

                ti = seg[-1]
                if sdx is None:
                    sdx = sdy = 1

                rv = math.log(1 / (ti * sdx * sdy))
                ms.append(rv)

        ranks, rank_ids = zip(*sorted(zip(ms, ids), key=lambda x: x[0]))

        ptformat = lambda x:','.join(map('{:0.3f}'.format, x)) if x else ''
#        pteformat = lambda x:','.join(map('{:0.1e}'.format, x)) if x else ''


        rows = []
        training_data = []
        klasses = []

        t_append = training_data.append
        rows_append = rows.append
        k_append = klasses.append
        write_row = writer.writerow
        rindex = rank_ids.index
        cnt = 0
        for r in rlist:
            for seg in r[1]:
                x, y, dx, dy, sdx, sdy = calc_devs(seg)

                klass = 1 if x and y else 0
                k_append(klass)

                kind = KINDDICT[seg[1]]
                tl = seg[2] if seg[2] else None
                th = seg[3] if seg[3] else None
                ti = seg[-1]

                rank = rindex(cnt)
                rankv = ranks[rank]
                cnt += 1

                prepro_ops = r[0]
                smooth = int(prepro_ops[0])
                contrast = int(prepro_ops[1])
                sharpen = int(prepro_ops[2])
                convextest = int(prepro_ops[3])

                rdata = [lv, holenum, kind,
                         #rank, # use rank or rankv having both adds unnecessary dimensionality 
                         #rankv,
                         tl, th,
                         ti, x, y, dx, dy, sdx, sdy,
                         smooth, contrast, sharpen, convextest
                         ]

                prepros = lambda x: x if x is not None else -1
                t_append(map(prepros, rdata))

                rdata[2] = seg[1]
                write_row(rdata)

                rows_append([klass, lv,
                              holenum, rank, rankv] +
                              list(seg[1:-1]) +
                            [
                            '{:0.3f}'.format(seg[-1]),
                            ptformat(seg[0]),
                            ptformat((dx, dy)) if dx else None,
                            ptformat((sdx, sdy)) if sdx else None,

                            ] + map(str, r[0])
                            )

        return klasses, training_data, rows

    def traits_view(self):
        v = View(
                 Item('execute', editor=ButtonEditor(label_value='execute_label')),
                 Item('light_value', style='readonly'),
                 Item('current_hole', style='readonly'),
                 resizable=True,
                 title='Stage Learner'
                 )
        return v



#============= EOF =============================================
