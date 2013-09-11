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
from traits.api import HasTraits, Instance, Int, Str, Float, Dict
# from traitsui.api import View, Item
#============= standard library imports ========================
import time
from datetime import datetime
from uncertainties import ufloat
from collections import namedtuple
#============= local library imports  ==========================
from src.processing.arar_age import ArArAge
from src.processing.analyses.summary import AnalysisSummary
from src.processing.analyses.db_summary import DBAnalysisSummary
# from src.database.orms.isotope_orm import meas_AnalysisTable
# from src.database.records.isotope_record import IsotopeRecordView
from src.experiment.utilities.identifier import make_runid
# from src.constants import NULL_STR
from src.processing.isotope import Isotope, Blank, Baseline, Sniff
from src.constants import ARGON_KEYS

Fit = namedtuple('Fit', 'fit filter_outliers filter_outlier_iterations filter_outlier_std_devs')



class Analysis(ArArAge):
    analysis_summary_klass = AnalysisSummary
    analysis_summary = Instance(AnalysisSummary)
    def flush(self, *args, **kw):
        '''
        '''
        return

    def commit(self, *args, **kw):
        '''
        '''
        return

    def sync(self, *args, **kw):
        '''
        '''
        return

    def _analysis_summary_default(self):
        return self.analysis_summary_klass(model=self)

class DBAnalysis(Analysis):
    analysis_summary_klass = DBAnalysisSummary
    status = Int
    record_id = Str
    uuid = Str

    sample = Str
    material = Str
    project = Str
    comment = Str
    mass_spectrometer = Str
    extract_device = Str
    position = Str
    extract_value = Float
    extract_units = Str
    cleanup_duration = Float
    extract_duration = Float
    analysis_type = Str

    ic_factors = Dict

    def get_baseline_corrected_signal_dict(self):
        get = lambda iso: iso.baseline_corrected_value()
        return self._get_isotope_dict(get)

    def get_baseline_dict(self):
        get = lambda iso: iso.baseline.uvalue
        return self._get_isotope_dict(get)

    def _get_isotope_dict(self, get):
        d = dict()
        for ki in ARGON_KEYS:
            if self.isotopes.has_key(ki):
                v = get(self.isotopes[ki])
            else:
                v = ufloat(0, 0)
            d[ki] = v

        return d


    def get_ic_factor(self, det):
        if det in self.ic_factors:
            r = self.ic_factors[det]
        else:
            r = (1, 0)
        return r

    def _get_ic_factors(self, meas_analysis):
        icfs = dict()
        if meas_analysis.selected_histories:
            hist = meas_analysis.selected_histories.selected_detector_intercalibration
            if hist:
                for ic in hist.detector_intercalibrations:
                    icfs[ic.detector.name] = (ic.user_value, ic.user_error)

#                 icf = next((ic for ic in hist.detector_intercalibrations
#                             if ic.detector.name == det), None)
#                 if icf:
#                     r = icf.user_value, icf.user_error

        return icfs

    def flush(self):
        '''
        '''
    def commit(self, sess):
        '''
            use the provided db adapter to 
            save changes to database
        '''

    def sync(self, obj):
        '''
            copy values from meas_AnalysisTable
            and other associated tables
        '''

        self._sync(obj)


    def _get_position(self, extraction):
        r = ''
        pos = extraction.positions

#         pos = self._get_extraction_value('positions')
#         if pos != NULL_STR:
        pp = []
        for pi in pos:
            pii = pi.position

            if pii:
                pp.append(pii)
            else:
                ppp = []
                x, y, z = pi.x, pi.y, pi.z
                if x is not None and y is not None:
                    ppp.append(x)
                    ppp.append(y)
                if z is not None:
                    ppp.append(z)

                if ppp:
                    pp.append('({})'.format(','.join(ppp)))

        if pp:
            r = ','.join(map(str, pp))

        return r


    def _sync_extraction(self, meas_analysis):
        extraction = meas_analysis.extraction
        if extraction:
            self.extract_device = self._get_extraction_device(extraction)
            self.extract_value = extraction.extract_value
#             self.extract_units = extraction.extract_units
            self.cleanup = extraction.cleanup_duration
            self.duration = extraction.extract_duration
            self.position = self._get_position(extraction)

    def _sync(self, meas_analysis):
        # copy meas_analysis attrs
        nocast = lambda x: x
        attrs = [
                 ('labnumber', 'labnumber', lambda x: x.identifier),
                 ('aliquot', 'aliquot', int),
                 ('step', 'step', str),
                 ('status', 'status', int),
                 ('comment', 'comment', str),
                 ('uuid', 'uuid', str),
                 ('_timestamp', 'analysis_timestamp',
                    lambda x: time.mktime(x.timetuple())
                 ),
               ]
        for key, attr, cast in attrs:
            v = getattr(meas_analysis, attr)
            setattr(self, key, cast(v))

#         analts = analysis.analysis_timestamp
#         return time.mktime(analts.timetuple())
        # copy related table attrs
        self._sync_irradiation(meas_analysis)
        self._sync_isotopes(meas_analysis)
        self._sync_detector_info(meas_analysis)
        self._sync_extraction(meas_analysis)
        self._sync_analysis_info(meas_analysis)

        self.record_id = make_runid(self.labnumber, self.aliquot, self.step)



    def _sync_analysis_info(self, meas_analysis):
        self.sample = self._get_sample(meas_analysis)
        self.material = self._get_material(meas_analysis)
        self.project = self._get_project(meas_analysis)
        self.rundate = self._get_rundate(meas_analysis)
        self.runtime = self._get_runtime(meas_analysis)
        self.mass_spectrometer = self._get_mass_spectrometer(meas_analysis)
        self.analysis_type = self._get_analysis_type(meas_analysis)

    def _sync_detector_info(self, meas_analysis):
        self.discrimination = self._get_discrimination(meas_analysis)
        self.ic_factors = self._get_ic_factors(meas_analysis)

    def _sync_irradiation(self, meas_analysis):
        ln = meas_analysis.labnumber
        self.irradiation_info = self._get_irradition_info(ln)
        self.j = self._get_j(ln)
        self.production_ratios = self._get_production_ratios(ln)

    def _sync_isotopes(self, meas_analysis):
        self.isotopes = self._get_isotopes(meas_analysis, unpack=True)

#         self._load_blanks(meas_analysis)
#         self._load_sniffs(meas_analysis)

#         self._load_peak_center(meas_analysis)

#     def _load_signals(self, meas_analysis, unpack=True):


    def _get_baselines(self, isotopes, meas_analysis, unpack):
        for dbiso in meas_analysis.isotopes:
            if not dbiso.molecular_weight:
                continue

            name = dbiso.molecular_weight.name
            det = dbiso.detector.name

            iso = isotopes[name]

            kw = dict(
                      dbrecord=dbiso,
                      name=name, detector=det)
            if dbiso.kind == 'baseline':
                result = None
                if dbiso.results:
                    result = dbiso.results[-1]

                r = Baseline(dbresult=result,
                             **kw)
                fit = self._get_db_fit(meas_analysis, name, 'baseline')
                if fit is None:
                    fit = Fit(fit='average_sem', filter_outliers=True,
                              filter_outlier_iterations=1,
                              filter_outlier_std_devs=2)
                r.set_fit(fit)
                iso.baseline = r

            elif dbiso.kind == 'sniff':
                r = Sniff(**kw)
                iso.sniff = r

#
#     def _get_blanks(self, isotopes, meas_analysis):
# #         blanks = self._get_blanks()
#
#
#         keys = isotopes.keys()
#         if blanks:
#             for bi in blanks:
#                 for ba in bi.blanks:
#                     isok = ba.isotope
#                     if isok in keys and isotopes.has_key(isok):
#                         r = Blank(dbrecord=ba, name=isok)
#                         isotopes[isok].blank = r
#                         keys.remove(isok)
#                         if not keys:
#                             break
#
#                 if not keys:
#                     break

    def _get_isotopes(self, meas_analysis, unpack):
        isotopes = dict()
        self._get_signals(isotopes, meas_analysis, unpack)
        self._get_baselines(isotopes, meas_analysis, unpack)
#         self._get_blanks(isotopes, meas_analysis)

        return isotopes


    def _get_db_fit(self, meas_analysis, name, kind):
        try:
            selhist = meas_analysis.selected_histories
            selfithist = selhist.selected_fits
            fits = selfithist.fits
            return next((fi for fi in fits
                                if fi.isotope.kind == kind and \
                                    fi.isotope.molecular_weight.name == name
                                    ), None)


        except AttributeError:
            pass


    def _get_signals(self, isodict, meas_analysis, unpack):
        for iso in meas_analysis.isotopes:
            if not iso.kind == 'signal' or not iso.molecular_weight:
                continue

            result = None
            if iso.results:
                result = iso.results[-1]

            name = iso.molecular_weight.name
            if name not in isodict:
                det = iso.detector.name

                r = Isotope(
                            dbrecord=iso,
                            dbresult=result,

                            name=name,
                            detector=det,
#                             refit=refit
                            unpack=unpack
                            )

                fit = None
                fit = self._get_db_fit(meas_analysis, name, 'signal')
                if fit is None:
                    fit = Fit(fit='linear', filter_outliers=True,
                              filter_outlier_iterations=1,
                              filter_outlier_std_devs=2)
                r.set_fit(fit)
                isodict[name] = r


#     def _load_blanks(self, meas_analysis):
#         pass
#     def _load_sniffs(self, meas_analysis):
#         pass
    def _load_peak_center(self, meas_analysis):
        pass

    def _get_extraction_device(self, extraction):
        r = ''
        if extraction.extraction_device:
            r = extraction.extraction_device.name
        return r
#===============================================================================
#
#===============================================================================
    def _get_analysis_type(self, meas_analysis):
        r = ''
        if meas_analysis:
            r = meas_analysis.measurement.analysis_type.name
        return r

    def _get_mass_spectrometer(self, meas_analysis):
        return meas_analysis.measurement.mass_spectrometer.name.lower()

    def _get_discrimination(self, meas_analysis):
        return ufloat(1, 0)

    def _get_sample(self, meas_analysis):
        ln = meas_analysis.labnumber
        r = ''
        if ln.sample:
            r = ln.sample.name
        return r

    def _get_material(self, meas_analysis):
        m = ''
        ln = meas_analysis.labnumber
        if ln.sample and ln.sample.material:
            m = ln.sample.material.name
        return m

    def _get_project(self, meas_analysis):
        ln = meas_analysis.labnumber
        sample = ln.sample
        r = ''
        if sample and sample.project:
            r = sample.project.name
        return r

    def _get_rundate(self, meas_analysis):
        if meas_analysis.analysis_timestamp:
            date = meas_analysis.analysis_timestamp.date()
            return date.strftime('%Y-%m-%d')

    def _get_runtime(self, meas_analysis):
        if meas_analysis.analysis_timestamp:
            ti = meas_analysis.analysis_timestamp.time()
            return ti.strftime('%H:%M:%S')
#===============================================================================
# irradiation
#===============================================================================
    def _get_timestamp(self):
        return self._timestamp


    def _get_j(self, ln):
        s, e = 1, 0
        if ln.selected_flux_history:
            f = ln.selected_flux_history.flux
            s = f.j
            e = f.j_err
        return ufloat(s, e)

    def _get_production_ratios(self, ln):
        lev = self._get_irradiation_level(ln)
        cak = 1
        clk = 1
        if lev:
            ir = lev.irradiation
            pr = ir.production
            cak, clk = pr.Ca_K, pr.Cl_K

        return dict(Ca_K=cak, Cl_K=clk)

    def _get_irradiation_level(self, ln):
        if ln:
            if ln.irradiation_position:
                l = ln.irradiation_position.level

                return l

    def _get_irradition_info(self, ln):
        '''
            return k4039, k3839,k3739, ca3937, ca3837, ca3637, cl3638, chronsegments, decay_time
        '''
        prs = (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), [], 1

        irradiation_level = self._get_irradiation_level(ln)
        if irradiation_level:
            irradiation = irradiation_level.irradiation
            if irradiation:
                self.irradiation = irradiation.name
                self.irradiation_level = irradiation_level.name


                pr = irradiation.production
                if pr:
                    prs = []
                    for pi in ['K4039', 'K3839', 'K3739', 'Ca3937', 'Ca3837', 'Ca3637', 'Cl3638']:
                        v, e = getattr(pr, pi), getattr(pr, '{}_err'.format(pi))
                        prs.append((v if v is not None else 1, e if e is not None else 0))

#                    prs = [(getattr(pr, pi), getattr(pr, '{}_err'.format(pi)))
#                           for pi in ['K4039', 'K3839', 'K3739', 'Ca3937', 'Ca3837', 'Ca3637', 'Cl3638']]

                chron = irradiation.chronology
#                def convert_datetime(x):
#                    try:
#                        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
#                    except ValueError:
#                        pass
#                convert_datetime = lambda x:datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

                convert_days = lambda x: x.total_seconds() / (60. * 60 * 24)
                if chron:
                    doses = chron.get_doses()
#                    chronblob = chron.chronology
#
#                    doses = chronblob.split('$')
#                    doses = [di.strip().split('%') for di in doses]
#
#                    doses = [map(convert_datetime, d) for d in doses if d]

                    analts = self.timestamp
                    if isinstance(analts, float):
                        analts = datetime.fromtimestamp(analts)

                    segments = []
                    for st, en in doses:
                        if st is not None and en is not None:
                            dur = en - st
                            dt = analts - st
                            segments.append((1, convert_days(dur), convert_days(dt)))

                    decay_time = 0
                    d_o = doses[0][0]
                    if d_o is not None:
                        decay_time = convert_days(analts - doses[0][0])

#                    segments = [(1, convert_days(ti)) for ti in durs]
                    prs.append(segments)
                    prs.append(decay_time)

        return prs


if __name__ == '__main__':
    pass
#============= EOF =============================================
