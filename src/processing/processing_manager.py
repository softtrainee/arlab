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
from traits.api import Str, Instance
from traitsui.api import View, Item
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.repo.repository import FTPRepository, Repository

#from src.processing.ideogram import Ideogram
#from src.processing.spectrum import Spectrum
#from src.processing.inverse_isochron import InverseIsochron
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.database.core.database_adapter import DatabaseAdapter
from src.processing.figures.figure import Figure
#from src.processing.processing_selector import ProcessingSelector
#from src.processing.figure import Figure
class ProcessingRepository(Repository):
    pass

class ProcessingManager(Manager):
    workspace_root = None
    workspace = None
    new_name = Str
    db = Instance(DatabaseAdapter)

    def connect_repo(self):
        host = 'localhost'
        usr = 'ross'
        pwd = 'jir812'

        repo = FTPRepository(host=host, username=usr, password=pwd,
                             remote='Sandbox/ftp/data'
                             )
        self.repo = repo

    def open_plot(self):
        kind = 'spectrum'

        #get get data
        names = self.get_names()
        if names:
            self.get_remote_files(names)
            func = getattr(self, 'plot_{}'.format(kind))
            func(names)

    def get_names(self):
        return ['B-92.h5', 'B-91.h5',
                  'B-90.h5',
                  'B-89.h5',
                  'B-88.h5',
                  ]

    def get_remote_file(self, name, force=False):
        out = os.path.join(self.workspace.root, name)
        if not os.path.isfile(out) or force:
            self.repo.retrieveFile(name, out)

    def get_remote_files(self, names, **kw):
        for n in names:
            self.get_remote_file(n, **kw)

    def open_workspace(self, name):
        self.workspace = ProcessingRepository(root=os.path.join(self.workspace_root, name))

    def new_workspace(self, name):
        while 1:
            if self._workspace_factory(name):
                #get another name
                info = self.edit_traits(view='new_workspace_view', kind='livemodal')
                if info.result:
                    name = self.new_name
                else:
                    break
            else:
                break

#    def _test_fired(self):
#        self.open_workspace('foo1')
#        self.get_remote_file('B-92.h5')

#        self.get_remote_file_list(names)
#        self.plot_intercepts(names, 'Ar40')
#        self.plot_baselines(names, 'Ar40')
#        self.plot_ideogram(names)
#        self.plot_spectrum(names)
#        self.plot_inverse_isochron(names)
#        self.open_plot()

#        self.new_figure()

#    def new_figure(self):
#        
#        fc.edit_traits()

#    def plot_inverse_isochron(self, names):
#        fits = [dict(
#                  Ar40=2,
#                  Ar39=2,
#                  Ar38=2,
#                  Ar37=2,
#                  Ar36=2,
#                  ) for n in names]
#
#        xs = []
#        ys = []
#        for n, fs in zip(names, fits):
#            df = self._open_file(n)
#
#            isos = self._get_signals(df)
#            ss = []
#            for ki in ['Ar40', 'Ar39', 'Ar36']:
#                x, y = isos[ki]
#                ss.append(polyfit(x, y, fs[ki])[-1])
#
#            xs.append(ss[1] / ss[0])
#            ys.append(ss[2] / ss[0])
#
#        iso = InverseIsochron()
#        iso.xs = xs
#        iso.ys = ys
#
#        g = iso._graph_factory()
#        g.edit_traits()

#    def plot_spectrum(self, names):
#        a = Spectrum(workspace=self.workspace)
#        a.load_analyses(names)
#        a.refresh()
#        a.edit_traits()
#        ages = [self._get_age(n) for n in names]
#        ages, errs = zip(*ages)
#
#        fits = [2 for n in names]
#
#        ar39s = []
#        for n, f in zip(names, fits):
#            data = self._get_signals(df=self._open_file(n))
#            x, y = data['Ar39']
#            a = polyfit(x, y, f)[-1]
#            ar39s.append(a)
#
#        ideo = Spectrum()
#        ideo.ages = ages
#        ideo.errors = errs
#        ideo.ar39s = ar39s
#        print ages
#        g = ideo._graph_factory()
#        g.edit_traits()

#    def plot_ideogram(self, names):
##        ages = [self._get_age(n) for n in names]
##        ages, errs = zip(*ages)
#
#        ideo = Ideogram(workspace=self.workspace)
##        ideo.load_analyses(names)
#        ideo.load_analyses(names[:2],)
#        ideo.load_analyses(names[2:4], gid=1)
#        ideo.load_analyses(names[4:], gid=2)
#
#        ideo.refresh()
#        ideo.edit_traits()


#    def plot_intercepts(self, names, isotope, fits=None):
#        def get_v(df, isotope, fit):
#            xs, ys = self._get_signals(df)[isotope]
#            return polyfit(xs, ys, fit)[-1]
#
#        if fits is None:
#            fits = [1 for n in names]
#
#        self._load_series(names, isotope, fits, get_v)
#
#    def plot_baselines(self, names, isotope, fits=None):
#        def get_v(df, isotope, fit):
#            _xs, ys = self._get_baselines(df)[isotope]
#            return array(ys).mean()
#
#        if fits is None:
#            fits = [1 for n in names]
#
#        self._load_series(names, isotope, fits, get_v)



#    def _load_series(self, names, isotope, fits, get_value):
#        ts = []
#        ss = []
#        for i, (n, fi) in enumerate(zip(names, fits)):
#            df = self._open_file(n)
#            try:
#
#                ft = get_value(df, isotope, fi)
#
#                try:
#                    t = df.root._v_attrs['TIMESTAMP'][0]
#                except KeyError:
#                    t = i
#                ts.append(t)
#                ss.append(ft)
#            except Exception, e:
##                import traceback
##                traceback.print_exc()
#                self.warning('fail loading {}'.format(n))
#
#        self._plot_series(ts, ss)

#    def _plot_series(self, ts, ss):
#        g = RegressionGraph()
#        g.new_plot()
#
#        g.new_series(ts, ss, type='scatter', marker='circle',
#                     marker_size=3
#                     )
#        g.set_x_limits(min=min(ts), max=max(ts), pad='0.1')
#        g.set_y_limits(min=min(ss), max=max(ss), pad='0.1')
#        g.edit_traits()

#    def _get_baselines(self, df):
#        isos = self._get_data(df, 'baselines')
#        if isos:
#            return isos
#
#        phbs = df.root.peakhop_baselines
#        det = next((n for n in phbs._f_iterNodes()), None)
#        if det:
#            isos = dict()
#            for tab in det._f_iterNodes():
#                isos[tab._v_name] = self._get_xy(tab)
#            return isos
#
#    def _get_signals(self, df):
#        return self._get_data(df, 'signals')
    def _figure_factory(self):
        fc = Figure(db=self.db,
                    repo=self.repo,
                    workspace=self.workspace)
        return fc

    def _workspace_factory(self, name):
        self.info('creating new workspace {}'.format(name))
        p = os.path.join(self.workspace_root, name)
        if os.path.isdir(p):
            self.warning_dialog('{} is already taken choosen another name'.format(name))
            return True
        else:
            os.mkdir(p)

    def new_workspace_view(self):
        return View(Item('new_name', label='Name',),
                    buttons=['OK', 'Cancel']
                    )

    def _db_default(self):
        db = IsotopeAdapter(kind='mysql',
                            dbname='isotopedb'
                            )
        return db

    def traits_view(self):
        return View('test')

if __name__ == '__main__':
    from globals import globalv
    globalv.show_infos = False
    globalv.show_warnings = False

    from src.helpers.logger_setup import logging_setup
    logging_setup('processing')

    pm = ProcessingManager()
    pm.connect_repo()
    pm.workspace_root = '/Users/ross/Sandbox/workspace'
    pm.open_workspace('foo1')
#    pm.configure_traits()
    fc = pm._figure_factory()
    fc.configure_traits()
#============= EOF =============================================
