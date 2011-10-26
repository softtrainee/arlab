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
from traits.api import HasTraits, Any, Instance, Str, \
    Directory, List, on_trait_change, Property, Enum, Float, Int, Button
from traitsui.api import View, Item, VSplit, TableEditor, VGroup, Group
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from pyface.api import FileDialog, OK
#from traitsui.menu import Action, Menu, MenuBar
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import shutil
import os
import sys

import commands
from threading import Thread
#============= local library imports  ==========================
from src.helpers.paths import modeling_data_dir as data_dir, hidden_dir
from src.helpers.paths import LOVERA_PATH
from src.graph.diffusion_graph import DiffusionGraph
from src.loggable import Loggable
from src.data_processing.modeling.data_loader import DataLoader
from src.data_processing.modeling.model_data_directory import ModelDataDirectory
from src.helpers.color_generators import colorname_generator
from src.data_processing.modeling.autoupdate_config_dialog import AutoupdateConfigDialog



#used to validate LOVERA_PATH            
NECESSARY_PROGRAMS = ['filesmod.exe', 'autoarr.exe', 'autoagemon.exe']
class RunConfiguration(HasTraits):
    '''
    '''
    data_dir = Directory('~/Pychrondata_beta/data/modeling')
    sample = Str('59702-52')
    geometry = Enum('plane', 'sphere', 'cylinder')
    max_domains = Int(8)
    min_domains = Int(3)
    nruns = Int(50)
    max_plateau_age = Float(375)
    def write(self):
        error = None
        def _write_attrs(p, names):
            with open(p, 'w') as f:
                for n in names:
                    f.write('#%s\n' % n)
                    f.write('%s\n' % getattr(self, n))

        if os.path.isdir(self.data_dir):
            #write files mod config
            p = os.path.join(self.data_dir, 'files_mod_config.in')
            _write_attrs(p, ['sample'])

            #write autoarr config
            p = os.path.join(self.data_dir, 'autoarr_config.in')
            _write_attrs(p, ['max_domains', 'min_domains'])

            #write autoage-mon config
            p = os.path.join(self.data_dir, 'autoage_mon_config.in')
            _write_attrs(p, ['nruns', 'max_plateau_age'])
        else:
            error = 'Invalid data directory %s' % self.data_dir
        return error

    def traits_view(self):
        '''
        '''
        files_mod_group = VGroup(Item('sample'),
                               Item('geometry'),
                               label='files_mod')
        autoarr_group = VGroup(Item('max_domains'),
                             Item('min_domains'),
                             label='autoarr')
        autoage_mon_group = VGroup(Item('nruns'),
                                 Item('max_plateau_age'),
                                 label='autoage-mon'
                                 )
        return View(
                       Item('data_dir'),
                       Group(
                             files_mod_group,
                             autoarr_group,
                             autoage_mon_group,
                             layout='tabbed'
                            ),
                    buttons=['OK', 'Cancel'],
                    resizable=True,
                    kind='modal',
                    width=500,
                    height=150
                    )

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

    run_configuration = None

#    def _refresh_fired(self):
#        print 'fas'
        
        
    @on_trait_change('graph.status_text')
    def update_statusbar(self, object, name, value):
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

    def open_run_configuration(self):
        def edit_config(*args):
            if args:
                m = args[0]
            else:
                m = RunConfiguration()

            info = m.edit_traits(kind='modal')
            if info.result:
                with open(p, 'w') as f:
                    pickle.dump(m, f)

                return m

        p = os.path.join(hidden_dir, '.run_config')
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    r = edit_config(pickle.load(f))
                    if r is not None:
                        self.run_configuration = r

                except:
                    r = edit_config()
                    if r is not None:
                        self.run_configuration = r
        else:
            r = edit_config()
            if r is not None:
                self.run_configuration = r


    def run_model(self):
        '''
        '''

        model_thread = Thread(target=self._run_model_)
        model_thread.start()

    def _run_model_(self, run_config=None):
        '''

        '''
#        src_dir = os.path.join(data_dir, 'TESTDATA')
        self.info('Running Model')
        if run_config is None:
            run_config = self.run_configuration

        if run_config is None:
            self.warning('no run configuration')
        else:
            self.info('Model Options')
            for a in ['sample', 'geometry', 'max_domains', 'min_domains', 'nruns', 'max_plateau_age']:
                self.info('{} = {}'.format(a, getattr(run_config, a)))

            #dump the individual config files
            error = self.run_configuration.write()
            if error:
                self.warning('Failed writing config file')
                self.warning('error = {}'.format(error))
                return

            if os.path.exists(LOVERA_PATH):
                #check to see dir has necessary programs
                if any([not ni in os.listdir(LOVERA_PATH) for ni in  NECESSARY_PROGRAMS]):
                    self.warning('Incomplete LOVERA_PATH {}'.format(LOVERA_PATH))
                    return

                src_dir = os.path.join(self.run_configuration.data_dir)

                self.info('copying fortran programs')
                #copy the lovera codes to src_dir
                for f in NECESSARY_PROGRAMS:
                    p = os.path.join(LOVERA_PATH, f)
                    self.info('copying {} > {}'.format(p, src_dir))
                    shutil.copy(p, src_dir)

                self.info('change to directory {}'.format(src_dir))
                #change the working directory
                os.chdir(src_dir)

            else:
                self.warning('Invalid LOVERA_PATH {}'.format(LOVERA_PATH))
                return

            #run the lovera code
            for cmd in ['filesmod', 'autoarr', 'autoagemon']:
                msg = 'execute {}'.format(cmd)
                self.status_test = msg
                self.info(msg)
                if sys.platform == 'win32':
                    os.system(cmd)
                else:
                    status, output = commands.getstatusoutput('./{}'.format(cmd))
                    self.info('{} {}' % (status, output))
                    if status:
                        break

            #delete the copied programs

            for f in NECESSARY_PROGRAMS:
                os.remove(os.path.join(src_dir, f))

            self.info('====== Modeling finished======')
            self.status_text = 'modeling finished'

    def parse_autoupdate(self):
        '''
        '''

        f = FileDialog(action='open', default_directory=data_dir)
        if f.open() == OK:
            self.info('loading autoupdate file {}'.format(f.path))

            #open a autoupdate config dialog
            adlg = AutoupdateConfigDialog()
            info = adlg.edit_traits(kind='modal')
            if info.result:
                self.info('tempoffset = {} (C), timeoffset = {} (min)'.format(adlg.tempoffset, adlg.timeoffset))
                self.data_loader.load_autoupdate(f.path, adlg.tempoffset, adlg.timeoffset)

        #path='/Users/Ross/Pychrondata_beta/data/modeling/ShapFurnace.txt' 
        #self.data_loader.load_autoupdate(path)


    def load_graph(self, data_directory, gid, color):
        '''
            
        '''
        self.info('loading graph for {}'.format(data_directory.path))
        g = self.graph

        dl = self.data_loader
        dl.root = data_directory.path

        data = dl.load_spectrum()
        if data is not None:
            try:
                g.build_spectrum(*data, **{'color':color})
            except:
                pass
            
        data = dl.load_logr_ro('logr.samp')
        if data is not None:
            try:
                g.build_logr_ro(*data)
                g.set_series_label('logr.samp', plotid=1, series=0)
            except:
                pass
            
        data = dl.load_logr_ro('logr.dat')
        if data is not None:
            try:
                g.build_logr_ro(ngroup=False, *data)
                g.set_series_label('logr.dat', plotid=1, series=1)
            except:
                pass
            
        data = dl.load_cooling_history()
        if data is not None:
            try:
                g.build_cooling_history(*data)
            except:
                pass

        data = dl.load_arrhenius('arr.samp')
        if data is not None:
            try:
                g.build_arrhenius(*data)
                g.set_series_label('arr.samp', plotid=2, series=0,)
            except:
                pass
            
        data = dl.load_arrhenius('arr.dat')
        if data is not None:
            try:
                g.build_arrhenius(ngroup=False, *data)
                g.set_series_label('arr.dat', plotid=2, series=1)
            except:
                pass

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
            g = DiffusionGraph()
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

            id = len(self.data)
            d = ModelDataDirectory(path=d,
                                modeler=self,
                                show=True, # if len(self.data) >= 1 else False,
                                bind=True,
                                id=id,
                                )

            self.graph.set_group_binding(id, True)
            self.data.append(d)
            self.selected = d

    @on_trait_change('refresh,data[]')
    def _update_(self):
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

            self.load_graph(d, gid, color_gen.next())

            #skip a color
            color_gen.next()

        self.update_graph_title()

if __name__ == '__main__':
    r = RunConfiguration()
    r.configure_traits()
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
