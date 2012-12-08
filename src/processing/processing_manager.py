#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Instance, cached_property, Property, List, Event, \
    Bool, Button
from traitsui.api import View, Item, TableEditor, EnumEditor, HGroup
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.processing.database_manager import DatabaseManager
from src.processing.processing_selector import ProcessingSelector
from src.processing.analysis import Analysis
from src.processing.script import ProcessScript
from src.paths import paths
from src.processing.plotters.plotter_options import PlotterOptions
#from src.constants import NULL_STR
from src.progress_dialog import MProgressDialog
from src.viewable import Viewable

class PlotterOptionsManager(Viewable):
    plotter_options_list = Property(List(PlotterOptions), depends_on='_plotter_options_list_dirty')
    _plotter_options_list_dirty = Event
    plotter_options = Instance(PlotterOptions)
    plotter_options_name = 'main'

    delete_options = Button('-')
    def close(self, ok):
        if ok:
            #dump the default plotter options
            p = os.path.join(paths.plotter_options_dir, '{}.default'.format(self.plotter_options_name))
            with open(p, 'w') as fp:
                obj = self.plotter_options.name
                pickle.dump(obj, fp)

            self.plotter_options.dump()

        return True
#===============================================================================
# handlers
#===============================================================================
    def _delete_options_fired(self):
        po = self.plotter_options
        if self.confirmation_dialog('Are you sure you want to delete {}'.format(po.name)):
            p = os.path.join(paths.plotter_options_dir, po.name)
            os.remove(p)
            self._plotter_options_list_dirty = True
            self.plotter_options = self.plotter_options_list[0]

    def traits_view(self):
        v = View(HGroup(
                    Item('plotter_options', show_label=False,
                                   editor=EnumEditor(name='plotter_options_list')
                                ),
                    Item('delete_options',
                         enabled_when='object.plotter_options.name!="Default"',
                         show_label=False),
                        ),
                 Item('plotter_options', show_label=False,
                      style='custom'),
#                               Item('edit_plotter_options', show_label=False),    
                 buttons=['OK', 'Cancel'],
                 handler=self.handler_klass
                )
        return v

    @cached_property
    def _get_plotter_options_list(self):
        r = paths.plotter_options_dir
        ps = [PlotterOptions(name='Default')]
        for n in os.listdir(r):
            if n.startswith('.') or n.endswith('.default') or n == 'Default':
                continue

            po = PlotterOptions(name=n)
            ps.append(po)

        return ps

    def _plotter_options_default(self):
        p = os.path.join(paths.plotter_options_dir, '{}.default'.format(self.plotter_options_name))

        n = 'Default'
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                try:
                    n = pickle.load(fp)
                except pickle.PickleError:
                    n = 'Default'

        po = next((pi for pi in self.plotter_options_list if pi.name == n), None)
        if not po:
            po = self.plotter_options_list[0]

        return po

class ProcessingManager(DatabaseManager):
    processing_selector = Instance(ProcessingSelector)

    plotter_options_manager = Instance(PlotterOptionsManager, ())
    only_fusions = Bool(True)
    include_omitted = Bool(True)
    display_omitted = Bool(True)

    _window_count = 0

    def new_series(self):
        #gather data
        if self._gather_data():

            #display tabular data
            self._display_tabular_data()

            #display plot
            self._display_series(key='Ar40/Ar36')

    def new_ideogram(self):
        self._new_figure('ideogram')

    def new_spectrum(self):
        self._new_figure('spectrum')

    def new_isochron(self):
        self._new_figure('isochron')

    def _new_figure(self, name):
        if self._gather_data():
            pom = self.plotter_options_manager
            info = pom.edit_traits(kind='livemodal')
            if info.result:
                po = pom.plotter_options
                ps = ProcessScript()
                ans = self._get_analyses()
                func = getattr(self, '_display_{}'.format(name))
                func(ps, ans, po)

#===============================================================================
# 
#===============================================================================
    def _gather_data(self):
        '''
            open a data selector view
            
            by default use a db connection
        '''
#        return True
        db = self.db
        db.connect()
        d = self.processing_selector

        d.select_labnumber(22233)
        info = d.edit_traits(kind='livemodal')
        if info.result:
            return True

    def _display_tabular_data(self):
        pass

    def _display_isochron(self, ps, ans, po):
        rr = ps._isochron(ans, show=False)
        if rr is not None:
            g, _isochron = rr
            self.open_view(g)

    def _display_spectrum(self, ps, ans, po):
        rr = ps._spectrum(ans, show=False)
        if rr is not None:
            g, _spec = rr
            self.open_view(g)

    def _display_ideogram(self, ps, ans, po):
        ps = ProcessScript()
        ans = self._get_analyses()

#        ans = ps._convert_records(recs)
#        ps._group_by_labnumber(ans)

        progress = self._open_progress(len(ans))
        for ai in ans:
            msg = 'loading {}'.format(ai.record_id)
            progress.change_message(msg)
            ai.load_age()
            progress.increment()

        rr = ps._ideogram(ans, aux_plots=po.get_aux_plots(), show=False)
#        rr = ps._ideogram(ans, aux_plots=['analysis_number'], show=False)
        if rr is not None:
            g, ideo = rr
            if self.display_omitted:
                #sort ans by age
                ta = sorted(ans, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                ideo.set_excluded_points(sel, 0)

            self._set_window_xy(g)
            self.open_view(g)
            self._window_count += 1

    def _display_series(self, key='Ar40'):
        ans = self._get_analyses()
        from src.graph.regression_graph import AnnotatedRegresssionTimeSeriesGraph
        an = AnnotatedRegresssionTimeSeriesGraph(
                                               graph_dict=dict(container_dict=dict(padding=5)),

                                               )
        g = an.graph
        p = g.new_plot(padding=[50, 5, 5, 35], xtitle='Time')
        p.value_range.tight_bounds = False

        def func(analysis, k):
            if '/' in k:
                n, d = k.split('/')
                nv = analysis.signals[n] - analysis.signals['{}bs'.format(n)]
                dv = analysis.signals[d] - analysis.signals['{}bs'.format(d)]
                v = (nv / dv).nominal_value

            else:
                v = analysis.signals[k].value

            return v

        x, y = zip(*[(ai.timestamp, func(ai, key)) for ai in ans])

#        import numpy as np
#        x = np.linspace(0, 10)
#        a = 1
#        b = 20
#        c = 3
#        y = a * x * x + b * x + c
#        y = a * x ** 1 + b
        p, s, l = g.new_series(x, y,
                     type='scatter', marker_size=1.5,
                     fit='parabolic'
#                     fit='average_SEM'
                     )

        g.set_x_limits(min(x), max(x), pad='0.1')
        g.refresh()
        self.open_view(an)


    def _get_analyses(self):
        ps = self.processing_selector
        ans = [Analysis(dbrecord=ri) for ri in ps.selected_records]
        return ans

    def _set_window_xy(self, obj):
        x = 50
        y = 25
        xoff = 25
        yoff = 25
        obj.window_x = x + xoff * self._window_count
        obj.window_y = y + yoff * self._window_count
#        do_later(g.edit_traits)

    def _open_progress(self, n):
        pd = MProgressDialog(max=n, size=(550, 15))
        pd.open()
        pd.center()
        return pd

    def _sort_analyses(self):
        self.analyses.sort(key=lambda x:x.age)

    def _processing_selector_default(self):
        return ProcessingSelector(db=self.db)


#============= EOF =============================================
