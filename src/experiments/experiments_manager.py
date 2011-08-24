#============= enthought library imports =======================
from traits.api import List
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from experiment import Experiment
from recall_window import RecallWindow
from src.envisage.core.envisage_manager import EnvisageManager
from src.envisage.core.envisage_editor import EnvisageEditor
from src.helpers.paths import experiment_dir

class EEditor(EnvisageEditor):
    '''
        G{classtree}
    '''
    id_name = 'Experiment'

class ExperimentsManager(EnvisageManager):
    '''
        G{classtree}
    '''
    experiments = List(Experiment)

    klass = Experiment
    editor_klass = EEditor
    default_directory = experiment_dir
    wildcard = '*.pxp'

    def get_database(self):
        '''
        '''
        return self.window.application.get_service('src.database.pychron_database_adapter.PychronDatabaseAdapter')

    def get_extraction_line_manager(self):
        '''
        '''
        return self.window.application.get_service('src.managers.extraction_line_manager.ExtractionLineManager')

    def add_and_edit(self, e):
        '''
            @type e: C{str}
            @param e:
        '''
        self.experiments.append(e)
        self.selected = e
        e.extraction_line_manager = self.get_extraction_line_manager()

        self.window.workbench.edit(e,
                                   kind = self.editor_klass,
                                   use_existing = False)

    def recall_analysis(self):
        '''
        '''
        r = RecallWindow(database = self.get_database())

        r.edit_traits()

    def new(self):
        '''
        '''
        e = Experiment(database = self.get_database())
        self.add_and_edit(e)

    def _bootstrap_hook(self, obj, path):
        return obj.bootstrap(path, database = self.get_database())

    def open_default(self):
        '''
        '''
        p = '/Users/Ross/Pychrondata_beta/experiments/default.pxp'
        if os.path.exists(p):
            self.open(path = p)
        else:
            self.new()



#============= views ===================================
#============= EOF ====================================
