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
from traits.api import HasTraits, List, Instance, Any, Property, Float
from traitsui.api import View, Item, HGroup, TableEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================
import os
import csv
import time
#============= local library imports  ==========================
from src.data_processing.regression.regressor import Regressor
from src.helpers.paths import setup_dir
from src.spectrometer.molecular_weights import MOLECULAR_WEIGHTS
import math
from src.graph.graph import Graph
from src.spectrometer.spectrometer_device import SpectrometerDevice
class CalibrationPoint(HasTraits):
    x = Float
    y = Float

class Magnet(SpectrometerDevice):
    mftable = List(
                   #[[40, 39, 38, 36], [2, 5, 10, 26]]
                   )
    regressor = Instance(Regressor, ())
    microcontroller = Any

    magnet_dac = Property(depends_on='_magnet_dac')
    _magnet_dac = Float
    magnet_dacmin = Float(0.0)
    magnet_dacmax = Float(10.0)

    settling_time = 0.01

    calibration_points = Property(depends_on='mftable')
    graph = Instance(Graph, ())
    def _get_calibration_points(self):
        pts = []
        xs, ys = self.mftable
        for xi, yi in zip(xs, ys):
            xi = MOLECULAR_WEIGHTS[xi]
            pts.append(CalibrationPoint(x=xi, y=yi))
        return pts

    def update_graph(self):
        pts = self._get_calibration_points()
        self.set_graph(pts)
        return pts

    def _get_magnet_dac(self):
        return self._magnet_dac

    def _set_magnet_dac(self, v):
        self.set_dac(v)

    def get_dac_for_mass(self, mass):
        reg = self.regressor
        data = [[MOLECULAR_WEIGHTS[i] for i in self.mftable[0]],
                self.mftable[1]
                ]
        if isinstance(mass, str):
            mass = MOLECULAR_WEIGHTS[mass]

        print data, mass
        if data:
            dac_value = reg.get_value('parabolic', data, mass)
        else:
            dac_value = 4

        return dac_value

    def set_axial_mass(self, x, hv_correction=1):
        '''
            set the axial detector to mass x
        '''
        reg = self.regressor

        data = [[MOLECULAR_WEIGHTS[i] for i in self.mftable[0]],
                self.mftable[1]
                ]
        dac_value = reg.get_value('parabolic', data, x)
        #print x, dac_value, hv_correction

        self.set_dac(dac_value * hv_correction)

    def set_dac(self, v):
        self._magnet_dac = v
        if self.microcontroller:
            _r = self.microcontroller.ask('SetMagnetDAC {}'.format(v), verbose=True)
            time.sleep(self.settling_time)

    def read_dac(self):
        if self.microcontroller is None:
            r = 0
        else:
            r = self.microcontroller.ask('GetMagnetDAC')
            try:
                r = float(r)
            except:
                pass
        return r

    def update_mftable(self, key, value):
        self.info('update mftable {} {}'.format(key, value))
        xs = self.mftable[0]
        ys = self.mftable[1]


        refindex = xs.index(key)
        delta = ys[refindex] - value
        #need to calculate all ys
        for i, xi in enumerate(xs):
            mass = MOLECULAR_WEIGHTS[xi]
            refmass = MOLECULAR_WEIGHTS[key]

            ys[i] -= delta * math.sqrt(mass / refmass)

        self.dump()

    def set_graph(self, pts):

        g = Graph(container_dict=dict(padding=10))
        g.clear()
        g.new_plot(xtitle='Mass',
                   ytitle='DAC',
                   padding=[30, 0, 0, 30],
                   zoom=True,
                   pan=True
                   )
        g.set_x_limits(0, 150)
        g.set_y_limits(0, 100)
        xs = [cp.x for cp in pts]
        ys = [cp.y * 10 for cp in pts]

        reg = self.regressor
        rdict = reg.parabolic(xs, ys, data_range=(0, 150), npts=5000)

        g.new_series(x=xs, y=ys, type='scatter')


        g.new_series(x=rdict['x'], y=rdict['y'])
        self.graph = g

    def mftable_view(self):
        cols = [ObjectColumn(name='x', label='Mass'),
              ObjectColumn(name='y', label='DAC'),
              ]
        teditor = TableEditor(columns=cols, editable=False)
        v = View(HGroup(
                        Item('calibration_points', editor=teditor, show_label=False),
                        Item('graph', show_label=False, style='custom')
                        ),
                 width=700,
                 height=500,
                 resizable=True

                 )
        return v


    def load(self):
        p = os.path.join(setup_dir, 'spectrometer', 'mftable.csv')
        with open(p, 'U') as f:
            reader = csv.reader(f)
            xs = []
            ys = []
            for line in reader:
                xs.append(line[0])
                ys.append(float(line[1]))

        self.mftable = [xs, ys]

    def dump(self):
        p = os.path.join(setup_dir, 'spectrometer', 'mftable.csv')
        with open(p, 'w') as f:
            writer = csv.writer(f)
            for x, y in zip(self.mftable[0], self.mftable[1]):
                writer.writerow([x, y])
#============= EOF =============================================
