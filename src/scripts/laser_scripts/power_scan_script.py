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
#@PydevCodeAnalysisIgnore

#=============enthought library imports=======================
#=============standard library imports ========================

#=============local library imports  ==========================
from laser_power_script import LaserPowerScript

from src.helpers.datetime_tools import time_generator

from src.graph.stacked_graph import StackedGraph

class PowerScanScript(LaserPowerScript):
    '''
    '''

    control_mode = 'open'

    def load_file(self):
        self.scan_setup = []
        plotid = 0
        series = 0

        for i, line in enumerate(self._file_contents_):
            #use a ------------- line to separate metadata from script data
            if line.startswith('----'):
                break
            else:
                args = line.split(',')
                obj = args[0]
                func = args[1]
                label = None

                if len(args) == 5:
                    label = args[2]
                    plotid = int(args[3])
                    series = int(args[4])

                    self.scan_setup.append((obj, func, dict(plotid = plotid, series = series,
                                                        label = label
                                                        )))


        self._file_contents_ = self._file_contents_[i:]

    def kill_script(self):
#        super(PowerScanScript, self).kill_script()
        LaserPowerScript.kill_script(self)
        self.manager.emergency_shutoff()

    def set_data_frame(self):
        '''
        '''

        if LaserPowerScript.set_data_frame(self):
            dm = self.data_manager
            dm.write_to_frame(['#===========plot metadata============'], 'run')
            #write a metadata
            header = ['#time', 'request_power']
            for obj, attr, plotinfo in self.scan_setup:
                header.append(attr)

                dm.write_to_frame(['#%s' % attr, plotinfo['plotid'], plotinfo['series']], 'run')

            dm.write_to_frame(['#===================================='], 'run')
            dm.write_to_frame(header, 'run')

            return True

    def set_graph(self):
        '''
        '''
        g = StackedGraph(title = 'Power Scan')

        g.new_plot(show_legend = 'ur')
        cur_plotid = 0
        for obj, func, plotinfo in self.scan_setup:

            plotid = plotinfo['plotid']
            series = plotinfo['series']
            label = plotinfo['label']
            if not cur_plotid == plotid:
                g.new_plot(show_legend = 'ur')
                cur_plotid = plotid

            g.new_series(type = 'line', render_style = 'connectedpoints', plotid = cur_plotid)
            if label is None:
                label = func
            g.set_series_label(label, series = series, plotid = cur_plotid)


        g.edit_traits()
        self.graph = g

    def execute_step(self, rpower, interval):
        '''
            @type rpower: C{str}
            @param rpower:

            @type interval: C{str}
            @param interval:
        '''

        manager = self.manager

        if not self.isAlive():
            return

        #step the laser power
        manager.set_laser_power(rpower, self.control_mode)

        #delay before measurement
        #time.sleep(interval)
        self.wait(interval)

        data = []

        if hasattr(self, 'timestamp_gen'):
            timestamp = self.timestamp_gen.next()
        else:
            timestamp = 0
            self.timestamp_gen = time_generator()

        drow = [timestamp, rpower]
        for obj, attr, info in self.scan_setup:
            obj = getattr(self.manager, obj)
            attr = getattr(obj, attr)
            if type(attr).__name__ == 'instancemethod':
                attr = attr()

            data.append(((rpower, attr), info))

            drow.append(attr)
        if data:
            for datum, info in data:
                #internal = random.random()
                kw = info.copy()
                kw.pop('label')
                self.graph.add_datum(datum, **kw)
                #self.graph.add_datum((rpower, internal))
        self.data_manager.write_to_frame(drow, 'run')
        return True

    def _run_(self):
        '''
        '''

        manager = self.manager

        manager.enable_laser()

        for line in self._file_contents_:

            if not self.isAlive():
                break

            args = line.split(',')
            if len(args) == 2:
                #set laser power to (power) and wait for (interval) seconds
                manager.set_laser_power(float(args[0]))

                self.wait(float(args[1]))

            elif len(args) == 4:
                pmin = int(args[0])
                pmax = int(args[1])
                k = int(args[2])
                pmin /= k
                pmax /= k
                if pmin < pmax:
                    incr = k
                else:
                    incr = -k

                interval = float(args[3])
                for pi in range(pmin, pmax + 1, 1):
                    pi *= incr
                    if not self.execute_step(pi, interval):
                        break

        self.clean_up()

#=========== EOF ================
