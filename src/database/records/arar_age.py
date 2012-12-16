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
    Event
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import datetime
#============= local library imports  ==========================
from src.processing.argon_calculations import calculate_arar_age
from src.processing.signal import Signal
from src.constants import AGE_SCALARS

class ArArAge(HasTraits):
    arar_result = Dict
    age_units = 'Ma'
    age_scalar = Property(depends_on='age_units')

    k39 = Property
    rad40_percent = Property

    kca = Property(depends_on='age_dirty')
    cak = Property(depends_on='age_dirty')
    kcl = Property(depends_on='age_dirty')
    clk = Property(depends_on='age_dirty')

    j = Property
    abundant_sensitivity = Property

    labnumber_record = Property
    _labnumber_record = None

    timestamp = Property
    irradiation_info = Property
    irradiation_level = Property
    irradiation_position = Property
    production_ratios = Property

    signals = Property(depends_on='age_dirty')
    _signals = Dict

    age = Property(depends_on='age_dirty')
    age_dirty = Event

    Ar40 = Property(depends_on='age_dirty')
    Ar39 = Property(depends_on='age_dirty')
    Ar38 = Property(depends_on='age_dirty')
    Ar37 = Property(depends_on='age_dirty')
    Ar36 = Property(depends_on='age_dirty')

    def _calculate_kca(self):
        result = self.arar_result
        if result:
            k = result['k39']
            ca = result['ca37']

            prs = self.production_ratios
            k_ca_pr = 1
            if prs:
                k_ca_pr = 1
#                k_ca_pr = 1 / prs.CA_K

            return k / ca * k_ca_pr

    def _calculate_kcl(self):
        result = self.arar_result
        if result:
            k = result['k39']
            cl = result['cl36']

            prs = self.production_ratios
            k_cl_pr = 1
            if prs:
                k_cl_pr = 1
#                k_cl_pr = 1 / prs.Cl_K

            return k / cl * k_cl_pr


    def _calculate_age(self):

#        self._load_signals()
#        signals = self._signals
        signals = self.signals
        nsignals = dict()
        keys = ['Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']
        for iso in keys:
            for k in ['', 'bs', 'bl', 'bg']:
                isok = iso + k
                if not signals.has_key(isok):
                    nsignals[isok] = (0, 0)
                else:
                    nsignals[isok] = signals[isok]

        def sigs(name):
            ss = []
            for iso in map('{{}}{}'.format(name).format, keys):
                sig = nsignals[iso]
                if isinstance(sig, Signal):
                    sig = sig.value, sig.error
                ss.append(sig)
            return ss

        fsignals = sigs('')
#        print fsignals[0]
        bssignals = sigs('bs')
        blsignals = sigs('bl')
        bksignals = sigs('bg')

#        ic = self.ic_factor
        j = self.j
        irrad = self.irradiation_info
        ab = self.abundant_sensitivity

        result = calculate_arar_age(fsignals, bssignals, blsignals, bksignals,
                                    j, irrad, abundant_sensitivity=ab)

        if result:
            self.arar_result = result
            ai = result['age']

            ai = ai / self.age_scalar
            return ai
#            age = ai.nominal_value
#            err = ai.std_dev()
#            return age, err

    def _load_signals(self):
        pass

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
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
        return 1 / self.kca

    @cached_property
    def _get_kcl(self):
        return self._calculate_kcl()

    @cached_property
    def _get_clk(self):
        return 1 / self.kcl

    def _get_age_scalar(self):
        try:
            return AGE_SCALARS[self.age_units]
        except KeyError:
            return 1

    @cached_property
    def _get_signals(self):
#        if not self._signals:
        self._load_signals()

        return self._signals

    @cached_property
    def _get_age(self):
        r = self._calculate_age()
        return r

    @cached_property
    def _get_timestamp(self):
        return datetime.datetime.now()

    @cached_property
    def _get_irradiation_level(self):
        try:
            if self.irradiation_position:
                return self.irradiation_position.level
        except AttributeError, e:
            print 'level', e

    @cached_property
    def _get_irradiation_position(self):
        try:
            return self.labnumber_record.irradiation_position
        except AttributeError, e:
            print 'pos', e

    @cached_property
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
                def convert_datetime(x):
                    try:
                        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass
#                convert_datetime = lambda x:datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

                convert_days = lambda x: x.total_seconds() / (60. * 60 * 24)
                if chron:
                    chronblob = chron.chronology

                    doses = chronblob.split('$')
                    doses = [di.split('%') for di in doses]

                    doses = [map(convert_datetime, d) for d in doses]

                    analts = self.timestamp
#                    analts = '{} {}'.format(analysis.rundate, analysis.runtime)
#                    analts = datetime.datetime.strptime(analts, '%Y-%m-%d %H:%M:%S')
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

    @cached_property
    def _get_abundant_sensitivity(self):
        return 3e-6

    def _set_labnumber_record(self, v):
        self._labnumber_record = v

    @cached_property
    def _get_labnumber_record(self):
        return self._labnumber_record

    @cached_property
    def _get_j(self):
        s = 1.0
        e = 1e-3

        try:
            f = self.labnumber_record.selected_flux_history.flux
            s = f.j
            e = f.j_err
        except AttributeError:
            pass

        return (s, e)

    @cached_property
    def _get_k39(self):
        return self.arar_result['k39']

    @cached_property
    def _get_rad40_percent(self):
        return self.arar_result['rad40'] / self.arar_result['tot40'] * 100

    @cached_property
    def get_Ar40(self):
        return self.arar_result['s40']

    @cached_property
    def get_Ar39(self):
        return self.arar_result['s39']

    @cached_property
    def get_Ar38(self):
        return self.arar_result['s38']

    @cached_property
    def get_Ar37(self):
        return self.arar_result['s37']

    @cached_property
    def get_Ar36(self):
        return self.arar_result['s36']
#        rr = self.dbrecord.arar_result
#        return rr['rad40'] / rr['tot40'] * 100

#============= EOF =============================================
