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
##============= enthought library imports =======================
#from traits.api import Button, DelegatesTo, Instance, Event, Property, Bool
#from traitsui.api import View, Item, Group, VGroup, HGroup, HSplit, spring
##============= standard library imports ========================
##import inspect
##import csv
#import numpy as np
#from scipy.stats.stats import scoreatpercentile
##============= local library imports  ==========================
#from src.helpers.datetime_tools import convert_timestamp
#from src.graph.time_series_graph import TimeSeriesGraph
#from src.graph.candle_graph import CandleGraph
#from src.hardware.core.core_device import CoreDevice
#
##from stream_manager import StreamManager
#from manager import Manager
#from src.helpers.color_generators import colorname_generator
#from src.data_processing.time_series.time_series import seasonal_subseries
#
#class DeviceStreamManager(Manager):
#    '''
#        G{classtree}
#    '''
#
#    stream_manager = Instance(StreamManager)
#
#    stream_button = Event
#    stream_button_label = Property(depends_on = '_streaming')
#    _streaming = Bool(False)
#
#    stream_loader = DelegatesTo('stream_manager')
#
#    open_stream = Button
#
#    def finish_loading(self):
#        #get all the devices    
#        devs = [getattr(self, n) for n in self._get_device_names()]
#        self.stream_manager.streams_factory(devs)
#
#    def _read_file(self, path):
#        print 'reading %s' % path
#        data = np.loadtxt(path, converters = {0:convert_timestamp}, delimiter = ',')
#        xs, ys = np.hsplit(data, 2)
#        return xs.flatten(), ys.flatten()
#
#    def _candle_graph(self, xs, ys):
#        mins = []
#        maxs = []
#        bmins = []
#        bmaxs = []
#        means = []
#
#        g = CandleGraph()
#        g.new_plot(title = '',
#                   xtitle = 'Hours',
#                   ytitle = 'Temp C',
#                   zoom = True,
#                   zoom_dict = dict(tool_mode = 'range',
#                                  axis = 'index'),
#                    padding_top = 10
#                   )
#
#        for yi in seasonal_subseries(xs, ys)[1]:
#            if yi:
#                yi = np.array(yi)
#
#                mins.append(min(yi))
#                bmins.append(scoreatpercentile(yi, 25))
#                means.append(np.median(yi))
#                bmaxs.append(scoreatpercentile(yi, 75))
#                maxs.append(max(yi))
#
#        xx = range(len(means))
#        g.new_series(x = xx,
#                      y = means,
#                      ymin = mins,
#                      ymax = maxs,
#                      ybarmin = bmins,
#                      ybarmax = bmaxs)
#        return g
#
#            #g.configure_traits()
#    def _seasonal_subseries_graph(self, xs, ys):
#        g = TimeSeriesGraph()
#        g.new_plot(title = '',
#                   xtitle = 'Time',
#                   ytitle = 'Temp C',
#                   zoom = True,
#                   zoom_dict = dict(tool_mode = 'range',
#                                  axis = 'index'),
#                   )
#        xbins, ybins, ms = seasonal_subseries(xs, ys)
#        cgen = colorname_generator()
#
#        for xi, yi, mi in zip(xbins, ybins, ms):
#            c = cgen.next()
#            g.new_series(x = xi,
#                     y = g.smooth(yi),
#                     render_style = 'connectedpoints',
#                     #marker_size = 0.75,
#                     color = c
#                     )
#
#            g.new_series(x = [xi[0], xi[-1]],
#                         y = [mi, mi],
#                         color = c
#                         )
#
#        g.new_plot(link = False,
#                   zoom = True,
#                   zoom_dict = dict(tool_mode = 'range',
#                                  axis = 'index'))
#        g.new_series(x = xs,
#                     y = g.smooth(ys, window_len = 120, window = 'flat'),
#                     #y = ys,
#                     render_style = 'connectedpoints',
#                     plotid = 1,
#                     timescale = True,
#                     #downsample = 120,
#                     )
#        return g
##            g.edit_traits()
#    def all(self, xs, ys):
#        g = self._seasonal_subseries_graph(xs, ys)
#        g2 = self._candle_graph(xs, ys)
#        g.plotcontainer.insert(0, g2.plots[0])
#        g.configure_traits()
#
#    def _open_stream_fired(self):
#        #path = self._file_dialog_('open', default_directory = os.path.join(data_dir, 'streams'))
#        import os
#        from src.helpers.paths import data_dir
#        path = os.path.join(data_dir, 'sandbox', 'DPi32TemperatureMonitor003.txt')
#        if path:
#            xs, ys = self._read_file(path)
#            #self.all(xs, ys)
##            g = self._candle_graph(xs, ys)
#            g = self._seasonal_subseries_graph(xs, ys)
#            g.configure_traits()
#
#    def _get_stream_button_label(self):
#        return 'Start' if not self._streaming else 'Stop'
#
#    def _stream_button_fired(self):
#        if not self._streaming:
#            self.stream_manager.initialize_streams()
#        else:
#            self.stream_manager.stop_streams()
#        self._streaming = not self._streaming
#
#    def _get_device_names(self):
#        r = []
#        for i in self.traits():
#            try:
#                a = getattr(self, i)
#            except AttributeError:
#                continue
#
#            if issubclass(a, CoreDevice):
#                r.append(i)
##            for a in inspect.getmro(a.__class__):
##                if 'CoreDevice' in a.__name__:
##                    r.append(i)
#        return r
#
#    def get_device_group(self):
#        '''
#        '''
#        dg = VGroup(label = 'Devices')
#        for name in self._get_device_names():
#            dg.content.append(
#                              Group(
#                                    Item(name, show_label = False,
#                                         style = 'custom'
#                                         ),
#                                    show_border = True,
#                                    label = name
#                                   )
#                             )
#
#        return dg
#
#    def traits_view(self):
#        '''
#        '''
#        return View(
#                    HSplit(
#                           Group(
#                                 Item('stream_loader', style = 'custom', show_label = False, width = 0.32, label = 'Streams Prefs'),
#                                 self.get_device_group(),
#                                 layout = 'tabbed'
#                                ),
#                           VGroup(
#                                  HGroup(
#                                         self._button_factory('stream_button', 'stream_button_label', None,),
#                                         self._button_factory('open_stream', None, None,),
#
#                                         spring),
#                                  Item('stream_manager', style = 'custom', show_label = False, width = 0.68)
#                                 )
#                          ),
#
#                    resizable = True,
#                    title = 'Device Streamer',
#                    width = 0.75,
#                    height = 0.6
#                    )
#
#    def _stream_manager_default(self):
#        sm = StreamManager()
#        return sm
#
##============= EOF ====================================
#def test():
#    dsm = DeviceStreamManager(name = 'device_streamer')
#    dsm._open_stream_fired()
#
#if __name__ == '__main__':
##    from timeit import Timer
##    t = Timer('test()', 'from __main__ import test')
##    print t.timeit(1)
#    test()
##    setup(name = 'device_streamer')
##    dsm = DeviceStreamManager(name = 'device_streamer')
##    dsm.bootstrap()
##    dsm.configure_traits()
##    def load(self):
##        '''
##        '''
##        config = self.get_configuration()
##
##        if config is not None:
##            devices = self.config_get(config, 'General', 'devices').split(',')
##            names = []
##            for d in devices:
##                if self.create_device(d):
##                    names.append(d)
##                    
##                    
##            self.names = names
##    def initialize(self):
##        names = self.names
##        print names
##        for n in names:
##            dev = getattr(self, n)
##            if dev:
##                dev.bootstrap()
##                self._adevices.append(dev)
##        self.stream_manager.streams_factory(self._adevices)
##        return True
