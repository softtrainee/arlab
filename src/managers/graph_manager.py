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
from traits.api import File, Str, Directory
from traitsui.api import View, Item, EnumEditor
#============= standard library imports ========================
import csv
import numpy as np
import os
#============= local library imports  ==========================
from src.graph.graph import Graph
#from src.graph.stacked_graph import StackedGraph
from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.graph.residuals_graph import ResidualsGraph
from src.data_processing.power_mapping.power_map_processor import PowerMapProcessor
from src.helpers.paths import data_dir
from manager import Manager
from src.envisage.core.envisage_editor import EnvisageEditor

KIND_VALUES = dict(peak_center='Peak Center',
                   powermap='Power Map',
                   xy='XY',
                   deflection='Deflection',
                   step_heat='Step Heat'
                   )
class GraphManager(Manager):
    path = File
    root = Directory
    kind = Str('deflection')
    def open_graph(self, kind, path=None):

        pfunc = getattr(self, '{}_parser'.format(kind))

        gfunc = getattr(self, '{}_factory'.format(kind))

        if path is None:
            path = self.open_file_dialog(default_directory=data_dir)


        if path is not None and os.path.exists(path):
            args = pfunc(path)
            if args[0] is not None:
                graph = gfunc(*args)
                graph.name = os.path.basename(path)
                if self.application is not None:
                    self.application.workbench.edit(graph,
                                                    kind=EnvisageEditor)
                else:
                    graph.edit_traits()
#===============================================================================
# parsers
#===============================================================================
    def powerscan_parser(self, path):
        xs = [1, 2, 3, 4, 5]
        ys = [3, 4, 10, 11, 14]

        title = 'adfasf'
        return xs, ys, title
    def peak_center_parser(self, path):
        data, title = self._default_xy_parser(path)
        xs = []
        ys = []
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                if line[0].startswith('#'):
                    xs.append(float(line[0][1:]))
                    ys.append(float(line[1]))

        minmaxdata = None
        if xs:
            minmaxdata = np.array((xs, ys))
        return data, minmaxdata, title

    def deflection_parser(self, path):
        return self._default_xy_parser(path)

    def powermap_parser(self, path):
        title = 'Graph'
        if path is None:
            path = self.open_file_dialog()
            title = os.path.basename(path)

        return path, title

    def xy_parser(self, path):
        return self._default_xy_parser(path)

    def step_heat_parser(self, path):
        title = '{}'.format(os.path.basename(path))

        tt_data, _atitle = self._default_xy_parser(os.path.join(path, 'time_vs_temp.csv'),

                                             )
        ra_data, _btitle = self._default_xy_parser(os.path.join(path, 'request_vs_actual.csv'),
                                              )

        return tt_data, ra_data, title

#===============================================================================
# factories
#===============================================================================
    def powerscan_factory(self, xs, ys, title):
        g = Graph()
        return g


    def step_heat_factory(self, ttdata, radata, title):
        g = TimeSeriesStreamGraph()
        g.new_plot(xtitle='Time',
                   ytitle='Temp C',
                   link=False,
                   data_limit=300,
                   scan_delay=1,
                   padding_top=10,
                   padding_left=20,
                   padding_right=10
                   )


        g.new_series(x=ttdata[0], y=ttdata[1])
        g.new_series(x=ttdata[0], y=ttdata[2])
        g.new_plot(xtitle='Request Temp C',
                   ytitle='Temp C',
                   link=False,
                   data_limit=50,
                   padding_top=10,
                   padding_left=20,
                   padding_right=10
                   )

        g.new_series(x=radata[0], y=radata[1], plotid=1, time_series=False)
        g.new_series(x=radata[0], y=radata[2], plotid=1, time_series=False)

        g.set_x_limits(min=min(radata[0]) - 5, max=max(radata[0]) + 5, plotid=1)
        g.name = title
        return g

    def xy_factory(self, data, title):
        g = self.graph_factory(
                               data=data,
                               graph_kwargs=dict(window_title=title),
                               plot_kwargs=dict(xtitle='X', ytitle='Y'),
                               series_kwargs={}
                               )
        return g

    def peak_center_factory(self, data, minmaxdata, title):
        '''
            the centering info should written as metadata instead of recalculating it
        '''
        plot_kwargs = dict(xtitle='Magnet DAC (V)',
                           ytitle='Intensity (fA)'
                           )
        g = self.graph_factory(data=data, graph_kwargs=dict(window_title=title),
                                    plot_kwargs=plot_kwargs,
                                    series_kwargs=dict()

                               )
        if minmaxdata is not None:
            g.new_series(x=minmaxdata[0], y=minmaxdata[1], type='scatter')

        return g

    def deflection_factory(self, data, title):
        graph_kwargs = dict(
                           container_dict=dict(padding=[20, 5, 15, 15]),
                           window_height=700,
                           window_title=title
                           )

        plot_kwargs = dict(padding_top=15,
                           padding_right=15,
                           xtitle='Deflection (V)',
                           ytitle='40Ar Peak Center (Magnet DAC V)'
                           )
        g = self.residuals_factory(data, graph_kwargs=graph_kwargs,
                                         plot_kwargs=plot_kwargs,
                                         series_kwargs={})
        return g

    def powermap_factory(self, data, title):
        '''
            data is a path in this case 
            let a PowerMapProcessor do all the work
        '''

        with open(data, 'r') as f:
            pmp = PowerMapProcessor()
            reader = csv.reader(f)
            #trim off header
            reader.next()
            return pmp.load_graph(reader)

    def residuals_factory(self, *args, **kw):

        klass = ResidualsGraph
        g = self._graph_factory(klass, *args, **kw)
        return g

    def graph_factory(self, *args, **kw):

        klass = Graph
        g = self._graph_factory(klass, *args, **kw)
        return g

    def _graph_factory(self, klass, data=None, graph_kwargs=None, plot_kwargs=None, series_kwargs=None):
        if graph_kwargs is None:
            graph_kwargs = {}

        g = klass(**graph_kwargs)
        if plot_kwargs is not None:
            g.new_plot(**plot_kwargs)
            if series_kwargs is not None:
                if data is not None:
                    g.new_series(x=data[0], y=data[1], **series_kwargs)
                else:
                    g.new_series(**series_kwargs)
        return g

#===============================================================================
# private
#===============================================================================
    def _dir_and_name_title(self, path):
        root, tail = os.path.split(path)
        root, bdir = os.path.split(root)
        return '{}/{}'.format(bdir, tail)

    def _default_xy_parser(self, path, **kw):
        _rheader, data = self._get_csv_data(path, **kw)
        return data, self._dir_and_name_title(path)

    def _get_csv_data(self, path, header=True, unpack=True, delimiter=',', **kw):
        rheader = None
        data = None
        if path is None:
            path = self.open_file_dialog(default_directory=data_dir)

        if path is not None:
            with open(path, 'r') as f:
                if header:
                    rheader = f.readline()

                data = np.loadtxt(f, delimiter=delimiter, unpack=unpack, **kw)

        return rheader, data

#    def open_power_scan_graph(self):
#        p = self._file_dialog_('open')
#        if p is not None:
#            with open(p, 'r') as f:
#                g = StackedGraph()
#                reader = csv.reader(f)
#                info = []
#                data = []
#                curplotid = 0
#                g.new_plot(show_legend = True)
#                for line in reader:
#                    if line[0].startswith('#==='):
#                        if not 'plot metadata' in line[0]:
#                            break
#                        else:
#                            continue
#                    name = line[0][1:]
#                    plotid = int(line[1])
#                    series = int(line[2])
#                    if plotid != curplotid:
#                        curplotid = plotid
#                        g.new_plot(show_legend = True)
#
#                    g.new_series(render_style = 'connectedpoints', plotid = curplotid)
#                    g.set_legend_label(name, series = series, plotid = curplotid)
#                    info.append((name, plotid, series))
#                    data.append([])
#
#                header = reader.next()
#                xs = []
#                for line in reader:
#                    x = float(line[1])
#                    xs.append(x)
#                    for i in range(len(header) - 2):
#                        data[i].append(float(line[i + 2]))
#
#                for i, da in enumerate(data):
#                    plotid = info[i][1]
#                    series = info[i][2]
#                    g.set_data(xs, plotid = plotid, series = series)
#                    g.set_data(da, axis = 1, plotid = plotid, series = series)
#                g.edit_traits()


    def _path_changed(self):
        self.open_graph(self.kind, self.path)

    def _root_changed(self):
        self.open_graph(self.kind, self.root)
#    def _test_fired(self):
#        kind = 'peak_center'
#        path = '/Users/Ross/Pychrondata_beta/data/magfield/def_calibration009/peak_scan_100.0.csv'
#        kind = 'powermap'
#        path = '/Users/Ross/Pychrondata_beta/data/powermap/beam00_001.txt'
#
#        kind = 'xy'
#        path = '/Users/Ross/Pychrondata_beta/data/magfield/def_calibration009/peak_scan_100.0.csv'
#
#        self.open_graph(self.kind, self.path)

        #self.application.workbench.edit()


    def traits_view(self):
        v = View(
                 #Item('test'),
                 Item('kind', editor=EnumEditor(values=KIND_VALUES)),
                 Item('path', visible_when='kind not in ["step_heat"]'),
                 Item('root', label='Path', visible_when='kind in ["step_heat"]')
                 )
        return v
if __name__ == '__main__':
    g = GraphManager()
    g.configure_traits()
#============= EOF =============================================
