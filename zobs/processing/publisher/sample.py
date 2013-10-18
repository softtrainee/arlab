##===============================================================================
# # Copyright 2012 Jake Ross
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #   http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
##===============================================================================
#
##============= enthought library imports =======================
##============= standard library imports ========================
##============= local library imports  ==========================
#
#
# class Sample(object):
#    analyses = None
#    info = None
#    def __init__(self, name):
#        self.name = name
#        self.analyses = []
#    def finish(self):
#        self._calculate_cumulative39()
#        self.find_plateau_steps()
#
#    def _calculate_cumulative39(self):
#        s = sum([a.ar39_ for a in self.analyses])
#        pv = 0
#        for a in self.analyses:
#            v = a.ar39_ / s * 100
#            pv += v
#            a.ar39_percent = pv
#
#    def _get_summed_err(self, k):
#        return reduce(lambda x, y:(x ** 2 + y ** 2) ** 0.5, [getattr(a, k) for a in self.analyses])
#
#    def _calculate_isotopic_recombination(self):
#
#        ar40_sum = sum([a.ar40_ for a in self.analyses])
#        ar39_sum = sum([a.ar39_ for a in self.analyses])
#        ar38_sum = sum([a.ar38_ for a in self.analyses])
#        ar37_sum = sum([a.ar37_ for a in self.analyses])
#        ar36_sum = sum([a.ar36_ for a in self.analyses])
#
#        ar40er_sum = self._get_summed_err('ar40_er')
#        ar39er_sum = self._get_summed_err('ar39_er')
#        ar38er_sum = self._get_summed_err('ar38_er')
#        ar37er_sum = self._get_summed_err('ar37_er')
#        ar36er_sum = self._get_summed_err('ar36_er')
#
#        age, _err = calculate_arar_age((ar40_sum,
#                                      ar40er_sum,
#                                      ar39_sum,
#                                      ar39er_sum,
#                                      ar38_sum,
#                                      ar38er_sum,
#                                      ar37_sum,
#                                      ar37er_sum,
#                                      ar36_sum,
#                                      ar36er_sum),
#
#                                      (a.p36cl38cl,
#                                       a.k4039, a.k3839,
#                                       a.ca3637, a.ca3937, a.ca3837),
#
#                                      (a.k4039er, a.ca3637er, a.ca3937er),
#
#                                      a.a37decayfactor,
#                                      a.a39decayfactor,
#                                      a.j,
#                                      a.jer,
#                                      a.d,
#                                      a.der
#                                      )
# #        print '{:0.2f}'.format(2 * err.nominal_value), err.nominal_value / age.std_dev()
# #        print '{:0.2f}'.format(2 * err.nominal_value),
# #        print  '{:0.2f}'.format(4 * age.std_dev())
#
#        return age.nominal_value, 2 * age.std_dev() ** 0.5 / len(self.analyses)
#
#    def get_isotopic_recombination_age(self):
#        a, e = self._calculate_isotopic_recombination()
#
#
#        return a, e
#
#    def get_kca(self, plateau=False):
#        if plateau:
#            kcas = [a.k_over_ca for a in self.analyses if a.plateau_status]
#            kerr = [a.k_over_ca_er for a in self.analyses if a.plateau_status]
#            kca, err = calculate_weighted_mean(kcas, kerr)
#
#        else:
#            kcas = [a.k_over_ca for a in self.analyses]
#            err = 0
#            kca = 0
#        return kca, err
#
#    def get_plateau_age(self, nsigma=2):
#        x, errs = self._get_plateau_ages()
#        a, e = calculate_weighted_mean(x, errs)
#
#        mswd = self.get_mswd()
#        return a, nsigma * e * mswd ** 0.5
#
#    def get_plateau_percent39(self):
#        s = 0
#        tot = self.get_total39()
#        for a in self.analyses:
#            if a.plateau_status:
#                s += a.ar39_moles
#
#        return s / tot * 100
#
#    def get_total39(self, plateau=False):
#
#        if plateau:
#            s = [a.ar39_moles for a in self.analyses if a.plateau_status]
#        else:
#            s = [a.ar39_moles for a in self.analyses]
#
#        return sum(s)
#
#    def get_mswd(self, all_steps=False):
#        x, errs = self._get_plateau_ages(all_steps)
#        mw = calculate_mswd(x, errs)
#        return mw
#
#    def _get_plateau_ages(self, all_steps=False):
#        x = [a.age for a in self.analyses if a.plateau_status or all_steps]
#        errs = [a.age_er for a in self.analyses if a.plateau_status or all_steps]
#        return x, errs
#
#    def get_nsteps(self):
#        return len(self.analyses)
#
#    def get_plateau_steps(self):
#        ps = [a.suffix for a in self.analyses if a.plateau_status]
#        if ps:
#            return ps[0], ps[-1], len(ps)
#
#    def find_plateau_steps(self):
#        ages, errs = self._get_plateau_ages(all_steps=True)
#        signals = [a.ar39_ for a in self.analyses]
#        plat = find_plateaus(ages, errs, signals)
#        if plat[0] == plat[1]:
#            msg = 'no plateau found'
#
#        else:
#            tot = sum(signals)
#            per = sum(signals[plat[0]:plat[1] + 1]) / tot * 100
#            a = [chr(i) for i in range(65, 65 + 26)]
#            msg = '{}-{} {}'.format(a[plat[0]], a[plat[1]], '%0.1f' % per)
#
#            for a in self.analyses[plat[0]:plat[1] + 1]:
#                a.plateau_status = True
#                a.status = ''
#        print self.name, msg
# #        print ages[plat[0]:plat[1] + 1]
##============= EOF =============================================
