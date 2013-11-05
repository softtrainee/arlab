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
from traits.api import Dict, Property, cached_property, \
    Event, Bool, Instance, Float, Any, Str, Tuple, on_trait_change
from src.pychron_constants import ARGON_KEYS
#============= standard library imports ========================
from datetime import datetime
from uncertainties import ufloat

#============= local library imports  ==========================
from src.processing.argon_calculations import calculate_arar_age
from src.processing.arar_constants import ArArConstants
from src.processing.isotope import Isotope

from src.loggable import Loggable
from src.helpers.isotope_utils import sort_isotopes
import time


def AgeProperty():
    return Property(depends_on='age_dirty')


arar_constants = None


class ArArAge(Loggable):
    j = Any
    irradiation = Str
    irradiation_str = Str
    irradiation_level = Str
    irradiation_pos = Str
    irradiation_label = Property(depends_on='irradiation, irradiation_level,irradiation_pos')
    irradiation_info = Tuple
    production_ratios = Dict
    discrimination = Any

    timestamp = Float

    include_j_error = Bool(True)
    include_irradiation_error = Bool(True)
    include_decay_error = Bool(False)

    arar_result = Dict
    #arar_updated=Event

    rad40 = AgeProperty()
    k39 = AgeProperty()
    ca37 = AgeProperty()
    cl36 = AgeProperty()
    rad40_percent = AgeProperty()

    kca = AgeProperty()
    cak = AgeProperty()
    kcl = AgeProperty()
    clk = AgeProperty()

    # ratios
    Ar40_39 = AgeProperty()
    Ar37_39 = AgeProperty()
    Ar36_39 = AgeProperty()

    sensitivity = Property
    sensitivity_multiplier = Property
    _sensitivity_multiplier = Float

    isotopes = Dict
    isotope_keys = Property

    age = None
    R = AgeProperty()

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

    ar39decayfactor = AgeProperty()
    ar37decayfactor = AgeProperty()

    arar_constants = Instance(ArArConstants)

    def __init__(self, *args, **kw):
        super(ArArAge, self).__init__(*args, **kw)
        self.age = ufloat(0, 0)

    def get_ic_factor(self, det):
        factors = self.arar_constants.ic_factors
        ic = 1, 1e-20
        if factors:
            ic = next(((ic.value, ic.error) for ic in factors
                       if ic.detector.lower() == det.lower()), (1.0, 1e-20))
        r = ufloat(*ic)
        return r

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

    def clear_baselines(self):
        for k in self.isotopes:
            self.set_baseline(k, (0, 0))

    def clear_blanks(self):
        for k in self.isotopes:
            self.set_blank(k, (0, 0))

    def clear_error_components(self):
        for iso in self.isotopes.itervalues():
            iso.age_error_component = 0

    def set_isotope_detector(self, det):
        name, det = det.isotope, det.name
        if name in self.isotopes:
            iso = self.isotopes[name]
        else:
            iso = Isotope(name=name)
            self.isotopes[name] = iso

        iso.detector = det
        iso.ic_factor = self.get_ic_factor(det).nominal_value

    def get_isotope(self, name=None, detector=None):
        if name is None and detector is None:
            raise NotImplementedError('name or detector required')

        if name:
            return self.isotopes[name]
            #attr = 'name'
        else:
            attr = 'detector'
            value = detector
            return next((iso for iso in self.isotopes.itervalues()
                         if getattr(iso, attr) == value), None)

    def set_isotope(self, iso, v, **kw):
        if not self.isotopes.has_key(iso):
            niso = Isotope(name=iso)
            self.isotopes[iso] = niso
        else:
            niso = self.isotopes[iso]

        niso.set_uvalue(v)
        niso.trait_set(**kw)

        return niso

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

    def calculate_age(self, force=False, **kw):
        """
            force: force recalculation of age. necessary if you want error components
        """
        #print 'calc', self.age, force
        #        self.debug('calculate age ={}'.format(self.age))
        if not self.age or force:
            #self.age=timethis(self._calculate_age, kwargs=kw, msg='calculate_age')
            self.age = self._calculate_age(**kw)

            self.age_dirty = True
        return self.age

    def load_irradiation(self, ln):
        self.timestamp = self._get_timestamp(ln)

        self.irradiation_info = self._get_irradiation_info(ln)
        self.j = self._get_j(ln)

        self.production_ratios = self._get_production_ratios(ln)


    #================================================================================
    # handlers
    #================================================================================
    @on_trait_change('age_dirty')
    def _handle_arar_result(self, new):
        #load error components into isotopes
        for iso in self.isotopes.itervalues():
            iso.age_error_component = self.get_error_component(iso.name)
            #            print iso.name, iso.age_error_component
            #================================================================================
            # private
            #================================================================================

    def _calculate_kca(self):
        result = self.arar_result
        ret = ufloat(0, 0)
        if result:
            k = result['k39']
            ca = result['ca37']
            prs = self.production_ratios

            k_ca_pr = 1
            if prs:
                cak = prs.get('Ca_K', 1)
                if cak is None:
                    cak = 1.0

                k_ca_pr = 1 / cak
            try:
                ret = k / ca * k_ca_pr
            except ZeroDivisionError:
                pass
        return ret

    def _calculate_kcl(self):
        result = self.arar_result
        ret = ufloat(0, 0)
        if result:
            k = result['k39']
            cl = result['cl36']

            prs = self.production_ratios
            k_cl_pr = 1
            if prs:
                clk = prs.get('Cl_K', 1)
                if clk is None:
                    clk = 1.0

                k_cl_pr = 1 / clk
            try:
                ret = k / cl * k_cl_pr
            except ZeroDivisionError:
                pass

        return ret

    def _make_ic_factors_dict(self):
        ic_factors = dict()
        for ki in ARGON_KEYS:
            if ki in self.isotopes:
                iso = self.isotopes[ki]
                ic_factors[ki] = self.get_ic_factor(iso.detector)

        return ic_factors

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

        fsignals = self._make_signals()
        bssignals = self._make_signals(kind='baseline')
        blsignals = self._make_signals(kind='blank')
        bksignals = self._make_signals(kind='background')

        ic_factors = self._make_ic_factors_dict()

        irrad = self.irradiation_info
        result = None
        if irrad:
            if not include_irradiation_error:
                #set errors to zero
                nirrad = []
                for ir in irrad[:-2]:
                    nirrad.append((ir[0], 0))
                nirrad.extend(irrad[-2:])
                irrad = nirrad

            ab = self.arar_constants.abundance_sensitivity
            result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals,
                                        self.j, irrad, abundance_sensitivity=ab,
                                        ic_factors=ic_factors,
                                        #ic=ic,
                                        #ic=self.ic_factor,
                                        include_decay_error=include_decay_error,
                                        arar_constants=self.arar_constants)

        if result:
            self.arar_result = result
            ai = result['age']
        else:
            ai = ufloat(0, 1.e-20)

        ai = ai / self.arar_constants.age_scalar

        return ai

        #            age = ai.nominal_value
        #            err = ai.std_dev()
        #            return age, err

    def _make_signals(self, kind=None):
        isos = self.isotopes
        #        print isos
        def func(k):
            tag = k if kind is None else '{}_{}'.format(k, kind)
            #             if kind is None:
            #                 tag = k
            #             else:
            #                 tag = '{}_{}'.format(k, kind)
            if k in isos:
                iso = isos[k]
                if kind:
                    iso = getattr(iso, kind)
                return iso.value, iso.error, tag
            else:
                return 0, 1e-20, tag

        return (func(ki)
                for ki in ARGON_KEYS)

    #===============================================================================
    # property get/set
    #===============================================================================
    #     @cached_property
    def _get_production_ratios(self):
        return dict(Ca_K=1, Cl_K=1)

    #        try:
    #            lev = self.irradiation_level
    #            ir = lev.irradiation
    #            pr = ir.production
    #            return pr
    #        except AttributeError:
    #            pass

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

            #     @cached_property
            #     def _get_age(self):
            #         print 'ggggg'
            #         r = self._calculate_age()
            #         return r

            #     @cached_property

    def _get_age_error(self):
        return self.age.std_dev

    #     @cached_property
    def _get_age_error_wo_j(self):
        try:
            return float(self.arar_result['age_err_wo_j'] / self.arar_constants.age_scalar)
        except KeyError:
            return 1e-20

    #     @cached_property
    #     def _get_timestamp(self):
    #         return datetime.now()

    def _get_irradiation_info(self, ln):
    #         '''
    #             return k4039, k3839,k3739, ca3937, ca3837, ca3637, cl3638, chronsegments, decay_time
    #         '''
        prs = (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), [], 1
        return prs

    def _get_j(self):
        s = 1.e-4
        e = 1e-6

        return ufloat(s, e, 'j')

    def _get_rad40(self):
        return self._get_arar_result_attr('rad40')

    def _get_k39(self):
        return self._get_arar_result_attr('k39')

    def _get_ca37(self):
        return self._get_arar_result_attr('ca37')

    def _get_cl36(self):
        return self._get_arar_result_attr('ca37')

    def _get_R(self):
        try:
            return self.rad40 / self.k39
        except (ZeroDivisionError, TypeError):
            return ufloat(0, 1e-20)

    def _get_rad40_percent(self):
        try:
            return self.rad40 / self.Ar40 * 100
        except (ZeroDivisionError, TypeError), e:
            self.debug('Rad40 Percent error {}'.format(e))
            return ufloat(0, 1e-20)

    def _get_Ar40(self):

        return self._get_arar_result_attr('Ar40')

    def _get_Ar39(self):
        return self._get_arar_result_attr('Ar39')

    def _get_Ar38(self):
        return self._get_arar_result_attr('Ar38')

    def _get_Ar37(self):
        return self._get_arar_result_attr('Ar37')

    def _get_Ar36(self):
        return self._get_arar_result_attr('Ar36')

    def _get_Ar40_error(self):
        r = self._get_arar_result_attr('Ar40')
        if r:
            return r.std_dev

    def _get_Ar39_error(self):
        r = self._get_arar_result_attr('Ar39')
        if r:
            return r.std_dev

    def _get_Ar38_error(self):
        r = self._get_arar_result_attr('Ar38')
        if r:
            return r.std_dev

    def _get_Ar37_error(self):
        r = self._get_arar_result_attr('Ar37')
        if r:
            return r.std_dev

    def _get_Ar36_error(self):
        r = self._get_arar_result_attr('Ar36')
        if r:
            return r.std_dev

    def _get_ar39decayfactor(self):
        return self._get_arar_result_attr('ar39decayfactor')

    def _get_ar37decayfactor(self):
        return self._get_arar_result_attr('ar37decayfactor')

    def _get_moles_Ar40(self):
        return 0.001

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
    #        print self.arar_result.keys()
        if key in self.arar_result:
            return self.arar_result[key]
        elif key in self.isotopes:
            return self.isotopes[key].uvalue
        else:
            keys = self.arar_result.keys()
            #self.warning('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ NO KEY {} {}'.format(key, keys))
            return ufloat(0, 1e-20)

            #if key.startswith('s'):
            #    key = key[1:]
            #elif key.startswith('Ar'):
            #    key = key[2:]
            #
            #arar_attr = 's{}'.format(key)
            #
            #elif self.arar_result.has_key(arar_attr):
            #    return self.arar_result[arar_attr]
            #else:
            #    iso_attr = 'Ar{}'.format(key)
            #    if self.isotopes.has_key(iso_attr):
            #        return self.isotopes[iso_attr].get_corrected_value()

            #return ufloat(0, 1e-20)

    def _get_isotope_keys(self):
        keys = self.isotopes.keys()
        return sort_isotopes(keys)

    def _get_timestamp(self, ln):
        x = datetime.now()
        return time.mktime(x.timetuple())

    def _get_irradiation_label(self):
        return '{}{} {}'.format(self.irradiation,
                                self.irradiation_level,
                                self.irradiation_pos
        )

    #===============================================================================
    #
    #===============================================================================

    def __getattr__(self, attr):
        if '/' in attr:
            #treat as ratio
            n, d = attr.split('/')
            try:
                return getattr(self, n) / getattr(self, d)
            except ZeroDivisionError:
                return ufloat(0, 1e-20)

    def _arar_constants_default(self):
        """
            use a global shared arar_constants
        """

        global arar_constants
        #self.debug('$$$$$$$$$$$$$$$$ {}'.format(arar_constants))
        #print 'asdf', arar_constants
        if arar_constants is None:
            arar_constants = ArArConstants()
            #return ArArConstants()
        return arar_constants

#============= EOF =============================================
