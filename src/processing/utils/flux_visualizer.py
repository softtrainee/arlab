#===============================================================================
# Copyright 2013 Jake Ross
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
from traitsui.api import View, Item
import csv
from pylab import polar, show, ylim, Inf, arange, meshgrid, zeros, \
    contour, ones, contourf, array, mgrid, plot, legend, mean, polyfit, \
    polyval, linspace, argmin, argmax, scatter, cm, cos, sin, xlabel, ylabel, \
    colorbar, hstack
import math
# from itertools import groupby
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
#============= standard library imports ========================
#============= local library imports  ==========================
def load_holder(holder):
    holes = []
    with open(holder, 'r') as fp:
        reader = csv.reader(fp, delimiter=',')
        reader.next()  # pop header

        for i, line in enumerate(reader):
            try:
                x, y = map(float, line)
                v = math.atan2(y, x)
#                print i + 1, v, x, y, math.degrees(v)
                holes.append((x, y, v))
            except Exception:
                pass
    return holes

def visualize_flux(p, holder, use_polar=False):
    '''
        load the x,y points for irrad holder 
        load the flux file
        
        schema:
            hole,j
            
    '''
    holes = load_holder(holder)
#    x, y, holes = zip(*holes)

    with open(p, 'U') as fp:
        reader = csv.reader(fp)
#        holes = []
#        js = []
        reader.next()
        groups = []
        group = []
        for line in reader:
            if not line:
                groups.append(group)
                group = []
            else:
                group.append(pt_factory(line, holes))
        groups.append(group)
        mi = Inf
        ma = -Inf

#        fig = Figure()
        if not use_polar:
            fig = plt.figure()
            ax = fig.add_subplot(111,
                                 projection='3d'
                                 )
#        ax = fig.gca(projection='3d')
        mi_rings = []
        ma_rings = []
        for args in groups:
#            print args
#            theta, r = zip(*args)
            if use_polar:
                x, y, theta, r = zip(*[ai for ai in args if ai])

                polar(theta, r)
                mi = min(min(r), mi)
                ma = max(max(r), ma)

            else:
                x, y, theta, j = zip(*[ai for ai in args if ai])
                x = array(x)
                y = array(y)
                r = (x ** 2 + y ** 2) ** 0.5

                m, b = polyfit(x, y, 1)

#                xs = linspace(0, 0.5)
#                mf, bf = polyfit(x, j, 1)
#                fj = polyval((mf, bf), xs)
#                ax.plot(xs, polyval((m, b), xs), fj,)
                ax.plot(x, y, j, color='blue'
#                        label='{}'.format(int(math.degrees(mean(theta))))
                        )
#                ax.plot(x, y)
                midx = argmin(j)
                madx = argmax(j)

                mi_rings.append((x[midx], y[midx], j[midx]))
                ma_rings.append((x[madx], y[madx], j[madx]))

        if not use_polar:
            x, y, j = zip(*ma_rings)
            ax.plot(x, y, j, color='black')
            x, y, j = zip(*mi_rings)
            ax.plot(x, y, j, color='black')
        else:
            ylim(mi * 0.95, ma)
#        ax.set_xlim(-1, 1)
#        ax.set_ylim(-1, 1)
#                print r
#        lines = [pt_factory(line, holes) for line in reader]
#        theta, r = zip(*[args for args in lines if args])
    legend()
    show()


def pt_factory(line, holes):
    '''
        return theta, r for each line
        theta is calculated from corresponding x,y 
        r is flux 
    '''
    try:
        hole, j, sample = line
#        if sample == 'FC-2':
        x, y, theta = holes[int(hole) - 1]
#        print hole, theta
        return x, y, theta, float(j)
    except Exception, e:
        print e

def draw_circular_grid(r, rings):
    for ray in range(0, 360, 10):

            m = -math.radians(ray)
            x = r * math.cos(m)
            y = r * math.sin(m)
            plot([0, x], [0, y], ls='-.', color='black')

    for ring in rings:
        ring /= 100.
        x = linspace(-ring, ring, 100)
        y = (ring ** 2 - x ** 2) ** 0.5

        plot(x, -y, ls='-.', color='black')
        x = linspace(-ring, ring, 100)
        y = (ring ** 2 - x ** 2) ** 0.5
        plot(x, y, ls='-.', color='black')

def visualize_flux_contour(p, holder,):
#    from traits.etsconfig.etsconfig import ETSConfig
#    ETSConfig.toolkit = 'qt4'
#    from src.regression.ols_regressor import MultipleLinearRegressor
    use_2d = True

    holes = load_holder(holder)
    x, y = zip(*[(x, y) for x, y, v in holes])
    scatter(x, y)
    with open(p, 'U') as fp:
        reader = csv.reader(fp)
        reader.next()

        mi = Inf
        ma = -Inf
        xy = []
        z = []
        rs = []
        for line in reader:
            if not line:
                continue
            hole = int(line[0])
            j = float(line[1])
            x, y, v = holes[hole - 1]
            xy.append((x, y))
            z.append(j)

            mi = min(mi, j)
            ma = max(ma, j)

            rs.append(round(((x ** 2 + y ** 2) ** 0.5) * 100))

        xy = array(xy)
        xx, yy = xy.T
        r = max(xx)
        rings = list(set(rs))



        zz = None
        z = array(z)
        mz = min(z)
        z = z - mz
        z /= mz
        z *= 100
#         xs = []
#         ys = []
#         zs = []

#         for t in (0,):
#             t = math.radians(t)
#             nxx = xx * cos(t) - yy * sin(t)
#             nyy = xx * sin(t) + yy * cos(t)
#
#             xs = hstack((xs, nxx))
#             ys = hstack((ys, nyy))
#             zs = hstack((zs, z))

        xi = linspace(0, r, z.shape[0])
        yi = linspace(-r, r, z.shape[0])
        X = xi[None, :]
        Y = yi[:, None]

        zi = griddata((xx, yy), z, (X, Y),
                       method='cubic'
                      )

        contourf(xi, yi, zi, 30, cmap=cm.jet)
        cb = colorbar()
        cb.set_label('J %')
        scatter(xx, yy, marker='o',
                cmap=cm.jet,
                c=z, s=50)
#         draw_circular_grid(r, rings)

        xlabel('X (mm)')
        ylabel('Y (mm)')

        show()

if __name__ == '__main__':
#     p = '/Users/ross/Sandbox/flux_visualizer/J_data_for_nm-258_tray_G_radial.txt'
    p = '/Users/ross/Sandbox/flux_visualizer/J_data_for_nm-258_tray_G2.txt'
#    p = '/Users/ross/Sandbox/flux_visualizer/J_data_for_nm-258_tray_G.txt'
    holder = '/Users/ross/Pychrondata_diode/setupfiles/irradiation_tray_maps/1_75mm_3level'
#    visualize_flux(p, holder)
#    visualize_flux_contour(p, holder)
    visualize_flux_contour(p, holder)
#============= EOF =============================================
