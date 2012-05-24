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



##@PydevCodeAnalysisIgnore
#
##===============================================================================
## This Module is out of date 
##===============================================================================
#
##=============enthought library imports=======================
#from traits.api import Instance, Button
#from traitsui.api import View, Item, VGroup
#from pyface.timer.api import Timer
#
##=============standard library imports ========================
#
##=============local library imports  ==========================
#from src.managers.data_managers.csv_data_manager import CSVDataManager
#from src.graph.time_series_graph import TimeSeriesStreamGraph
#from stream_loader import StreamLoader
#
#from manager import Manager
#
#class StreamManager(Manager):
#    '''
#        G{classtree}
#    '''
#
#    graph = Instance(TimeSeriesStreamGraph)
#    data_manager = Instance(Manager)
#
#    stream_loader = Instance(StreamLoader)
#
#    open = Button
#    warned = False
#    running = False
#    def __init__(self, *args, **kw):
#        '''
#
#        '''
#
#        super(StreamManager, self).__init__(*args, **kw)
#
#        self.reload()
#
#    def save_graph(self):
#        '''
#        '''
#        graph = self.graph
#
#        p = self.save_file_dialog()
#        if p is not None:
#            graph.save(p)
#
#    def set_graphable(self):
#        '''
#        '''
#        self.graph = self._graph_factory()
#
#
#    def reload(self):
#        '''
#        '''
#
#        self.graph = self._graph_factory()
#        self.graph.plotcontainer.request_redraw()
#        self.streamids = []
#        self.timers = []
#        self.timer_functions = []
#        self.scan_args = []
#        self.scan_kwargs = []
#        self.timer_delays = []
#        self.parents = []
#        self.graph_info = []
#        self.data_info = []
#
#    def set_stream_tableid(self, id, tableid):
#        '''
#            @_type id: C{str}
#            @param id:
#
#            @_type tableid: C{str}
#            @param tableid:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#        self.data_info[id] = tableid
#
#    def set_stream_file_id(self, id, file_id):
#        '''
#            @type id: C{str}
#            @param id:
#
#            @type file_id: C{str}
#            @param file_id:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#        self.data_info[id] = file_id
#
#
#    def record(self, value, id, graph = True, file = True):
#        '''
#            @_type value: C{str}
#            @param value:
#
#            @_type id: C{str}
#            @param id:
#
#            @_type graph: C{str}
#            @param graph:
#
#            @_type file: C{str}
#            @param file:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#        if file:
#            di = self.data_info[id]
#            self.data_manager.add_time_stamped_value(value, di)
#
#        if graph:
#            p, s = self.graph_info[id]
#
#            if isinstance(value, tuple):
#                value = value[0]
#
#            if self.graph is not None:
#                self.graph.record(value, plotid = p, series = s)
#
#    def sample_stream(self, id, integrate = 1):
#        '''
#            @_type id: C{str}
#            @param id:
#
#            @_type integrate: C{str}
#            @param integrate:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#
#        r = 0
##        if integrate == 1:
##            r = self.parents[id].current_value
##        else:
#        #get the last integrate seconds from the data buffer
#        p, s = self.graph_info[id]
#        #x=self.graph.get_data(p,s,0)
#        y = self.graph.get_data(p, s, 1)
#        if len(y) < integrate:
#            integrate = len(y)
#        if integrate > 0:
#            r = sum(y[-integrate:]) / integrate
#
#            #r = reduce(lambda a, b: a + b, y[-integrate:]) / integrate
#        return r
#
#    def block_stream(self, id, block):
#        '''
#            @_type id: C{str}
#            @param id:
#
#            @_type block: C{str}
#            @param block:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#        self.parents[id].block = block
#
#    def start_streams(self, *streams):
#        '''
#
#        '''
#        if len(streams) == 0:
#
#            streams = [self.streamids]
#
#
#        for id in streams[0]:
#            self.start_stream(id)
#
#
#
#    def stop_streams(self, *args):
#        '''
#  
#        '''
#        if len(args) == 0:
#            #stop all running streams
#            args = self.streamids
#
#        for a in args:
#            self.stop_stream(a)
#
#        self.running = False
#
#    def start_stream(self, id):
#        '''
#            @_type id: C{str}
#            @param id:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#
#        self.timers[id] = Timer(self.timer_delays[id], self.timer_functions[id],
#                                *self.scan_args[id],
#                                **self.scan_kwargs[id]
#                                )
#
#    def stop_stream(self, id):
#        '''
#            @_type id: C{str}
#            @param id:
#        '''
#        id = id if isinstance(id, int) else self.streamids.index(id)
#
#
#
#        t = self.timers[id]
#        if t:
#            t.Stop()
#
#
#    def load_streams(self, s, start = False):
#        '''
#            @_type s: C{str}
#            @param s:
#
#            @_type start: C{str}
#            @param start:
#        '''
#        streamids = [self.load_stream(si, start) for si in s]
#        if streamids and start:
#            self.start_streams(streamids)
#
#        return streamids
#
#    def load_stream(self, options, start):
#        '''
#        '''
#        parent = options['parent']
#        self.parents.append(parent)
#        if 'id' not in options:
#            id = parent.name
#        else:
#            id = options['id']
#
#        if id not in self.streamids:
#            self.info('loading %s' % id)
#            self.streamids.append(id)
#
##            if self.data_manager.style == 'txt':
##                #self.logger.info('creating new frame for %s'%id)
##                self.data_manager.new_frame(None, base_frame_name = id)
#            f = self.data_manager.new_frame(base_frame_name = id)
#
#
#            self.data_info.append(f)
#            kw = dict(title = options['title']) \
#                if options.has_key('title') else dict()
#
#            kw['zoom'] = True
#            kw['pan'] = True
#            kw['show_legend'] = options['show_legend'] if options.has_key('show_legend') else False
#            self.timers.append(None)
#
#
#            self.timer_functions.append(parent.scan)
#            args = options['scan_args'] if options.has_key('scan_args') else []
#            self.scan_args.append(args)
#
#            kwargs = options['scan_kwargs'] if options.has_key('scan_kwargs') else {}
#            self.scan_kwargs.append(kwargs)
#
#            de = options['delay'] * 1000.0 if options.has_key('delay') else 1000
#            self.timer_delays.append(de)
#
#            plotid = options['plotid'] if options.has_key('plotid') else 0
#            series = options['series'] if options.has_key('series') else 0
#            parent.plotid = plotid
#            parent.series = series
#            self.graph_info.append((plotid, series))
#
##            tableid = options['tableid'] if options.has_key('tableid') else None
##            load_table = options['load_table'] if options.has_key('load_table') else False
##
##            self.data_info.append(tableid)
##            if tableid and load_table:
##                #self.data_manager.build_table(tableid)
##                pass
#
#            if self.graph is not None:
#                if options['new_plot'] if options.has_key('new_plot') else True:
#
#                    title = 'ytitle'
#                    if options.has_key(title):
#                        kw[title] = options[title]
#                    kw['xtitle'] = 'Time'
#                    self.graph.new_plot(
#                                        data_limit = 1800,
#                                        scan_delay = de / 1000.0,
#                                        padding = [25, 5, 25, 30],
#                                        ** kw
#                                        )
#
#
#                label = options['label'] if options.has_key('label') else None
#                if label:
#                    self.graph.set_series_label(label, plotid = plotid, series = series)
#
#                self.graph.new_series(plotid = plotid,
#                                      x = [0],
#                                      y = [0],
#                                      kind = options['_type'] if options.has_key('_type') else 'scatter',
#                                      marker = options['marker'] if options.has_key('marker') else 'circle',
#                                      marker_size = options['marker_size'] if options.has_key('marker_size') else 2.5,
#                                      )
#
#
##                        self.graph._set_title('%s_axis' % t, options[title], plotid)
##                        
#            return id
#
#        return False
##    def load_from_file(self,p,group,table, value_field='value'):
##        
##        df=tables.openFile(p,'r')
##        
##        g=Graph(show_editor=True)
##        g.new_plot(pan=True,zoom=True)
##        
##        group=getattr(df.root,group)
##        table=getattr(group,table)
##        
##        y=[row[value_field] for row in table.iterrows()]
##        x=range(len(y))
##        g.new_series(x=x,y=y)
##        
##        g.edit_traits()
#    def streams_factory(self, streams):
#        self.stream_loader = StreamLoader()
#        for s in streams:
#            self.stream_loader.add_stream(s)
#
#    def initialize_streams(self):
#        self.reload()
#        sl = self.stream_loader
#        st = []
#        for i, s in enumerate(sl.streams):
#            if s.include:
#
#                s.parent.stream_manager = self
#                d = dict(parent = s.parent,
#                       delay = s.delay * sl.time_units,
#                       plotid = i,
#                       title = s.parent.name,
#                       type = s._type)
#                st.append(d)
#
#        #self.data_manager.style = sl.save_type
#        if sl.save_type == 'h5':
#            if sl.save_data:
#                pass
##                    if sl.default_path:
##                        self.data_manager.new_frame(None)
##                    else:
##                        p = self.save_file_dialog()
##                        if p is not None:
##                            self.data_manager.new_frame(p)
#
#        self.load_streams(st, start = True)
#        self.running = True
#        #self.start_streams()
#        return st
#
#
#
#    def _graph_factory(self):
#        '''
#        '''
#        return TimeSeriesStreamGraph(container_dict = dict(padding = 10))
#
#    def _graph_default(self):
#        '''
#        '''
#        g = self._graph_factory()
#        return g
#
#    def _data_manager_default(self):
#        '''
#        '''
#        return CSVDataManager()
#
#    def traits_view(self):
#        '''
#        '''
#        return View(VGroup(
#                           Item('graph', show_label = False, style = 'custom'),
#                           ),
#
#
#
#                    resizable = True,
#                    #title = 'Streams',
#                    x = self.window_x,
#                    y = self.window_y,
#                    width = 600,
#                    height = 500
#                    )

#============= EOF ============================================

#    def open_stream_loader(self, streams):
#        '''
#            @_type streams: C{str}
#            @param streams:
#        '''
#        if self.running:
#            return 'running'
#
#
#        #self.reload()
#
#        #close the data manager
#        #self.data_manager.close()
#
#        sl = StreamLoader()
#        for s in streams:
#            sl.add_stream(s)
#
#        info = sl.edit_traits(kind = 'modal')
#        if info.result:
#            return self.initialize_streams()
#        else:
#            return False      

