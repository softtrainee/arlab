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
#============= standard library imports ========================
from sqlalchemy.sql.expression import  and_
#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from src.database.selectors.isotope_selector import IsotopeAnalysisSelector

#meas_
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_ExperimentTable, meas_ExtractionTable, meas_IsotopeTable, meas_MeasurementTable, \
    meas_SpectrometerParametersTable, meas_SpectrometerDeflectionsTable, \
    meas_SignalTable, proc_IsotopeResultsTable, proc_FitHistoryTable, \
    proc_FitTable, meas_PeakCenterTable, gen_SensitivityTable

#proc_
from src.database.orms.isotope_orm import proc_DetectorIntercalibrationHistoryTable, proc_DetectorIntercalibrationTable, proc_SelectedHistoriesTable, \
    proc_BlanksTable, proc_BackgroundsTable, proc_BlanksHistoryTable, proc_BackgroundsHistoryTable

#irrad_
from src.database.orms.isotope_orm import irrad_HolderTable, irrad_ProductionTable, irrad_IrradiationTable, irrad_ChronologyTable, irrad_LevelTable, \
    irrad_PositionTable

#flux_
from src.database.orms.isotope_orm import flux_FluxTable, flux_HistoryTable, flux_MonitorTable

#gen_
from src.database.orms.isotope_orm import gen_DetectorTable, gen_ExtractionDeviceTable, gen_ProjectTable, \
    gen_MolecularWeightTable, gen_MaterialTable, gen_MassSpectrometerTable, \
    gen_SampleTable, gen_LabTable, gen_AnalysisTypeTable, gen_UserTable, gen_ImportTable


from src.database.core.functions import add, sql_retrieve, get_one, \
    delete_one

from src.experiment.identifier import convert_identifier
from src.repo.repository import Repository, ZIPRepository
from src.paths import paths

#@todo: change rundate and runtime to DateTime columns

class IsotopeAdapter(DatabaseAdapter):
    '''
        new style adapter 
        be careful with super methods you use they may deprecate
        
        using decorators is the new model
    '''

    selector_klass = IsotopeAnalysisSelector
#    path_table = meas_AnalysisPathTable

#    def initialize_database(self):
#        self.add_sample('B')
#        self.commit()
#        self.add_labnumber('A')
    def clone_record(self, a):
        sess = self.new_session()
        q = sess.query(meas_AnalysisTable)
        q = q.filter(meas_AnalysisTable.id == a.id)
        r = q.one()
#        sess.expunge_all()
#        sess.close()
#        sess.remove()
        return r

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

    def add_blanks(self, history, **kw):
        return self._add_series_item('Blanks', 'blanks', history, **kw)

    def add_blanks_set(self, blank, analysis, **kw):
        return self._add_set('Blanks', 'blank', blank, analysis, **kw)

    def add_backgrounds_history(self, analysis, **kw):
        return self._add_history('Backgrounds', analysis, **kw)

    def add_backgrounds(self, history, **kw):
        return self._add_series_item('Backgrounds', 'backgrounds', history, **kw)

    def add_backgrounds_set(self, background, analysis, **kw):
        return self._add_set('Backgrounds', 'background', background, analysis, **kw)

    @add
    def add_detector(self, name, **kw):
        det = gen_DetectorTable(name=name, **kw)
        return self._add_unique(det, 'detector', name)

    def add_detector_intercalibration_history(self, analysis, **kw):
        return self._add_history('DetectorIntercalibration', analysis, **kw)

    def add_detector_intercalibration(self, history, detector, **kw):
        a = self._add_series_item('DetectorIntercalibration',
                                     'detector_intercalibration', history, **kw)
        if a:
            detector.intercalibrations.append(a)

        return a
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
        exp = meas_ExperimentTable(name=name, **kw)
        return exp, True

    @add
    def add_extraction(self, analysis, name, extract_device=None, **kw):
        ex = meas_ExtractionTable(script_name=name, **kw)
        analysis = self.get_analysis(analysis)
        if analysis:
            analysis.extraction = ex

        extract_device = self.get_extraction_device(extract_device)
        if extract_device:
            extract_device.extractions.append(ex)

        return ex, True

    @add
    def add_extraction_device(self, name, **kw):
        item = gen_ExtractionDeviceTable(name=name, **kw)
        return self._add_unique(item, 'extraction_device', name)

    @add
    def add_fit_history(self, analysis, **kw):
        hist = proc_FitHistoryTable(**kw)
        if analysis:
            analysis.fit_histories.append(hist)
            analysis.selected_histories.selected_fits = hist
            return hist, True
        else:
            return hist, False
    @add
    def add_fit(self, history, isotope, **kw):
        f = proc_FitTable(**kw)
        if history:
            history.fits.append(f)
        if isotope:
            isotope.fits.append(f)

        return f, True

    @add
    def add_flux(self, j, j_err):
        f = flux_FluxTable(j=j, j_err=j_err)
        return f, True

    @add
    def add_flux_history(self, pos, **kw):
        ft = flux_HistoryTable(**kw)
        if pos:
            ft.position = pos
            return ft, True
        else:
            return ft, False
    @add
    def add_flux_monitor(self, name, **kw):
        fx = flux_MonitorTable(name=name, **kw)
        return self._add_unique(fx, 'flux_monitor', name)

    @add
    def add_irradiation(self, name, production=None, chronology=None):
        production = self.get_irradiation_production(production)
        chronology = self.get_irradiation_chronology(chronology)

        ir = irrad_IrradiationTable(name=name,
                                    production=production,
                                    chronology=chronology)
        return self._add_unique(ir, 'irradiation', name)

    @add
    def add_irradiation_holder(self, name , **kw):
#        print name, 'fffff', self.get_irradiation_holder(name)
#        return None, False
        ih = irrad_HolderTable(name=name, **kw)
        return self._add_unique(ih, 'irradiation_holder', name)

    @add
    def add_irradiation_production(self, **kw):
        ip = irrad_ProductionTable(**kw)
        return ip, True

    @add
    def add_irradiation_position(self, pos, labnumber, irrad, level, **kw):
        labnumber = self.get_labnumber(labnumber)
        dbpos = irrad_PositionTable(position=pos, labnumber=labnumber)

        irrad = self.get_irradiation(irrad)
#        level = self.get_irradiation_level(irrad, level)
        if isinstance(level, str):
            level = next((li for li in irrad.levels if li.name == level), None)

        if level:
            level.positions.append(dbpos)
            return dbpos, True
        else:
            return dbpos, False

    @add
    def add_irradiation_chronology(self, chronblob):
        '''
            startdate1 starttime1%enddate1 endtime1$startdate2 starttime2%enddate2 endtime2
        '''
        ch = irrad_ChronologyTable(chronology=chronblob)
        return ch, True

    @add
    def add_irradiation_level(self, name, irradiation, holder):
        irradiation = self.get_irradiation(irradiation)
        holder = self.get_irradiation_holder(holder)

        irn = irradiation.name if irradiation else None
        hn = holder.name if holder else None
        self.info('adding level {} {} to {}'.format(name, hn, irn))

        level = irrad_LevelTable(name=name)
        if irradiation is not None:
            irradiation.levels.append(level)

        if holder is not None:
            holder.levels.append(level)

        return level, True

    @add
    def add_import(self, **kw):
        ih = gen_ImportTable(**kw)
        return ih, True

    @add
    def add_isotope(self, analysis, molweight, det, **kw):
        iso = meas_IsotopeTable(**kw)
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
    def add_isotope_result(self, isotope, history, **kw):
        r = proc_IsotopeResultsTable(**kw)
        if isotope:
            isotope.results.append(r)
            if history:
                history.results.append(r)
                return r, True

        return r, False

    @add
    def add_measurement(self, analysis, analysis_type, mass_spec, name, **kw):
        ms = meas_MeasurementTable(script_name=name, **kw)
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
        ms = gen_MassSpectrometerTable(name=name)
        return self._add_unique(ms, 'mass_spectrometer', name)

    @add
    def add_material(self, name, **kw):
        mat = gen_MaterialTable(name=name, **kw)
        return self._add_unique(mat, 'material', name)

    @add
    def add_molecular_weight(self, name, mass):
        mw = gen_MolecularWeightTable(name=name, mass=mass)
        return self._add_unique(mw, 'molecular_weight', name)

    @add
    def add_project(self, name, **kw):
        proj = gen_ProjectTable(name=name, **kw)
        return self._add_unique(proj, 'project', name)

    @add
    def add_peak_center(self, analysis, **kw):
        pc = meas_PeakCenterTable(**kw)
        if analysis:
            analysis.peak_center = pc
            return pc, True
        return pc, False

    @add
    def add_user(self, name, project=None, **kw):
        user = gen_UserTable(name=name, **kw)
        if isinstance(project, str):
            project = self.get_project(project)

        q = self._build_query_and(gen_UserTable, name, gen_ProjectTable, project)

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
        sample = gen_SampleTable(name=name, **kw)
#        if isinstance(project, str):

#        if isinstance(material, str):

        sess = self.get_session()
        q = sess.query(gen_SampleTable)
        q = q.filter(gen_SampleTable.name == name)

#        if material:
#            q = q.join(gen_MaterialTable)
#            material = self.get_material(material)
#            q = q.filter(gen_MaterialTable.name == material.name)
#        if project:
#            q = q.join(gen_ProjectTable)
#            project = self.get_project(project)
#            q = q.filter(gen_ProjectTable.name == project.name)
#
        sam = sql_retrieve(q.one)
#        print sam, name, material, project
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
            self.info('adding sample {} project={}, material={}'.format(name,
                                                                        project.name if project else 'None',
                                                                        material.name if material else 'None',))
            return sample, True


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
    def add_signal(self, isotope, data):
        s = meas_SignalTable(data=data)
        if isotope:
            isotope.signals.append(s)

            return s, True
        else:
            return s, False

    @add
    def add_spectrometer_parameters(self, meas, **kw):
        sp = meas_SpectrometerParametersTable(**kw)
        if meas:
            meas.spectrometer_parameters = sp
            return sp, True
        else:
            return sp, False

    @add
    def add_deflection(self, meas, det, value):
        sp = meas_SpectrometerDeflectionsTable(deflection=value)
        if meas:
            meas.deflections.append(sp)
            det = self.get_detector(det)
            if det:
                det.deflections.append(sp)
            return sp, True
        else:
            return sp, False

    @add
    def add_labnumber(self, labnumber,
#                      aliquot, 
                      sample=None, **kw):
        pln = self.get_labnumber(labnumber)
        if pln is not None:
            return pln, False

        ln = gen_LabTable(labnumber=labnumber,
#                      aliquot=aliquot,
                      ** kw)

        sample = self.get_sample(sample)

#        ln = self._add_unique(ln, 'labnumber', labnumber)
#        if pln is not None:
#            if pln.aliquot == aliquot:
#                return ln, False

        if sample is not None and ln is not None:
            sample.labnumbers.append(ln)

        self.info('adding labnumber {}'.format(labnumber))
        return ln, True

    @add
    def add_analysis(self, labnumber, **kw):
#        if isinstance(labnumber, (str, int, unicode)):
        labnumber = self.get_labnumber(labnumber)

        anal = meas_AnalysisTable(**kw)
        if labnumber is not None:
            labnumber.analyses.append(anal)

        return anal, True

#    @add
#    def add_analysis_path(self, path, analysis=None, **kw):
#        kw = self._get_path_keywords(path, kw)
#        anal_path = meas_AnalysisPathTable(**kw)
#        if isinstance(analysis, (str, int, long)):
#            analysis = self.get_analysis(analysis)
##
#        if analysis is not None:
#            analysis.path = anal_path
#            return anal_path, True
#
#        return None, False

    @add
    def add_analysis_type(self, name):
        at = gen_AnalysisTypeTable(name=name)
        return self._add_unique(at, 'analysis_type', name)

    @add
    def add_sensitivity(self, ms, **kw):
        si = gen_SensitivityTable(**kw)
        ms = self.get_mass_spectrometer(ms)
        if ms is not None:
            ms.sensitivities.append(si)
            return si, True
        return si, False


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
        return meas_AnalysisTable, 'lab_id'

    @get_one
    def get_analysis_type(self, name):
        return gen_AnalysisTypeTable

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
        return gen_DetectorTable

    @get_one
    def get_detector_intercalibration(self, name):
        return proc_DetectorIntercalibrationTable

    @get_one
    def get_detector_intercalibration_history(self, name):
        return proc_DetectorIntercalibrationHistoryTable

    @get_one
    def get_experiment(self, name):
        return meas_ExperimentTable

    @get_one
    def get_extraction_device(self, name):
        return gen_ExtractionDeviceTable

    @get_one
    def get_irradiation_chronology(self, name):
        return irrad_ChronologyTable

    @get_one
    def get_irradiation_holder(self, name):
        return irrad_HolderTable

    @get_one
    def get_irradiation_production(self, name):
        return irrad_ProductionTable

    @get_one
    def get_irradiation(self, name):
        return irrad_IrradiationTable

    def get_irradiation_level(self, irrad, level):
        sess = self.get_session()
        q = sess.query(irrad_LevelTable)
        q = q.join(irrad_IrradiationTable)
        q = q.filter(irrad_IrradiationTable.name == irrad)
        q = q.filter(irrad_LevelTable.name == level)
        try:
            return q.one()
        except Exception, e:
            pass

    def get_irradiation_position(self, irrad, level, pos):
        sess = self.get_session()
        q = sess.query(irrad_PositionTable)
        q = q.join(irrad_LevelTable)
        q = q.join(irrad_IrradiationTable)
        q = q.filter(irrad_IrradiationTable.name == irrad)
        q = q.filter(irrad_LevelTable.name == level)

        if isinstance(pos, (list, tuple)):
            q = q.filter(irrad_PositionTable.position.in_(pos))
            func = 'all'
        else:
            q = q.filter(irrad_PositionTable.position == pos)
            func = 'one'
        try:
            return getattr(q, func)()
        except Exception, e:
            pass

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
        return gen_LabTable, 'labnumber'

    @get_one
    def get_mass_spectrometer(self, name):
        return gen_MassSpectrometerTable

    @get_one
    def get_material(self, name):
        return gen_MaterialTable

    @get_one
    def get_molecular_weight(self, name):
        return gen_MolecularWeightTable

    @get_one
    def get_project(self, name):
        return gen_ProjectTable

    @get_one
    def get_sample(self, name):
        return gen_SampleTable

    @get_one
    def get_flux_history(self, name):
        return flux_HistoryTable

    @get_one
    def get_flux_monitor(self, name):
        return flux_MonitorTable
#===============================================================================
# ##getters multiple
#===============================================================================
    def get_analyses(self, **kw):
        return self._get_items(meas_AnalysisTable, globals(), **kw)

#    def get_analysis_types(self, **kw):
#        return self._get_items(gen_AnalysisTypeTable, globals(), **kw)

    def get_irradiations(self, **kw):
        return self._get_items(irrad_IrradiationTable, globals(), **kw)

    def get_irradiation_productions(self, **kw):
        return self._get_items(irrad_ProductionTable, globals(), **kw)

    def get_labnumbers(self, **kw):
        return self._get_items(gen_LabTable, globals(), **kw)

#    def get_mass_spectrometers(self, **kw):
#        return self._get_items(gen_MassSpectrometerTable, globals(), **kw)

    def get_materials(self, **kw):
        return self._get_items(gen_MaterialTable, globals(), **kw)

#    def get_projects(self, **kw):
#        return self._get_items(gen_ProjectTable, globals(), **kw)


    def get_samples(self, **kw):
        return self._get_items(gen_SampleTable, globals(), **kw)

    def get_users(self, **kw):
        return self._get_items(gen_UserTable, globals(), **kw)

    def get_flux_monitors(self, **kw):
        return self._get_items(flux_MonitorTable, globals(), **kw)

    '''
        new style using _retrieve_items, _get_items is deprecated. 
        rewritten functionality if required
    '''
    def get_projects(self, **kw):
        return self._retrieve_items(gen_ProjectTable)

    def get_sensitivities(self, **kw):
        return self._retrieve_items(gen_SensitivityTable)

    def get_mass_spectrometers(self, **kw):
        return self._retrieve_items(gen_MassSpectrometerTable)

    def get_analysis_types(self, **kw):
        return self._retrieve_items(gen_AnalysisTypeTable)

#===============================================================================
# deleters
#===============================================================================
    @delete_one
    def delete_user(self, name):
        return gen_UserTable

    @delete_one
    def delete_project(self, name):
        return gen_ProjectTable

    @delete_one
    def delete_material(self, name):
        return gen_MaterialTable

    @delete_one
    def delete_sample(self, name):
        return gen_SampleTable

    @delete_one
    def delete_labnumber(self, name):
        return gen_LabTable, 'labnumber'


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

#                        name='isotopedb_dev_migrate',
#                        name='isotopedb_FC2',
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


        dbs = IsotopeAnalysisSelector(db=ia,
#                                      style='simple'
                                      )
#        repo = Repository(root=paths.isotope_dir)
#        repo = Repository(root='/Users/ross/Sandbox/importtest')
#        repo = ZIPRepository(root='/Users/ross/Sandbox/importtest/archive004.zip')
#        dbs.set_data_manager(kind='local',
#                             repository=repo,
#                             workspace_root=paths.default_workspace_dir
#                             )
    #    dbs._execute_query()
#        dbs.load_recent()
        dbs.load_last(n=100)


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
