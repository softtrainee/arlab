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
import datetime
from sqlalchemy.sql.expression import and_, not_
from src.database.orms.massspec_orm import AnalysesTable, MachineTable, \
    LoginSessionTable, RunScriptTable
from sqlalchemy.orm.exc import NoResultFound
import time
from src.helpers.filetools import unique_path
import os
from src.paths import paths
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
        return DBConnectionSpec(database='massspecdata_minnabluff',
                                username='root',
                                password='Argon',
                                host='localhost'
                                )
#        return DBConnectionSpec(database='massspecdata',
#                                username='massspec',
#                                password='DBArgon',
#                                host='129.138.12.160'
#                                )

    def _connect_button_fired(self):
        self.connect()

    def connect(self):
        self.db.name = self.dbconn_spec.database
        self.db.username = self.dbconn_spec.username
        self.db.password = self.dbconn_spec.password
        self.db.host = self.dbconn_spec.host
        self.db.kind = 'mysql'
        self.db.connect()

    def import_irradiation(self, dest, name,
                           include_analyses=False,
                           include_blanks=False,
                           include_airs=False,
                           include_cocktails=False,
                           include_list=None,
                           dry_run=True,):
        self.connect()
        p, c = unique_path(paths.data_dir, 'import')
        self.import_err_file = open(p, 'w')
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
        self._add_levels(dest, dbirrad, name,
                         include_analyses,
                         include_blanks,
                         include_airs,
                         include_cocktails,
                         include_list,
                         )
        if not dry_run:
            dest.commit()

        self.import_err_file.close()
        return ImportName(name=name, skipped=skipped)

    def _add_levels(self, dest, dbirrad, name,
                    include_analyses=False,
                    include_blanks=False,
                    include_airs=False,
                    include_cocktails=False,
                    include_list=None):
        '''
            add all levels and positions for dbirrad
            if include_analyses is True add all analyses
        '''
        levels = self.db.get_levels_by_irradname(name)
        if include_list is None:
            include_list = [li.Level for li in levels]

        for mli in levels:
            if mli.Level not in include_list:
                continue

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

                sample = self._add_sample_project(dest, ip)
                ln.sample = sample

                if include_analyses:
                    self.info('============ Adding Analyses ============')
                    for ai in ip.analyses:
                        self._add_analysis(dest, ln, ai)

                        if include_blanks:
                            self._add_associated_unknown_blanks(dest, ai)
                        if include_airs:
                            self._add_associated_airs(dest, ai)
                        if include_cocktails:
                            self._add_associated_cocktails(dest, ai)


                dest.flush()

    def _add_associated_cocktails(self, dest, dba):
        ms = dba.login_session.machine
        if ms:
            ms = ms.Label
            if not ms in ('Pychron Obama', 'Pychron Jan', 'Obama', 'Jan'):
                return

            self.info('============ Adding Associated Cocktails ============')
            def add_hook(dest, bi):
                self._add_cocktail_blanks(dest, bi)

            def make_labnumber(bi):
                ln = bi.RID
                if ln.startswith('c-'):
                    ln = '-'.join(bi.RID.split('-')[:-1])
                else:
                    msname = self._get_ms_identifier(bi)
                    ln = 'c-00-{}'.format(msname)
                return ln

            self._add_associated(dest, dba, make_labnumber,
                                 atype=1,
                                 add_hook=add_hook,
                                 analysis_type='cocktail'
                                 )

    def _add_associated_airs(self, dest, dba):
        '''
        '''
        ms = dba.login_session.machine
        if ms:
            ms = ms.Label
            if not ms in ('Pychron Obama', 'Pychron Jan', 'Obama', 'Jan'):
                return

            self.info('============ Adding Associated Airs ============')
            def add_hook(dest, bi):
                self._add_air_blanks(dest, bi)

            def make_labnumber(bi):
                ln = bi.RID
                if ln.startswith('a-'):
                    ln = '-'.join(ln.split('-')[:-1])
                else:
                    msname = self._get_ms_identifier(bi)
                    ln = 'a-00-{}'.format(msname)
                return ln

            self._add_associated(dest, dba, make_labnumber,
                                 atype=2,
                                 add_hook=add_hook,
                                 analysis_type='air'
                                 )

    def _add_air_blanks(self, dest, dba):
        def make_labnumber(bi):
            ln = bi.RID

            if not ln.startswith('ba'):
                ms = self._get_ms_identifier(bi)
                ln = 'ba-00-{}'.format(ms)
            else:
                # remove aliquot
                ln = '-'.join(ln.split('-')[:-1])
            return ln

        self._add_associated(dest, dba, make_labnumber, atype=5,
                             analysis_type='blank_air'
                             )

    def _add_cocktail_blanks(self, dest, dba):
        def make_labnumber(bi):
            ln = bi.RID

            if not ln.startswith('bc'):
                ms = self._get_ms_identifier(bi)
                ln = 'bc-00-{}'.format(ms)
            else:
                # remove aliquot
                ln = '-'.join(ln.split('-')[:-1])
            return ln

        self._add_associated(dest, dba, make_labnumber, atype=5,
                             analysis_type='blank_coctail'
                             )

    def _add_associated_unknown_blanks(self, dest, dba):
        '''
            get blanks +/- Nhrs from dba run date
        
        '''
        self.info('============ Adding Associated Blanks ============')

        def make_labnumber(bi):
            ln = bi.RID

            if not ln.startswith('bu'):
                ed = 'F' if ln.startswith('B2') else 'C02'
                ms = self._get_ms_identifier(bi)
                ln = 'bu-{}-{}'.format(ed, ms)
            else:
                # remove aliquot
                ln = '-'.join(ln.split('-')[:-1])
            return ln

        def filter_func(q):
            q = q.join(RunScriptTable)
            q = q.filter(not_(RunScriptTable.Label.in_(['Blank Pipette 1', 'Blank Pipette 2'])))
            return q

        self._add_associated(dest, dba, make_labnumber,
                             filter_hook=filter_func)

    def _add_associated(self, dest, dba, make_labnumber,
                        _cache=[],
                        atype=5,
                        analysis_type='blank_unknown',
                        add_hook=None,
                        **kw
                        ):
        post = dba.RunDateTime
        ms = dba.login_session.machine.Label
        br = self._find_analyses(ms, post, -2, atype, **kw)
        ar = self._find_analyses(ms, post, 2, atype, maxtries=1, **kw)

        for bi in br + ar:
            ln = make_labnumber(bi)
            if ln not in _cache:
                _cache.append(ln)
                ln = dest.add_labnumber(ln)
                dest.flush()

            if self._add_analysis(dest, ln, bi, analysis_type=analysis_type):
                if add_hook:
                    add_hook(dest, bi)

    def _get_ms_identifier(self, ai):
        msname = ai.login_session.machine
        if msname == 'Pychron Obama':
            msname = 'PO'
        elif msname == 'Pychron Jan':
            msname = 'PJ'
        elif msname == 'Jan':
            msname = 'J'
        else:
            msname = 'O'
        return msname

    def _find_analyses(self, ms, post, delta, atype, step=100, maxtries=10, **kw):
        if delta < 0:
            step = -step

        for i in range(maxtries):
            rs = self._filter_analyses(ms, post, delta + i * step, 5, atype, **kw)
            if rs:
                return rs
        else:
            return []

    def _filter_analyses(self, ms, post, delta, lim, at, filter_hook=None):
        '''
            ms= spectrometer 
            post= timestamp
            delta= time in hours
            at=analysis type
            
            if delta is negative 
            get all before post and after post-delta

            if delta is post 
            get all before post+delta and after post
        '''
        sess = self.db.get_session()
        q = sess.query(AnalysesTable)
        q = q.join(LoginSessionTable)
        q = q.join(MachineTable)
#
        win = datetime.timedelta(hours=delta)
        dt = post + win
        if delta < 0:
            a, b = dt, post
        else:
            a, b = post, dt

        q = q.filter(MachineTable.Label == ms)
        q = q.filter(and_(
                          AnalysesTable.SpecRunType == at,
                          AnalysesTable.RunDateTime >= a,
                          AnalysesTable.RunDateTime <= b,
                          )
                     )

        if filter_hook:
            q = filter_hook(q)
        q = q.limit(lim)

        try:
            return q.all()
        except NoResultFound:
            pass

    def _add_analysis(self, dest, dest_labnumber, dbanalysis, analysis_type='unknown', _ed_cache=[], _an_cache=[]):
        #=======================================================================
        # add analysis
        #=======================================================================
        aliquot = dbanalysis.Aliquot
        step = dbanalysis.Increment
        changeable = dbanalysis.changeable

        try:
            al = int(aliquot)
        except ValueError:
            if '-' in aliquot:
                al = int(aliquot.split('-')[-1])
            else:
                al = id(aliquot)

        ans = dest.get_unique_analysis(dest_labnumber, al, step=step)
        if ans:
#            self.debug('{}-{}{} already exists'.format(dest_labnumber, aliquot, step))
            return

        dest_an = dest.add_analysis(dest_labnumber,
                                 aliquot=al,
                                 comment=changeable.Comment,
                                 step=step,
                                 analysis_timestamp=dbanalysis.RunDateTime,
                                 status=changeable.StatusLevel
                                 )
        if dest_an is None:
            return

        dest.flush()

        if isinstance(dest_labnumber, (str, int, long)):
            iden = str(dest_labnumber)
        else:
            iden = dest_labnumber.identifier

        identifier = '{}-{}{}'.format(iden, al, step)
        self.info('Adding analysis {}'.format(identifier))

        #=======================================================================
        # add measurement
        #=======================================================================
        ms = dbanalysis.login_session.machine
        if ms:
            ms = ms.Label.lower()
            if ms == 'pychron obama':
                ms = 'obama'
            elif ms == 'pychron jan':
                ms = 'jan'
            dest.add_measurement(dest_an, analysis_type, ms)

        #=======================================================================
        # add extraction
        #=======================================================================

        ed = dbanalysis.HeatingItemName
        if ed not in _ed_cache:
            dest.add_extraction_device(ed)
            _ed_cache.append(ed)

        ext = dest.add_extraction(dest_an, cleanup_duration=dbanalysis.FirstStageDly + dbanalysis.SecondStageDly,
                            extract_duration=dbanalysis.TotDurHeating,
                            extract_value=dbanalysis.FinalSetPwr,
                            )

        pos = sorted(dbanalysis.positions, key=lambda x:x.PositionOrder)
        for pi in pos:
            dest.add_analysis_position(ext, pi)

        #=======================================================================
        # add isotopes
        #=======================================================================
        fit_hist = None
        if len(dbanalysis.isotopes) < 4 or len(dbanalysis.isotopes) > 7:
            self.import_err_file.write('{}\n'.format(identifier))

        for iso in dbanalysis.isotopes:
            pkt = iso.peak_time_series[-1]
            blob = pkt.PeakTimeBlob
            endianness = '>'
            sy, sx = zip(*[struct.unpack('{}ff'.format(endianness),
                                       blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

            blob = pkt.PeakNeverBslnCorBlob
            try:
                noncor_y = [struct.unpack('{}f'.format(endianness),
                                       blob[i:i + 4])[0] for i in xrange(0, len(blob), 4)]
            except Exception:
                self.import_err_file.write('{}\n'.format(identifier))
                continue

            det = None
            try:
                detname = iso.detector.detector_type.Label
                det = dest.get_detector(detname)
                if det is None:
                    det = dest.add_detector(detname)
                    dest.flush()
            except AttributeError, e:
                self.debug('mass spec extractor {}', e)

            '''
                mass spec saves peak time with baseline correction.
                pychron wants uncorrected
            '''
            baseline = ''
            if iso.baseline:
                baseline = iso.baseline.PeakTimeBlob
                '''
                    mass spec stores blobs as y,x
                
                    pychron stores as x,y
                '''
                ys, xs = zip(*[struct.unpack('{}ff'.format(endianness),
                                       baseline[i:i + 8]) for i in xrange(0, len(baseline), 8)])

                baseline = ''.join([struct.pack('>ff', x, y) for x, y in zip(xs, ys)])

            data = ''.join([struct.pack('>ff', x, y) for x, y in zip(sx, noncor_y)])
            # add baseline
            for data, k in (
                              (baseline, 'baseline'),
                              (data, 'signal')
                              ):

                dbiso = dest.add_isotope(dest_an, iso.Label, det, kind=k)
                dest.add_signal(dbiso, data)

            # add to fit history
            #### How to extract fits from Mass Spec???? #####
#            fit = None
#            if fit:
#                if fit_hist is None:
#                    fit_hist = dest.add_fit_history(dest_an)
#                dest.add_fit(fit_hist, dbiso, fit=fit)

        self.dbimport.analyses.append(dest_an)
        return True

    def _add_sample_project(self, dest, dbpos):

        sample = dbpos.sample
        project = sample.project
        material = dbpos.Material

        dest.add_material(material)

        project = dest.add_project(project.Project)

        return dest.add_sample(
                        sample.Sample,
                        material=material,
                        project=project)

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

    def get_labnumbers(self, filter_str=None):
        self.connect()
        lns = [ImportName(name='{}'.format(i[0])) for i in self.db.get_run_ids(filter_str=filter_str)]
        return lns

    def get_irradiations(self):
        self.connect()
        irs = [ImportName(name='{}'.format(i[0])) for i in self.db.get_irradiation_names()]
        return irs

#============= EOF =============================================
