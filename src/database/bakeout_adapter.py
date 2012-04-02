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
from src.database.core.database_adapter import DatabaseAdapter
from src.database.pychron_orm import Analyses, Paths, Intercepts, \
     AnalysisTypes, Spectrometers
from src.database.bakeout_orm import BakeoutTable, ControllerTable, PathTable

from traits.api import HasTraits, Str, Button, List, Any, Long, Event, \
    Date, Time, Instance, Dict
from traitsui.api import View, Item, TabularEditor, EnumEditor, HGroup
from traitsui.tabular_adapter import TabularAdapter

from datetime import datetime, timedelta
import numpy as np

from src.helpers.datetime_tools import get_datetime, get_date

from wx import GetDisplaySize
from src.graph.graph import Graph
from src.graph.time_series_graph import TimeSeriesStackedGraph
import os
from src.loggable import Loggable
DISPLAYSIZE = GetDisplaySize()

class DBResult(HasTraits):
    id = Long
    _db_result = Any

    rundate = Date
    runtime = Time

    directory = Str
    filename = Str
    window_x = 0.1
    window_y = 0.1
    title = Str

    graph = Instance(Graph)



    def _bakeout_h5_parser(self, path):
        from src.managers.data_managers.h5_data_manager import H5DataManager
        dm = H5DataManager()
        if not dm.open_data(path):
            return

        controllers = dm.get_groups()
        datagrps = []
        attrs = []
        ib = [0, 0, 0]
        for ci in controllers:

            attrs_i = dict()
            for ai in ['script', 'setpoint', 'duration', 'script_text']:
                attrs_i[ai] = getattr(ci._v_attrs, ai)
            attrs.append(attrs_i)
            data = []
            for i, ti in enumerate(['temp', 'heat']):
                try:
                    table = getattr(ci, ti)
                    xs = [x['time'] for x in table]
#                    print 'xs', xs
                    ys = [x['value'] for x in table]
                    if i == 0:
                        data.append(xs)
                    data.append(ys)
                    ib[i] = 1
                except Exception, e:
                    print 'bakeout_manager._bakeout_h5_parser', e

            if data:
                datagrps.append(data)

        names = [ci._v_name for ci in controllers]
        nseries = len(controllers) * sum(ib)
        return names, nseries, ib, np.array(datagrps), path, attrs

    def _bakeout_csv_parser(self, path):
        import csv
        attrs = None
        with open(path, 'r') as f:
#            reader = csv.reader(open(path, 'r'))
            reader = csv.reader(f)

            # first line is the include bits
            l = reader.next()
            l[0] = (l[0])[1:]
#
            ib = map(int, l)

            # second line is a header
            header = reader.next()
            header[0] = (header[0])[1:]
            nseries = len(header) / (sum(ib) + 1)
            names = [(header[(1 + sum(ib)) * i])[:-5] for i in range(nseries)]

#            average load time for 2MB file =0.42 s (n=10)
#            data = np.loadtxt(f, delimiter=',')

#            average load time for 2MB file = 0.19 s (n=10)
            data = np.array([r for r in reader], dtype=float)

            data = np.array_split(data, nseries, axis=1)
        return (names, nseries, ib, data, path, attrs)

    def _load_graph(self, path):

        ish5 = True if path.endswith('.h5') else False

        if ish5:
            args = self._bakeout_h5_parser(path)
        else:
            args = self._bakeout_csv_parser(path)

        if args is None:
            return
#        names = args[0]
#        attrs = args[-1]
        self.graph = self._bakeout_graph_factory(ph=0.65,
                *args,
                container_dict=dict(
                                    #bgcolor='red',
                                    #fill_bg=True,
                                    padding_top=60
                                    ),
                transpose_data=not ish5
                )

    def _graph_factory(
        self,
        include_bits=None,
        panel_height=None,
        plot_kwargs=None,
        **kw
        ):

        if plot_kwargs is None:
            plot_kwargs = dict()

        if include_bits is None:
            include_bits = [self.include_temp, self.include_heat,
                            self.include_pressure]

        n = max(1, sum(map(int, include_bits)))
#        if graph is None:
        if panel_height is None:
            panel_height = DISPLAYSIZE.height * 0.65 / n

        graph = TimeSeriesStackedGraph(panel_height=panel_height,
                                        **kw)

        graph.clear()
        #kw['data_limit'] = self.scan_window * 60 / self.update_interval
        #kw['scan_delay'] = self.update_interval

        self.plotids = [0, 1, 2]

        # temps

        if include_bits[0]:
            graph.new_plot(show_legend='ll', **kw)
            graph.set_y_title('Temp (C)')
        else:
            self.plotids = [0, 0, 1]

        # heat power

        if include_bits[1]:
            graph.new_plot(**kw)
            graph.set_y_title('Heat Power (%)', plotid=self.plotids[1])
        elif not include_bits[0]:
            self.plotids = [0, 0, 0]
        else:
            self.plotids = [0, 0, 1]

        # pressure

#        if include_bits[2]:
#            graph.new_plot(**kw)
#            graph.set_y_title('Pressure (torr)', plotid=self.plotids[2])
#
#        if include_bits:
#            graph.set_x_title('Time')
#            graph.set_x_limits(0, self.scan_window * 60)

        return graph

    def _bakeout_graph_factory(
        self,
#        header,
        names,
        nseries,
        include_bits,
        data,
        path,
        attrs,
        ph=0.5,
        transpose_data=True,
        ** kw
        ):

        ph = DISPLAYSIZE.height * ph / max(1, sum(include_bits))

        graph = self._graph_factory(stream=False,
                                    include_bits=include_bits,
                                    panel_height=ph,
                                    plot_kwargs=dict(pan=True, zoom=True),
                                     **kw)
        plotids = self.plotids
#        print names, nseries, include_bits
#        for i in range(nseries / sum(include_bits)):
#            print i
            # set up graph
#            name = names[i]#[i / sum(include_bits)]
        for i, name in enumerate(names):
            for j in range(3):
                if include_bits[j]:
                    graph.new_series(plotid=plotids[j])
                    graph.set_series_label(name, series=i,
                                           plotid=plotids[j])

        ma0 = -1
        mi0 = 1e8
        ma1 = -1
        mi1 = 1e8
        ma2 = -1
        mi2 = 1e8
#        print data
        for (i, da) in enumerate(data):

            if transpose_data:
                da = np.transpose(da)

            x = da[0]
            if include_bits[0]:
                y = da[1]
                ma0 = max(ma0, max(y))
                mi0 = min(mi0, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[0])
                graph.set_data(da[1], series=i, axis=1,
                               plotid=plotids[0])
                graph.set_y_limits(mi0, ma0, pad='0.1',
                                   plotid=plotids[0])

            if include_bits[1]:
                y = da[2]
                ma1 = max(ma1, max(y))
                mi1 = min(mi1, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[1])
                graph.set_data(y, series=i, axis=1, plotid=plotids[1])
                graph.set_y_limits(mi1, ma1, pad='0.1',
                                   plotid=plotids[1])

            if include_bits[2]:
                y = da[3]
                ma2 = max(ma2, max(y))
                mi2 = min(mi2, min(y))
                graph.set_data(x, series=i, axis=0, plotid=plotids[2])
                graph.set_data(y, series=i, axis=1, plotid=plotids[2])
                graph.set_y_limits(mi2, ma2, pad='0.1',
                                   plotid=plotids[2])

                # prevent multiple pressure plots

                include_bits[2] = False

        graph.set_x_limits(min(x), max(x))
#        (name, _ext) = os.path.splitext(name)
#        graph.set_title(name)
        return graph

    def load_graph(self):
        self._load_graph(os.path.join(self.directory,
                                      self.filename
                                      ))

    def load(self):
        dbr = self._db_result
        if dbr is not None:
            self.id = dbr.id
            self.rundate = dbr.rundate
            self.runtime = dbr.runtime
            p = dbr.path
            if p is not None:
                self.directory = p.root
                self.filename = p.filename



            self.title = 'Bakeout {}'.format(self.id)

    def traits_view(self):
        return View(
                    Item('id', style='readonly', label='ID'),
                    Item('rundate', style='readonly', label='Run Date'),
                    Item('runtime', style='readonly', label='Run Time'), # enabled_when='0',)
                    Item('directory', style='readonly'),
                    Item('filename', style='readonly'),
                    Item('graph', show_label=False, style='custom'),

                    width=600,
                    height=300,
                    resizable=True,
                    x=self.window_x,
                    y=self.window_y,
                    title=self.title
                    )


class DBResultsAdapter(TabularAdapter):
    columns = [('ID', 'id')]

COMPARISONS = dict(num=['=', '<', '>', '<=', '>='],
                   negative_num=['=', '<', '<=']
                   )
COMPARATOR_TYPE = {'id':'num',
                    'this month':'negative_num'
                    }


class DBSelector(Loggable):
    parameter = Str('rundate')
    comparator = Str('=')
    _comparisons = List(COMPARISONS['num'])
    criteria = Str('this month')

    execute = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any

    wx = 0.5
    wy = 0.5
    opened_windows = Dict

    def _dclicked_fired(self):
        s = self.selected

        if s is not None:
            if s.id in self.opened_windows:
                self.opened_windows[s.id].control.Raise()
            else:
                s.load_graph()
                s.window_x = self.wx
                s.window_y = self.wy

                info = s.edit_traits()
                self.opened_windows[s.id] = info

                self.wx += 0.005
                self.wy += 0.03

                if self.wy > 0.65:
                    self.wx = 0.5
                    self.wy = 0.5

    def _parameter_changed(self):
        c = COMPARATOR_TYPE[self.parameter]
        self._comparisons = COMPARISONS[c]

    def _criteria_changed(self):
        try:
            c = COMPARATOR_TYPE[self.criteria]
            self._comparisons = COMPARISONS[c]
        except KeyError, _:
            pass

    def _get_filter_str(self):
        if self.parameter == 'rundate':
            c = self.criteria.replace('/', '-')
            if self.criteria == 'today':
                c = get_date()
            elif self.criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if self.comparator == '=':
                    d = d - timedelta(days=d.day)
                    c = '{}{}"{}" AND {}{}"{}"'.format(self.parameter,
                                                   '>=',
                                                   d,
                                                   self.parameter,
                                                   '<=',
                                                   today
                                                   )

                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '"{}"'.format(c)
        else:
            c = self.criteria

        s = ''.join((self.parameter,
                   self.comparator,
                   c))
        return s

    def _execute_fired(self):
        self._execute()

    def _execute_(self):
        self.results = []
        db = self._db
        if db is not None:
            s = self._get_filter_str()
            dbs = db.get_bakeouts(filter_str=s)
            self.info('query {} returned {} results'.format(s,
                                    len(dbs) if dbs else 0))
            if dbs:
                for di in dbs:
                    d = DBResult(_db_result=di)
                    d.load()
                    self.results.append(d)

    def traits_view(self):

        qgrp = HGroup(
                Item('parameter'),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )

        editor = TabularEditor(adapter=DBResultsAdapter(),
                               dclicked='object.dclicked',
                               selected='object.selected'
                               )
        v = View(

                 Item('results', style='custom',
                      editor=editor,
                      show_label=False
                      ),
                 qgrp,
                 Item('execute'),

                 resizable=True,
                 width=500,
                 height=500,
                 x=0.1,
                 y=0.1,
                 title='Recall'
                 )
        return v


class BakeoutAdapter(DatabaseAdapter):
    test_func = None
#===============================================================================
#    getters
#===============================================================================

    def get_bakeouts(self, filter_str=None):
        try:
            q = self._get_query(BakeoutTable, filter_str=filter_str)
            return q.all()
        except Exception:
            pass

#    def get_analyses_path(self):
##        sess = self.get_session()
##        q = sess.query(Paths)
##        s = q.filter_by(name='analyses')
#        q = self._get_query(Paths, name='analyses')
#        p = q.one()
#        p = p.path
#        return p
#
#    def get_intercepts(self, analysis_id):
#        q = self._get_query(Intercepts, analysis_id=analysis_id)
#        return q.all()
#
#    def get_analysis_type(self, **kw):
#        q = self._get_query(AnalysisTypes, **kw)
#        return q.one()
#
#    def get_spectrometer(self, **kw):
#        q = self._get_query(Spectrometers, **kw)
#        return q.one()

    def _get_query(self, klass, filter_str=None, **clause):
        sess = self.get_session()
        q = sess.query(klass)
        if filter_str:
            q = q.filter(filter_str)
        else:
            q = q.filter_by(**clause)
        return q

    def open_selector(self):
        s = DBSelector(_db=self)
        s._execute_()
        s.edit_traits()#kind='livemodal')

#==============================================================================
#   adder
#==============================================================================
    def add_bakeout(self, commit=True, **kw):
        b = BakeoutTable(**kw)
        self._add_item(b, commit)
        return b

    def add_controller(self, bakeout, commit=True, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return c

    def add_path(self, bakeout, commit=True, **kw):
        p = PathTable(**kw)
        bakeout.path = p
        if commit:
            self.commit()
#        self._add_item(c, commit)
        return p

    def _add_item(self, obj, commit):
        sess = self.get_session()
        sess.add(obj)
        if commit:
            sess.commit()


#======== EOF ================================
#    def add_intercepts(self, **kw):
#        o = Intercepts(**kw)
#        self._add_item(o)
#
#    def add_analysis(self, atype=None, spectype=None, **kw):
#        if atype is not None:
#            a = self.get_analysis_type(name=atype)
#            kw['type_id'] = a.id
#
#        if spectype is not None:
#            s = self.get_spectrometer(name=spectype)
#            kw['spectrometer_id'] = s.id
#
#        o = Analyses(**kw)
#        self._add_item(o)
#        return o.id
