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
from traits.api import Float, Enum
from pyface.timer.timer import Timer

#============= standard library imports ========================

#============= local library imports  ==========================

from src.scripts.core.core_script import CoreScript
from src.graph.stacked_graph import StackedGraph
from src.helpers.datetime_tools import time_generator
from src.scripts.laser.degas_script_parser import DegasScriptParser
from src.graph.time_series_graph import TimeSeriesStreamStackedGraph
import math

class DegasScript(CoreScript):


    parser_klass = DegasScriptParser
    setpoint = Float
    control_mode = Enum('closed', 'open')
#    record_data = True

    def get_documentation(self):
        from src.scripts.core.html_builder import HTMLDoc, HTMLText

        doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')

        doc.add_heading('Degas Documentation', heading=2, color='red')

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
        #plotid = 0
        #series = 0
        
        #first line should be scan period
        self.scan_period = float(self._file_contents_[0].strip())
        self._file_contents_.pop(0)
        for i, line in enumerate(self._file_contents_):
            #use a ------------- line to separate metadata from script data
            if line.startswith('----'):
                break
            else:
                args = line.split(',')
                obj = args[0]
                func = args[1]
                #label = None

                if len(args) >= 5:
                    d = dict(
                        label=args[2],
                        plotid=int(args[3]),
                        series=int(args[4]))
                    
                    vscale = 'linear'
                    formatter = None
                    try:
                        vscale = args[5].strip()
                        def format(x):
                            if x < 1:
                                return '{:02n}'.format(math.floor(math.log(x, 10))) if abs(math.floor(math.log(x, 10)) - math.log(x, 10)) <= 1e-6 else ''
                            else:
                                return '{:02n}'.format(math.ceil(math.log(x, 10))) if abs(math.ceil(math.log(x, 10)) - math.log(x, 10)) <= 1e-6 else ''
                        formatter = format
                    except IndexError:
                        pass
                    
                    d['formatter'] = formatter
                        
                    d['value_scale'] = vscale
                    
                    self.scan_setup.append((obj, func, d))


        self._file_contents_ = self._file_contents_[i + 1:]

        self.set_data_frame()

        return True

    def get_frame_header(self):
        metadata = []
        metadata.append(['#===========plot metadata============'])
       
        header = ['#time', 'request_power']
        for _obj, attr, plotinfo in self.scan_setup:
            header.append(attr)

            metadata.append(['#%s' % attr, plotinfo['plotid'], plotinfo['series']])

        metadata.append(header)
        metadata.append(['#===================================='])
        return metadata

    def set_graph(self):
        '''
        '''
        g = TimeSeriesStreamStackedGraph(
                                         panel_height=175
                                         #window_title='Degas Scan %s' % self.file_name
                                         )        
        g.new_plot(show_legend='ur')
        g.set_x_title('Time')
        g.set_y_title('Setpoint (C)')
            
        g.new_series()
        g.new_series()
        
        g.set_series_label('Request')
        g.set_series_label('Process Value', series=1)
            
        cur_plotid = 0
        for _obj, func, plotinfo in self.scan_setup:

            plotid = plotinfo['plotid']
            series = plotinfo['series']
            label = plotinfo['label']
            value_scale = plotinfo['value_scale']
            formatter = plotinfo['formatter']
            
            
            if not cur_plotid == plotid:
                g.new_plot(show_legend='ur')
                cur_plotid = plotid

            if formatter:
                g.plots[cur_plotid].value_axis.tick_label_formatter = formatter
                
            g.new_series(type='line', value_scale=value_scale, render_style='connectedpoints', plotid=cur_plotid)
            if label is None:
                label = func

            g.set_series_label(label, series=series, plotid=cur_plotid)

        g.set_y_title('Pressure', plotid=1)
        g.set_y_title('Temp', plotid=2)
        
        self.scan_timer = Timer(self.scan_period * 1000,
                              self._scan_
                              )
        
        self.graph = g
        
    def _scan_(self):
        if hasattr(self, 'timestamp_gen'):
            timestamp = self.timestamp_gen.next()
        else:
            timestamp = 0
            self.timestamp_gen = time_generator()

        pv = self.manager.temperature_controller.process_value
        drow = [timestamp, self.setpoint, pv]
        
        for obj, attr, info in self.scan_setup:    
            manager, device = obj.split('.')
            if manager == 'laser':
                manager = self.manager
            else:
                if manager == 'gauge':
                    protocol = 'src.managers.gauge_manager.GaugeManager'
                manager = self.manager.application.get_service(protocol)
            v = 0
            try:
                dev = getattr(manager, device)
                attr = getattr(dev, attr)
                
                if type(attr).__name__ == 'instancemethod':
                    v = attr()
                    self.graph.record(v, **info)
            except AttributeError, e:
                self.warning(e)
                self.kill_script(failure_reason=e, force=True)
            
            drow.append(v)
        
        self.graph.record(self.setpoint, plotid=0)
        self.graph.record(pv, plotid=0, series=1)
        
        self.data_manager.write_to_frame(drow)
        
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
        self.setpoint = pwr
        manager = self.manager
        if manager is not None:
                manager.set_laser_power(pwr, mode=self.control_mode)
        self.wait(dur)

    
    def _kill_script(self):
        self.scan_timer.Stop()
        self.manager.emergency_shutoff()
    
#============= EOF ====================================
