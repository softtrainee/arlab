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
from traits.api import HasTraits, Dict, Property, cached_property, \
    Event, Bool, Instance, Float
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
import datetime
from uncertainties import ufloat

#============= local library imports  ==========================
from src.processing.argon_calculations import calculate_arar_age
from src.processing.arar_constants import ArArConstants
from src.processing.isotope import Isotope

def AgeProperty():
    return Property(depends_on='age_dirty')


class ArArAge(HasTraits):
    include_j_error = Bool(True)
    include_irradiation_error = Bool(True)
    include_decay_error = Bool(False)

    arar_result = Dict

    rad40 = AgeProperty()
    k39 = AgeProperty()
    rad40_percent = AgeProperty()

    kca = AgeProperty()
    cak = AgeProperty()
    kcl = AgeProperty()
    clk = AgeProperty()

    # ratios
    Ar40_39 = AgeProperty()
    Ar37_39 = AgeProperty()
    Ar36_39 = AgeProperty()

    j = AgeProperty()

    sensitivity = Property
    sensitivity_multiplier = Property
    _sensitivity_multiplier = Float

    labnumber_record = None

    timestamp = Property
    irradiation_info = Property
    irradiation_level = Property
    irradiation_position = Property
    production_ratios = Property

#    signals = AgeProperty()
#    _signals = Dict
    isotopes = Dict

    age = Property(depends_on='include_decay_error, include_j_error, include_irradiation_error,age_dirty')
    age_error = AgeProperty()
    age_error_wo_j = AgeProperty()
    age_dirty = Event

    Ar40 = AgeProperty()
    Ar39 = AgeProperty()
    Ar38 = AgeProperty()
    Ar37 = AgeProperty()
    Ar36 = AgeProperty()
    Ar40_error = AgeProperty()
    Ar39_error = AgeProperty()
    Ar38_error = AgeProperty()
    Ar37_error = AgeProperty()
    Ar36_error = AgeProperty()

    moles_Ar40 = AgeProperty()
    moles_K39 = AgeProperty()


    ic_factor = Property(depends_on='arar_constants:[ic_factor_v, ic_factor_e]')

    arar_constants = Instance(ArArConstants, ())
    def __init__(self, *args, **kw):
        super(ArArAge, self).__init__(*args, **kw)
#        if self.application:
        try:
            bind_preference(self.arar_constants, 'lambda_b_v', 'pychron.experiment.constants.lambda_b')
            bind_preference(self.arar_constants, 'lambda_b_e', 'pychron.experiment.constants.lambda_b_error')
            bind_preference(self.arar_constants, 'lambda_e_v', 'pychron.experiment.constants.lambda_e')
            bind_preference(self.arar_constants, 'lambda_e_e', 'pychron.experiment.constants.lambda_e_error')
            bind_preference(self.arar_constants, 'lambda_Cl36_v', 'pychron.experiment.constants.lambda_Cl36')
            bind_preference(self.arar_constants, 'lambda_Cl36_e', 'pychron.experiment.constants.lambda_Cl36_error')
            bind_preference(self.arar_constants, 'lambda_Ar37_v', 'pychron.experiment.constants.lambda_Ar37')
            bind_preference(self.arar_constants, 'lambda_Ar37_e', 'pychron.experiment.constants.lambda_Ar37_error')
            bind_preference(self.arar_constants, 'lambda_Ar39_v', 'pychron.experiment.constants.lambda_Ar39')
            bind_preference(self.arar_constants, 'lambda_Ar39_e', 'pychron.experiment.constants.lambda_Ar39_error')

            bind_preference(self.arar_constants, 'atm4036_v', 'pychron.experiment.constants.Ar40_Ar36_atm')
            bind_preference(self.arar_constants, 'atm_4036_e', 'pychron.experiment.constants.Ar40_Ar36_atm_error')
            bind_preference(self.arar_constants, 'atm4038_v', 'pychron.experiment.constants.Ar40_Ar38_atm')
            bind_preference(self.arar_constants, 'atm_4038_e', 'pychron.experiment.constants.Ar40_Ar38_atm_error')

            bind_preference(self.arar_constants, 'k3739_mode', 'pychron.experiment.constants.Ar37_Ar39_mode')
            bind_preference(self.arar_constants, 'k3739_v', 'pychron.experiment.constants.Ar37_Ar39')
            bind_preference(self.arar_constants, 'k3739_e', 'pychron.experiment.constants.Ar37_Ar39_error')

    #        bind_preference(self, 'abundance_sensitivity', 'pychron.spectrometer.abundance_sensitivity')
#             wr = weakref.ref(self)()
            wr = self.arar_constants
            bind_preference(wr, 'age_units', 'pychron.experiment.general_age.age_units')
            bind_preference(wr, 'abundance_sensitivity', 'pychron.experiment.constants.abundance_sensitivity')
            bind_preference(wr, 'ic_factor_v', 'pychron.experiment.constants.ic_factor')
            bind_preference(wr, 'ic_factor_e', 'pychron.experiment.constants.ic_factor_error')

        except AttributeError, e:
            print 'arar init', e

    def get_error_component(self, key):
        v = next((error for (var, error) in self.age.error_components().items()
                                if var.tag == key), 0)
        ae = self.age_error
        if ae:
            return v ** 2 / self.age_error ** 2 * 100
        else:
            return 0


    def get_signal_value(self, k):
        return self._get_arar_result_attr(k)

    def set_isotope(self, iso, v):
        if not self.isotopes.has_key(iso):
            niso = Isotope(name=iso)
            self.isotopes[iso] = niso
        else:
            niso = self.isotopes[iso]

        niso.set_uvalue(v)

    def set_blank(self, iso, v):
        if not self.isotopes.has_key(iso):
            niso = Isotope(name=iso)
            self.isotopes[iso] = niso

        self.isotopes[iso].blank.set_uvalue(v)

    def set_baseline(self, iso, v):
        if not self.isotopes.has_key(iso):
            niso = Isotope(name=iso)
            self.isotopes[iso] = niso

        self.isotopes[iso].baseline.set_uvalue(v)

    def _calculate_kca(self):
        result = self.arar_result
        if result:
            k = result['k39']
            ca = result['ca37']
            prs = self.production_ratios

            k_ca_pr = 1
            if prs:
#                k_ca_pr = 1
                cak = prs.Ca_K
                cak = cak if cak else 1
                k_ca_pr = 1 / cak

            try:
                return k / ca * k_ca_pr
            except ZeroDivisionError:
                return ufloat(0, 0)

    def _calculate_kcl(self):
        result = self.arar_result
        if result:
            k = result['k39']
            cl = result['cl36']

            prs = self.production_ratios
            k_cl_pr = 1
            if prs:
                clk = prs.Cl_K
                clk = clk if clk else 1
                k_cl_pr = 1 / clk

            try:
                return k / cl * k_cl_pr
            except ZeroDivisionError:
                return ufloat(0, 0)


    def calculate_age(self, **kw):
        return self._calculate_age(**kw)

    def _calculate_age(self, include_j_error=None, include_decay_error=None, include_irradiation_error=None):
        if include_decay_error is None:
            include_decay_error = self.include_decay_error
        else:
            self.include_decay_error = include_decay_error

        if include_j_error is None:
            include_j_error = self.include_j_error
        else:
            self.include_j_error = include_j_error

        if include_irradiation_error is None:
            include_irradiation_error = self.include_irradiation_error
        else:
            self.include_irradiation_error = include_irradiation_error

#        signals = self.signals

#        nsignals = dict()
#        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
#        for iso in keys:
#            for k in ['', 'bs', 'bl', 'bg']:
#                isok = iso + k
#                if not signals.has_key(isok):
#                    nsignals[isok] = (0, 0)
#                else:
#                    nsignals[isok] = signals[isok]
#
#        def sigs(name):
#            ss = []
#            for iso in map('{{}}{}'.format(name).format, keys):
#                sig = nsignals[iso]
#                if isinstance(sig, Signal):
#                    sig = sig.value, sig.error
#                ss.append(sig)
#            return ss

#        fsignals = sigs('')
# #        print fsignals[0]
#        bssignals = sigs('bs')
#        blsignals = sigs('bl')
#        bksignals = sigs('bg')

        fsignals = self._make_signals()
        bssignals = self._make_signals(kind='baseline')
        blsignals = self._make_signals(kind='blank')
        bksignals = self._make_signals(kind='background')

#        j = copy.copy(self.j)
#        if not include_j_error:
#            j.set_std_dev(0)
#            j = j[0], 0

        irrad = self.irradiation_info
        if not include_irradiation_error:
            nirrad = []
            for ir in irrad[:-2]:
                nirrad.append((ir[0], 0))
            nirrad.extend(irrad[-2:])
            irrad = nirrad

        ab = self.arar_constants.abundance_sensitivity

        result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals,
                                    self.j, irrad, abundance_sensitivity=ab, ic=self.ic_factor,
                                    include_decay_error=include_decay_error,
                                    arar_constants=self.arar_constants
                                    )


        if result:
            self.arar_result = result
            ai = result['age']
            ai = ai / self.arar_constants.age_scalar
            return ai
#            age = ai.nominal_value
#            err = ai.std_dev()
#            return age, err
    def _make_signals(self, kind=None):
        isos = self.isotopes
#        print isos
        def func(k):
            if kind is None:
                tag = k
            else:
                tag = '{}_{}'.format(k, kind)

            if k in isos:
                iso = self.isotopes[k]
                if kind:
                    iso = getattr(iso, kind)

                return iso.value, iso.error, tag
            else:
                return 0, 1e-20, tag

        return [func(ki)
                    for ki in ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']]

#===============================================================================
# property get/set
#===============================================================================
#     @cached_property
    def _get_production_ratios(self):
        try:
            lev = self.irradiation_level
            ir = lev.irradiation
            pr = ir.production
            return pr
        except AttributeError:
            pass

    @cached_property
    def _get_kca(self):
        return self._calculate_kca()

    @cached_property
    def _get_cak(self):
        try:
            return 1 / self.kca
        except ZeroDivisionError:
            return 0

    @cached_property
    def _get_kcl(self):
        return self._calculate_kcl()

    @cached_property
    def _get_clk(self):
        try:
            return 1 / self.kcl
        except ZeroDivisionError:
            return ufloat(0, 0)

#    @cached_property
#    def _get_signals(self):
# #        if not self._signals:
# #        self._load_signals()
#
#        return self._signals

    @cached_property
    def _get_age(self):
        r = self._calculate_age()
        return r

#     @cached_property
    def _get_age_error(self):
        return self.age.std_dev

#     @cached_property
    def _get_age_error_wo_j(self):
        return float(self.arar_result['age_err_wo_jerr'] / self.arar_constants.age_scalar)

#     @cached_property
    def _get_timestamp(self):
        return datetime.datetime.now()

#     @cached_property
    def _get_irradiation_level(self):
        try:
            if self.irradiation_position:
                return self.irradiation_position.level
        except AttributeError, e:
            print 'level', e

#     @cached_property
    def _get_irradiation_position(self):
        try:
            return self.labnumber_record.irradiation_position
        except AttributeError, e:
            print 'pos', e

#     @cached_property
    def _get_irradiation_info(self):
        '''
            return k4039, k3839,k3739, ca3937, ca3837, ca3637, cl3638, chronsegments, decay_time
        '''
        prs = (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), [], 1
#        analysis = self.dbrecord

        irradiation_level = self.irradiation_level

        if irradiation_level:
            irradiation = irradiation_level.irradiation
            if irradiation:
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
                        analts = datetime.datetime.fromtimestamp(analts)

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

#    @cached_property
#    def _get_abundance_sensitivity(self):
#        return 3e-6

#     def _set_labnumber_record(self, v):
#         self._labnumber_record = v

#     @cached_property
#     def _get_labnumber_record(self):
#         return self._labnumber_record

#     @cached_property
    def _get_j(self):
        s = 1.0
        e = 1e-3

        try:
            f = self.labnumber_record.selected_flux_history.flux
            s = f.j
            e = f.j_err
        except AttributeError:
            pass

        return ufloat(s, e, 'j')

#     @cached_property
    def _get_rad40(self):
        return self.arar_result['rad40']

#     @cached_property
    def _get_k39(self):
        return self.arar_result['k39']

#     @cached_property
    def _get_rad40_percent(self):
        try:
            return self.rad40 / self.Ar40 * 100
        except (ZeroDivisionError, TypeError):
            return ufloat(0, 1e-20)
#        return self.arar_result['rad40'] / self.arar_result['tot40'] * 100

#     @cached_property
    def _get_Ar40(self):
        return self._get_arar_result_attr('40')

#        return self.arar_result['s40']

#     @cached_property
    def _get_Ar39(self):
        return self._get_arar_result_attr('39')
#        return self.arar_result['s39']

#     @cached_property
    def _get_Ar38(self):
        return self._get_arar_result_attr('38')
#        return self.arar_result['s38']

#     @cached_property
    def _get_Ar37(self):
        return self._get_arar_result_attr('37')
#        return self.arar_result['s37']

#     @cached_property
    def _get_Ar36(self):
        return self._get_arar_result_attr('36')
#        return self.arar_result['s36']

#     @cached_property
    def _get_Ar40_error(self):
        r = self._get_arar_result_attr('40')
        if r:
            return r.std_dev
#        return self.arar_result['s40'].std_dev()

#     @cached_property
    def _get_Ar39_error(self):
        r = self._get_arar_result_attr('39')
        if r:
            return r.std_dev

#        return self.arar_result['s39'].std_dev()

#     @cached_property
    def _get_Ar38_error(self):
        r = self._get_arar_result_attr('38')
        if r:
            return r.std_dev

#        return self._get_arar_result_attr('38').std_dev()
#        return self.arar_result['s38'].std_dev()

#     @cached_property
    def _get_Ar37_error(self):
        r = self._get_arar_result_attr('37')
        if r:
            return r.std_dev

#        return self._get_arar_result_attr('37').std_dev()
#        return self.arar_result['s37'].std_dev()

#     @cached_property
    def _get_Ar36_error(self):
        r = self._get_arar_result_attr('36')
        if r:
            return r.std_dev

#        return self._get_arar_result_attr('36').std_dev()
#        return self.arar_result['s36'].std_dev()

#     @cached_property
    def _get_moles_Ar40(self):
        return 0.001

#     @cached_property
    def _get_moles_K39(self):
        return self.k39 * self.sensitivity * self.sensitivity_multiplier

    def _get_ic_factor(self):
        return ufloat(self.arar_constants.ic_factor_v,
                      self.arar_constants.ic_factor_e, 'ic_factor')

#     @cached_property
    def _get_Ar40_39(self):
        try:
            return self.rad40 / self.k39
        except ZeroDivisionError:
            return ufloat(0, 0)

#     @cached_property
    def _get_Ar37_39(self):
        try:
            return self.Ar37 / self.Ar39
        except ZeroDivisionError:
            return ufloat(0, 0)

#     @cached_property
    def _get_Ar36_39(self):
        try:
            return self.Ar36 / self.Ar39
        except ZeroDivisionError:
            return ufloat(0, 0)

    def _get_sensitivity(self):
        return 1.0

    def _set_sensitivity_multiplier(self, v):
        self._sensitivity_multiplier = v

    def _get_sensitivity_multiplier(self):
        return self._sensitivity_multiplier

    def _get_arar_result_attr(self, key):

        if key.startswith('s'):
            key = key[1:]
        elif key.startswith('Ar'):
            key = key[2:]

        arar_attr = 's{}'.format(key)

#        print self.arar_result
        if self.arar_result.has_key(arar_attr):
            return self.arar_result[arar_attr]
        else:
            iso_attr = 'Ar{}'.format(key)
            if self.isotopes.has_key(iso_attr):
                return self.isotopes[iso_attr].get_corrected_value()





#============= EOF =============================================
