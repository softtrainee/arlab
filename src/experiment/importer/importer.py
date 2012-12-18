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
from traits.api import HasTraits, Any, Button, Instance, Str, Date, File, Int, \
    List, Enum
from traitsui.api import View, Item, TableEditor, VGroup, HGroup, EnumEditor, \
    FileEditor, spring
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
#from src.repo.repository import Repository
from src.managers.data_managers.table_descriptions import TimeSeriesTableDescription
from src.database.orms.massspec_orm import IrradiationLevelTable, \
    IrradiationChronologyTable, IrradiationPositionTable, AnalysesTable, \
    SampleTable, ProjectTable, BaselinesChangeableItemsTable, FittypeTable
from threading import Thread
import time
from src.paths import paths
from src.processing.signal import Signal
from src.database.orms.isotope_orm import meas_AnalysisTable, gen_LabTable
from sqlalchemy.sql.expression import and_
#from src.helpers.datetime_tools import get_datetime
#from datetime import datetime

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

    start_date = Date
    end_date = Date
    input_file = File
    labnumber = Int
    project = Str
    import_choice = Str('labnumber')

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
#            print di, fit, grp, k
            di = di.replace(' ', '_')
            frame.createGroup('/{}'.format(grp), k)
            where = '/{}/{}'.format(grp, k)
            tab = frame.createTable(where, di, TimeSeriesTableDescription)

            tab.attrs.fit = fit
            for y, x in data:
#                print y, x
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
        dategrp = HGroup(
                    Item('start_date'),
                    Item('end_date'),
                    enabled_when='import_choice=="date"'
                    )
        filegrp = Item('input_file',
#                       editor=FileEditor(root_path=paths.root_dir),
                       enabled_when='import_choice=="file"'
                       )
        labnumbergrp = Item('labnumber',
                       enabled_when='import_choice=="labnumber"'
                       )
        projectgrp = Item('project',
                       enabled_when='import_choice=="project"'
                       )

        v = View(
                 HGroup(Item('import_choice',
                             show_label=False,
                             style='custom',
                             editor=EnumEditor(values=['date', 'file', 'labnumber', 'project'],
                                               cols=1),
                             ),
                        VGroup(dategrp, filegrp, labnumbergrp,
                               projectgrp)),

                 HGroup(spring, Item('import_button', show_label=False)),
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
                self.destination.flush()
#                self.destination.commit()
        self.destination.commit()
#        self.info('compress repository')
#        self.repository.compress()

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
        if not dblabnumber:
            dblabnumber = dest.add_labnumber(labnumber)
            dest.flush()
#            dest.commit()

            self._import_irradiation(msrecord, dblabnumber)

#            import_monitors = False
            import_monitors = True
            if import_monitors:
                #get all the monitors and add
                monitors = self._get_monitors(msrecord)
                if monitors:
                    for mi in monitors:
                        self._import_item(mi)
                        dest.flush()
#                    dest.commit()

#            analyses += monitors

#        analyses = dblabnumber.analyses

#        def test(ai):
#            a = int(ai.aliquot) == int(aliquot)
#            b = ai.step == step
#            return a and b

#        dbanal = next((ai for ai in analyses if test(ai)), None)
        sess = dest.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.join(gen_LabTable)
        q = q.filter(gen_LabTable.labnumber == dblabnumber.labnumber)
        q = q.filter(and_(meas_AnalysisTable.aliquot == aliquot,
                           meas_AnalysisTable.step == step))
        try:
            dbanal = q.one()
        except Exception, e:
            dbanal = None
#        print dbanal, dblabnumber.labnumber, step, aliquot
        if not dbanal:
            self._import_analysis(msrecord, dblabnumber)
            dest.flush()
            return True
#            print 'exception geting {}{}'.format(aliquot, step), e

    def _import_analysis(self, msrecord, dblabnumber):
        aliquot = msrecord.Aliquot
        step = msrecord.Increment
        rdt = msrecord.RunDateTime
        status = msrecord.changeable[-1].StatusLevel

        dest = self.destination
        self.info('adding analysis {} {}{}'.format(dblabnumber.labnumber, aliquot, step))
        self.import_count += 1
        dbanal = dest.add_analysis(dblabnumber,
                                   uuid=uuid.uuid4(),
                                   aliquot=aliquot,
                                   step=step,
                                   timestamp=rdt,
#                                   runtime=rdt.time(),
#                                   rundate=rdt.date(),
                                   status=status
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

        selhist = dest.add_selected_histories(dbanal)
        self._import_signals(msrecord, dbanal, selhist)
#        dest.add_analysis_path(path, dbanal)

        self._import_blanks(msrecord, dbanal, selhist)

    def _import_blanks(self, msrecord, dbanal, selhist):
        '''
            get Bkgd and BkgdEr from IsotopeResultsTable
            get isotope results from isotope
            
        '''
        dest = self.destination
        isotopes = msrecord.isotopes
        dbhist = dest.add_blanks_history(dbanal)

        selhist.selected_blanks = dbhist
        for iso in isotopes:
            #use the last result
            result = iso.results[-1]
            bk, bk_er = result.Bkgd, result.BkgdEr
            dest.add_blanks(dbhist, user_value=bk, user_error=bk_er,
                            use_set=False, isotope=iso.Label)

    def _import_signals(self, msrecord, analysis, selhist):

        dest = self.destination
        ichist = dest.add_detector_intercalibration_history(analysis)
        selhist.selected_detector_intercalibration = ichist

        isotopes = msrecord.isotopes
        dbhist = dest.add_fit_history(analysis, user=self.username)

#        selhist.selected_fits = dbhist
        for iso in isotopes:
            pt = iso.peak_time_series[0]
            det = iso.detector.detector_type.Label
            detname = det if det else 'Null_Det'

            det = dest.get_detector(detname)
            if det is None:
                det = dest.add_detector(detname)

            v = iso.detector.ICFactor
            e = iso.detector.ICFactorEr
#            dest.add_detector_intercalibration(ichist, det, user_value=v, user_error=e)
            dest.add_detector_intercalibration(ichist, det, user_value=v, user_error=e)

            #need to get xs from PeakTimeBlob
            blob = pt.PeakTimeBlob
            _ys, xs = zip(*[struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

            #get PeakNeverBslnCorBlob
            blob = pt.PeakNeverBslnCorBlob
            #this blob is different 
            #it is a flat list of ys
            ys = [struct.unpack('>f', blob[i:i + 4])[0] for i in xrange(0, len(blob), 4)]
            fit = iso.results[-1].fit.Label

            baseline = iso.baseline
            if baseline:
                blob = baseline.PeakTimeBlob
                bys, bxs = zip(*[struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)])

                sess = self.source.get_session()
                q = sess.query(BaselinesChangeableItemsTable)
                q = q.filter(BaselinesChangeableItemsTable.BslnID == baseline.BslnID)
                ch = q.one()

                q = sess.query(FittypeTable)
                q = q.filter(FittypeTable.Fit == ch.Fit)
                dbfi = q.one()
                if dbfi:
                    bfit = dbfi.Label
                else:
                    bfit = 'average_sem'
            else:
                bys, bxs = [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]
                bfit = 'average_sem'

            for k, (xi, yi), fi in (('signal', (xs, ys), fit), ('baseline', (bxs, bys), bfit)):
                data = ''.join([struct.pack('>ff', x, y) for x, y in zip(xi, yi)])
                #add isotope
#                print iso.Label
                smw = self.source.get_molecular_weight(iso.Label)
#                print iso.Label, smw
                molweight = dest.get_molecular_weight(iso.Label)
                if not molweight:
                    smw = self.source.get_molecular_weight(iso.Label)
                    mass = smw.AtomicWeight
                    molweight = dest.add_molecular_weight(iso.Label, mass)
                    dest.flush()

                dbiso = dest.add_isotope(analysis, molweight, det, kind=k)

                #add signal data
                dest.add_signal(dbiso, data)

                #add fit
                if fi == 'Average Y':
                    fi = 'average_SEM'

                dest.add_fit(dbhist, dbiso,
                             fit=fi, filter_outliers=True,
                             filter_outlier_iterations=1, filter_outlier_std_devs=2
                             )

                #do pychron fit of the data
                sig = Signal(xs=xi, ys=yi, fit=fi,
                             filter_outliers=True,
                             filter_outlier_iterations=1,
                             filter_outlier_std_devs=2)

#                print sig.value
                #add isotope result
                try:
                    s, e = sig.value, sig.error
                except TypeError:
                    print k, fi
                    print xi, yi
                    s, e = 0, 0
                dest.add_isotope_result(dbiso,
                                      dbhist,
                                      signal_=s, signal_err=e,
                                      )
                dest.flush()

#            signals[iso.Label] = det, zip(ys, xs), fit
#            baselines[iso.Label] = det, data, 'average_SEM'

#        return self._dump_file(signals, baselines)

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
                prs = ['K4039', 'K3839', 'K3739', 'Ca3937', 'Ca3837', 'Ca3637',
                       ('P36Cl38Cl', 'Cl3638'),
                       ('Ca_K')
                       ]
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
                q = q.order_by(IrradiationChronologyTable.EndTime.asc())
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
        import_choice = self.import_choice
        if import_choice == 'labnumber':
            return self._gather_data_by_labnumber(sess, self.labnumber)
        elif import_choice == 'file':
            lns = self._get_import_ids(self.input_file)
            return self._gather_data_by_labnumber(sess, lns)
        elif import_choice == 'project':
            return self._gather_data_by_project(sess, self.project)
        elif import_choice == 'date':
            return self._gather_data_by_date_range(sess, self.start_date,
                                                         self.end_date)


    def _gather_data_by_labnumber(self, sess, labnumber):
        #get by labnumber
        def get_analyses(ip):
            q = sess.query(IrradiationPositionTable)
            q = q.filter(IrradiationPositionTable.IrradPosition == ip)
            irrad_pos = q.one()
            return irrad_pos.analyses

        if not isinstance(labnumber, list):
            labnumber = [labnumber]
#        ips = self._get_import_ids()
        return [a for ip in labnumber
                    for a in get_analyses(ip)]

    def _gather_data_by_project(self, sess, project):
        #get by project
        def get_analyses(ni):
            q = sess.query(IrradiationPositionTable)
            q = q.join(SampleTable)
            q = q.join(ProjectTable)
            q = q.filter(ProjectTable.Project == ni)
            return q.all()

        if not isinstance(project, list):
            project = [project]

#        prs = ['FC-Project']
        ips = [ip for pr in project
                for ip in get_analyses(pr)
               ]
        ans = [a for ipi in ips
                for a in ipi.analyses]

        return ans

    def _gather_data_by_date_range(self, sess, start, end):
        '''
            fmt = '%m/%d/%Y'
            d = '10/24/2012'
            s = datetime.strptime(d, fmt)
    
            d = '10/31/2012'
            e = datetime.strptime(d, fmt)
        '''
        #get by range
        q = sess.query(AnalysesTable)
        q = q.filter(and_(AnalysesTable.RunDateTime >= start, AnalysesTable.RunDateTime < end))
        return q.all()

    def _get_import_ids(self, p):
#        p = '/Users/ross/Sandbox/importtest/importfile2.txt'

        ips = []
        with open(p, 'r') as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith('#'):
                    continue
                ips.append(l)

        ips = list(set(ips))
        return ips

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_experiment')
    logging_setup('importer')

#    repo = Repository(root='/Users/ross/Sandbox/importtest/data')
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
                       name='isotopedb_dev')
    d.connect()

    im.source = s
    im.destination = d

#    im.repository = repo
    im.configure_traits()


#============= EOF =============================================
