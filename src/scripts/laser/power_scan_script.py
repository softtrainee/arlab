#===============================================================================
# Copyright 2011 Jake Ross
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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================

from src.scripts.core.core_script import CoreScript
from power_scan_script_parser import PowerScanScriptParser
from src.graph.stacked_graph import StackedGraph
from src.helpers.datetime_tools import time_generator

class PowerScanScript(CoreScript):


    parser_klass = PowerScanScriptParser

#    record_data = True

    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText

        doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')

        doc.add_heading('Power Scan Documentation', heading=2, color='red')

        doc.add_heading('Header', heading=3)
        doc.add_text('Configure what measurements to make during scan and how to plot them<br>')

        doc.add_heading('Parameters', heading=3)
        doc.add_text('Device, Func, Label, Plotid, Series<br>')
        doc.add_list(['Device -- object name of device to measure',
                      'Func -- function to call to get a measurement',
                      'Label -- plot label',
                      'Plotid -- plot identifier',
                      'Series -- series identifier'])

        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])

        r2 = HTMLText('1,5,0.1,10.', face='courier', size='2')
        table.add_row([r2])

        doc.add_heading('Type A Parameters', heading=3)
        doc.add_text('Power, Hold <br>')
        doc.add_list(['Power setting (0-100) -- percent of total power',
                      'Hold (secs) -- time to hold power'])

        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])
        r2 = HTMLText('20,10.', face='courier', size='2')
        table.add_row([r2])

        doc.add_heading('Type B Parameters', heading=3)
        doc.add_text('''PowerStart, PowerEnd, k, Hold<br>
    Step by k from power start to power end and wait for hold secs<br><br>
    ''')

        doc.add_list([
                      'Power start setting (0-100) -- percent of total power',
                      'Power end setting (0-100) -- percent of total power',
                      'Power increment (integer) --',
                      'Hold (secs) -- time to hold power'])

        table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
        r1 = HTMLText('Ex.', face='courier', size='2')
        table.add_row([r1])
        r2 = HTMLText('0,50,1,5.', face='courier', size='2')
        table.add_row([r2])

        return doc


    def load(self):
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

                    self.scan_setup.append((obj, func, dict(plotid=plotid, series=series,
                                                        label=label
                                                        )))


        self._file_contents_ = self._file_contents_[i + 1:]

        self.set_data_frame()

        return True

    def get_frame_header(self):
        metadata = []
        metadata.append(['#===========plot metadata============'])
        metadata.append(['#time', 'request_power'])

        header = []
        for _obj, attr, plotinfo in self.scan_setup:
            header.append(attr)

            metadata.append(['#%s' % attr, plotinfo['plotid'], plotinfo['series']])

        metadata.append(['#===================================='])
        metadata.append(header)
        return metadata

    def set_graph(self):
        '''
        '''
        g = StackedGraph(window_title='Power Scan %s' % self.file_name)

        g.new_plot(show_legend='ur')
        cur_plotid = 0

        for _obj, func, plotinfo in self.scan_setup:

            plotid = plotinfo['plotid']
            series = plotinfo['series']
            label = plotinfo['label']
            if not cur_plotid == plotid:
                g.new_plot(show_legend='ur')
                cur_plotid = plotid

            g.new_series(type='line', render_style='connectedpoints', plotid=cur_plotid)
            if label is None:
                label = func

            g.set_series_label(label, series=series, plotid=cur_plotid)

        g.edit_traits()
        self.graph = g

    def _pre_run_(self):
        if self.manager.enable_laser():
            return True

    def raw_statement(self, args):
        if len(args) == 2:
            self._execute_step(*args)
        else:
            pmin = int(args[0])
            pmax = int(args[1])
            k = int(args[2])
            pmin /= k
            pmax /= k
            if pmin < pmax:
                incr = k
            else:
                incr = -k

            dur = float(args[3])
            for pi in range(pmin, pmax + 1, 1):
                pi *= incr
                if not self.isAlive():
                    break
                self._execute_step(pi, dur)

    def _execute_step(self, pwr, dur):
        pwr = float(pwr)
        dur = float(dur)
        manager = self.manager
        if manager is not None:
                manager.set_laser_power(pwr)
        self.wait(dur)

        if hasattr(self, 'timestamp_gen'):
            timestamp = self.timestamp_gen.next()
        else:
            timestamp = 0
            self.timestamp_gen = time_generator()

        data = []
        drow = [timestamp, pwr]
        for obj, attr, info in self.scan_setup:
            obj = getattr(self.manager, obj)
            attr = getattr(obj, attr)
            if type(attr).__name__ == 'instancemethod':
                attr = attr()

            data.append(((pwr, attr), info))

            drow.append(attr)
        if data:
            for datum, info in data:
                #internal = random.random()
                kw = info.copy()
                kw.pop('label')
                self.graph.add_datum(datum, **kw)
                #self.graph.add_datum((rpower, internal))
        self.data_manager.write_to_frame(drow)

    def _kill_script(self):
        self.manager.emergency_shutoff()

#============= EOF ====================================
