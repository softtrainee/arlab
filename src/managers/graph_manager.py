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
from traits.api import File, Str, Directory, List
from traitsui.api import View, Item, EnumEditor
from chaco.api import ArrayDataSource
#============= standard library imports ========================
import csv
from numpy import array, loadtxt
import os
#============= local library imports  ==========================
from src.graph.graph import Graph
#from src.graph.stacked_graph import StackedGraph
from src.helpers.paths import data_dir
from manager import Manager
from matplotlib.dates import datestr2num
from src.data_processing.time_series.time_series import downsample_1d, smooth
from src.graph.time_series_graph import TimeSeriesGraph
import dateutil
import time
from datetime import datetime
KIND_VALUES = dict(
                   tempmonitor='Temp Monitor',
                   bakeout='Bakeout',
                   degas='Degas',
                   peak_center='Peak Center',
                   powermap='Power Map',
                   xy='XY',
                   deflection='Deflection',
                   step_heat='Step Heat',
                   powerrecord='Power Record'

                   )


class GraphManager(Manager):
    path = File
    root = Directory
    kind = Str('deflection')

    extension_handlers = List

    def _test_fired(self):
#        self.open_graph('degas', path='/Users/Ross/Pychrondata_beta/data/degas/scan001.txt')
        self.open_graph('tempmonitor', path='/Users/ross/Desktop/argus_temp_monitor046.txt')
#        self.open_graph('inverse_isochron', path='/Users/Ross/Desktop/data.csv')
        #self.open_graph('age_spectrum', path='/Users/Ross/Desktop/test.csv')

    def open_graph(self, kind, path=None):
        get_pfunc = lambda c, k:getattr(c, '{}_parser'.format(k))
        get_gfunc = lambda c, k:getattr(c, '{}_factory'.format(k))
        pfunc = None
        try:
            pfunc = get_pfunc(self, kind)
            gfunc = get_gfunc(self, kind)
        except AttributeError:

            for eh in self.extension_handlers:
                try:
                    pfunc = get_pfunc(eh, kind)
                    gfunc = get_gfunc(eh, kind)
                except AttributeError:
                    raise NotImplementedError('no parser or factory for {}'.format(kind))
            if not pfunc:
                raise NotImplementedError('no parser or factory for {}'.format(kind))

#        print pfunc, gfunc
        if path is None:
            path = self.open_file_dialog(default_directory=data_dir)

#        print path
        if path is not None and os.path.exists(path):
            args = pfunc(path)
#            print args
            if args[0] is not None:
                graph = gfunc(*args)
                graph.name = os.path.basename(path)
#                print graph
                if self.application is not None:
                    from src.envisage.core.envisage_editor import EnvisageEditor
                    self.application.workbench.edit(graph,
                                                    kind=EnvisageEditor)
                else:
                    graph.edit_traits()
#===============================================================================
# parsers
#===============================================================================
    def _scan_parser(self, path, nargs=2, normalize=True, downsample=False, zero_filter=False):

        converters = {0:lambda x: time.mktime(dateutil.parser.parse(x).timetuple())}
        args = loadtxt(path,
                       converters=converters,
                       delimiter=',', unpack=True)
        if nargs == 2:
            x, y = args
        else:
            t, x, y = args

        if downsample:
            x = downsample_1d(x, factor=downsample)
            y = downsample_1d(y, factor=downsample)

        if normalize:
            #normalize to 0 
            x = [(xi - x[0]) * 3600 * 24 for xi in x]
        else:
            x = t

        if zero_filter:
            args = zip(x, y)
            args = [(xi, yi) for xi, yi in args if yi > 0]
            x, y = zip(*args)

        return x, y, path

    def powerrecord_parser(self, path):
        return self._scan_parser(path)

    def tempmonitor_parser(self, path):
        return self._scan_parser(path, nargs=3, normalize=False,
                                 zero_filter=True,
                                 downsample=500)

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
            minmaxdata = array((xs, ys))
        return data, minmaxdata, title

    def degas_parser(self, path):
        f = open(path, 'r')

        metadata = self.read_metadata(f)
        data = loadtxt(f, delimiter=',', unpack=True)

        title = 'foo'
        f.close()

        return data, metadata, title

    def read_metadata(self, fobj, delimiter=','):
        m = []
        for l in fobj:
            l = l.split(delimiter)
            if l[0].startswith('#') and '#=====' not in l[0]:

                try:
                    m.append((l[0][1:], int(l[1]), int(l[2])))
                except ValueError:
                    #this it the header do really need it currently
                    pass

            if l[0].strip() == '#====================================':
                break

        return m

    def deflection_parser(self, path):
        return self._default_xy_parser(path)

    def powermap_parser(self, path):
#        title = 'Graph'
#        if path is None:
#            path = self.open_file_dialog()
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

    def age_spectrum_parser(self, path):
        '''
            return 2 lists of tuples 
            x= [(start39, end39), ...]
            y=[(age,error),...]
        '''
        ar39signals = [0.1, 3, 0.25, 0.1]

        ages = [5, 4, 3, 2, 1]
        errors = [0.25, 0.25, 0.25, 0.25]

        total39 = sum(ar39signals)
        x = []

        start = 0
        end = 0
        nages = []
        nerrors = []
        for ai, ei, si in zip(ages, errors, ar39signals):
            end += si / total39
            x.append((start, end))
            start = end
            nages.append(ai)
            nerrors.append(ei)
            nages.append(ai)
            nerrors.append(ei)
        return x, zip(nages, nerrors), 'foo'

    def inverse_isochron_parser(self, path):
        '''
            inverse isochron
            39/40 vs 36/40
        '''
        rheader, data = self._get_csv_data(path)


        rheader = rheader.strip().split(',')
        ar40signals = array(data[rheader.index('Ar40_')])
        ar40signals_er = array(data[rheader.index('Ar40_Er')])
        ar39signals = array(data[rheader.index('Ar39_')])
        ar39signals_er = array(data[rheader.index('Ar39_Er')])
        ar36signals = array(data[rheader.index('Ar36_')])
        ar36signals_er = array(data[rheader.index('Ar36_Er')])


#        ar39signals = array([3.3, 3.35, 3.2, 3.0])
#        
#        ar40signals = array([4.3, 4.35, 4.2, 4.0])
#        ar36signals = ar40signals * array([1 / 300.1, 1 / 303.1, 1 / 299.1, 1 / 305.1])
#        

        v1 = ar40signals
        e1 = ar40signals_er
        v2 = ar39signals
        e2 = ar39signals_er

        err = lambda v1, e1, v2, e2:(((e1 / v1) ** 2 + (e2 / v2) ** 2) ** 0.5) * (v2 / v1)
        xers = err(v1, e1, v2, e2)

        v2 = ar36signals
        e2 = ar36signals_er
        yers = err(v1, e1, v2, e2)
        return ar39signals / ar40signals, ar36signals / ar40signals, xers, yers, 'foo'

#===============================================================================
# factories
#===============================================================================
    def tempmonitor_factory(self, xs, ys, path):
        name = os.path.splitext(os.path.basename(path))[0]
        g = self._graph_factory(TimeSeriesGraph, data=(xs, ys), graph_kwargs={'window_title':path},
                                  series_kwargs={},
                                  plot_kwargs=dict(xtitle='time (s)',
                                               ytitle='temp',
                                               title='Time vs Temp ({})'.format(name) ,
                                               )
                                  )
#        xsm = smooth(xs)
        ysm = smooth(ys)
        g.new_series(xs, ysm)
        return g

    def inverse_isochron_factory(self, xs, ys, xers, yers, title):
        from src.graph.regression_graph import RegressionGraph
        g = RegressionGraph(show_regression_editor=False)

        g.new_plot()
        _plot, scatter, _line = g.new_series(x=xs, y=ys, marker='pixel')

        from src.graph.error_ellipse_overlay import ErrorEllipseOverlay
        scatter.overlays.append(ErrorEllipseOverlay())
        scatter.xerror = ArrayDataSource(xers)
        scatter.yerror = ArrayDataSource(yers)

        g.set_x_limits(0.125, 0.15)
        g.set_y_limits(0, 0.0035)
        return g

    def age_spectrum_factory(self, xs, ys, title):
        g = Graph()
        g.new_plot(xtitle='Cum. 39Ark',
                   ytitle='Age (Ma)',
                   title=title)

        x = []
        for xi in xs:
            x.append(xi[0])
            x.append(xi[1])
        y = [y[0] for y in ys]

        g.new_series(x=x, y=y)
#                     , render_style='connectedhold')

        ox = x[:]
        x.reverse()
        xp = ox + x

        yu = [yi[0] + yi[1] for yi in ys]

        yl = [yi[0] - yi[1] for yi in ys]
        yl.reverse()

        yp = yu + yl
        g.new_series(x=xp, y=yp, type='polygon',
                     color='orange',
                     )

        lpad = 2
        upad = 2
#        g.set_y_limits(0, 10)
        g.set_y_limits(min(y) - lpad, max(y) + upad)
        return g

    def powerrecord_factory(self, xs, ys, path):
        name = os.path.splitext(os.path.basename(path))[0]
        return self.graph_factory(data=(xs, ys), graph_kwargs={'window_title':path},
                                  series_kwargs={},
                                  plot_kwargs=dict(xtitle='time (s)',
                                               ytitle='8bit power',
                                               title='Time vs Power ({})'.format(name) ,
                                               )
                                  )


    def powerscan_factory(self, xs, ys, title):
        g = Graph()
        return g

    def step_heat_factory(self, ttdata, radata, title):
        from src.graph.time_series_graph import TimeSeriesStreamGraph

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

    def degas_factory(self, data, metalist, title):

        g = self.stream_stacked_factory(data=data, graph_kwargs=dict(window_title=title),
                               #plot_kwargs=None,
                               #series_kwargs=None
                               )
        curplot = 0
        g.new_plot()
        g.new_series(x=data[0], y=data[1])

        mi = min(data[1])
        ma = max(data[1])
        g.set_y_limits(mi, ma, pad='0.1')


        for i, mi in enumerate(metalist):
            x = data[0]
            y = data[2 + i]
            if mi[1] == curplot:
                g.new_series(x=x, y=y, plotid=curplot)
            else:
                g.new_plot()
                g.new_series(x=x, y=y)
                curplot += 1

            mi = min(y)
            ma = max(y)


            g.set_y_limits(mi, ma, pad='0.1', plotid=curplot)
        g.set_x_limits(min(data[0]), max(data[0]))

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
        from src.data_processing.power_mapping.power_map_processor import PowerMapProcessor

        with open(data, 'r') as f:
            pmp = PowerMapProcessor()
            reader = csv.reader(f)
            #trim off header
            reader.next()
            return pmp.load_graph(reader)

    def stream_stacked_factory(self, *args, **kw):
        from src.graph.stream_graph import StreamStackedGraph
        return self._graph_factory(StreamStackedGraph, *args, **kw)

    def residuals_factory(self, *args, **kw):
        from src.graph.residuals_graph import ResidualsGraph

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
            with open(path, 'U') as f:
                if header:
                    rheader = f.readline()
                data = loadtxt(f, delimiter=delimiter, unpack=unpack, **kw)
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
        print self.path
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
                 Item('test'),
                 Item('kind', editor=EnumEditor(values=KIND_VALUES)),
                 Item('path', visible_when='kind not in ["step_heat"]'),
                 Item('root', label='Path', visible_when='kind in ["step_heat"]')
                 )
        return v
if __name__ == '__main__':
    g = GraphManager(kind='tempmonitor')
    g.configure_traits()
#============= EOF =============================================
