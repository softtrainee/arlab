#===============================================================================
# Copyright 2011 Jake Ross
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



##============= enthought library imports =======================
#from traits.api import HasTraits
#from src.database.pychron_database_adapter import PychronDatabaseAdapter
#from src.experiments import time_series_helper
#from regression.regressor import Regressor
#from src.experiments.summary_window import SummaryWindow
##============= standard library imports ========================
#from datetime import datetime
##============= local library imports  ==========================
#from uncertainties import ufloat
#from uncertainties.umath import pow
#from argon_calculations import age_calculation, j_calculation
#from production_ratio import ProductionRatio
#from pylab import cos, array, pi
#
##============= views ===================================
#class ExperimentProcessor(HasTraits):
#    eid = 37
#    def calc_flux(self, irrad_id, suffix, age):
#        irrad, sess = self.database.get_irradiations(id = irrad_id,
#                                                   filter = dict(suffix = suffix),
#                                                    func = 'one')
#        #irrad.holes
#
#
#        #need to specify the the analyses used to calculate the flux for this irradiation tray
#        #just getting them by experiment id now
#        analyses, sess = self.database.get_analyses(filter = dict(experiment_id = self.eid,
#                                                                  kind = 'analysis'
#                                                                  ),
#                                                                  func = 'all',
#                                                                  sess = sess
#                                                                  )
#        js = []
#        hole_pos = []
#        for a in analyses:
#
#            values = [(s.detector.mass, s.corrected_signal) for s in a.signals]
#            values.sort()
#            values.reverse()
#            #get the production ratios
#            dbr = a.sample.hole.irradiation.production_ratios
#            pr = ProductionRatio(dbr)
#
#            #get the irradiation chronology
#            dbr = a.sample.hole.irradiation.chronology
#            irrad_params = self.get_irradiation_chronology_params(a, dbr)
#
#            args = (age,) + tuple([ufloat((v[1].intercept, v[1].error)) for v in values]) + (pr,) + irrad_params
#            j = j_calculation(*args)
#            hole_pos.append(a.sample.hole.hole)
#            js.append(j)
#
#        #calculate a least squares fit
#        #xd = range(1, 7, 1)
#        #yd = array(js)
#
#        #convert to radians
##        ndegs = 2 * pi / len(xd)
##        xd = array([ndegs * (xi - 1) for xi in xd] + [2 * pi])
#
##        #define a model 
##        fitfunc = lambda p, x: p[0] * cos(p[1] * x)
##        #define an initial guess must match len(p)
##        p0=[1,1]
##        #define func to calculate residuals
##        if weighted:
##            #weights equal to 1/std**2  
##            errfunc = lambda p, x, y: (fitfunc(p, x) - y) *pow(err,-2)            
##        else:
##            errfunc = lambda p, x, y: fitfunc(p, x) - y
#
##        r = Regressor()
##        out= r.least_squares(xd, yd, [0, 2 * pi], errfunc = errfunc, fitfunc = fitfunc,
##                              p0 = p0)
##        print out
#
#    def process(self, force_add = False):
#
#        analyses, sess = self.database.get_analyses(filter = dict(experiment_id = self.eid,
#                                                                  kind = 'analysis'),
#                                                    func = 'all')
#
#        blanks, sess = self.database.get_analyses(filter = dict(experiment_id = self.eid,
#                                                                  kind = 'blank'),
#                                                    func = 'all',
#                                                    sess = sess)
#
#        af = 'parabolic'
#        bc = 'average'
#        #bc = 'none'
#        for fit in ['parabolic']:#, 'average', 'linear']:
#            for a in analyses:
#                #correct the analysis for blank and discrimination
#                corrected_intercepts = self.correct_analysis(a, blanks,
#                                                             analysis_fit = fit,
#                                                             blank_correction = bc)
#                #save the corrected intercepts
#                for (mass, inter), sig in zip(corrected_intercepts, a.signals):
#                    #sess.delete(sig.corrected_signal)
#                    if sig.corrected_signal is None or force_add:
#                        csignal, sess = self.database.add_corrected_signal(dict(intercept = inter.nominal_value,
#                                                                                error = inter.std_dev(),
#                                                                                fit = af,
#                                                                                blank_correction = bc),
#                                                           dbsignal = sig,
#                                                           sess = sess
#                                                           )
#
#                #calculate the age
#                age = self.calc_age(corrected_intercepts, a)
#
#                #save the age
#                ararage = self.database.add_ararage(dict(age = age.nominal_value,
#                                                         error = age.std_dev()),
#                                                    dbanalysis = a
#                                                         )
#
#        sess.commit()
#        sess.close()
#
#    def get_irradiation_chronology_params(self, analysis, dbr):
#        days_since_irradiation = (analysis.timestamp - dbr.end_time).days
#
#        idelta = dbr.end_time - dbr.start_time
#        ti = (idelta.microseconds + (idelta.seconds + idelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6
#        irradiation_time = ti / 3600.0
#        return days_since_irradiation, irradiation_time
#
#    def calc_age(self, isotopes, analysis):
#        sample = analysis.sample
#        isotopes.sort()
#        isotopes.reverse()
#
#        args = tuple([i[1] for i in isotopes])
#
#        #get j value and error
#        j = ufloat((sample.hole.j, sample.hole.jer))
#        j = 7.5e-4
#        #get the production ratios
#        dbr = sample.hole.irradiation.production_ratios
#        pr = ProductionRatio(dbr)
#
#        #get the irradiation chronology
#        dbr = sample.hole.irradiation.chronology
#        irrad_args = self.get_irradiation_chronology_params(analysis, dbr)
#
#        a = (j,) + args + (pr,) + irrad_args
#        age = age_calculation(*a)
#
#        a = (age,) + args + (pr,) + irrad_args
#        j = j_calculation(*a)
#
#        return age
#
#    def get_intercepts(self, analysis, disc, fits = 'linear'):
#        r = Regressor()
#        intercepts = []
#        for i, signal in enumerate(analysis.signals):
#            if isinstance(fits, (list, tuple)):
#                fit = fits[i]
#            else:
#                fit = fits
#            t, v = time_series_helper.parse_time_series_blob(signal.time_series)
#
#            rdict = getattr(r, fit)(t, v, [0, max(t)])
#            coeffs = rdict['coefficients']
#
#            #this isnt the error in the intercept?
##            error = rdict['upper_y'][0] - rdict['lower_y'][0]
#            coeff_errors = rdict['coeff_errors']
#            error = coeff_errors[1]
#
#            #correct the intercept for discrimination
#            inter = ufloat((coeffs[-1], error))
#            offset = signal.detector.mass - 36
#            inter = inter * pow(disc, offset)
#
#            intercepts.append((signal.detector.mass, inter))
#        return intercepts
#
#
#
#    def correct_analysis(self, analysis, blanks, analysis_fit = 'linear', blank_fit = 'linear', blank_correction = 'preceding'):
#
#        pblanks = []
#        sblanks = []
#        for b in blanks:
#            delta = b.timestamp - analysis.timestamp
#            if delta.days < 0 or delta.seconds < 0:
#                pblanks.append((delta, b))
#            else:
#                sblanks.append((delta, b))
#
#        pblanks.sort()
#        sblanks.sort()
#
#        disc = 1.004
#        analysis_intercepts = self.get_intercepts(analysis, disc, fits = analysis_fit)
#        blank_intercepts = [(0, 0)] * len(analysis_intercepts)
#        if blank_correction == 'preceding_correction':
#            blank_intercepts = self.get_intercepts(pblanks[-1][1], disc, fits = blank_fit)
#
#        elif blank_correction == 'average':
#            av_intercepts = []
#            for ts, pb in pblanks:
#                for i, inter in enumerate(self.get_intercepts(pb, disc, fits = blank_fit)):
#                    try:
#                        av_intercepts[i].append(inter)
#                    except IndexError:
#                        av_intercepts.append([inter])
#
#            for ts, sb in sblanks:
#                for i, inter in enumerate(self.get_intercepts(sb, disc, fits = blank_fit)):
#                    av_intercepts[i].append(inter)
#
#            for i, av in enumerate(av_intercepts):
#                intercept = 0
#                for item in av:
#                    intercept += item[1]
#                blank_intercepts[i] = item[0], intercept / len(av)
#
#        corrected_intercepts = map(lambda i:(i[0][0], i[0][1] - i[1][1]), zip(analysis_intercepts, blank_intercepts))
#        return corrected_intercepts
#
#if __name__ == '__main__':
#    db = PychronDatabaseAdapter(kind = 'mysql')
#    db.dbname = 'pychrondb'
#    db.host = 'localhost'
#    db.user = 'root'
#    db.password = 'Argon'
#    db.connect()
#    d = ExperimentProcessor(database = db)
# #   a = d.process()
#
#  #  d.calc_flux('NM-001', 'A', a)
#    d.test()
##============= EOF ====================================
