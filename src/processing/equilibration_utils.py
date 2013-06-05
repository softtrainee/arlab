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
#============= standard library imports ========================
from numpy import asarray, convolve, exp, linspace, where, ones_like
from pylab import plot, show, axvline, legend, \
    xlabel, ylabel, polyval, axhline
#============= local library imports  ==========================
def calc_optimal_eqtime(xs, ys):

    xs, ys = asarray(xs), asarray(ys)
    # calculate rise rate for 10s window
    window = [-1, 1]
    rise_rates = convolve(ys, window, mode='same') / convolve(xs, window, mode='same')

    tol = 0.1
    rm = where(rise_rates < tol)[0]
    idx = min(rm)
    return rise_rates, xs[idx], ys[idx]

# def sniff(t, mag=1):
#    rate = 0.5
#    return mag * (1 - exp(-rate * t))
#
# def test_eq_calc():
#    ts = linspace(0, 50, 51)
#    ys = sniff(ts, 40)
#
#    rs = calc_optimal_eqtime(ts, ys)
#    plot(ts, ys, label='I')
#    plot(ts, rs, label='dI')
#
#    tol = 0.1
#    rm = where(rs < tol)[0]
#    axvline(x=ts[min(rm)], ls='--', color='black')
#    legend()
#    show()

def F(t, mag=1, rate=0.5):
    '''
        extraction line - mass spec equilibration function
    '''
    return mag * (1 - exp(-rate * t))

def G(t, rate=1):
    '''
        mass spec consumption function during equilibration
    '''
    return -rate * t
#    return ones_like(t) * mag
#    return mag * (exp(-rate * t))


if __name__ == '__main__':
    eq_m = -1
    mag = 100
    ts = linspace(0, 20, 500)
    f = F(ts, mag=mag)
    g = G(ts, rate=eq_m)
    fg = f - g
    plot(ts, f, label='F Equilibration')
    plot(ts, g, label='G Consumption')
    plot(ts, fg, label='F-G (Sniff Evo)')

    rf, ti, vi = calc_optimal_eqtime(ts, f)
    axvline(x=ti, ls='--', color='blue')
    rfg, ti, vi = calc_optimal_eqtime(ts[1:], fg[1:])
    axvline(x=ti, ls='--', color='red')

    m = -2
    b = vi - m * ti
    evo = polyval((m, b), ts)
    plot(ts, evo, ls='-.', color='red', label='Static Evo.')
    ee = where(evo > 100)[0]
    ti = ts[max(ee)]
    print ti

    axvline(x=ti, ls='-', color='black')
    axhline(y=mag, ls='-', color='black')
    plot([ti], [mag], 'bo')

    legend(loc=0)
    ylabel('Intensity')
    xlabel('t (s)')
#    fig = gcf()
#    fig.text(0.1, 0.01, 'asdfasfasfsadfsdaf')


    show()


#============= EOF =============================================
