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
from traits.api import  Any, Instance, Str, \
    Directory, List, on_trait_change, Property, Enum, Int, Button
from traitsui.api import View, Item, VSplit, TableEditor, CheckListEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from pyface.api import FileDialog, OK
from pyface.message_dialog import information
from pyface.directory_dialog import DirectoryDialog
#from enthought.pyface.timer import do_later
#from traitsui.menu import Action, Menu, MenuBar
#import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
from Queue import Queue
from threading import Thread
import time
import sys
#============= local library imports  ==========================
from src.helpers.paths import modeling_data_dir as data_dir, clovera_root, \
    modeling_data_dir
#from src.helpers.paths import LOVERA_PATH
from src.graph.diffusion_graph import DiffusionGraph, GROUPNAMES
from src.loggable import Loggable
from src.data_processing.modeling.data_loader import DataLoader
from src.data_processing.modeling.model_data_directory import ModelDataDirectory
from src.helpers.color_generators import colorname_generator
from src.data_processing.modeling.fortran_process import FortranProcess

class DummyDirectoryDialog(object):
    path = os.path.join(modeling_data_dir, '59702-43')
    def open(self):
        return OK

class Modeler(Loggable):
    '''
    '''

    graph = Instance(DiffusionGraph)
    name = Str(enter_set=True, auto_set=False)

    datum = Directory(value=data_dir)
    data = List(ModelDataDirectory)

    selected = Any

    refresh = Button

    data_loader = Instance(DataLoader)
    graph_title = Property

    status_text = Str
    sync_groups = None

    include_panels = List(GROUPNAMES[:-1])

    logr_ro_line_width = Int(1)
    arrhenius_plot_type = Enum('scatter', 'line', 'line_scatter')

#===============================================================================
# fortran
#===============================================================================
    def parse_autoupdate(self):
        '''
        '''

        f = FileDialog(action='open', default_directory=data_dir)
        if f.open() == OK:
            self.info('loading autoupdate file {}'.format(f.path))

            #open a autoupdate config dialog
            from clovera_configs import AutoUpdateParseConfig
            adlg = AutoUpdateParseConfig('', '')
            info = adlg.edit_traits()
            if info.result:
                self.info('tempoffset = {} (C), timeoffset = {} (min)'.format(adlg.tempoffset, adlg.timeoffset))
                rids = self.data_loader.load_autoupdate(f.path, adlg.tempoffset, adlg.timeoffset)
                auto_files = True
                if auto_files:
                    for rid in rids:
                        self.execute_files(rid=rid, root=f.path + '_data')

        #=======================================================================
        # debug
        #=======================================================================
        #path='/Users/Ross/Pychrondata_beta/data/modeling/ShapFurnace.txt' 
        #self.data_loader.load_autoupdate(path)

    def execute_files(self, rid=None, root=None):
        if rid is None:
            rid, root = self._get_rid_root()

        if rid is not None:
            from clovera_configs import FilesConfig
            #make a config obj
            f = FilesConfig(rid, root)

            #write config to ./files.cl
            f.dump()

            #change current working dir
            os.chdir(os.path.join(root, rid))

            #now ready to run fortran
            name = 'files_py'
            if sys.platform is not 'darwin':
                name += '.exe'
            self._execute_fortran(name)

    def _get_rid_root(self):

        #=======================================================================
        # #debug

#        d = DummyDirectoryDialog()
#        =======================================================================

        d = DirectoryDialog(action='open', default_path=modeling_data_dir)

        if d.open() == OK:
            rid = os.path.basename(d.path)
            root = os.path.dirname(d.path)

            #set this root as the working directory
            os.chdir(d.path)
            self.info('setting working directory to {}'.format(d.path))

            return rid, root
        return None, None

    def execute_autoarr(self):
        self.info('------- Autoarr -------')
        rid, root = self._get_rid_root()
        if rid:
            from clovera_configs import AutoarrConfig
            a = AutoarrConfig(rid, root)
            info = a.edit_traits()
            if info.result:
                self._execute_fortran('autoarr_py')
            else:
                self.info('------- Autoarr aborted-------')
        else:
            self.info('------- Autoarr aborted-------')

    def execute_autoagemon(self):
        self.info('------- Autoagemon -------')
        rid, root = self._get_rid_root()
        if rid:
            from clovera_configs import AutoagemonConfig
            a = AutoagemonConfig(rid, root)
            info = a.edit_traits()
            if info.result:
                self._execute_fortran('autoagemon_py')
            else:
                self.info('------- Autoagemon aborted-------')
        else:
            self.info('------- Autoagemon aborted-------')


    def execute_autoagefree(self):
        self.info('------- Autoagefree -------')
        rid, root = self._get_rid_root()
        if rid:
            from clovera_configs import AutoagefreeConfig
            a = AutoagefreeConfig(rid, root)
            info = a.edit_traits()
            if info.result:
                self._execute_fortran('autoagefree_py')
            else:
                self.info('------- Autoagefree aborted-------')
        else:
            self.info('------- Autoagefree aborted-------')

    def execute_confidence_interval(self):
        self.info('------- Confidence Interval-------')
        rid, root = self._get_rid_root()
        if rid:
            from clovera_configs import ConfidenceIntervalConfig
            a = ConfidenceIntervalConfig(rid, root)
            info = a.edit_traits()
            if info.result:
                self._execute_fortran('confint_py')
            else:
                self.info('------- Confidence Interval aborted-------')

        else:
            self.info('------- Confidence Interval aborted-------')

    def _execute_fortran(self, name):
        self.info('excecute fortran program {}'.format(name))
        q = Queue()

        self._fortran_process = t = FortranProcess(name, clovera_root, q)
        t.start()

        t = Thread(target=self._handle_stdout, args=(name, t, q))
        t.start()

    def _handle_stdout(self, name, t, q):
        def _handle(msg):
            if msg:
                self.logger.info(msg)
                #func(msg)
                #information(None, msg)

        #func = getattr(self, '_handle_{}'.format(name))

#        reset clock
#        time.clock()
        st = time.time()
        #handle std.out 
        while t.isAlive() or not q.empty():
            l = q.get().rstrip()
            _handle(l)

        #handle addition msgs
        for m in self._fortran_process.get_remaining_stdout():
            _handle(m)

        dur = time.time() - st
        self.info('{} run time {:0.1f} s'.format(name, dur))
        self.info('------ {} finished ------'.format(name.capitalize()))

    def _handle_autoarr_py(self, m):
        pass
    def _handle_autoagemon_py(self, m):
        pass
    def _handle_autoagefree_py(self, m):
        pass
    def _handle_confint_py(self, m):
        pass
    def _handle_files_py(self, m):
        pass

    #===========================================================================
    # graph
    #===========================================================================

    def load_graph(self, data_directory, gid, color):
        '''
            
        '''
        data_directory.id = gid

        path = data_directory.path
        self.info('loading graph for {}'.format(path))
        g = self.graph

        runid = g.add_runid(path, kind='path')
        dl = self.data_loader
        dl.root = data_directory.path

        plotidcounter = 0

        if 'spectrum' in self.include_panels:
            data = dl.load_spectrum()
            if data is not None:
                try:
                    g.build_spectrum(color=color,
                                     pid=plotidcounter,
                                     *data)
                    s = 3 if data_directory.model_spectrum_enabled else 2
                    g.set_series_label('{}.meas-err'.format(runid), plotid=plotidcounter, series=s * gid)
                    g.set_series_label('{}.meas'.format(runid), plotid=plotidcounter, series=s * gid + 1)

                except Exception, err:
                    self.info(err)

            if data_directory.model_spectrum_enabled:
                data = dl.load_model_spectrum()
                if data is not None:
                    try:

                        p = g.build_spectrum(*data, ngroup=False, pid=plotidcounter)
                        g.set_series_label('{}.model'.format(runid), plotid=plotidcounter, series=3 * gid + 2)
                        g.color_generators[-1].next()
                        p.color = g.color_generators[-1].next()

                    except Exception, err:
                        self.info(err)

            if data_directory.inverse_model_spectrum_enabled:

                data = dl.load_inverse_model_spectrum()
                if data is not None:
                    try:
                        for ar39, age in zip(*data):
                            p = g.build_spectrum(ar39, age, ngroup=False, pid=plotidcounter)
#                        g.set_series_label('{}.inverse'.format(runid), plotid=plotidcounter, series=3 * gid + 2)
#                        g.color_generators[-1].next()
#                        p.color = g.color_generators[-1].next()

                    except Exception, err:
                        self.info(err)


            plotidcounter += 1

        if 'logr_ro' in self.include_panels:
            data = dl.load_logr_ro('logr.samp')
            if data is not None:
                try:
                    p = g.build_logr_ro(pid=plotidcounter, line_width=self.logr_ro_line_width, *data)
                    s = 2 if data_directory.model_arrhenius_enabled else 1
                    g.set_series_label('{}.meas'.format(runid), plotid=plotidcounter, series=gid * s)
                    p.on_trait_change(data_directory.update_pcolor, 'color')
                except Exception, err:
                    self.info(err)

            if data_directory.model_arrhenius_enabled:
                data = dl.load_logr_ro('logr.dat')
                if data is not None:
                    try:
                        p = g.build_logr_ro(ngroup=False, line_width=self.logr_ro_line_width, pid=plotidcounter, *data)
                        g.set_series_label('{}.model'.format(runid), plotid=plotidcounter, series=2 * gid + 1)
                        data_directory.secondary_color = p.color
                        p.on_trait_change(data_directory.update_scolor, 'color')

                    except Exception, err:
                        self.info(err)
            plotidcounter += 1

        if 'arrhenius' in self.include_panels:
            data = dl.load_arrhenius('arr.samp')
            if data is not None:
                try:
                    g.build_arrhenius(pid=plotidcounter, type=self.arrhenius_plot_type, *data)
                    g.set_series_label('{}.meas'.format(runid), plotid=plotidcounter, series=2 * gid)
                except Exception, err:
                    self.info(err)

            if data_directory.model_arrhenius_enabled:
                data = dl.load_arrhenius('arr.dat')
                if data is not None:
                    try:
                        g.build_arrhenius(ngroup=False, pid=plotidcounter, type=self.arrhenius_plot_type, *data)
                        g.set_series_label('{}.model'.format(runid), plotid=plotidcounter, series=2 * gid + 1)
                    except Exception, err:
                        self.info(err)
            plotidcounter += 1

        if 'cooling_history' in self.include_panels:
            data = dl.load_cooling_history()
            if data is not None:
                try:
                    g.build_cooling_history(pid=plotidcounter, *data)
                except Exception, err:
                    self.info(err)
            plotidcounter += 1

        if 'unconstrained_thermal_history' in self.include_panels:
            data = dl.load_unconstrained_thermal_history()
            if data is not None:
                try:
                    g.build_unconstrained_thermal_history(data, pid=plotidcounter)
                except Exception, err:
                    self.info(err)

        #sync the colors
        if self.sync_groups:
            for si in self.sync_groups:

                tg = g.groups[si]
                sg = self.sync_groups[si]

                for i, subgroup in enumerate(sg):
                    for j, series in enumerate(subgroup):
                        try:

                            tseries = tg[i][j]
                            if series.__class__.__name__ == 'PolygonPlot':
                                for a in ['face_color', 'edge_color']:
                                    color = series.trait_get(a)
                                    tseries.trait_set(**color)
                            else:
                                tseries.trait_set(**{'color':series.color})

                        except IndexError:
                            pass

        g.set_group_visiblity(data_directory.show, gid=data_directory.id)

    def refresh_graph(self):
        '''
        '''
        # before destroying the current graph we should sync with its values
        sync = False

        g = self.graph
        if g is None:

            panels = GROUPNAMES#['spectrum','logr_ro','arrenhius','cooling_history']
            if self.include_panels:
                panels = self.include_panels

            l = len(panels)
            r = int(round(l / 2.0))
            c = 1
            if l > 2:
                c = 2

            g = DiffusionGraph(include_panels=panels,
                               container_dict=dict(
                                            type='h' if c == 1 else 'g',
                                            bgcolor='white',
                                            padding=[10, 10, 40, 10],

                                            #padding=[25, 5, 50, 30],
                                            #spacing=(5,5),
                                            #spacing=32 if c==1 else (32, 25),
                                            shape=(r, c)
                                            )

                               )

            self.graph = g
        else:
        #if g is not None:
            sync = True
            xlims = []
            ylims = []

            title = g._title
            title_font = g._title_font
            title_size = g._title_size

            bgcolor = g.plotcontainer.bgcolor
            graph_editor = g.graph_editor

            self.sync_groups = g.groups
            bindings = g.bindings

            for i, _p in enumerate(g.plots):
                xlims.append(g.get_x_limits(plotid=i))
                ylims.append(g.get_y_limits(plotid=i))


        #self.graph = g = DiffusionGraph()
        g.clear()
        g.new_graph()

        if sync:
            g.bindings = bindings
            g.set_title(title, font=title_font, size=title_size)
            g.plotcontainer.bgcolor = bgcolor
            for i, lim in enumerate(zip(xlims, ylims)):
                xlim = lim[0]
                ylim = lim[1]
                #check to see limits are not inf or -inf
                if xlim[0] != float('-inf') and xlim[1] != float('inf'):
                    g.set_x_limits(min=xlim[0], max=xlim[1], plotid=i)
                    g.set_y_limits(min=ylim[0], max=ylim[1], plotid=i)
            #sync open editors    
            if graph_editor is not None:
                graph_editor.graph = g

#============= views ===================================
#    def _get_menubar(self):
#        '''
#        '''
#        load_auto = Action(name = 'Load autoupdate file',
#                         action = 'load_autoupdate_file')
#        run_model = Action(name = 'Run Model',
#                         action = 'run_model')
#        file_menu = Menu(load_auto,
#                       run_model,
#                       name = 'File')
#        menus = [file_menu]
#        return MenuBar(*menus)
#    
    def traits_view(self):
        return self.data_select_view()

    def data_select_view(self):
        tree = Item('datum', style='custom', show_label=False, height=0.75,
                  width=0.25)

        cols = [
                ObjectColumn(name='name', editable=False),
                CheckboxColumn(name='show'),
                CheckboxColumn(name='bind'),
                ObjectColumn(name='primary_color', editable=False, label='Pc', style='simple'),
                ObjectColumn(name='secondary_color', editable=False, label='Sc', style='simple'),
                CheckboxColumn(name='model_spectrum_enabled', label='Ms'),
                CheckboxColumn(name='inverse_model_spectrum_enabled', label='IMs'),
                CheckboxColumn(name='model_arrhenius_enabled', label='Ma'),

              ]

        editor = TableEditor(columns=cols,
                             editable=True,
                             reorderable=True,
                             deletable=True,
                             show_toolbar=True,
                             selection_mode='rows',
                             selected='selected'
                             )
        selected = Item('data', show_label=False, height=0.25,
                      editor=editor,
                      width=0.25
                      )

        v = View(Item('refresh', show_label=False),
                 VSplit(selected,
                        tree))
        return v
    def graph_view(self):
        graph = Item('graph', show_label=False,
                    style='custom',
                    #width = 0.75
                    )
        v = View(graph)
        return v

    def configure_view(self):
        v = View(Item('include_panels', editor=CheckListEditor(values=GROUPNAMES),
                    show_label=False,
                    style='custom'
                    ),
               kind='modal',
               buttons=['OK', 'Cancel']
               )
        return v

    def _data_loader_default(self):
        '''
        '''
        return DataLoader()

    def _datum_changed(self):
        '''
        '''

        d = self.datum
        #validate datum as proper directory
        if self.data_loader.validate_data_dir(d):

            #dont add if already in list
            for di in self.data:
                if di.path == d:
                    self.selected = d
                    return

            pid = len(self.data)
            d = ModelDataDirectory(path=d,
                                modeler=self,
                                show=True, # if len(self.data) >= 1 else False,
                                bind=True,
                                model_spectrum_enabled=True,
                                inverse_model_spectrum_enabled=True,
                                model_arrhenius_enabled=True,
                                id=pid,
                                )

            self.graph.set_group_binding(pid, True)
            self.data.append(d)
            self.selected = d

    @on_trait_change('refresh,data[]')
    def _update_(self, a, b, c, d):
        '''
        '''
        self._update_graph()

        #force update of notes and summary 
        d = self.selected
        self.selected = None
        self.selected = d

    def _update_graph(self):
        '''
        '''
        self.refresh_graph()
        color_gen = colorname_generator()
        for gid, d in enumerate(self.data):
            #need to load all graphs even if we are not going to show them 
            #this is to ensure proper grouping
            #set visiblity after
            c = color_gen.next()
            d.primary_color = c

            self.load_graph(d, gid, c)

            #skip a color
            color_gen.next()

        self.update_graph_title()

    @on_trait_change('graph.status_text')
    def update_statusbar(self, obj, name, value):
        '''
        '''
        if name == 'status_text':
            self.status_text = value

    def _get_graph_title(self):
        '''
        '''
        return ', '.join([a.name for a in self.data if a.show])

    def update_graph_title(self):
        '''
        '''
        self.graph.set_title(self.graph_title, size=18)
def runfortran():
    q = Queue()
    t = FortranProcess('hello_world', '/Users/Ross/Desktop', q)
    t.start()

    while t.isAlive() or not q.empty():
        l = q.get().rstrip()

        print l

    print t.get_remaining_stdout()


if __name__ == '__main__':
    runfortran()
#    r = RunConfiguration()
#    r.configure_traits()
#============= EOF ====================================
#    setup('modeler')
#    m = Modeler()
#    m.refresh_graph()
#
#    m.configure_traits()
#    def traits_view(self):
#        '''
#        '''
#        namegrp = HGroup(Item('name', show_label = False), spring)
#
#        v = View(HSplit(VSplit(selected,
#                             tree
#                             ),
#                      graph),
#                    width = 800,
#                    height = 600,
#                    menubar = self._get_menubar(),
#                    statusbar = 'status_text',
#                    resizable = True,
#
#                    )
#
#        return v

#def run_model(self):
#        '''
#        '''
#
#        model_thread = Thread(target=self._run_model_)
#        model_thread.start()
#
#    def _run_model_(self, run_config=None):
#        '''
#
#        '''
##        src_dir = os.path.join(data_dir, 'TESTDATA')
#        self.info('Running Model')
#        if run_config is None:
#            run_config = self.run_configuration
#
#        if run_config is None:
#            self.warning('no run configuration')
#        else:
#            self.info('Model Options')
#            for a in ['sample', 'geometry', 'max_domains', 'min_domains', 'nruns', 'max_plateau_age']:
#                self.info('{} = {}'.format(a, getattr(run_config, a)))
#
#            #dump the individual config files
#            error = self.run_configuration.write()
#            if error:
#                self.warning('Failed writing config file')
#                self.warning('error = {}'.format(error))
#                return
#
#            if os.path.exists(LOVERA_PATH):
#                #check to see dir has necessary programs
#                if any([not ni in os.listdir(LOVERA_PATH) for ni in  NECESSARY_PROGRAMS]):
#                    self.warning('Incomplete LOVERA_PATH {}'.format(LOVERA_PATH))
#                    return
#
#                src_dir = os.path.join(self.run_configuration.data_dir)
#
#                self.info('copying fortran programs')
#                #copy the lovera codes to src_dir
#                for f in NECESSARY_PROGRAMS:
#                    p = os.path.join(LOVERA_PATH, f)
#                    self.info('copying {} > {}'.format(p, src_dir))
#                    shutil.copy(p, src_dir)
#
#                self.info('change to directory {}'.format(src_dir))
#                #change the working directory
#                os.chdir(src_dir)
#
#            else:
#                self.warning('Invalid LOVERA_PATH {}'.format(LOVERA_PATH))
#                return
#
#            #run the lovera code
#            for cmd in ['filesmod', 'autoarr', 'autoagemon']:
#                msg = 'execute {}'.format(cmd)
#                self.status_test = msg
#                self.info(msg)
#                if sys.platform == 'win32':
#                    os.system(cmd)
#                else:
#                    status, output = commands.getstatusoutput('./{}'.format(cmd))
#                    self.info('{} {}' % (status, output))
#                    if status:
#                        break
#
#            #delete the copied programs
#
#            for f in NECESSARY_PROGRAMS:
#                os.remove(os.path.join(src_dir, f))
#
#            self.info('====== Modeling finished======')
#            self.status_text = 'modeling finished'
#def open_run_configuration(self):
#        def edit_config(*args):
#            if args:
#                m = args[0]
#            else:
#                m = RunConfiguration()
#
#            info = m.edit_traits(kind='modal')
#            if info.result:
#                with open(p, 'w') as f:
#                    pickle.dump(m, f)
#
#                return m
#
#        p = os.path.join(hidden_dir, '.run_config')
#        if os.path.isfile(p):
#            with open(p, 'rb') as f:
#                try:
#                    r = edit_config(pickle.load(f))
#                    if r is not None:
#                        self.run_configuration = r
#
#                except:
#                    r = edit_config()
#                    if r is not None:
#                        self.run_configuration = r
#        else:
#            r = edit_config()
#            if r is not None:
#                self.run_configuration = r
#class RunConfiguration(HasTraits):
#    '''
#    '''
#    data_dir = Directory('~/Pychrondata_beta/data/modeling')
#    sample = Str('59702-52')
#    geometry = Enum('plane', 'sphere', 'cylinder')
#    max_domains = Int(8)
#    min_domains = Int(3)
#    nruns = Int(50)
#    max_plateau_age = Float(375)
#    def write(self):
#        error = None
#        def _write_attrs(p, names):
#            with open(p, 'w') as f:
#                for n in names:
#                    f.write('#%s\n' % n)
#                    f.write('%s\n' % getattr(self, n))
#
#        if os.path.isdir(self.data_dir):
#            #write files mod config
#            p = os.path.join(self.data_dir, 'files_mod_config.in')
#            _write_attrs(p, ['sample'])
#
#            #write autoarr config
#            p = os.path.join(self.data_dir, 'autoarr_config.in')
#            _write_attrs(p, ['max_domains', 'min_domains'])
#
#            #write autoage-mon config
#            p = os.path.join(self.data_dir, 'autoage_mon_config.in')
#            _write_attrs(p, ['nruns', 'max_plateau_age'])
#        else:
#            error = 'Invalid data directory %s' % self.data_dir
#        return error

#    def traits_view(self):
#        '''
#        '''
#        files_mod_group = VGroup(Item('sample'),
#                               Item('geometry'),
#                               label='files_mod')
#        autoarr_group = VGroup(Item('max_domains'),
#                             Item('min_domains'),
#                             label='autoarr')
#        autoage_mon_group = VGroup(Item('nruns'),
#                                 Item('max_plateau_age'),
#                                 label='autoage-mon'
#                                 )
#        return View(
#                       Item('data_dir'),
#                       Group(
#                             files_mod_group,
#                             autoarr_group,
#                             autoage_mon_group,
#                             layout='tabbed'
#                            ),
#                    buttons=['OK', 'Cancel'],
#                    resizable=True,
#                    kind='modal',
#                    width=500,
#                    height=150
#                    )
