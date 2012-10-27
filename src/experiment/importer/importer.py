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
    IrradiationChronologyTable, IrradiationPositionTable
#from src.database.orms.isotope_orm import meas_AnalysisTable

class Importer(Loggable):
    username = Str('root')
    source = Any
    destination = Any
    import_button = Button
    display = Instance(RichTextDisplay)
    repository = Any
    _dbimport = None

    def info(self, msg, log=True, **kw):
        if log:
            super(Importer, self).info(msg, **kw)
        self.display.add_text(msg)

    def _import_button_fired(self):
        self._import()

    def _import(self):
        pass

    def _gather_data(self):
        pass

    def _dump_file(self, signals, baselines):
        dm = H5DataManager()
        name = uuid.uuid4()
        name = '{}.h5'.format(name)
        path = os.path.join(self.repository.root, name)
        frame = dm.new_frame(path=path)

        frame.createGroup('/', 'signals')
        frame.createGroup('/', 'baselines')
        #make new h5 file

        def write_file(di, data, grp, k):
            di = di.replace(' ', '_')
            frame.createGroup('/{}'.format(grp), k)
            where = '/{}/{}'.format(grp, k)
            tab = frame.createTable(where, di, TimeSeriesTableDescription)
            for y, x in data:
                nrow = tab.row
                nrow['time'] = x
                nrow['value'] = y
                nrow.append()
            tab.flush()

        for k, v in signals.iteritems():
            det, data = v
            write_file(det, data, 'signals', k)

            det, data = baselines[k]
            write_file(det, data, 'baselines', k)
#                frame.createTable(grp, 'Det')

        dm.close()
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
        items = self._gather_data()
        for item in items:
            self._import_item(item)
            self.destination.commit()

    def _import_item(self, msrecord):
        dest = self.destination
        labnumber = msrecord.IrradPosition
        aliquot = msrecord.Aliquot
        step = msrecord.Increment
        rdt = msrecord.RunDateTime

        dblabnumber = dest.get_labnumber(labnumber)
        if not dblabnumber:
            dblabnumber = dest.add_labnumber(labnumber)
            self._import_irradiation(msrecord, dblabnumber)

        analyses = dblabnumber.analyses
        def test(ai):
            a = int(ai.aliquot) == int(aliquot)
            b = ai.step == step
            return a and b

        dbanal = next((ai for ai in analyses if test(ai)), None)
        if not dbanal:
            self.info('adding analysis {} {}{}'.format(dblabnumber.labnumber, aliquot, step))
            dbanal = dest.add_analysis(dblabnumber,
                                       aliquot=aliquot,
                                       step=step,
                                       runtime=rdt.time(),
                                       rundate=rdt.date()
                                       )
            if self._dbimport is None:
                #add import 
                dbimp = dest.add_import(user=self.username)
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
            result = iso.result
            bk, bk_er = result.Bkgd, result.BkgdEr
            dest.add_blanks(dbhist, user_value=bk, user_error=bk_er,
                            use_set=False, isotope=iso.Label)



    def _import_signals(self, msrecord):
        signals = dict()
        baselines = dict()
        isotopes = msrecord.isotopes
        for iso in isotopes:
            pt = iso.peak_time_series
            det = iso.detector.Label
            det = det if det else 'Null_Det'

            blob = pt.PeakTimeBlob
            data = [struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)]
            signals[iso.Label] = det, data

            pt = iso.baseline
            blob = pt.PeakTimeBlob
            data = [struct.unpack('>ff', blob[i:i + 8]) for i in xrange(0, len(blob), 8)]
            baselines[iso.Label] = det, data

        return self._dump_file(signals, baselines)
#            dest.commit()
    def _import_irradiation(self, msrecord, dblabnumber):
        src = self.source
        dest = self.destination
        #get irradiation position
        irrad_position = msrecord.irradiation_position

        #get irradiation level
        name, level = irrad_position.IrradiationLevel[:-1], irrad_position.IrradiationLevel[-1:]
        if name and level:
            sess = src.get_session()
            q = sess.query(IrradiationLevelTable)
            q = q.filter(IrradiationLevelTable.IrradBaseID == name)
            q = q.filter(IrradiationLevelTable.Level == level)
            irrad_level = q.one()
#            print irrad_level.IrradBaseID, irrad_level.Level

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
        def get_analyses(ip):
            q = sess.query(IrradiationPositionTable)
            q = q.filter(IrradiationPositionTable.IrradPosition == ip)
            irrad_pos = q.one()
            return irrad_pos.analyses

        ips = self._get_import_ids()
        return [a for ip in ips
                    for a in get_analyses(ip)]

    def _get_import_ids(self):
#        ips = ['17348']
        ips = []
        p = '/Users/ross/Sandbox/importtest/importfile.txt'
        with open(p, 'r') as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith('#'):
                    continue
                ips.append(l)

        return ips



if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
#    paths.build('_test')
    logging_setup('importer')

    repo = Repository(root='/Users/ross/Sandbox/importtest')
    im = MassSpecImporter()

    s = MassSpecDatabaseAdapter(kind='mysql', username='root', password='Argon', name='massspecdata_local')
    s.connect()
    d = IsotopeAdapter(kind='mysql', username='root', password='Argon',
                        name='isotopedb_dev_import')
    d.connect()

    im.source = s
    im.destination = d

    im.repository = repo
    im.configure_traits()


#============= EOF =============================================
