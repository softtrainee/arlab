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
from traits.api import HasTraits, Any, Button, Instance, Str
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import struct
import os
import uuid
#============= local library imports  ==========================
from src.loggable import Loggable
from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.displays.rich_text_display import RichTextDisplay
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.repo.repository import Repository
from src.managers.data_managers.table_descriptions import TimeSeriesTableDescription
from src.database.orms.massspec_orm import IrradiationLevelTable, \
    IrradiationChronologyTable, IrradiationPositionTable, AnalysesTable, \
    SampleTable, ProjectTable
from threading import Thread
import time
from src.paths import paths
#from src.database.orms.isotope_orm import meas_AnalysisTable

class Importer(Loggable):
    username = Str('root')
    source = Any
    destination = Any
    import_button = Button
    display = Instance(RichTextDisplay)
    repository = Any
    _dbimport = None
    import_count = 0
    def info(self, msg, **kw):
        self.display.add_text(msg)
        super(Importer, self).info(msg, **kw)

    def _import_button_fired(self):
        t = Thread(target=self._import)
        t.start()

    def _import(self):
        pass

    def _gather_data(self):
        pass

    def _dump_file(self, signals, baselines):
        dm = H5DataManager()
        name = uuid.uuid4()
        name = '{}.h5'.format(name)
        path = os.path.join(self.repository.root, name)
        frame = dm.new_frame(path=path, verbose=False)

        frame.createGroup('/', 'signals')
        frame.createGroup('/', 'baselines')
        #make new h5 file

        def write_file(di, data, fit, grp, k):
            di = di.replace(' ', '_')
            frame.createGroup('/{}'.format(grp), k)
            where = '/{}/{}'.format(grp, k)
            tab = frame.createTable(where, di, TimeSeriesTableDescription)
            tab.attrs['fit'] = fit
            for y, x in data:
                nrow = tab.row
                nrow['time'] = x
                nrow['value'] = y
                nrow.append()
            tab.flush()

        for k, v in signals.iteritems():
            det, data, fit = v
            write_file(det, data, fit, 'signals', k)

            det, data, fit = baselines[k]
            write_file(det, data, fit, 'baselines', k)

        dm.close()

#        with zipfile.ZipFile('/Users/ross/Sandbox/importtest/archive.zip', 'a') as z:
#            z.write(path, os.path.basename(path))
#
#        os.remove(path)

        return name

    def traits_view(self):
        v = View(Item('import_button', show_label=False),
                 Item('display', show_label=False, style='custom', width=300, height=300)
                 )
        return v

    def _display_default(self):
        d = RichTextDisplay(width=290, height=300,
                            bg_color='#FFFFCC'
                            )
        return d

class MassSpecImporter(Importer):
    def _import(self):
        self.info('Adding defaults database')
        from src.database.defaults import load_isotopedb_defaults

        load_isotopedb_defaults(self.destination)
        st = time.time()
        self.info('starting import')
        items = self._gather_data()

        for item in items:
            if self._import_item(item):
                self.destination.commit()

        self.info('compress repository')
        self.repository.compress()

        t = (time.time() - st) / 60.
        self.info('Import completed')
        self.info('imported {} analyses in {:0.1f} mins'.format(self.import_count, t))

    def _import_item(self, msrecord):
        dest = self.destination
        labnumber = msrecord.IrradPosition
        aliquot = msrecord.Aliquot
        step = msrecord.Increment

#        monitors = self._get_monitors(msrecord)
#        print monitors
#        return

#        analyses = []
        dblabnumber = dest.get_labnumber(labnumber)
#        print labnumber, dblabnumber
        if not dblabnumber:
            dblabnumber = dest.add_labnumber(labnumber)
            dest.commit()

            self._import_irradiation(msrecord, dblabnumber)

            #get all the monitors and add
            monitors = self._get_monitors(msrecord)
            for mi in monitors:
                self._import_item(mi)
            dest.commit()

#            analyses += monitors

        analyses = dblabnumber.analyses

        def test(ai):
            a = int(ai.aliquot) == int(aliquot)
            b = ai.step == step
            return a and b

        dbanal = next((ai for ai in analyses if test(ai)), None)
        if not dbanal:
            self._import_analysis(msrecord, dblabnumber)
#            self.info('adding analysis {} {}{}'.format(dblabnumber.labnumber, aliquot, step))
#            dbanal = dest.add_analysis(dblabnumber,
#                                       aliquot=aliquot,
#                                       step=step,
#                                       runtime=rdt.time(),
#                                       rundate=rdt.date()
#                                       )
#            if self._dbimport is None:
#                #add import 
#                dbimp = dest.add_import(user=self.username,
#                                        source=self.source.name,
#                                        source_host=self.source.host
#
#                                        )
#                self._dbimport = dbimp
#            else:
#                dbimp = self._dbimport
#            self._dbimport.analyses.append(dbanal)
#            path = self._import_signals(msrecord)
#            dest.add_analysis_path(path, dbanal)
#
#            self._import_blanks(msrecord, dbanal)
            return True

    def _import_analysis(self, msrecord, dblabnumber):
        aliquot = msrecord.Aliquot
        step = msrecord.Increment
        rdt = msrecord.RunDateTime
        dest = self.destination
        self.info('adding analysis {} {}{}'.format(dblabnumber.labnumber, aliquot, step))
        self.import_count += 1
        dbanal = dest.add_analysis(dblabnumber,
                                   aliquot=aliquot,
                                   step=step,
                                   runtime=rdt.time(),
                                   rundate=rdt.date()
                                   )
        ms = msrecord.login_session.machine
        if ms:
            ms = ms.Label.lower()
        #add measurement
        dest.add_measurement(dbanal, 'unknown', ms, 'MassSpec RunScript')

        if self._dbimport is None:
            #add import 
            dbimp = dest.add_import(user=self.username,
                                    source=self.source.name,
                                    source_host=self.source.host

                                    )
            self._dbimport = dbimp
        else:
            dbimp = self._dbimport

        dbimp.analyses.append(dbanal)
        path = self._import_signals(msrecord)
        dest.add_analysis_path(path, dbanal)

        self._import_blanks(msrecord, dbanal)

    def _import_blanks(self, msrecord, dbanal):
        '''
            get Bkgd and BkgdEr from IsotopeResultsTable
            get isotope results from isotope
            
        '''
        dest = self.destination
        isotopes = msrecord.isotopes
        dbhist = dest.add_blanks_history(dbanal)

        selhist = dest.add_selected_histories(dbanal)
        selhist.selected_blanks = dbhist
        for iso in isotopes:
            #use the last result
            result = iso.result[-1]
            bk, bk_er = result.Bkgd, result.BkgdEr
            dest.add_blanks(dbhist, user_value=bk, user_error=bk_er,
                            use_set=False, isotope=iso.Label)

    def _import_signals(self, msrecord):
        signals = dict()
        baselines = dict()
        isotopes = msrecord.isotopes
        for iso in isotopes:
            pt = iso.peak_time_series[-1]
            det = iso.detector.Label
            det = det if det else 'Null_Det'

            blob = pt.PeakTimeBlob
            data = [struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)]

            fit = iso.results[-1].fit
            signals[iso.Label] = det, data, fit

            pt = iso.baseline
            blob = pt.PeakTimeBlob
            data = [struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)]
            baselines[iso.Label] = det, data, 'average_SEM'

        return self._dump_file(signals, baselines)

    def _get_monitors(self, msrecord):
        irrad_level = self._get_irradiation_level(msrecord)
        if irrad_level:
            '''
                get all analyses at this irradiation level that are FC-2 and project is monitor
            '''
            src = self.source
            sess = src.get_session()
            q = sess.query(AnalysesTable)
            q = q.join(IrradiationPositionTable)
            q = q.join(SampleTable)
            q = q.join(ProjectTable)
            q = q.filter(IrradiationPositionTable.IrradiationLevel == msrecord.irradiation_position.IrradiationLevel)
            q = q.filter(SampleTable.Sample == 'FC-2')
            q = q.filter(ProjectTable.Project == 'J-Curve')
            return q.all()
#            qs = q.all()
#            for qi in qs:
#                print qi
#            q = sess.query(AnalysesTable)
#            q = q.join(IrradiationPositionTable)
#            q=q.filter(IrradiationPositionTable.IrradPosition=)
#            q = q.join(IrradiationLevelTable)
#            q = q.filter(IrradiationLevelTable.id == irrad_level.id)
#            print q.all()

    def _get_irradiation_level(self, msrecord, name=None, level=None):
        #get irradiation level
        irrad_position = msrecord.irradiation_position
        if name is None:
            name = irrad_position.IrradiationLevel[:-1]
        if level is None:
            level = irrad_position.IrradiationLevel[-1:]

        if name and level:
#            irrad_level = self._get_irradiation_level(name, level)

            src = self.source
            sess = src.get_session()
            q = sess.query(IrradiationLevelTable)
            q = q.filter(IrradiationLevelTable.IrradBaseID == name)
            q = q.filter(IrradiationLevelTable.Level == level)
            irrad_level = q.one()
            return irrad_level

    def _import_irradiation(self, msrecord, dblabnumber):
#        src = self.source
        dest = self.destination
        #get irradiation position
        irrad_position = msrecord.irradiation_position
#
#        #get irradiation level
        name, level = irrad_position.IrradiationLevel[:-1], irrad_position.IrradiationLevel[-1:]
#        if name and level:
#            irrad_level = self._get_irradiation_level(name, level)
        irrad_level = self._get_irradiation_level(msrecord, name=name, level=level)
        if irrad_level:

            #get irradiation holder
            holder = irrad_level.SampleHolder

            #get the production ratio
            pri = irrad_level.production
            prname = pri.Label
            dbpr = dest.get_irradiation_production(prname)
            if not dbpr:
                kw = dict(name=prname)
                prs = ['K4039', 'K3839', 'Ca3937', 'Ca3837', 'Ca3637', ('P36Cl38Cl', 'Cl3638')]
                for k in prs:
                    if not isinstance(k, tuple):
                        ko = k
                    else:
                        k, ko = k
                    ke = '{}Er'.format(k)
                    v = getattr(pri, k)
                    e = getattr(pri, ke)
                    kw[ko] = v
                    kw['{}_err'.format(ko)] = e

                self.info('adding production ratio {}'.format(prname))
                dbpr = dest.add_irradiation_production(**kw)

            #get irradiation
            dbirrad = dest.get_irradiation(name)
            if dbirrad is None:
                sess = self.source.get_session()
                #get the chronology
                q = sess.query(IrradiationChronologyTable)
                q = q.filter(IrradiationChronologyTable.IrradBaseID == name)
                chrons = q.all()
                chronblob = '$'.join(['{}%{}'.format(ci.StartTime, ci.EndTime) for ci in chrons])

                self.info('adding irradiation and chronology for {}'.format(name))
                dbchron = dest.add_irradiation_chronology(chronblob)
                dbirrad = dest.add_irradiation(name, production=dbpr, chronology=dbchron)

            #get irradiation level
            dblevel = next((li.name for li in dbirrad.levels if li.name == level), None)
            if not dblevel:
                self.info('adding irradiation level {}'.format(level))
                dblevel = dest.add_irradiation_level(level, dbirrad, holder)

            #add position
            dbpos = dest.add_irradiation_position(irrad_position.HoleNumber, dblabnumber, dbirrad, dblevel)

            #set the flux
            dbhist = dest.add_flux_history(dbpos)
            dbflux = dest.add_flux(irrad_position.J, irrad_position.JEr)
            dbflux.history = dbhist
            dblabnumber.selected_flux_history = dbhist

            #add the sample
            sam = irrad_position.sample
            dbproj = dest.add_project('{}-MassSpecImport'.format(sam.project.Project))
#                proj = sam.project
            dbmat = dest.add_material(irrad_position.Material)
            dbsam = dest.add_sample(sam.Sample, material=dbmat,
                                    project=dbproj)
            dblabnumber.sample = dbsam

    def _gather_data(self):
        '''
           input a list of irradiation positions (labnumbers in pychron parlance)
           get all analyses
            
        '''
        src = self.source
        sess = src.get_session()
        #get by labnumber
#        def get_analyses(ip):
#            q = sess.query(IrradiationPositionTable)
#            q = q.filter(IrradiationPositionTable.IrradPosition == ip)
#            irrad_pos = q.one()
#            return irrad_pos.analyses

#        ips = self._get_import_ids()
#        return [a for ip in ips
#                    for a in get_analyses(ip)]
        #get by project
        def get_analyses(ni):
            q = sess.query(IrradiationPositionTable)
            q = q.join(SampleTable)
            q = q.join(ProjectTable)
            q = q.filter(ProjectTable.Project == ni)
            return q.all()

        prs = ['FC-Project']
        ips = [ip for pr in prs
                for ip in get_analyses(pr)
               ]
        ans = [a for ipi in ips
                for a in ipi.analyses]
        return ans

    def _get_import_ids(self):
#        ips = ['17348']
        ips = []
        p = '/Users/ross/Sandbox/importtest/importfile2.txt'
        with open(p, 'r') as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith('#'):
                    continue
                ips.append(l)
        ips = list(set(ips))
#        with open('{}_out'.format(p), 'w') as f:
#            f.write('\n'.join(ips))
#        return ['58631']
#        return ['58621']
#        return ['57739']
        return ips#[:1]



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_experiment')
    logging_setup('importer')

    repo = Repository(root='/Users/ross/Sandbox/importtest/data')
    im = MassSpecImporter()

    s = MassSpecDatabaseAdapter(kind='mysql',
#                                username='root',
#                                password='Argon',
#                                host='localhost',
#                                name='massspecdata_local'
                                username='massspec',
                                password='DBArgon',
                                host='129.138.12.131',
                                name='massspecdata'
                                )
    s.connect()
    d = IsotopeAdapter(kind='mysql',
                       username='root',
                       host='localhost',
#                       host='129.138.12.131',
                       password='Argon',
                       name='isotopedb_FC')
    d.connect()

    im.source = s
    im.destination = d

    im.repository = repo
    im.configure_traits()


#============= EOF =============================================
