#===============================================================================
# Copyright 2013 Jake Ross
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
# from traits.api import HasTraits
import os
import yaml
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.paths import paths, rec_make
from src.processing.importer.import_manager import ImportManager

class SmartProjectTask(AnalysisEditTask):
    id = 'pychron.processing.smart_project'
    def process_project_file(self):
        p = os.path.join(paths.processed_dir, 'minna_bluff_prj.yaml')
        with open(p, 'r') as fp:
            md = yaml.load_all(fp)

            setup = md.next()

            project = setup['project']

            meta = md.next()
            if setup['import_irradiations']:
                self._import_irradiations(meta)

            meta = md.next()
            if setup['fit_isotopes']:
                self._fit_isotopes(meta)
            if setup['fit_blanks']:
                self._fit_blanks(meta, project)
            if setup['fit_detector_intercalibrations']:
                self._fit_detector_intercalibrations(meta, project)
            if setup['fit_flux']:
                self._fit_flux(meta)

            meta = md.next()
            if setup['make_figures']:
                self._make_figures(meta, project)
            if setup['make_tables']:
                self._make_tables(meta, project)

#===============================================================================
# import
#===============================================================================
    def _import_irradiations(self, meta):
        self.debug('importing analyses')

        if not self._set_destination(meta):
            return

        im = ImportManager(db=self.manager.db)
        self._set_source(meta, im)

        self._set_importer(meta, im)

        if im.do_import(new_thread=False):
            self.debug('import finished')
        else:
            self.warning('import failed')

    def _make_import_selection(self, meta):
        s = [(irrad['name'], irrad['levels'].split(','))
                    for irrad in meta['irradiations']]
        return s

    def _set_importer(self, meta, im):
        imports = meta['imports']

        im.include_analyses = meta['atype'] == 'unknown'
        im.include_blanks = imports['blanks']
        im.include_airs = imports['airs']
        im.include_cocktails = imports['cocktails']

        im.import_kind = 'irradiation'

        im.selected = self._make_import_selection(meta)

    def _set_destination(self, meta):
        dest = meta['destination']
        db = self.manager.db
        db.name = dest['database']
        db.username = dest['username']
        db.password = dest['password']
        db.host = dest['host']
        return db.connect()

    def _set_source(self, meta, im):
        source = meta['source']
        dbconn_spec = im.importer.dbconn_spec
        dbconn_spec.database = source['database']
        dbconn_spec.username = source['username']
        dbconn_spec.password = source['password']
        dbconn_spec.host = source['host']

#===============================================================================
# figures/tables
#===============================================================================
    def _make_figures(self, meta, project):
        '''
            figs: dict 
              keys: 
                type: str, name: str, samples: list
        '''
        figures = meta['figures']
        if figures:
            self._make_output_dir(figures[0]['output'], project)

            for fi in figures[1:]:
                self._make_figure(fi)

    def _make_tables(self, meta, project):
        '''
            tabs: dict 
              keys: 
                type: str, name: str, samples: list
        '''
        tables = meta['tables']
        if tables:
            self._make_output_dir(tables[0]['output'], project)
            for ti in tables[1:]:
                self._make_table(ti)

    def _make_figure(self, fdict):
        pass
    def _make_table(self, tdict):
        pass

    def _make_output_dir(self, path, project):
        if path.startswith('.'):
            # assume relative to processed dir
            path = os.path.join(paths.processed_dir,
                                project,
                                path[1:])

        rec_make(path)

#===============================================================================
# fitting
#===============================================================================
    def _fit_isotopes(self, meta):
        pass

    def _fit_blanks(self, meta, project):
        # make graphs
        if meta[0]['figure']:
            path = meta[0]['output']
            self._make_output_dir(path, project)

    def _fit_detector_intercalibrations(self, meta, project):
        # make graphs
        if meta[0]['figure']:
            path = meta[0]['output']
            self._make_output_dir(path, project)


    def _fit_flux(self, meta):
        pass

#============= EOF =============================================
