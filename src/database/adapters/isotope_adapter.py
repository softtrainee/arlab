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
from sqlalchemy.sql.expression import  and_, func
# import hashlib
from cStringIO import StringIO
#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from src.database.selectors.isotope_selector import IsotopeAnalysisSelector

# meas_
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_ExperimentTable, meas_ExtractionTable, meas_IsotopeTable, meas_MeasurementTable, \
    meas_SpectrometerParametersTable, meas_SpectrometerDeflectionsTable, \
    meas_SignalTable, meas_PeakCenterTable, meas_PositionTable, \
    meas_ScriptTable, meas_MonitorTable, loading_LoadTable, gen_LoadHolderTable, \
    loading_PositionsTable, proc_FigurePrefTable


# med_
from src.database.orms.isotope_orm import med_ImageTable, med_SnapshotTable

# proc_
from src.database.orms.isotope_orm import proc_DetectorIntercalibrationHistoryTable, \
    proc_DetectorIntercalibrationTable, proc_SelectedHistoriesTable, \
    proc_BlanksTable, proc_BackgroundsTable, proc_BlanksHistoryTable, proc_BackgroundsHistoryTable, \
    proc_BlanksSetTable, proc_BackgroundsSetTable, proc_DetectorIntercalibrationSetTable, \
    proc_DetectorParamHistoryTable, proc_IsotopeResultsTable, proc_FitHistoryTable, \
    proc_FitTable, proc_DetectorParamTable, proc_NotesTable, proc_FigureTable, proc_FigureAnalysisTable

# irrad_
from src.database.orms.isotope_orm import irrad_HolderTable, irrad_ProductionTable, irrad_IrradiationTable, \
    irrad_ChronologyTable, irrad_LevelTable, irrad_PositionTable

# flux_
from src.database.orms.isotope_orm import flux_FluxTable, flux_HistoryTable, flux_MonitorTable

# gen_
from src.database.orms.isotope_orm import gen_DetectorTable, gen_ExtractionDeviceTable, gen_ProjectTable, \
    gen_MolecularWeightTable, gen_MaterialTable, gen_MassSpectrometerTable, \
    gen_SampleTable, gen_LabTable, gen_AnalysisTypeTable, gen_UserTable, \
    gen_ImportTable, gen_SensitivityTable


from src.database.core.functions import delete_one

# from src.experiment.utilities.identifier import convert_identifier
# from src.repo.repository import Repository, ZIPRepository
# from src.paths import paths
# import binascii
import hashlib
from sqlalchemy.orm.exc import NoResultFound

# @todo: change rundate and runtime to DateTime columns

class IsotopeAdapter(DatabaseAdapter):
    '''
        new style adapter 
        be careful with super methods you use they may deprecate
        
        using decorators is the new model
    '''

    selector_klass = IsotopeAnalysisSelector

    def add_load(self, name, **kw):
        l = loading_LoadTable(name=name, **kw)
        self._add_item(l)
        return l

    def add_load_position(self, labnumber, **kw):
        lp = loading_PositionsTable(**kw)

        ln = self.get_labnumber(labnumber)
        if ln:
            lp.lab_identifier = ln.identifier

        self._add_item(lp)
        return lp

    def get_loadtable(self, name=None):
        lt = None
        if name is not None:
            lt = self._retrieve_item(loading_LoadTable, name)
        else:
            q = self.get_query(loading_LoadTable)
            if q:
                q = q.order_by(loading_LoadTable.create_date.desc())
                try:
                    lt = q.first()
                except Exception, e:
                    import traceback
                    traceback.print_exc()

        return lt
#===============================================================================
#
#===============================================================================
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
                item.history_id = history.id
#                 getattr(history, key).append(item)
            except AttributeError, e:
                self.debug('add_series_item key={}, error={}'.format(key, e))
                setattr(history, key, item)
            self._add_item(item)

        return item

    def add_import(self, **kw):
        dbimport = gen_ImportTable(**kw)
        self._add_item(dbimport)
        return dbimport

    def add_snapshot(self, path, **kw):
        dbsnap = med_SnapshotTable(path, **kw)
        self._add_item(dbsnap)
        return dbsnap

    def add_image(self, name, image=None):
        if image is not None:
            if not isinstance(image, str):
                buf = StringIO()
                image.save(buf)
                image = buf.getvalue()

        dbim = med_ImageTable(name=name, image=image)
        self._add_item(dbim)
        return dbim

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

    def add_detector_parameter_history(self, analysis, **kw):
        return self._add_history('DetectorParam', analysis, **kw)

    def add_detector_parameter(self, history, **kw):
        obj = proc_DetectorParamTable(**kw)
        a = self._add_item(obj)
        if history:
            history.parameters.append(a)
            obj.history_id = history.id

        return a

    def add_detector_intercalibration_history(self, analysis, **kw):
        return self._add_history('DetectorIntercalibration', analysis, **kw)

    def add_detector_intercalibration(self, history, detector, **kw):
        a = self._add_series_item('DetectorIntercalibration',
                                     'detector_intercalibrations', history, **kw)
        if a:
            detector = self.get_detector(detector)
            if detector:
                a.detector_id = detector.id
#             detector.intercalibrations.append(a)

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
            ex.extract_device_id = ed.id

#             ed.extractions.append(ex)

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
            fig.project_id = project.id

        self._add_item(fig)

        return fig
    def add_figure_preference(self, figure, **kw):
        fa = proc_FigurePrefTable(**kw)
        figure = self.get_figure(figure)
        if figure:
            self.info('adding preference to figure {}'.format(figure.name))
            fa.figure_id = figure.id
        self._add_item(fa)
        return fa

    def add_figure_analysis(self, figure, analysis, **kw):
        fa = proc_FigureAnalysisTable(**kw)
        figure = self.get_figure(figure)
        if figure:
            fa.figure_id = figure.id

        analysis = self.get_analysis(analysis)
        if analysis:
            fa.analysis_id = analysis.id

        self._add_item(fa)
        return fa


#         if figure:
#             figure.analyses.append(fa)
#             if analysis:
#                 analysis.figure_analyses.append(fa)
# #                self._add_item(fa)
#
#         return fa

    def add_fit_history(self, analysis, **kw):
        kw['user'] = self.save_username
        hist = proc_FitHistoryTable(**kw)
        if analysis:
            hist.analysis_id=analysis.id
        
#            analysis.fit_histories.append(hist)
            analysis.selected_histories.selected_fits = hist

        return hist

    def add_fit(self, history, isotope, **kw):
        f = proc_FitTable(**kw)
        if history:
#             history.fits.append(f)
            f.history_id = history.id

        if isotope:
            f.isotope_id = isotope.id
#             isotope.fits.append(f)

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

        ir = irrad_IrradiationTable(name=name,
                                    production=production,
                                    chronology=chronology)
        self._add_item(ir)
        return ir

    def add_load_holder(self, name, **kw):
        lh = gen_LoadHolderTable(name=name, **kw)
        return self._add_unique(lh, 'load_holder', name)

    def add_irradiation_holder(self, name , **kw):
        ih = irrad_HolderTable(name=name, **kw)
        return self._add_unique(ih, 'irradiation_holder', name)

    def add_irradiation_production(self, **kw):
        ip = irrad_ProductionTable(**kw)
        self._add_item(ip)
        return ip

    def add_irradiation_position(self, pos, labnumber, irrad, level, **kw):
        if labnumber:
            labnumber = self.get_labnumber(labnumber)

        irrad = self.get_irradiation(irrad)
        if isinstance(level, (str, unicode)):
            level = next((li for li in irrad.levels if li.name == level), None)

        if level:
            dbpos = next((di for di in level.positions if di.position == pos), None)
            if not dbpos:
                dbpos = irrad_PositionTable(position=pos,
                                            labnumber=labnumber, **kw)
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
        if irradiation:
            irn = irradiation.name
            level = next((li for li in irradiation.levels if li.name == name), None)
            if not level:
                holder = self.get_irradiation_holder(holder)
    #             irn = irradiation.name if irradiation else None
                hn = holder.name if holder else None
                self.info('adding level {}, holder={} to {}'.format(name, hn, irn))

                level = irrad_LevelTable(name=name, z=z)
                if irradiation is not None:
                    irradiation.levels.append(level)

                if holder is not None:
                    holder.levels.append(level)

                self._add_item(level)
            return level
        else:
            self.info('no irradiation to add to as this level. irradiation={}'.format(irradiation))


#    def add_import(self, **kw):
#        ih = gen_ImportTable(**kw)
#        self._add_item(ih)
#        return ih

    def add_isotope(self, analysis, molweight, det, **kw):
        iso = meas_IsotopeTable(**kw)
        analysis = self.get_analysis(analysis)
        if analysis:
            iso.analysis_id = analysis.id
#            analysis.isotopes.append(iso)

        det = self.get_detector(det)
        if det is not None:
            iso.detector_id = det.id
#            det.isotopes.append(iso)

        molweight = self.get_molecular_weight(molweight)
        if molweight is not None:
            iso.molecular_weight_id = molweight.id
#            molweight.isotopes.append(iso)

        self._add_item(iso)
        return iso

    def add_isotope_result(self, isotope, history, **kw):
        r = proc_IsotopeResultsTable(**kw)
        if isotope:
            r.isotope_id = isotope.id
#             isotope.results.append(r)
            if history:
                r.history_id = history.id
#                 history.results.append(r)

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
#             at.measurements.append(meas)
            meas.analysis_type_id = at.id
        if ms:
            meas.mass_spectrometer_id = ms.id
#             ms.measurements.append(meas)

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

    def add_user(self, name, **kw):
        user = gen_UserTable(name=name, **kw)
        self._add_item(user)
        return user
#    def add_user(self, name, **kw):
#        user = gen_UserTable(name=name, **kw)
#        if isinstance(project, str):
#            project = self.get_project(project)
#
#        q = self._build_query_and(gen_UserTable, name, gen_ProjectTable, project)
#
#        addflag = True
#        u = q.one()
#        if u is not None:
#            addflag = not (u.project == project)
#
#        if addflag:
#            self.info('adding user {}'.format(name))
#            if project is not None:
#                project.users.append(user)
#            self._add_item(user)
#        return user


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
            s.isotope_id=isotope.id
#            isotope.signals.append(s)
        self._add_item(s)
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
            meas.spectrometer_parameters_id = sp.id

        return sp

    def add_deflection(self, meas, det, value):
        sp = meas_SpectrometerDeflectionsTable(deflection=value)
        if meas:
            sp.measurement_id = meas.id
#             meas.deflections.append(sp)
            det = self.get_detector(det)
            if det:
                sp.detector_id = det.id
#                 det.deflections.append(sp)

        return sp

    def add_labnumber(self, labnumber,
#                      aliquot,
                      sample=None,
                      unique=True,
                      **kw):
        if unique:
            ln = self.get_labnumber(labnumber)
        else:
            ln = None

        if ln is None:
            ln = gen_LabTable(identifier=labnumber, **kw)

            sample = self.get_sample(sample)
            if sample is not None:
                ln.sample_id = sample.id
#                 sample.labnumbers.append(ln)
                sname = sample.name
            else:
                self.debug('sample {} does not exist'.format(sample))
                sname = ''

            self.info('adding labnumber={} sample={}'.format(labnumber, sname))
            self._add_item(ln)

        return ln

    def add_analysis(self, labnumber, **kw):
#        if isinstance(labnumber, (str, int, unicode)):
        labnumber = self.get_labnumber(labnumber)

        anal = meas_AnalysisTable(**kw)
        if labnumber is not None:
            anal.lab_id = labnumber.id
#             labnumber.analyses.append(anal)

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
    def get_last_labnumber(self):
        sess = self.get_session()
        q = sess.query(gen_LabTable)
        q = q.order_by(func.abs(gen_LabTable.identifier).desc())
        try:
            return q.first()
        except NoResultFound, e:
            self.debug('get last labnumber {}'.format(e))
            return

    def get_last_analysis(self, ln, aliquot=None):
        ln = self.get_labnumber(ln)
        if not ln:
            return

        sess = self.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.join(gen_LabTable)
        q = q.filter(getattr(meas_AnalysisTable, 'labnumber') == ln)
        if aliquot:
            q = q.filter(meas_AnalysisTable.aliquot == aliquot)
#             q = q.order_by(meas_AnalysisTable.step.asc())

        q = q.order_by(meas_AnalysisTable.analysis_timestamp.desc())
#         q = q.limit(1)
        try:
            return q.first()
        except NoResultFound, e:
            self.debug('get last analysis {}'.format(e))
            return

    def get_unique_analysis(self, ln, ai, step=None):
        sess = self.get_session()

        ln = self.get_labnumber(ln)
        if not ln:
            return

        q = sess.query(meas_AnalysisTable)
        q = q.join(gen_LabTable)
        q = q.filter(getattr(meas_AnalysisTable, 'labnumber') == ln)

        try:
            ai = int(ai)
        except ValueError:
            return

        q = q.filter(meas_AnalysisTable.aliquot == int(ai))
        if step:
            q = q.filter(meas_AnalysisTable.step == step)
        q = q.limit(1)
        try:
            return q.one()
        except NoResultFound:
            return

    def get_analysis_uuid(self, value):
#         return self.get_analysis(value, key)
# #        return meas_AnalysisTable, 'uuid'
        return self._retrieve_item(meas_AnalysisTable, value, key='uuid')

    def get_analysis_record(self, value):
        return self._retrieve_item(meas_AnalysisTable, value, key='id')

    def get_image(self, name):
        return self._retrieve_item(med_ImageTable, name, key='name')

    def get_analysis(self, value, key='lab_id'):
        return self._retrieve_item(meas_AnalysisTable, value, key=key)

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

    def get_detector_intercalibrations_history(self, *args, **kw):
        return self.get_detector_intercalibration_history(*args, **kw)

    def get_experiment(self, value, key='name'):
        return self._retrieve_item(meas_ExperimentTable, value, key)

    def get_extraction(self, value, key='id'):
        return self._retrieve_item(meas_ExtractionTable, value, key)

#    def get_extraction(self, value):
#        return self._retrieve_item(meas_ExtractionTable, value, key='hash')

    def get_extraction_device(self, value):
        return self._retrieve_item(gen_ExtractionDeviceTable, value)

    def get_figure(self, value):
        return self._retrieve_item(proc_FigureTable, value)

    def get_irradiation_chronology(self, value):
        return self._retrieve_item(irrad_ChronologyTable, value)

    def get_load_holder(self, value):
        return self._retrieve_item(gen_LoadHolderTable, value)

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

    def get_labnumber(self, labnum, **kw):
        return self._retrieve_item(gen_LabTable, labnum,
                                   key='identifier',
                                   **kw
                                   )
#        if isinstance(labnum, str):
#            labnum = convert_identifier(labnum)
#
#        try:
#            labnum = int(labnum)
#        except (ValueError, TypeError):
#            pass
#
#        return self._retrieve_item(gen_LabTable, labnum, key='labnumber')

    def get_mass_spectrometer(self, value):
        return self._retrieve_item(gen_MassSpectrometerTable, value)

    def get_material(self, value):
        return self._retrieve_item(gen_MaterialTable, value)

#    def get_measurement(self, value):
#        return self._retrieve_item(meas_MeasurementTable, value, key='hash')

    def get_molecular_weight(self, value):
        return self._retrieve_item(gen_MolecularWeightTable, value)

    def get_user(self, value):
        return self._retrieve_item(gen_UserTable, value)

    def get_project(self, value):
        return self._retrieve_item(gen_ProjectTable, value)

    def get_script(self, value):
        return self._retrieve_item(meas_ScriptTable, value, key='hash')

    def get_sample(self, value, project=None):
        kw = dict()
        if project:
            kw['joins'] = [gen_ProjectTable]
            kw['filters'] = [gen_ProjectTable.name == project]

        return self._retrieve_item(gen_SampleTable, value, **kw)

    def get_flux_history(self, value):
        return self._retrieve_item(flux_HistoryTable, value)

    def get_flux_monitor(self, value):
        return self._retrieve_item(flux_MonitorTable, value)
#===============================================================================
# ##getters multiple
#===============================================================================
#     def get_analyses(self, **kw):
#         return self._get_items(meas_AnalysisTable, globals(), **kw)

    '''
        new style using _retrieve_items, _get_items is deprecated. 
        rewrite functionality if required
    '''
    def get_analyses(self, **kw):
        '''
            kw: meas_Analysis attributes
        '''
        q = self.sess.query(meas_AnalysisTable)
        for k, v in kw.iteritems():
            q = q.filter(getattr(meas_AnalysisTable, k) == v)

        q = q.order_by(meas_AnalysisTable.analysis_timestamp.desc())

        return q.all()

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

    def get_samples(self, project=None, **kw):
        if project:
            f = []
            if 'filters' in kw:
                f = kw['filters']
            f.append(gen_ProjectTable.name == project)
            kw['filters'] = f

            j = []
            if 'joins' in kw:
                j = kw['joins']
            j.append(gen_ProjectTable)
            kw['joins'] = j

        return self._retrieve_items(gen_SampleTable, **kw)

    def get_users(self, **kw):
        return self._retrieve_items(gen_UserTable, **kw)

    def get_labnumbers(self, last=None, **kw):
        return self._retrieve_items(gen_LabTable, **kw)

    def get_flux_monitors(self, **kw):
        return self._retrieve_items(flux_MonitorTable, **kw)

    def get_irradiations(self, **kw):
#        return self._retrieve_items(irrad_IrradiationTable, order=irrad_IrradiationTable.name, ** kw)
        return self._retrieve_items(irrad_IrradiationTable,
                                    order=irrad_IrradiationTable.name.desc(),
                                    **kw)

    def get_irradiation_productions(self, **kw):
        return self._retrieve_items(irrad_ProductionTable, **kw)

    def get_projects(self, **kw):
        return self._retrieve_items(gen_ProjectTable, **kw)

    def get_sensitivities(self, **kw):
        return self._retrieve_items(gen_SensitivityTable, **kw)

    def get_mass_spectrometers(self, **kw):
        return self._retrieve_items(gen_MassSpectrometerTable, **kw)

    def get_extraction_devices(self, **kw):
        return self._retrieve_items(gen_ExtractionDeviceTable, **kw)

    def get_analysis_types(self, **kw):
        return self._retrieve_items(gen_AnalysisTypeTable, **kw)

    def get_spectrometer_parameters(self, value):
        return self._retrieve_item(meas_SpectrometerParametersTable, value, key='hash')

    def get_load_holders(self, **kw):
        return self._retrieve_items(gen_LoadHolderTable, **kw)

    def get_loads(self, **kw):
        return self._retrieve_items(loading_LoadTable, **kw)

    def get_molecular_weights(self, **kw):
        return self._retrieve_items(gen_MolecularWeightTable, **kw)
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
