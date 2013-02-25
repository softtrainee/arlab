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
    proc_FitTable, meas_PeakCenterTable, gen_SensitivityTable, proc_FigureTable, \
    proc_FigureAnalysisTable, meas_PositionTable, meas_ScriptTable, \
    proc_NotesTable, meas_MonitorTable

#proc_
from src.database.orms.isotope_orm import proc_DetectorIntercalibrationHistoryTable, \
    proc_DetectorIntercalibrationTable, proc_DetectorIntercalibrationSetTable, proc_SelectedHistoriesTable, \
    proc_BlanksTable, proc_BackgroundsTable, proc_BlanksHistoryTable, proc_BackgroundsHistoryTable, \
    proc_BlanksSetTable, proc_BackgroundsSetTable, proc_DetectorIntercalibrationSetTable

#irrad_
from src.database.orms.isotope_orm import irrad_HolderTable, irrad_ProductionTable, irrad_IrradiationTable, irrad_ChronologyTable, irrad_LevelTable, \
    irrad_PositionTable

#flux_
from src.database.orms.isotope_orm import flux_FluxTable, flux_HistoryTable, flux_MonitorTable

#gen_
from src.database.orms.isotope_orm import gen_DetectorTable, gen_ExtractionDeviceTable, gen_ProjectTable, \
    gen_MolecularWeightTable, gen_MaterialTable, gen_MassSpectrometerTable, \
    gen_SampleTable, gen_LabTable, gen_AnalysisTypeTable, gen_UserTable, gen_ImportTable


from src.database.core.functions import delete_one

from src.experiment.identifier import convert_identifier
#from src.repo.repository import Repository, ZIPRepository
#from src.paths import paths
#import binascii
import hashlib

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

        return r

#===========================================================================
# adders
#===========================================================================

    def _add_history(self, name, analysis, **kw):
        table = globals()['proc_{}HistoryTable'.format(name)]
        analysis = self.get_analysis(analysis)
        h = table(analysis=analysis, **kw)
        self._add_item(h)
        return h

    def _add_set(self, name, key, value, analysis, idname=None, **kw):
        table = globals()['proc_{}SetTable'.format(name)]
        nset = table(**kw)
        pa = getattr(self, 'get_{}'.format(key))(value)

        analysis = self.get_analysis(analysis)
        if analysis:
            if idname is None:
                idname = key
            setattr(nset, '{}_analysis_id'.format(idname), analysis.id)
        if pa:
            pa.sets.append(nset)
        return nset

    def _add_series_item(self, name, key, history, **kw):
        item = globals()['proc_{}Table'.format(name)](**kw)
        history = getattr(self, 'get_{}_history'.format(key))(history)
        if history:
            try:
                getattr(history, key).append(item)
            except AttributeError:
                setattr(history, key, item)
            self._add_item(item)

        return item

    def add_monitor(self, analysis, **kw):
        dbm = meas_MonitorTable(**kw)
        analysis = self.get_analysis(analysis)
        if analysis:
            analysis.monitors.append(dbm)

        return dbm

    def add_analysis_position(self, extraction, pos, **kw):
        try:
            pos = int(pos)
        except (ValueError, TypeError):
            pos = 0

        dbpos = meas_PositionTable(position=pos, **kw)
        if extraction:
            extraction.positions.append(dbpos)

        return dbpos

    def add_note(self, analysis, note, **kw):
        analysis = self.get_analysis(analysis)
        obj = proc_NotesTable(note=note, user=self.save_username)
        if analysis:
            analysis.notes.append(obj)
        return obj

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

    def add_detector(self, name, **kw):
        det = gen_DetectorTable(name=name, **kw)
        return self._add_unique(det, 'detector', name)

    def add_detector_intercalibration_history(self, analysis, **kw):
        return self._add_history('DetectorIntercalibration', analysis, **kw)

    def add_detector_intercalibration(self, history, detector, **kw):
        a = self._add_series_item('DetectorIntercalibration',
                                     'detector_intercalibration', history, **kw)
        if a:
            detector = self.get_detector(detector)
            detector.intercalibrations.append(a)

        return a

    def add_detector_intercalibration_set(self, detector_intercalibration, analysis, **kw):
        return self._add_set('DetectorIntercalibration', 'detector_intercalibration',
                             detector_intercalibration, analysis, idname='ic', **kw)

    def add_experiment(self, name, **kw):
        exp = meas_ExperimentTable(name=name, **kw)
        self._add_item(exp)
        return exp

    def add_extraction(self, analysis, extract_device=None, **kw):
#        ex = self._get_script('extraction', script_blob)
#        if ex is None:
#            ha = self._make_hash(script_blob)
        ex = meas_ExtractionTable(**kw)
        self._add_item(ex)

        an = self.get_analysis(analysis)
        if an:
            an.extraction = ex

        ed = self.get_extraction_device(extract_device)
        if ed:
            ed.extractions.append(ex)

        return ex

    def add_extraction_device(self, name, **kw):
        item = gen_ExtractionDeviceTable(name=name, **kw)
        return self._add_unique(item, 'extraction_device', name)

    def add_figure(self, project=None, **kw):
        fig = proc_FigureTable(
                               user=self.save_username,
                               **kw
                               )
        project = self.get_project(project)
        if project:
            project.figures.append(fig)
        self._add_item(fig)

        return fig

    def add_figure_analysis(self, figure, analysis, **kw):
        fa = proc_FigureAnalysisTable(**kw)
        figure = self.get_figure(figure)
        if figure:
            figure.analyses.append(fa)
            if analysis:
                analysis.figure_analyses.append(fa)
#                self._add_item(fa)

        return fa

    def add_fit_history(self, analysis, **kw):
        hist = proc_FitHistoryTable(**kw)
        if analysis:
            analysis.fit_histories.append(hist)
            analysis.selected_histories.selected_fits = hist

        return hist

    def add_fit(self, history, isotope, **kw):
        f = proc_FitTable(**kw)
        if history:
            history.fits.append(f)
        if isotope:
            isotope.fits.append(f)
        self._add_item(f)
        return f

    def add_flux(self, j, j_err):
        f = flux_FluxTable(j=j, j_err=j_err)
        self._add_item(f)
        return f

    def add_flux_history(self, pos, **kw):
        ft = flux_HistoryTable(**kw)
        if pos:
            ft.position = pos
        return ft

    def add_flux_monitor(self, name, **kw):
        fx = flux_MonitorTable(name=name, **kw)
        return self._add_unique(fx, 'flux_monitor', name)

    def add_irradiation(self, name, production=None, chronology=None):
        production = self.get_irradiation_production(production)
        chronology = self.get_irradiation_chronology(chronology)

        #print production, chronology
        ir = irrad_IrradiationTable(name=name,
                                    production=production,
                                    chronology=chronology)
        self._add_item(ir)
        return ir
#        return self._add_unique(ir, 'irradiation', name)

    def add_irradiation_holder(self, name , **kw):
        ih = irrad_HolderTable(name=name, **kw)
        return self._add_unique(ih, 'irradiation_holder', name)

    def add_irradiation_production(self, **kw):
        ip = irrad_ProductionTable(**kw)
        self._add_item(ip)
        return ip

    def add_irradiation_position(self, pos, labnumber, irrad, level, **kw):
        labnumber = self.get_labnumber(labnumber)
        dbpos = irrad_PositionTable(position=pos, labnumber=labnumber)

        irrad = self.get_irradiation(irrad)
        if isinstance(level, str):
            level = next((li for li in irrad.levels if li.name == level), None)

        if level:
            level.positions.append(dbpos)

        return dbpos

    def add_irradiation_chronology(self, chronblob):
        '''
            startdate1 starttime1%enddate1 endtime1$startdate2 starttime2%enddate2 endtime2
        '''
        ch = irrad_ChronologyTable(chronology=chronblob)
        self._add_item(ch)
        return ch

    def add_irradiation_level(self, name, irradiation, holder, z=0):
        irradiation = self.get_irradiation(irradiation)
        holder = self.get_irradiation_holder(holder)

        irn = irradiation.name if irradiation else None
        hn = holder.name if holder else None
        self.info('adding level {}, holder={} to {}'.format(name, hn, irn))

        level = irrad_LevelTable(name=name, z=z)
        if irradiation is not None:
            irradiation.levels.append(level)

        if holder is not None:
            holder.levels.append(level)

        self._add_item(level)
        return level

    def add_import(self, **kw):
        ih = gen_ImportTable(**kw)
        self._add_item(ih)
        return ih

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

        self._add_item(iso)
        return iso

    def add_isotope_result(self, isotope, history, **kw):
        r = proc_IsotopeResultsTable(**kw)
        if isotope:
            isotope.results.append(r)
            if history:
                history.results.append(r)

        return r

    def add_measurement(self, analysis, analysis_type, mass_spec, **kw):
        meas = meas_MeasurementTable(**kw)
#        if isinstance(analysis, str):

        self._add_item(meas)

        an = self.get_analysis(analysis)
        at = self.get_analysis_type(analysis_type)
        ms = self.get_mass_spectrometer(mass_spec)
        if an:
            an.measurement = meas

        if at:
            at.measurements.append(meas)

        if ms:
            ms.measurements.append(meas)

        return meas

    def add_mass_spectrometer(self, name):
        ms = gen_MassSpectrometerTable(name=name)
        return self._add_unique(ms, 'mass_spectrometer', name)

    def add_material(self, name, **kw):
        mat = gen_MaterialTable(name=name, **kw)
        return self._add_unique(mat, 'material', name)

    def add_molecular_weight(self, name, mass):
        mw = gen_MolecularWeightTable(name=name, mass=mass)
        return self._add_unique(mw, 'molecular_weight', name)

    def add_project(self, name, **kw):
        proj = gen_ProjectTable(name=name, **kw)
        return self._add_unique(proj, 'project', name)

    def add_peak_center(self, analysis, **kw):
        pc = meas_PeakCenterTable(**kw)
        if analysis:
            analysis.peak_center = pc
        return pc

    def add_user(self, name, project=None, **kw):
        user = gen_UserTable(name=name, **kw)
        if isinstance(project, str):
            project = self.get_project(project)

        q = self._build_query_and(gen_UserTable, name, gen_ProjectTable, project)

        addflag = True
        u = q.one()
        if u is not None:
            addflag = not (u.project == project)

        if addflag:
            self.info('adding user {}'.format(name))
            if project is not None:
                project.users.append(user)
            self._add_item(user)
        return user


    def add_sample(self, name, project=None, material=None, **kw):
        project = self.get_project(project)
        material = self.get_material(material)

        sess = self.get_session()
        q = sess.query(gen_SampleTable)
        q = q.filter(and_(gen_SampleTable.name == name,
                          getattr(gen_SampleTable, 'material') == material,
                          getattr(gen_SampleTable, 'project') == project,
                          ))

        try:
            sample = q.one()
        except Exception, e:
            print e
            sample = None

#        print sample
        if sample is None:
            sample = self._add_sample(name, project, material)
        else:
            materialname = material.name if material else None
            projectname = project.name if project else None

            sample_material_name = sample.material.name if sample.material else None
            sample_project_name = sample.project.name if sample.project else None
#            print sample_material_name, sample_project_name, materialname, projectname
            if sample_material_name != materialname and \
                sample_project_name != projectname:
                sample = self._add_sample(name, project, material)

        return sample

    def _add_sample(self, name, project, material):
        sample = gen_SampleTable(name=name)

        if project is not None:
            project.samples.append(sample)

        if material is not None:
            material.samples.append(sample)

        self.info('adding sample {} project={}, material={}'.format(name,
                                                                    project.name if project else 'None',
                                                                    material.name if material else 'None',))

        self._add_item(sample)
        return sample

    def add_script(self, name, blob):
        seed = '{}{}'.format(name, blob)
        ha = self._make_hash(seed)
        scr = self.get_script(ha)
        if scr is None:
            scr = meas_ScriptTable(name=name, blob=blob, hash=ha)
            self._add_item(scr)

        return scr

    def add_selected_histories(self, analysis, **kw):
        sh = analysis.selected_histories
        if sh is None:
            sh = proc_SelectedHistoriesTable(analysis_id=analysis.id)
            analysis.selected_histories = sh
        return sh

    def add_signal(self, isotope, data):
        s = meas_SignalTable(data=data)
        if isotope:
            isotope.signals.append(s)

        return s

    def add_spectrometer_parameters(self, meas, params):
        '''
        '''
        ha = self._make_hash(params)
        sp = self.get_spectrometer_parameters(ha)
        if sp is None:
            sp = meas_SpectrometerParametersTable(hash=ha,
                                                  **params)

        if meas:
            sp.measurements.append(meas)

        return sp

    def add_deflection(self, meas, det, value):
        sp = meas_SpectrometerDeflectionsTable(deflection=value)
        if meas:
            meas.deflections.append(sp)
            det = self.get_detector(det)
            if det:
                det.deflections.append(sp)

        return sp

    def add_labnumber(self, labnumber,
#                      aliquot, 
                      sample=None, irradiation=None, **kw):
        ln = self.get_labnumber(labnumber)
        if ln is None:
            ln = gen_LabTable(labnumber=labnumber,
    #                      aliquot=aliquot,
                          ** kw)

            sample = self.get_sample(sample)

            if sample is not None and ln is not None:
                sample.labnumbers.append(ln)

            self.info('adding labnumber {}'.format(labnumber))
            self._add_item(ln)

        return ln


    def add_analysis(self, labnumber, **kw):
#        if isinstance(labnumber, (str, int, unicode)):
        labnumber = self.get_labnumber(labnumber)

        anal = meas_AnalysisTable(**kw)
        if labnumber is not None:
            labnumber.analyses.append(anal)

        self._add_item(anal)
        return anal

    def add_analysis_type(self, name):
        at = gen_AnalysisTypeTable(name=name)
        return self._add_unique(at, 'analysis_type', name)

    def add_sensitivity(self, ms, **kw):
        si = gen_SensitivityTable(**kw)
        ms = self.get_mass_spectrometer(ms)
        if ms is not None:
            ms.sensitivities.append(si)
        return ms

#===========================================================================
# getters single
#===========================================================================

    def get_analysis_uuid(self, uuid):
#        return meas_AnalysisTable, 'uuid'
        return self._retrieve_item(meas_AnalysisTable, uuid, key='uuid')

    def get_analysis_record(self, value):
        return self._retrieve_item(meas_AnalysisTable, value, key='id')

    def get_analysis(self, value):
        return self._retrieve_item(meas_AnalysisTable, value, key='lab_id')

    def get_analysis_type(self, value):
        return self._retrieve_item(gen_AnalysisTypeTable, value)

    def get_blank(self, value):
        return self._retrieve_item(proc_BlanksTable, value)

    def get_blanks_history(self, value):
        return self._retrieve_item(proc_BlanksHistoryTable, value)

    def get_background(self, value):
        return self._retrieve_item(proc_BackgroundsTable, value)

    def get_backgrounds_history(self, value):
        return self._retrieve_item(proc_BackgroundsHistoryTable, value)

    def get_detector(self, value):
        return self._retrieve_item(gen_DetectorTable, value)

    def get_detector_intercalibration(self, value):
        return self._retrieve_item(proc_DetectorIntercalibrationTable, value)

    def get_detector_intercalibration_history(self, value):
        return self._retrieve_item(proc_DetectorIntercalibrationHistoryTable, value)

    def get_experiment(self, value):
        return self._retrieve_item(meas_ExperimentTable, value)

#    def get_extraction(self, value):
#        return self._retrieve_item(meas_ExtractionTable, value, key='hash')

    def get_extraction_device(self, value):
        return self._retrieve_item(gen_ExtractionDeviceTable, value)

    def get_figure(self, value):
        return self._retrieve_item(proc_FigureTable, value)

    def get_irradiation_chronology(self, value):
        return self._retrieve_item(irrad_ChronologyTable, value)

    def get_irradiation_holder(self, value):
        return self._retrieve_item(irrad_HolderTable, value)

    def get_irradiation_production(self, value):
        return self._retrieve_item(irrad_ProductionTable, value)

    def get_irradiation(self, value):
        return self._retrieve_item(irrad_IrradiationTable, value)

    def get_irradiation_level(self, irrad, level):
        sess = self.get_session()
        q = sess.query(irrad_LevelTable)
        q = q.join(irrad_IrradiationTable)
        q = q.filter(irrad_IrradiationTable.name == irrad)
        q = q.filter(irrad_LevelTable.name == level)
        try:
            return q.one()
        except Exception, _:
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
        except Exception, _:
            pass

    def get_labnumber(self, labnum):
        if isinstance(labnum, str):
            labnum = convert_identifier(labnum)

        try:
            labnum = int(labnum)
        except (ValueError, TypeError):
            pass

        return self._retrieve_item(gen_LabTable, labnum, key='labnumber')

    def get_mass_spectrometer(self, value):
        return self._retrieve_item(gen_MassSpectrometerTable, value)

    def get_material(self, value):
        return self._retrieve_item(gen_MaterialTable, value)

#    def get_measurement(self, value):
#        return self._retrieve_item(meas_MeasurementTable, value, key='hash')

    def get_molecular_weight(self, value):
        return self._retrieve_item(gen_MolecularWeightTable, value)

    def get_project(self, value):
        return self._retrieve_item(gen_ProjectTable, value)

    def get_script(self, value):
        return self._retrieve_item(meas_ScriptTable, value, key='hash')

    def get_sample(self, value):
        return self._retrieve_item(gen_SampleTable, value)

    def get_flux_history(self, value):
        return self._retrieve_item(flux_HistoryTable, value)

    def get_flux_monitor(self, value):
        return self._retrieve_item(flux_MonitorTable, value)
#===============================================================================
# ##getters multiple
#===============================================================================
    def get_analyses(self, **kw):
        return self._get_items(meas_AnalysisTable, globals(), **kw)

#    def get_labnumbers(self, **kw):
#        return self._get_items(gen_LabTable, globals(), **kw)

#    def get_materials(self, **kw):
#        return self._get_items(gen_MaterialTable, globals(), **kw)
#
#    def get_samples(self, **kw):
#        return self._get_items(gen_SampleTable, globals(), **kw)
#
#    def get_users(self, **kw):
#        return self._get_items(gen_UserTable, globals(), **kw)

    '''
        new style using _retrieve_items, _get_items is deprecated. 
        rewrite functionality if required
    '''
    def get_figures(self, project=None):
        if project:
            project = self.get_project(project)
            if project:
                return project.figures

        else:
            return self._retrieve_items(proc_FigureTable)

    def get_aliquots(self, **kw):
        return self._retrieve_items(meas_AnalysisTable, **kw)

    def get_steps(self, **kw):
        return self._retrieve_items(meas_AnalysisTable, **kw)

    def get_materials(self, **kw):
        return self._retrieve_items(gen_MaterialTable, **kw)

    def get_samples(self, **kw):
        return self._retrieve_items(gen_SampleTable, **kw)

    def get_users(self, **kw):
        return self._retrieve_items(gen_UserTable, **kw)

    def get_labnumbers(self, **kw):
        return self._retrieve_items(gen_LabTable, **kw)

    def get_flux_monitors(self, **kw):
        return self._retrieve_items(flux_MonitorTable, **kw)

    def get_irradiations(self, **kw):
        return self._retrieve_items(irrad_IrradiationTable, **kw)

    def get_irradiation_productions(self, **kw):
        return self._retrieve_items(irrad_ProductionTable, **kw)

    def get_projects(self, **kw):
        return self._retrieve_items(gen_ProjectTable, **kw)

    def get_sensitivities(self, **kw):
        return self._retrieve_items(gen_SensitivityTable, **kw)

    def get_mass_spectrometers(self, **kw):
        return self._retrieve_items(gen_MassSpectrometerTable, **kw)

    def get_analysis_types(self, **kw):
        return self._retrieve_items(gen_AnalysisTypeTable, **kw)

    def get_spectrometer_parameters(self, value):
        return self._retrieve_item(meas_SpectrometerParametersTable, value, key='hash')
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

#===============================================================================
# private
#===============================================================================
#    def _get_script(self, name, txt):
#        getter = getattr(self, 'get_{}'.format(name))
#        m = self._hash_factory()
#        m.update(txt)
#        return getter(m.hexdigest())

    def _make_hash(self, txt):
        if isinstance(txt, dict):
            txt = repr(frozenset(txt.items()))

        ha = self._hash_factory(txt)
        return ha.hexdigest()

    def _hash_factory(self, text):
        return hashlib.md5(text)

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
