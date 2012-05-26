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



from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Instance, List, Bool, Button, on_trait_change, Any
from traitsui.api import View, Item, TableEditor, HGroup
from traitsui.table_column import ObjectColumn
import apptools.sweet_pickle as pickle

#============= standard library imports ========================
from threading import Thread
#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from analysis import AutomatedRun
from src.graph.graph import Graph
from spectrometer_dummy import Spectrometer
from src.extraction_line.extraction_line_manager import ExtractionLineManager
from src.envisage.core.envisage_editable import EnvisageEditable

class Experiment(EnvisageEditable):
    '''
    '''
    analyses = List(AutomatedRun)
    blanks = List(AutomatedRun)
    database = Instance(DatabaseAdapter, transient=True)
    extraction_line_manager = Instance(ExtractionLineManager, transient=True)
    graph = Instance(Graph, transient=True)

    active_analysis = Instance(AutomatedRun)

    spectrometer = Instance(Spectrometer, transient=True)
    file_extension = '.pxp'
    _alive = Bool(False)

    add_blank = Button
    start_with_blank = True

    db_id = 0
    _selected = Any(transient=True)
    def _spectrometer_default(self):
        '''
        '''
        return Spectrometer(name='ArgusVI')

    def execute(self):
        '''
        '''

        t = Thread(target=self._execute_)
        t.start()

        #process view wants a return valve
        return True

    def _pre_execute_(self):
        self._alive = True

        #reset the analysis graphs
        for a in self.analyses:
            a.graph.clear()

        #save a new experiment
        dbexperiment, sess = self.database.add_experiment(dict())
        sess.flush()
        self.db_id = dbexperiment.id
        sess.close()

    def _post_execute_(self):

        self._alive = False

    def _execute_(self):
        '''
        '''
        #saves a experiment record to db
        self._pre_execute_()

        for a in self.analyses:
            self.active_analysis = a
            a.database = self.database
            a.execute(dict(spectrometer=self.spectrometer,
                           extraction_line_manager=self.extraction_line_manager,
                           experiment_id=self.db_id
                           ))

        self._post_execute_()


    def kill(self):
        if self.active_analysis:
            self.active_analysis.kill()
        self._alive = False

    def save(self, path=None):
        oldname, path = self._pre_save(path)
        self._dump_items(path, self)
        return oldname

    def bootstrap(self, p, database=None):
        '''
            @type p: C{str}
            @param p:

            @type database: C{str}
            @param database:
        '''
        ok = True
        with open(p, 'r') as f:
            try:
                obj = pickle.load(f)

                for a in obj.traits():
                    if a is not 'name':
                        self.trait_set(**obj.trait_get(a))

                if database is not None:
                    self.database = database
                    for a in self.analyses:
                        a.database = database
                        a._add_logger()
            except pickle.UnpicklingError, e:
                self.warning('Invalid experiment file %s' % e)
                ok = False
            except EOFError:
                ok = False
        return ok

    def _add_blank_fired(self):

        a = self._analysis_factory(kind='blank',
                                   prep_script=self.active_analysis.prep_script
                                   )
        if self._selected:
            index = self.analyses.index(self._selected[-1])
            self.analyses.insert(index + 1, a)
        else:
            self.analyses.append(a)

    def row_factory(self):
        '''items are not explicitly added ie returned here 
            but are assigned by the analysis
        '''
        a = self._analysis_factory()
        a.edit_traits(kind='livemodal')

    def _analysis_factory(self, *args, **kw):
        self.dirty = True
        a = AutomatedRun(database=self.database,
                     experiment=self,
                     **kw)
        return a

    @on_trait_change('analyses[]')
    def _analyses_changed(self, obj, name, old, new):
        if name == 'analyses_items':
            self.dirty = True
            self.active_analysis = new[-1]

    def traits_view(self):
        '''
        '''
        cols = [ObjectColumn(name='kind'),
                ObjectColumn(name='runid', width=50, editable=False),
              ObjectColumn(name='power', width=50),
              ObjectColumn(name='prep_script')
              #ObjectColumn(name = '')
              ]
        editor = TableEditor(columns=cols,
                             row_factory=self.row_factory,
                             show_toolbar=True,
                             deletable=True,
                             selection_mode='rows',
                             selected='_selected')
        v = View(Item('analyses', editor=editor, show_label=False),
                 HGroup(Item('add_blank', enabled_when='analyses', show_label=False)),
                 height=500,
                 width=500)
        return v

    def graph_view(self):
        '''
        '''
        v = View(Item('graph', show_label=False))
        return v
#============= views ===================================

if __name__ == '__main__':
    e = Experiment()
    #e = AutomatedRun()
    e.configure_traits()
#============= EOF ====================================
