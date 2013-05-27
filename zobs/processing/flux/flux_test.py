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
import struct
from src.processing.argon_calculations import calculate_flux
from src.database.records.isotope_record import IsotopeRecord
from uncertainties import ufloat
from src.regression.ols_regressor import MultipleLinearRegressor
# from src.graph.graph3D import Graph3D
# from mayavi import mlab
import numpy as np
#============= standard library imports ========================
#============= local library imports  ==========================

class FluxView(HasTraits):
    def model_flux(self, analyses, monitor_age):
        '''
            analysis: dict of key=holenum, value=(xy, [analyses list])
        '''
        def calc_j(ai):
            ai._calculate_age()
            ar40 = ai.arar_result['rad40']
            ar39 = ai.arar_result['k39']
            return calculate_flux(ar40, ar39, monitor_age)

        def mean_j(ans):
            js, wts = zip(*[calc_j(ai) for ai in ans])
            return np.average(js, weights=wts), np.std(js)
#        positions = []
#        ys = []
#        for k, (position, ans) in analyses.iteritems():
#            print k, position, len(analyses)
#            Z = sum([calc_j(ai) for ai in ans]) / len(ans)

#            X, Y = position
#            print X, Y, Z
#            positions.append(position)
#            ys.append(Z.nominal_value)
        positions, ys = zip(*[(pos, mean_j(ans)) for (pos, ans) in analyses.itervalues()])

        ys, ye = zip(*ys)
# #        print positions
        reg = MultipleLinearRegressor(xs=positions, ys=ys)
# #        p = reg.predict([(0.0, 0.85)]) #0.00484421950062+/-8.3063828332e-06
# #        print p, p - 0.00484421950062
#        g = Graph3D()
#        import numpy as np
        x, y = zip(*positions)
        x = np.array(x)
        y = np.array(y)
        ys = np.array(ys)

        w = max(x) - min(x)
        c = len(x)
        r = len(y)
        n = r * 2 - 1
        xx, yy = np.mgrid[0:n + 1, 0:n + 1]
        xx = xx / float(n) * w - w / 2.
        yy = yy / float(n) * w - w / 2.

#        xx = xx * r / 2. - w
#        yy = yy * r / 2. - w
        z = np.zeros((r * 2, c * 2))

        for i in range(r * 2):
            for j in range(c * 2):
                pt = (xx[i, j],
                      yy[i, j])
                z[i, j] = reg.predict([pt])[0]

        normalize = False
        if normalize:
            z *= 1 / z.max()  # * w - w / 2.
            z *= 100
            z -= z.min() + (z.max() - z.min()) / 2.

    #        w = ys.max() - ys.min()
            ys *= 1 / ys.max() - ys.min()  # * w - w / 2.
            ys *= 100
            ys -= ys.min() + (ys.max() - ys.min()) / 2.

#        z = z / abs(z).max() * 100
#        ys *= 1 / ys.max() * 100
#                print pt, z[j, i]
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_surface(xx, yy, z, alpha=0.3,
                        rstride=1, cstride=1,
                        cmap=cm.coolwarm,
                        linewidths=0

                        )
#        ax.scatter(x, y, zs)
        ax.scatter(x, y, ys)
        for xi, yi, zi, ei in zip(x, y, ys, ye):
#        for i in np.arange(0, len(x)):
            ax.plot([xi, xi], [yi, yi], [zi - ei, zi + ei],
                    color='black',
                    marker='_'
                    )
        plt.show()
#        mlab.surf(z, warp_scale=10000)
#        mlab.axes()
#        mlab.outline()
#        mlab.points3d(x, y, zs * 10000)
#        mlab.show()
#        z = reg.predict([(0, 0)])
#        print z
#
#        z = z.reshape((r, c))
#        print z


#        print xx
#        print z
#        g.plot_surf(z, warp_scale='auto')
#        g.plot_surf(np.zeros((r, c)))
#        print ys

#        g.plot_lines(x, y, ys)
#        print len(x), len(y), len(zs)
#        g.plot_points(x, y, np.array(zs) * 10000)
#        g.plot_points(x, y, np.array(ys) * 10000)
#        g.configure_traits()

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('ia')
    from src.database.adapters.isotope_adapter import IsotopeAdapter
    db = IsotopeAdapter(name='isotopedb_dev',
                        username='root',
                        password='Argon',
                        host='localhost',
                        kind='mysql')
    db.connect()

    fv = FluxView()

    irrad = db.get_irradiation('NM-251')
    level = db.get_irradiation_level('NM-251', 'H')
    geom = level.holder.geometry
    irrads = db.get_irradiation_position('NM-251', 'H', [7, 8, 9, 10, 11, 12])

    geometry = [struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)]

#    positions = dict()
    analyses = dict()
    for ir in irrads:
        xy = geometry[ir.position - 1]

        ans = []
#        print ir.labnumber.labnumber
#        for an in ir.labnumber.analyses:
#            if an.status
#            print an.status
#            a = IsotopeRecord(_dbrecord=an)
#            ans.append(a)
        ans = [IsotopeRecord(_dbrecord=an) for an in ir.labnumber.analyses if an.status == 0]
        analyses[ir.position] = (xy, ans)


#    ans = dict([(ir.position, ir.labnumber.analyses) for ir in irrads])
#    print irrad
#    ans =

    fv.model_flux(analyses, ufloat(28.02e6, 0))
#    xs = [[ 0.          , 0.85000002  ],
#           [ 0.80000001  , 0.40000001  ],
#           [ 0.80000001 , -0.40000001  ],
#           [ 0.         , -0.85000002  ],
#           [-0.80000001 , -0.40000001  ],
#           [-0.80000001  , 0.40000001  ]]
#    ys = [1, 1, 1, 1, 1, 1]
#    xs = [(0, 0), (1, 0), (2, 0)]
#    ys = [0, 1, 2]
#    reg = MultipleLinearRegressor(xs=xs, ys=ys)
# #        p = reg.predict([(0.0, 0.85)]) #0.00484421950062+/-8.3063828332e-06
# #        print p, p - 0.00484421950062
#    g = Graph3D()
#    import numpy as np
#    x, y = zip(*xs)
#    xx, yy = np.meshgrid(x, y)
#    r = len(x)
#    c = len(y)
#    pts = [(xx[j, i], yy[j, i]) for i in range(r)
#                                     for j in range(c)]
#
#    z = reg.predict(pts)
#
#    z = z.reshape((r, c))
# #    z = np.column_stack((xs, ys))
# #        print z
#
# #    ys = np.ones((3, 3))
# #    zs = ys * z
# #    print x
# #    print y
# #    print zs
#    g.plot_surf(z)
# #    g.plot_surf(x, y, ys)
# #    g.plot_surf(x, y, zs)
#    g.configure_traits()
#============= EOF =============================================
