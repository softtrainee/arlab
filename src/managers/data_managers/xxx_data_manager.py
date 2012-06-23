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



#'''
#@author: Jake Ross
#@copyright: 2009
#@license: Educational Community License 1.0
#'''
##=============enthought library imports=======================
#from traits.api import Property, \
# Enum, Bool, List, Dict, String, Int
#from traitsui.api import View, Item, VGroup, \
#EnumEditor, RangeEditor
#
#from chaco.default_colormaps import color_map_name_dict
#mlab = None
#
##=============standard library imports ========================
#import time
#import math
#
##tables import seems to be the import bottle neck
##a straight import tables takes approx. 2s 
##from tables import ... speeds import up to 0.5s
#
#
#from tables import *#Float32Col, IsDescription, StringCol, openFile
#from tables.exceptions import NodeError
#
#import os
#
#from numpy import transpose, array, shape, max, linspace
#
##=============local library imports  ==========================
##from globals import gdata_dir
#
##from preferences import preferences
#from src import paths
#from src.managers.manager import Manager
#
##lazy load the graphs
##TimeSeriesGraph = None
##RegressionGraph = None
##ResidualsGraph = None
##Graph = None
##ContourGraph = None
#
##from graph.time_series_graph import TimeSeriesGraph
##from graph.residuals_graph import ResidualsGraph
##from graph.regression_graph import RegressionGraph
#from src.graph.api import *
#from src.filetools import unique_path, generate_timestamp
#
#
#
##_color_maps = [key for key in color_map_name_dict]
#
#class XXXDataManager(Manager):
#    '''
#        G{classtree}
#    '''
#   # data_frames = []
##    def close(self):
##        '''
##        '''
##
##        if self.data_frames:
##            for df in self.data_frames:
##                df.close()
##        self.data_frames = []
#    #available_filters = Enum('Beam Profile', 'Power Scan', 'Plot Series')
#    style = 'h5'
#
#    available_filters = Enum(*('Pyrometer Calibration Scan',
#                             'Contour Plot Series', 'Power Scan', 'Explorer')
#                             )
#    _type = Enum(*('Barchart', 'ContourSurface', 'Contour', 'Surface'))
#    levels = Int(10)
#    llow = 1
#    lhigh = 100
#    color_map = String('hot')
#
#    _available_tables = Dict
#    available_tables = Property
#    selected_table = String
#
#    available_groups = List
#    selected_group = String
#
#    # = Bool(True)
#    regress = Bool(True)
#    correct_baseline = Bool(True)
#
#    note = String
#    def __init__(self, *args, **kw):
#        super(DataManager, self).__init__(*args, **kw)
#        self.data_frames = []
#        #self.levelsint = 10
#    def close(self):
#        for df in self.data_frames:
#            df.close()
#        self.data_frames = []
#
#    def flush(self):
#        for df in self.data_frames:
#            df.flush()
#
#    def _get_available_tables(self):
#        tt = [t for t in self._available_tables]
#        tt.sort()
#        return tt
#
#    def filter_select_view(self):
#        cmap_grp = VGroup(Item('color_map', editor = EnumEditor(values = color_map_name_dict.keys())),
#                                Item('levels',
#                                     editor = RangeEditor(mode = 'spinner', low_name = 'llow',
#                                                                        high_name = 'lhigh',
#                                                                        ),
#                                         ),
#                                Item('correct_baseline'),
#                                visible_when = 'available_filters in ["Plot Series","Explorer"]')
#
#        v = View(Item('available_filters', show_label = False),
#               Item('selected_table', show_label = False,
#                    editor = EnumEditor(values = self.available_tables),
#                    visible_when = 'available_filters in ["Power Scan"]',
#                    ),
#                cmap_grp,
#
#               Item('_type', visible_when = 'available_filters=="Beam Profile"'),
#               #Item('editable', visible_when = 'available_filters=="Power Scan"'),
#               Item('regress', visible_when = 'available_filters=="Power Scan"'),
#
#               Item('selected_group',
#                    editor = EnumEditor(values = self.available_groups),
#                    visible_when = 'available_filters=="Power Scan"'),
#               buttons = ['OK', 'Cancel', 'Revert'],
#               title = 'Select Filter',
#               kind = 'livemodal'
#               )
#        return v
#
#    def open_graph(self, filter = None, p = None):
#        import string
#        if p is None:
#            p = self.open_file_dialog()
#
#
#        if p is None:
#            return
#
#        df = openFile(p, 'r')
#        if not filter:
#            self._available_tables = self._get_tables(df)
#            self.available_groups = self._get_groups(df)
#            info = self.edit_traits(view = 'filter_select_view',)
#            if info.result:
#                filter = self.available_filters
#
#                filter = filter.translate(string.maketrans(' ', '_')).lower()
#            else:
#                return
#
#
#        f = getattr(self, filter)
#        f(df, window_title = os.path.basename(p))
#
#    def timeseries(self, df, window_title, **kw):
#        if TimeSeriesGraph is None:
#            from graph.time_series_graph import TimeSeriesGraph
#
#        g = TimeSeriesGraph()
#        #g.plotcontainer.padding_left=40
#        tabs = self._get_tables(df)
#        ag = [None, None, None]
#        rg = [None, None, None]
#
#        for t in tabs:
#
#            id = int(t[5])
#            if id < 3:
#                ag[id] = tabs[t]
#            else:
#                rg[id - 3] = tabs[t]
#
#        gauge_map = ['Ion', 'Backing', 'Tank']
#        for i, ai in enumerate(rg):
#
#            g.new_plot(show_legend = True, bounds = (200, 150))
#            x, y = self.extract_time_series_data(ai)
#            vs = 'linear'
#            kw = dict(x = x, y = y, plotid = i)
#            if i == 0:
#                kw['value_scale'] = 'log'
#            if i == 2:
#                kw['title'] = 'Roughing Pressures'
#
#            g.set_legend_label(gauge_map[i], plotid = i)
#            g.new_series(**kw)
#
#        g.plots[0].value_axis.tick_label_formatter = lambda x: '%0.2e' % x
#
#        g.set_y_limits(min = 1e-10, max = 1)
#        g.set_y_limits(min = 0, max = 1, plotid = 2)
#        g.set_x_title('Time')
#        for i in range(3):
#            g.set_y_title('Pressure (Torr)', plotid = i)
#
#        g.window_width = 500
#        g.window_height = 600
#        g.edit_traits()
#    def pyrometer_calibration_scan(self, df, window_title = '', **kw):
#        if TimeSeriesGraph is None:
#            from graph.time_series_graph import TimeSeriesGraph
#
#        g = TimeSeriesGraph()
#        tabs = self._get_tables(df)
#        x, y = self.extract_time_series_data(tabs['temperature_controller.stream'])
#        g.new_plot(show_legend = True)
#        g.set_x_title('Time')
#        g.set_y_title('Temp (C)')
#        g.new_series(x = x,
#                     y = y,
#                     normalize = True)
#        g.set_legend_label('Thermocouple')
#
#        x, y = self.extract_time_series_data(tabs['pyrometer_tm.stream'])
#        g.new_series(x = x,
#                     y = y, series = 1,
#                     normalize = True
#                     )
#        g.set_legend_label('Pyrometer', series = 1)
#
#        g.new_plot(title = 'Pyrometer Scan (%s)' % window_title)
#        g.set_y_title('Emissivity', plotid = 1)
#        x, y = self.extract_time_series_data(tabs['emissivity.stream'])
#        g.new_series(x = x,
#                     y = y,
#                     normalize = True,
#                     plotid = 1)
#
#
#        g.title = window_title
#
#
#
#        g.add_guide(750, color = (1, 0.4, 0))
#        g.add_guide(850, color = (1, 0.4, 0))
#        g.add_guide(950, color = (1, 0.4, 0))
#
#        g.edit_traits()
#        if ResidualsGraph is None:
#            from graph.residuals_graph import ResidualsGraph
#        rg = ResidualsGraph()
#        rg.new_plot()
#        x = range(5)
#        y = [4, 5, 3, 1, 4]
#        rg.new_series(x = x, y = y)
#
#        rg.title = 'Emissivity Calibration'
#        rg.window_x = 30
#        rg.window_y = 30
#        #rg.edit_traits()
#
#    def power_scan(self, df, window_title = ''):
#        if self.regress:
#            if RegressionGraph is None:
#                from graph.regression_graph import RegressionGraph
#            G = RegressionGraph
#        else:
#            if Graph is None:
#                from graph.graph import Graph
#            G = Graph
#
#        g = G()#show_editor = self.editable)
#        plotinc = 0
#        for group in df.walkGroups('/'):
#            grpname = self._get_group_name(group)
#            if grpname == self.selected_group:
#                for tab in df.listNodes(group, classname = 'Table'):
#                    x = [row['power_requested'] for row in tab]
#                    y = [row['power_achieved'] for row in tab]
#
#                    title = grpname.translate(string.maketrans('_', ' ')).capitalize()
#
#                    g.new_plot(title = title)
#                    g.set_x_title('Power Steps', plotid = plotinc)
#                    g.set_y_title('Power', plotid = plotinc)
#
#                    g.new_series(x = x, y = y, plotid = plotinc)
#                    plotinc += 1
#
#
#        g.title = window_title
#        g.edit_traits()
#
#
#
#
#    def contour_plot_series(self, df, **kw):
#        graph = ContourGraph()
#
#
#        tabs = self._get_tables(df)
#        self._set_plot_series_container(len(tabs), graph)
#        for id, t in enumerate(tabs):
#
#            table = tabs[t]
#            graph.new_plot(title = 'Beam Diam %s (%i)' % (table.attrs.beam_diameter, table.attrs.power_request))
#
#            z = self.extract_power_map_data(table)
#            x, y, z = self.prep_2D_data(z)
#           # st=table.attrs.steps
#            sl = table.attrs.step_len
#            pa = table.attrs.padding
#
#            ra = (-pa, pa)
#
#            plot, names, rd = graph.new_series(x = x, y = y, z = z,
#                          xbounds = ra,
#                          ybounds = ra,
#                          plotid = id, style = 'contour',
#                          cmap = self.color_map,
#                          levels = self.levels,
#                          colorbar = True
#
#                          )
#            graph.set_x_title('mm')
#            graph.set_y_title('mm')
#           # ps.add_line_inspector(plot, color = 'blue')
#          #  ps.add_line_inspector(plot, axis = 'y', color = 'blue')
#        graph.window_height = 600
#        graph.window_width = 600
#        graph.edit_traits()
#
#
#    def explorer(self, df, window_title = '', **kw):
#
#
#        cg = ContourGraph()
#        cg.plotcontainer = cg._container_factory('h')
#
#        stable = self.selected_table
#
#        table = self._get_tables(df)[stable]
#        z = self.extract_power_map_data(table)
#        x, y, z = self.prep_2D_data(z)
#
#
#        bounds = (-table.attrs.padding, table.attrs.padding)
#
#        cplot = cg.new_plot(add = False,
#                            padding_top = 10,
#                            padding_left = 20,
#                            padding_right = 5,
#                            resizable = '',
#                            bounds = [400, 400],
#                          )
#        cplot.index_axis.title = 'mm'
#        cplot.value_axis.title = 'mm'
#
#        cg.new_series(x = x, y = y, z = z, style = 'contour',
#                      xbounds = bounds,
#                      ybounds = bounds,
#                      cmap = self.color_map,
#                      colorbar = True,
#                      levels = self.levels)
#
#        cpolyplot = cplot.plots['plot0'][0]
#        options = dict(style = 'cmap_scatter',
#                     type = 'cmap_scatter',
#                     marker = 'circle',
#                     color_mapper = cpolyplot.color_mapper
#                     )
#
#        p_xaxis = cg.new_plot(add = False,
#                            padding_bottom = 0,
#                            padding_left = 20,
#                            padding_right = 5,
#                            resizable = '',
#                            bounds = [400, 100],
#                            title = 'Power Map'
#                            )
#
#        p_xaxis.index_axis.visible = False
#        p_xaxis.value_axis.title = 'Power (%)'
#        cg.new_series(plotid = 1, render_style = 'connectedpoints')
#        cg.new_series(plotid = 1, **options)
#
#        p_yaxis = cg.new_plot(add = False, orientation = 'v',
#                              padding_left = 0,
#                             # padding_right = 5,
#                              resizable = '',
#                              bounds = [100, 400]
#                             )
#
#        p_yaxis.index_axis.visible = False
#        p_yaxis.value_axis.title = 'Power (%)'
#
#        cg.new_series(plotid = 2, render_style = 'connectedpoints')
#        cg.new_series(plotid = 2, **options)
#
#        ma = max([max(z[i, :]) for i in range(len(x))])
#        mi = min([min(z[i, :]) for i in range(len(x))])
#
#        cg.set_y_limits(min = mi, max = ma, plotid = 1)
#        cg.set_y_limits(min = mi, max = ma, plotid = 2)
#
#        cg.show_crosshairs()
#
#        cpolyplot.index.on_trait_change(cg.metadata_changed,
#                                           'metadata_changed')
#
#        container = cg._container_factory('v',
#                                     resizable = 'hv',
#                                     )
#        container.add(cplot)
#        container.add(p_xaxis)
#
#        cg.plotcontainer.add(container)
#        cg.plotcontainer.add(p_yaxis)
#
#
#
#        cg.plotcontainer.padding_left = 50
#        cg.plotcontainer.padding_top = 50
#       # cg.plotcontainer.request_redraw()
#        cg.window_width = 735
#        cg.window_height = 690
#        cg.title = window_title
#        cg.resizable = False
#        cg.edit_traits()
#
#
#    def extract_time_series_data(self, table):
#        xr = []
#        yr = []
#        for index, row in enumerate(table):
#            xr.append(row['timestamp'])
#            yr.append(row['value'])
#
#        return array(xr), array(yr)
#
#    def extract_power_map_data(self, table):
#
#        cells = []
#
#        for index, row in enumerate(table):
#
#            try:
#                x = int(row['col'])
#            except:
#                x = int(row['x'])
#
#            try:
#                nr = cells[x]
#
#            except:
#                cells.append([])
#
#                nr = cells[x]
#
#            baseline = self.calc_baseline(table, index) if self.correct_baseline else 0.0
#            nr.append(max(row['power'] - baseline, 0))
#
#        return array(cells)
#
#    def calc_baseline(self, table, index):
#
#
#        try:
#            b1 = table.attrs.baseline1
#            b2 = table.attrs.baseline2
#        except:
#            b1 = b2 = 0
##        print b1,b2
#   # ps=[row['power'] for row in table]
#   # b1=ps[0]
#   # b2=ps[-1:][0]
#        size = table.attrs.NROWS - 1
#
#        bi = (b2 - b1) / size * index + b1
#
#        return bi
#
#    def prep_2D_data(self, z):
#        z = transpose(z)
#        mx = float(max(z))
#        z = array([100 * x / mx for x in [y for y in z]])
#
#        r, c = shape(z)
#        x = linspace(0, 1, r)
#        y = linspace(0, 1, c)
#        return x, y, z
#
#    def beam_profile(self, df, **kw):
#        table = self._available_tables[self.selected_table]
#
#        cells = self.extract_power_map_data(table)
#
#        plot = getattr(self, self._type.lower())
#
#        pa = table.attrs.padding
#        ranges = [[-pa, pa], [-pa, pa], [0, 100]]
#        plot(cells, beam_diameter = table.attrs.beam_diameter, ranges = ranges)
#
#    def decorate(self, options):
#        global mlab
#        if mlab is None:
#            from mayavi import mlab
#
#        mlab.axes(xlabel = 'x',
#                  ylabel = 'y',
#                  zlabel = 'power',
#                  ranges = options['ranges'] if options.has_key('ranges') else [0, 10, 0, 10, 0, 10]
#                  )
#
#        if options.has_key('beam_diameter'):
#            mlab.text(0.5, 0.9, 'Beam Diameter %(beam_diameter)i' % options)
#
#
##    @mlab.show
##    def barchart(self, z, **kw):
##
##
##        mlab.barchart(z)
##        self.decorate(kw)
##    @mlab.show
##    def contoursurface(self, z, **kw):
##        c = 25
##        lw = 1
##        mlab.contour_surf(z, contours = c, line_width = lw)
##        self.decorate(kw)
##
##    @mlab.show
##    def contour(self, z, **kw):
##        mlab.contour3d(z)
##        self.decorate(kw)
##
##    @mlab.show
##    def surface(self, z, **kw):
##        mlab.surf(z)
##        self.decorate(kw)
#
#
#
#    def new_frame(self, p, id = None, directory = 'streams', base_frame_name = 'stream'):
#        '''
#            @_type p: C{str}
#            @param p:
#        '''
#        if p is None:
#            base = os.path.join(paths.data_dir, directory)
#            if not os.path.isdir(base):
#                os.mkdir(base)
#
#            p = unique_path(base, base_frame_name, filetype = self.style)
#
#
#        if self.style == 'h5':
#            df = openFile(p, 'w')
#
#        else:
#            df = p
#            f = open(p, 'w')
#            f.close()
#
#        if id is None:
#            self.data_frames.append(df)
#        else:
#            self.data_frames[id] = df
#
#    def record(self, values, table, id = 0):
#        df, ptable = self._get_parent(table, id = id)
#        nr = ptable.row
#
#
#        for key in values.keys():
#            nr.__setitem__(key, values[key])
#
#        nr.append()
#        ptable.flush()
#
#    def add_timestamped_value(self, value, table, id = 0, delimiter = '\t'):
#        '''
#            @_type value: C{str}
#            @param value:
#
#            @_type table: C{str}
#            @param table:
#
#            @_type id: C{str}
#            @param id:
#        '''
#
#        tstamp=generate_timestamp()
#        if self.style == 'h5' and table:
#
#            df, ptable = self._get_parent(table, id = id)
#
#            nr = ptable.row
#            nr['timestamp'] = tstamp
#            nr['value'] = value
#            nr.append()
#            ptable.flush()
#        else:
#
#            #print table,'adsf',self.data_frames
#            p = self.data_frames[id]
#            df = open(p, 'a')
#
#            ti = str(ti)
#            if isinstance(value, tuple):
#
#                value = delimiter.join([str(v) for v in value])
#            else:
#                value = str(value)
#
#            row = delimiter.join((ti, tstamp, value))
#
#
#            df.write(row + '\n')
#            df.close()
#
#    def add_table(self, table, table_style = 'Timestamp', parent = 'root', id = None):
#        '''
#            @_type table: C{str}
#            @param table:
#
#            @_type parent: C{str}
#            @param parent:
#
#            @_type id: C{str}
#            @param id:
#        '''
#        df, pgrp = self._get_parent(parent, id = id)
#
#        alpha = [chr(i) for i in range(65, 91)]
#        s = array([['%s%s' % (b, a) for a in alpha] for b in alpha]).ravel()
#
#        add = True
#        cnt = 0
#        base_table = table
#        while add:
#            try:
#                df.createTable(pgrp, table, table_description_factory(table_style))
#            except NodeError:
#                table = '%s%s' % (base_table, s[cnt])
#                cnt += 1
#                add = True
#            finally:
#                add = False
#
#
#
#        return table
#
#    def add_group(self, group, parent = 'root', id = None):
#        '''
#            @_type group: C{str}
#            @param group:
#
#            @_type parent: C{str}
#            @param parent:
#
#            @_type id: C{str}
#            @param id:
#        '''
#
#        df, pgrp = self._get_parent(parent, id = id)
#        df.createGroup(pgrp, group)
#
#    def add_note(self, note = None):
#        df = self.data_frames[len(self.data_frames) - 1]
#        self._available_tables = self._get_tables(df)
#        info = self.edit_traits(view = 'note_view')
#        if info.result:
#            table = self._get_tables(df)[self.selected_table]
#            setattr(table.attrs, 'note', self.note)
#
#    def note_view(self):
#        return View(Item('note', style = 'custom', show_label = False),
#                    Item('selected_table', show_label = False,
#                                editor = EnumEditor(values = self.available_tables)),
#                    buttons = ['OK', 'Cancel'],
#                    kind = 'modal'
#                    )
#    def build_table(self, path, **kw):
#        '''
#        path format  root.grpname...tablename
#        '''
#        args = path.split('.')
#
#        table = args[-1:][0]
#        parent = 'root'
#        for gi in args[1:-1]:
#
#            self.add_group(gi, parent = parent)
#            parent = '%s.%s' % (parent, gi)
#
#        self.add_table(table, parent = parent, **kw)
#
#    def set_table_attribute(self, key, value, table):
#        df, table = self._get_parent(table)
#
#        setattr(table.attrs, key, value)
#
#    def _set_plot_series_container(self, ntabs, graph):
#        s = math.sqrt(ntabs)
#        rows = math.floor(s)
#        cols = rows
#        if rows * rows < ntabs:
#            cols = rows + 1
#            if cols * rows < ntabs:
#                rows += 1
#
#        graph.plotcontainer = graph._container_factory('g', shape = (rows, 2 * cols))
#
#    def _get_group_name(self, group):
#        s = group.__str__()
#        p, c, d = s.split(' ')
#        return p.split('/')[-1:][0]
#
#    def _get_parent(self, parent, df = None, id = None):
#        '''
#            @_type parent: C{str}
#            @param parent:
#
#            @_type df: C{str}
#            @param df:
#
#            @_type id: C{str}
#            @param id:
#        '''
#        if not df:
#
#            if id is None:
#                id = len(self.data_frames) - 1
#
#            try:
#                df = self.data_frames[id]
#            except IndexError:
#                df = self.data_frames[0]
#
#        p = parent.split('.')
#        pgrp = None
#        prev_obj = None
#        for i, pi in enumerate(p):
#            if i == 0:
#                obj = df
#            else:
#                obj = prev_obj
#
#            pgrp = getattr(obj, pi)
#            prev_obj = pgrp
#
#        return df, pgrp
#
#    def _get_tables(self, df):
#        names = []
#        tabs = {}
#
#        for group in df.walkGroups('/'):
#
#            grpname = self._get_group_name(group)
#            for table in df.listNodes(group, classname = 'Table'):
#                name = '%s.%s' % (grpname, table.name)
#                tabs[name] = table
#                names.append(name)
#
#        self.selected_table = names[0]
#        return tabs
#
#    def _get_groups(self, df):
#        grps = df.root._v_groups.keys()
#        self.selected_group = grps[0]
#        return grps
##    def load_from_file(self, p, table):
##        '''
##            @_type p: C{str}
##            @param p:
##
##            @_type table: C{str}
##            @param table:
##        '''
##        if not table:
##            table = 'root.streams.gauge1_pressure'
##        
##        
##        df = tables.openFile(p, 'r')
##
##        df, table = self._get_parent(table, df = df)
##        y = [r[1] for i, r in enumerate(table) if i % 50 == 0]
##        x = [r[0] for i, r in enumerate(table) if i % 50 == 0]
##
##        return x, y
#       # self.new_graph(x, y):
##    def new_graph(self, x, y):
##        '''
##            @_type x: C{str}
##            @param x:
##
##            @_type y: C{str}
##            @param y:
##        '''
##        
##        g = DateGraph(show_editor = True)
##
##
##        g.new_plot(pan = True, zoom = True)
##        g.new_series(x = x, y = y)
##        #g.refresh_editor()
##        g.configure_traits()
##        
##    def new_graphs(self, xs, ys):
##        '''
##            @_type xs: C{str}
##            @param xs:
##
##            @_type ys: C{str}
##            @param ys:
##        '''
##       # from graph.date_graph import DateGraph
##        g = DateGraph(show_editor = True)
##        for i, xi in enumerate(xs):
##            yi = ys[i]
##            g.new_plot(pan = True, zoom = True)
##            g.new_series(xi, yi, plotid = i)
##
##        g.configure_traits()
