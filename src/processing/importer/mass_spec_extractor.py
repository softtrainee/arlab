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
from traits.api import HasTraits, Str, Bool, Instance, Button
from src.processing.importer.extractor import Extractor
from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter
from src.database.database_connection_spec import DBConnectionSpec
import struct
#============= standard library imports ========================
#============= local library imports  ==========================
class ImportName(HasTraits):
    name = Str
    skipped = Bool(False)


class MassSpecExtractor(Extractor):
    dbconn_spec = Instance(DBConnectionSpec, ())
    connect_button = Button('Connect')
    db = Instance(MassSpecDatabaseAdapter, ())

    def _dbconn_spec_default(self):
        return DBConnectionSpec(database='massspecdata',
                                username='massspec',
                                password='DBArgon',
                                host='129.138.12.160'
                                )
    def _connect_button_fired(self):
        self.connect()

    def connect(self):
        self.db.name = self.dbconn_spec.database
        self.db.username = self.dbconn_spec.username
        self.db.password = self.dbconn_spec.password
        self.db.host = self.dbconn_spec.host
        self.db.kind = 'mysql'
        self.db.connect()

    def import_irradiation(self, dest, name, include_analyses=False):
        self.connect()

        self.dbimport = dest.add_import(
                                        source=self.db.name,
                                        source_host=self.db.host,
                                        )
        # is irrad already in dest
        dbirrad = dest.get_irradiation(name)
        skipped = True
        if dbirrad is None:
            # add chronology
            dbchron = self._add_chronology(dest, name)
            # add production
            dbpr = self._add_production_ratios(dest, name)
            # add irradiation
            dbirrad = dest.add_irradiation(name, production=dbpr, chronology=dbchron)
            skipped = False

        dest.flush()
        # add all the levels and positions for this irradiation
        self._add_levels(dest, dbirrad, name, include_analyses)

        dest.commit()
        return ImportName(name=name, skipped=skipped)

    def _add_levels(self, dest, dbirrad, name, include_analyses):
        '''
            add all levels and positions for dbirrad
            if include_analyses is True add all analyses
        '''
        levels = self.db.get_levels_by_irradname(name)
        for mli in levels:

            # is level already in dest
            dbl = dest.get_irradiation_level(name, mli.Level)
            if dbl is None:
                dest.add_irradiation_level(mli.Level, dbirrad, mli.SampleHolder)

            # add all irradiation positions for this level
            positions = self.db.get_irradiation_positions(name, mli.Level)
            for ip in positions:
                # is labnumber already in dest
                ln = dest.get_labnumber(ip.IrradPosition)
                if not ln:
                    ln = dest.add_labnumber(ip.IrradPosition)
                    dbpos = dest.add_irradiation_position(ip.HoleNumber, ln, name, mli.Level)

                    fh = dest.add_flux_history(dbpos)
                    ln.selected_flux_history = fh
                    fl = dest.add_flux(ip.J, ip.JEr)
                    fh.flux = fl

#                    dbpos = dest.add_irradiation_position(ip.HoleNumber, ln, name, mli.Level)
                sample = self._add_sample_project(dest, ip)
                ln.sample = sample

                if include_analyses:
                    for ai in ip.analyses:
                        self._add_analysis(dest, ln, ai)

                dest.flush()

    def _add_analysis(self, dest, dest_labnumber, dbanalysis):
        #=======================================================================
        # add analysis
        #=======================================================================
        aliquot = dbanalysis.Aliquot
        step = dbanalysis.Increment
        changeable = dbanalysis.changeable

        dest_an = dest.add_analysis(dest_labnumber,
                                 aliquot=int(aliquot),
                                 comment=changeable.Comment,
                                 step=step
                                 )

        #=======================================================================
        # add isotopes
        #=======================================================================
        kind = 'signal'
        fit_hist = None
        for iso in dbanalysis.isotopes:
            pkt = iso.peak_time_series
            blob = pkt.PeakTimeBlob
            endianness = '>'
            sx, sy = zip(*[struct.unpack('{}ff'.format(endianness),
                                       blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

            blob = pkt.PeakNeverBslnCorBlob
            noncor_y = zip(*[struct.unpack('{}f'.format(endianness),
                                       blob[i:i + 4]) for i in xrange(0, len(blob), 4)])

            detname = iso.detector.Label
            det = dest.get_detector(detname)
            if det is None:
                det = dest.add_detector(detname)
#                    db.flush()

            '''
                mass spec saves peak time with baseline correction.
                pychron wants uncorrected
            '''
            baseline = iso.baseline.PeakTimeBlob

            data = ''.join([struct.pack('>ff', x, y) for x, y in zip(sx, noncor_y)])
            # add baseline
            for data, k in (
                              (baseline, 'baseline'),
                              (data, 'signal')
                              ):
                dbiso = dest.add_isotope(dest_an, iso, det, kind=k)
                dest.add_signal(dbiso, data)

            # add to fit history
            #### How to extract fits from Mass Spec???? #####
            fit = None
            if fit:
                if fit_hist is None:
                    fit_hist = dest.add_fit_history(dest_an)
                dest.add_fit(fit_hist, dbiso, fit=fit)


        self.dbimport.analyses.append(dest_an)

    def _add_sample_project(self, dest, dbpos):

        sample = dbpos.sample
        project = sample.project
        material = dbpos.Material

        dest.add_material(material)
        dest.add_project(project.Project)

        return dest.add_sample(
                        sample.Sample,
                        material=material,
                        project=project.Project)

    def _add_chronology(self, dest, name):
        chrons = self.db.get_chronology_by_irradname(name)
        chronblob = '$'.join(['{}%{}'.format(ci.StartTime, ci.EndTime) for ci in chrons])

        self.info('adding irradiation and chronology for {}'.format(name))
        return dest.add_irradiation_chronology(chronblob)

    def _add_production_ratios(self, dest, name):
        production = self.db.get_production_ratio_by_irradname(name)
        if production is not None:
            prname = production.Label
            dbpr = dest.get_irradiation_production(prname)
            if not dbpr:
                kw = dict(name=prname)
                prs = ['K4039', 'K3839', 'K3739', 'Ca3937', 'Ca3837', 'Ca3637',
                       ('P36Cl38Cl', 'Cl3638'),
                       ('CaOverKMultiplier', 'Ca_K'),
                       ('ClOverKMultiplier', 'Cl_K')
                       ]
                for k in prs:
                    if not isinstance(k, tuple):
                        ko = k
                    else:
                        k, ko = k

                    ke = '{}Er'.format(k)
                    v = getattr(production, k)
                    e = getattr(production, ke)
                    kw[ko] = v
                    kw['{}_err'.format(ko)] = e
                self.info('adding production ratio {}'.format(prname))
                dbpr = dest.add_irradiation_production(**kw)
            return dbpr
#    def _add_irradiation(self, dest, name, dbpr, dbchron):
#        dbirrad = dest.add_irradiation(name, production=dbpr, chronology=dbchron)
    def get_labnumbers(self, filter_str=None):
        self.connect()
        lns = [ImportName(name='{}'.format(i[0])) for i in self.db.get_run_ids(filter_str=filter_str)]
        return lns

    def get_irradiations(self):
        self.connect()
        irs = [ImportName(name='{}'.format(i[0])) for i in self.db.get_irradiation_names()]
        return irs

#============= EOF =============================================
