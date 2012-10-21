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
from src.database.core.database_adapter import DatabaseAdapter
from src.database.selectors.isotope_selector import IsotopeAnalysisSelector

from src.paths import paths
from src.database.orms.isotope_orm import ProjectTable, UserTable, SampleTable, \
    MaterialTable, AnalysisTable, AnalysisPathTable, LabTable, ExtractionTable, \
    MeasurementTable, ExperimentTable, MassSpectrometerTable, AnalysisTypeTable, \
    proc_BlanksHistoryTable, proc_BlanksTable, proc_BlanksSetTable, \
    proc_BackgroundsHistoryTable, proc_BackgroundsTable, \
    proc_BackgroundsSetTable, IsotopeTable, DetectorTable, MolecularWeightTable, \
    irrad_ProductionTable, irrad_IrradiationTable, irrad_HolderTable, \
    proc_DetectorIntercalibrationHistoryTable, \
    proc_DetectorIntercalibrationTable, proc_DetectorIntercalibrationSetTable, \
    proc_SelectedHistoriesTable
#import sqlalchemy
from sqlalchemy.sql.expression import or_, and_
from src.database.core.functions import add, sql_retrieve, get_one, \
    delete_one
from src.experiment.identifier import convert_identifier
from src.repo.repository import Repository
#from src.database.adapters.adapter_decorators import add, get_one, commit
#from sqlalchemy.sql.expression import or_
#============= standard library imports ========================
#============= local library imports  ==========================

#@todo: change rundate and runtime to DateTime columns

class IsotopeAdapter(DatabaseAdapter):
    '''
        new style adapter 
        be careful with super methods you use they may deprecate
        
        using decorators is the new model
    '''

    selector_klass = IsotopeAnalysisSelector
    path_table = AnalysisPathTable

#    def initialize_database(self):
#        self.add_sample('B')
#        self.commit()
#        self.add_labnumber('A')

#===========================================================================
# adders
#===========================================================================
    @add
    def _add_history(self, name, analysis, **kw):
        table = globals()['proc_{}HistoryTable'.format(name)]
        analysis = self.get_analysis(analysis)
        h = table(analysis=analysis, **kw)
        return h, True

    @add
    def _add_set(self, name, key, value, analysis, **kw):
        table = globals()['proc_{}SetTable'.format(name)]
        nset = table(**kw)
#        bs = proc_BlanksSetTable(**kw)

#        blank = self.get_blank(blank)
        pa = getattr(self, 'get_{}'.format(key))(value)

        analysis = self.get_analysis(analysis)

        if analysis:
            setattr(nset, '_analysis_id'.format(key), analysis)
#            bs.blank_analysis_id = analysis.id
        if pa:
            pa.sets.append(nset)
#        if blank:
#            blank.sets.append(bs)
        return nset, True

    @add
    def _add_series_item(self, name, key, history, **kw):
        item = globals()['proc_{}Table'.format(name)](**kw)
        history = getattr(self, 'get_{}_history'.format(key))(history)
        if history:
            try:
                getattr(history, key).append(item)
            except AttributeError:
                setattr(history, key, item)
            return item, True
        return item, False

    def add_blanks_history(self, analysis, **kw):
        return self._add_history('Blanks', analysis, **kw)
#        analysis = self.get_analysis(analysis)
#        bh = proc_BlanksHistoryTable(analysis=analysis, **kw)
#        return bh, True

    def add_blanks(self, history, **kw):
        return self._add_series_item('Blanks', 'blanks', history, **kw)


#        b = proc_BlanksTable(**kw)
#        history = self.get_blanks_history(history)
#        if history:
#            history.blanks.append(b)
#            return b, True
#        return b, False

    def add_blanks_set(self, blank, analysis, **kw):
        return self._add_set('Blanks', 'blank', blank, analysis, **kw)
#        bs = proc_BlanksSetTable(**kw)
#        blank = self.get_blank(blank)
#        analysis = self.get_analysis(analysis)
#
#        if analysis:
#            bs.blank_analysis_id = analysis.id
#        if blank:
#            blank.sets.append(bs)
#        return bs, True


    def add_backgrounds_history(self, analysis, **kw):
        return self._add_history('Backgrounds', analysis, **kw)
#        analysis = self.get_analysis(analysis)
#        bh = proc_BackgroundsHistoryTable(analysis=analysis, **kw)
#        return bh, True


    def add_backgrounds(self, history, **kw):
        return self._add_series_item('Backgrounds', 'backgrounds', history, **kw)
#        b = proc_BackgroundsTable(**kw)
#        history = self.get_backgrounds_history(history)
#        if history:
#            history.backgrounds.append(b)
#            return b, True
#        return b, False


    def add_backgrounds_set(self, background, analysis, **kw):
        return self._add_set('Backgrounds', 'background', background, analysis, **kw)

#        bs = proc_BackgroundsSetTable(**kw)
#        background = self.get_background(background)
#        analysis = self.get_analysis(analysis)
#
#        if analysis:
#            bs.background_analysis_id = analysis.id
#        if background:
#            background.sets.append(bs)
#        return bs, True

    @add
    def add_detector(self, name, **kw):
        det = DetectorTable(name=name, **kw)
        return self._add_unique(det, 'detector', name)

    def add_detector_intercalibration_history(self, analysis, **kw):
        return self._add_history('DetectorIntercalibration', analysis, **kw)
#        analysis = self.get_analysis(analysis)
#        dh = proc_DetectorIntercalibrationHistoryTable(analysis=analysis, **kw)
#        return dh, True

    def add_detector_intercalibration(self, history, **kw):
        return self._add_series_item('DetectorIntercalibration',
                                     'detector_intercalibration', history, **kw)
#        d = proc_DetectorIntercalibrationTable(**kw)
#        history = self.get_detector_intercalibration_history(history)
#        if history:
#            history.detector_intercalibration.append(d)
#            return d, True
#        return d, False

    def add_detector_intercalibration_set(self, detector_intercalibration, analysis, **kw):
        return self._add_set('DetectorIntercalibration', 'detector_intercalibration',
                             detector_intercalibration, analysis, **kw)
#        ds = proc_DetectorIntercalibrationSetTable(**kw)
#        detector_intercalibration = self.get_detector_intercalibration(detector_intercalibration)
#        analysis = self.get_analysis(analysis)
#
#        if analysis:
#            ds.detector_intercalibration_analysis_id = analysis.id
#        if detector_intercalibration:
#            detector_intercalibration.sets.append(ds)
#        return ds, True

    @add
    def add_experiment(self, name, **kw):
        exp = ExperimentTable(name=name, **kw)
        return exp, True

    @add
    def add_extraction(self, analysis, name, **kw):
        ex = ExtractionTable(script_name=name, **kw)
        analysis = self.get_analysis(analysis)
        if analysis:
            analysis.extraction = ex
        return ex, True

    @add
    def add_irradiation_holder(self, name, **kw):
#        print name, 'fffff', self.get_irradiation_holder(name)
#        return None, False
        ih = irrad_HolderTable(name=name, **kw)
        return self._add_unique(ih, 'irradiation_holder', name)

    @add
    def add_irradiation_production(self, **kw):
        ip = irrad_ProductionTable(**kw)
        return ip, True

    @add
    def add_isotope(self, analysis, molweight, det, **kw):
        iso = IsotopeTable(**kw)
        analysis = self.get_analysis(analysis)
        if analysis:
            analysis.isotopes.append(iso)

        det = self.get_detector(det)
        if det is not None:
            det.isotopes.append(iso)

        molweight = self.get_molecular_weight(molweight)
        if molweight is not None:
            molweight.isotopes.append(iso)

        return iso, True

    @add
    def add_measurement(self, analysis, analysis_type, mass_spec, name, **kw):
        ms = MeasurementTable(script_name=name, **kw)
#        if isinstance(analysis, str):
        analysis = self.get_analysis(analysis)
        analysis_type = self.get_analysis_type(analysis_type)
        mass_spec = self.get_mass_spectrometer(mass_spec)
        if analysis:
            analysis.measurement = ms

        if analysis_type:
            analysis_type.measurements.append(ms)

        if mass_spec:
            mass_spec.measurements.append(ms)

        return ms, True

    @add
    def add_mass_spectrometer(self, name):
        ms = MassSpectrometerTable(name=name)
        return self._add_unique(ms, 'mass_spectrometer', name)

    @add
    def add_material(self, name, **kw):
        mat = MaterialTable(name=name, **kw)
        return self._add_unique(mat, 'material', name)

    @add
    def add_molecular_weight(self, name, mass):
        mw = MolecularWeightTable(name=name, mass=mass)
        return self._add_unique(mw, 'molecular_weight', name)

    @add
    def add_project(self, name, **kw):
        proj = ProjectTable(name=name, **kw)
        return self._add_unique(proj, 'project', name)

    @add
    def add_user(self, name, project=None, **kw):
        user = UserTable(name=name, **kw)
        if isinstance(project, str):
            project = self.get_project(project)

        q = self._build_query_and(UserTable, name, ProjectTable, project)

        addflag = True
        u = sql_retrieve(q.one)
        if u is not None:
            addflag = not (u.project == project)

        if addflag:
            self.info('adding user {}'.format(name))
            if project is not None:
                project.users.append(user)

            #second parameter indicates to the decorator if 
            #the item should be added
            return user, True

        else:
#            self.info('user={} project={} already exists'.format(name, project.name if project else 'None'))
            return user, False


#    @add
#    def add_sample(self, name, material=None, **kw):
#        sample = SampleTable(name=name, **kw)
#        if isinstance(material, str):
#            material = self.get_material(material)
#
#        q = self._build_query_and(SampleTable, name, MaterialTable, material)
#
#        sam = sql_retrieve(q.one)
##        if sam is not None:
##            addflag = not sam.material == material
#        if sam is None:
#            return sample, True
#        else:
#            self.info('sample={} material={} already exists'.format(name, material.name))
#            return sample, False
    @add
    def add_sample(self, name, project=None, material=None, **kw):
        sample = SampleTable(name=name, **kw)
#        if isinstance(project, str):
        project = self.get_project(project)

#        if isinstance(material, str):
        material = self.get_material(material)

        sess = self.get_session()
        q = sess.query(SampleTable)
        q = q.join(MaterialTable)
        q = q.join(ProjectTable)
        q = q.filter(SampleTable.name == name)
        q = q.filter(MaterialTable.name == material.name)
        q = q.filter(ProjectTable.name == project.name)
        sam = sql_retrieve(q.one)

        if sam is not None:
#            self.info('sample={} material={} project={} already exists'.format(name,
#                                                                           material.name if material else 'None',
#                                                                           project.name if project else 'None'
#                                                                           ))
            return sam, False
        else:
            if project is not None:
                project.samples.append(sample)
            if material is not None:
                material.samples.append(sample)

            return sample, True
#        q = self._build_query_and(SampleTable, name, MaterialTable, material)
#        q = self._build_query_and(SampleTable, name, ProjectTable, project, q=q)

#        addflag = True
#
#        sam = sql_retrieve(q.one)
#        if sam is not None:
#            addflag = not (sam.project == project or sam.material == material)
#
#        if addflag:
#            self.info('adding sample {}'.format(name))
#            if project is not None:
#                project.samples.append(sample)
#                material.samples.append(sample)
#
#            return sample, True
#        else:
#            self.info('sample={} material={} project={} already exists'.format(name,
#                                                                           material.name if material else 'None',
#                                                                           project.name if project else 'None'
#                                                                           ))
#            return sample, False

    @add
    def add_selected_histories(self, analysis, **kw):
        sh = analysis.selected_histories
        if sh is None:
            sh = proc_SelectedHistoriesTable(analysis_id=analysis.id)
            analysis.selected_histories = sh
            return sh, True
        else:
            return sh, False

    @add
    def add_labnumber(self, labnumber, aliquot, sample=None, **kw):
        ln = LabTable(labnumber=labnumber,
                      aliquot=aliquot,
                      ** kw)

        sample = self.get_sample(sample)

#        ln = self._add_unique(ln, 'labnumber', labnumber)
        pln = self.get_labnumber(labnumber)
        if pln is not None:
            if pln.aliquot == aliquot:
                return ln, False

        if sample is not None and ln is not None:
            sample.labnumbers.append(ln)

        return ln, True

    @add
    def add_analysis(self, labnumber, **kw):
#        if isinstance(labnumber, (str, int, unicode)):
        labnumber = self.get_labnumber(labnumber)

        anal = AnalysisTable(**kw)
        if labnumber is not None:
            labnumber.analyses.append(anal)

        return anal, True

    @add
    def add_analysis_path(self, path, analysis=None, **kw):
        kw = self._get_path_keywords(path, kw)
        anal_path = AnalysisPathTable(**kw)
        if isinstance(analysis, (str, int, long)):
            analysis = self.get_analysis(analysis)
#
        if analysis is not None:
            analysis.path = anal_path
            return anal_path, True

        return None, False
    @add
    def add_analysis_type(self, name):
        at = AnalysisTypeTable(name=name)
        return self._add_unique(at, 'analysis_type', name)

#    @add
#    def add_irradiation_chronology(self, irradiations, **kw):
#        '''
#            blob the chronology
#            
#            
#            irradiations = [(start, stop),...]
#             
#        '''
#    def add_irradiation_production(self, name, **kw):
#        item = None
#        self._add_unique(item, 'irradiation_production', name)

#===========================================================================
# getters single
#===========================================================================
#    @get_one
#    def get_analysis(self):

    @get_one
    def get_analysis(self, rid):
        return AnalysisTable, 'lab_id'

    @get_one
    def get_analysis_type(self, name):
        return AnalysisTypeTable

    @get_one
    def get_blank(self, name):
        return proc_BlanksTable

    @get_one
    def get_blanks_history(self, name):
        return proc_BlanksHistoryTable

    @get_one
    def get_background(self, name):
        return proc_BackgroundsTable

    @get_one
    def get_backgrounds_history(self, name):
        return proc_BackgroundsHistoryTable

    @get_one
    def get_detector(self, name):
        return DetectorTable

    @get_one
    def get_detector_intercalibration(self, name):
        return proc_DetectorIntercalibrationTable

    @get_one
    def get_detector_intercalibration_history(self, name):
        return proc_DetectorIntercalibrationHistoryTable

    @get_one
    def get_experiment(self, name):
        return ExperimentTable

    @get_one
    def get_irradiation_holder(self, name):
        return irrad_HolderTable

    @get_one
    def get_irradiation_production(self, name):
        return irrad_ProductionTable

    def get_labnumber(self, labnum):
        if isinstance(labnum, str):
            labnum = convert_identifier(labnum)

        try:
            labnum = int(labnum)
        except (ValueError, TypeError):
            pass

        return self._get_labnumber(labnum)

    @get_one
    def _get_labnumber(self, name):
        return LabTable, 'labnumber'

    @get_one
    def get_mass_spectrometer(self, name):
        return MassSpectrometerTable

    @get_one
    def get_material(self, name):
        return MaterialTable

    @get_one
    def get_molecular_weight(self, name):
        return MolecularWeightTable

    @get_one
    def get_project(self, name):
        return ProjectTable

    @get_one
    def get_sample(self, name):
        return SampleTable

#===============================================================================
# ##getters multiple
#===============================================================================
    def get_analyses(self, **kw):
        return self._get_items(AnalysisTable, globals(), **kw)

    def get_analysis_types(self, **kw):
        return self._get_items(AnalysisTypeTable, globals(), **kw)

    def get_irradiations(self, **kw):
        return self._get_items(irrad_IrradiationTable, globals(), **kw)

    def get_irradiation_productions(self, **kw):
        return self._get_items(irrad_ProductionTable, globals(), **kw)

    def get_labnumbers(self, **kw):
        return self._get_items(LabTable, globals(), **kw)

    def get_mass_spectrometers(self, **kw):
        return self._get_items(MassSpectrometerTable, globals(), **kw)

    def get_materials(self, **kw):
        return self._get_items(MaterialTable, globals(), **kw)

    def get_projects(self, **kw):
        return self._get_items(ProjectTable, globals(), **kw)

    def get_samples(self, **kw):
        return self._get_items(SampleTable, globals(), **kw)

    def get_users(self, **kw):
        return self._get_items(UserTable, globals(), **kw)

#===============================================================================
# deleters
#===============================================================================
    @delete_one
    def delete_user(self, name):
        return UserTable

    @delete_one
    def delete_project(self, name):
        return ProjectTable

    @delete_one
    def delete_material(self, name):
        return MaterialTable

    @delete_one
    def delete_sample(self, name):
        return SampleTable

    @delete_one
    def delete_labnumber(self, name):
        return LabTable, 'labnumber'


    def _build_query_and(self, table, name, jtable, attr, q=None):
        '''
            joins table and jtable 
            filters using an andclause
            
            e.g.
            q=sess.query(Table).join(JTable).filter(and_(Table.name==name, JTable.name==attr.name))
             
        '''

        sess = self.get_session()
        andclause = tuple()
        if q is None:
            q = sess.query(table)
            andclause = (table.name == name,)

        if attr:
            q = q.join(jtable)
            andclause += (jtable.name == attr.name,)

        if len(andclause) > 1:
            q = q.filter(and_(*andclause))

        elif len(andclause) == 1:
            q = q.filter(andclause[0])

        return q




if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('ia')
    ia = IsotopeAdapter(

                        name='isotopedb_dev',
                        username='root',
                        password='Argon',
                        host='localhost',
                        kind='mysql'
#                        name='/Users/ross/Sandbox/exprepo/root/isotopedb.sqlite',
#                        name=paths.isotope_db,
#                        kind='sqlite'
                        )

    if ia.connect():


        dbs = IsotopeAnalysisSelector(_db=ia, style='simple')

        dbs.set_data_manager(kind='local',
                             repository=Repository(root=paths.isotope_dir),
                             workspace_root=paths.default_workspace_dir
                             )
    #    dbs._execute_query()
        dbs.load_recent()

        dbs.configure_traits()
#    ia.add_user(project=p, name='mosuer', commit=True)
#    p = ia.get_project('Foo3')
#    m = ia.get_material('sanidine')
#    ia.add_sample(name='FC-7sdh2n', project=p, material=m, commit=True)
    #===========================================================================
    # test getting
    #===========================================================================
#    print ia.get_user('mosuer').id
#============= EOF =============================================
