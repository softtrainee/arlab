'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import Instance, Button
from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================
import csv
import struct
import os
#from pylab import transpose
from numpy import loadtxt
#============= local library imports  ==========================
from src.database.nmgrl_database_adapter import NMGRLDatabaseAdapter
from src.loggable import Loggable
#from src.helpers.paths import data_dir
from src.helpers.logger_setup import setup
from src.data_processing.regression.ols import OLS
from src.managers.manager import Manager

mkeys = ['l2 value', 'l1 value', 'ax value', 'h1 value', 'h2 value']

'''
following information is necessary


'''

RUN_TYPE_DICT = dict(Air=2, Blank=5)
SAMPLE_DICT = dict(Air=2, Blank=1)
ISO_LABELS = dict(H1='Ar40', AX='Ar39', L1='Ar38', L2='Ar37', CDD='Ar36')

DEBUG = True


class MassSpecDatabaseImporter(Manager):
    '''
        this class takes an csw file from Imhotep preps it for
        saving into a database
    '''
    _db = Instance(NMGRLDatabaseAdapter, dict(dbname='massspecdata_test'))

    load_button = Button



    def upload_data(self, path):
        '''
        '''
        fail = ''
        root = os.path.dirname(path)
        if os.path.isfile(path):
            self.info('uploading {}'.format(path))
            fail = self.write_data_to_db(root, path)
        else:
            self.warning('Invalid data path {}'.format(path))
            return

        if fail:
            self.info(fail)
            self._db.rollback()

        else:
            self.info('committing session')
            self._db.commit()
            self._db.close()

        self.info('upload finished')

    def write_data_to_db(self, root, path):
        '''
        '''
        if DEBUG:
            for name in ['AnalysesChangeableItemsTable',
                         'DetectorTable', 'BaselinesTable',
                         'IsotopeTable', 'IsotopeResultsTable',
                         'PeakTimeTable']:
                self._db.clear_table(name)
                self._db.commit()

        fail = None

        header, lines = self._load_config_file(path, delimiter='\t')
        for l in lines:
            #make a dictionary of the values using header as keys
            analysis_args = dict(zip(header, l))
            #==================================================================
            # #save project info
            #==================================================================
            try:
                d = dict(Project=analysis_args['Project'])
                _dbproject = self._db.add_project(d)
            except KeyError:
                pass

            #==================================================================
            # save sample info
            #==================================================================
            d = dict(Sample=analysis_args['Sample'])
            try:
                project = analysis_args['Project']
            except KeyError:
                project = None
            _dbsample = self._db.add_sample(d, project=project)

            #==================================================================
            # add analysis
            #==================================================================
            rid = analysis_args['RID']
            try:
                samplekey = analysis_args['Sample'].strip()
            except KeyError:
                self.warning('invalid sample using default 5 (Air)')
                samplekey = 5

            try:
                runtype = analysis_args['RunType'].strip()
            except KeyError:
                self.warning('invalid runt type using default Air')
                runtype = 'Air'

            try:
                runtime = analysis_args['RunDateTime'].strip()
            except KeyError:
                runtime = '2012-03-01 01:01:01'

            try:
                a = analysis_args['Detectors'].strip()
                det_keys = a.split(',')
            except KeyError:
                return 'Need to specify Detectors in config file'

            try:
                labels = analysis_args['Labels'].strip()
            except KeyError:
                labels = [ISO_LABELS[dk.upper()] for dk in det_keys]

            d = dict(RID=rid,
                   RedundantSampleID=SAMPLE_DICT[samplekey],
                   RunDateTime=runtime,
                   LoginSessionID=1,
                   SpecRunType=RUN_TYPE_DICT[runtype]
                   )

            self.info('adding analysis {}'.format(rid))
            dbanalysis, _new = self._db.add_analysis(d, dbirradiationpos= -2)
            self._db.flush()
            self._load_analysis_items(root, rid, dbanalysis, det_keys, labels)

        return fail

    def _load_analysis_items(self, root, rid, dbanalysis, detector_keys,
                              iso_labels):
        #load baseline
        pb = os.path.join(root, '{}-baseline001.txt'.format(rid))
        baseline_data = loadtxt(pb, delimiter=',', unpack=True)

        #======================================================================
        # #load time v intensity
        #======================================================================
        p = os.path.join(root, '{}-intensity001.txt'.format(rid))

        ISO_FORMAT_STR = "%Y-%m-%d %H:%M:%S"
        from datetime import datetime
        dt = datetime.fromtimestamp(os.stat(p).st_mtime)
        dbanalysis.RunDateTime = dt.strftime(ISO_FORMAT_STR)

        intensity_data = loadtxt(p, delimiter=',', unpack=True)
        #======================================================================
        # add the detector info
        #======================================================================
        detectors = []

        for i, (dk, label) in enumerate(zip(detector_keys, iso_labels)):
            args = dict(DetectorTypeID=i + 24,
                        Disc=1,
                        DiscEr=0,
                        ICFactor=1,
                        ICFactorEr=0,
                        Label=dk.upper()
                        )
            dbdetector = self._db.add_detector(args)
            self._db.flush()
            detectors.append(dbdetector)

            tb = baseline_data[0]
            vb = baseline_data[i + 1]

            blob = self._build_timeblob(tb, vb)
            d = dict(PeakTimeBlob=blob,
                      Label='{} Baseline'.format(dk.upper()),
                      NumCnts=tb.shape[0])

            dbbaseline = self._db.add_baseline(d)
            bi = vb.mean()
            bie = vb.std()

            self._db.flush()

            d = dict(Label=label, NumCnts=1)
            d['BslnID'] = dbbaseline.BslnID

            dbisotope = self._db.add_isotope(d,
                               dbanalysis=dbanalysis,
                               dbdetector=detectors[i])
            t = intensity_data[0]
            v = intensity_data[i + 1]

            o = OLS(t, v, fitdegree=2)
            i = o.get_coefficients()[2]
            ie = o.get_coefficient_standard_errors()[2]

#            self._db.add_isotope_result(
#                                        dict(Intercept=i,
#                                             InterceptEr=ie,
#                                             Iso=i - bi,
#                                             IsoEr=(ie ** 2 + bie ** 2) ** 0.5,
#                                             DataReductionSessionID=0,
#                                             BkgdDetTypeID=0
#                                             ),
#                                        dbisotope=dbisotope)
            if dbisotope is not None:
                #add the peak time series
                _pk = self._db.add_peaktimeblob(self._build_timeblob(t, v),
                                      dbisotope=dbisotope)

    def _build_timeblob(self, t, v):
        '''
        '''
        blob = ''
        for ti, vi in zip(t, v):
            blob += struct.pack('>ff', float(vi), float(ti))
        return blob

    def _parse_timeblob(self, blob):
        '''
        '''
        v = []
        t = []
        for i in range(0, len(blob), 8):
            vi, ti = struct.unpack('>ff', blob[i:i + 8])
            v.append(vi)
            t.append(ti)

        return t, v

    def _load_config_file(self, path, **kw):
        '''
        '''
        with open(path, 'U') as f:
            reader = csv.reader(f, **kw)
            header = reader.next()
            lines = [line for line in reader]
            return header, lines

    def traits_view(self):
        v = View(Item('_db', show_label=False,
                      style='custom'),
                 Item('load_button',
                      show_label=False)
                 )
        return v

    def _load_button_fired(self):
        p = self.open_file_dialog()
        if p is not None:
            self._db.connect()
            self.upload_data(p)

if __name__ == '__main__':

    setup('db_import')
    d = MassSpecDatabaseImporter()
    d.configure_traits()
#    d._db = NMGRLDatabaseAdapter(dbname='massspecdata_test')



#    d._db.connect()
#    p = os.path.join(data_dir, 'automated_runs', 'mswd_counting_experiment',
#                     'upload_config.txt')
#    d.upload_data(p)
#============= EOF ====================================
#    def connect(self):
#        '''
#            establish a database connection
#            creates _db object 
#        '''
#        debug = True
#        dbtype = 'mysql'
#        if debug:
#            user = 'root'
#            dbname = 'argustestdata'
#            host = 'localhost'
#            password = None
#        else:
#            user = 'massspec'
#            dbname = 'Argustestdatabase'
#            host = '129.138.12.131'
#            password = 'DBArgon'
#        self.info('connecting to %s@%s' % (dbname, host))
#
#        self._db = NMGRLDatabaseAdapter(dbtype, user, host, dbname, password)
            #add a araranalysis
#        sess = self._db.add_arar_analysis(dict(), sess=sess, dbanalysis=dbanalysis)

#        return sess
#
#                dkeys = [('cdd gain', 'cdd type'),
#                         ('l2 gain', 'l2 type'), ('l1 gain', 'l1 type'), ('ax gain', 'ax type'),
#                       ('h1 gain', 'h1 type'), ('h2 gain', 'h2 type')]
#                args = dict()
#                for dk_1, dk_2 in dkeys:
#                    if dk_1 in analysis_args and dk_2 in analysis_args:
#                        args['Gain'] = analysis_args[dk_1]
#                        args['DetectorTypeID'] = analysis_args[dk_2]
#                        detector, sess = self._db.add_detector(None, args, sess=sess)
                        #keep a list of the added detectorIDs
                        #list will be in order from L2 to H2
#                        sess.flush()
#                        detector_ids.append(detector.DetectorID)
#                    else:
#                        fail = 'detector args %s %s' % (dk_1, dk_2)
#                        break
#                if fail:
#                    break

#                #update the isotope dict
#            if not new:
#                pass
#                #get the isotopes and update
#                isos, sess = self._db.get_isotopes(dbanalysis.AnalysisID, sess=sess)
#                for i, iso in enumerate(isos):
#                    iso.NumCnts += 1
#                    #update peak time table
#                    pk, sess = self._db.get_peaktimeblob(iso.IsotopeID, sess=sess)
#                    ts, vs = self._parse_timeblob(pk.PeakTimeBlob)
#                    vs.append(analysis_args[mkeys[i]])
#                    ts.append(analysis_args['Time'])
#                    pk.PeakTimeBlob = self._build_timeblob(ts, vs)
#                sess = self.delete_analysis(dbanalysis, sess)
#                sess = self.load_analysis(root, rid, dbanalysis, sess)
#            else:
#    def parse_input_file(self, path):

#    def parse_imhootep_file(self, path):
#        '''
#            
#        '''
#        _header, lines = self.read_csv_file(path, delimiter='\t')
#        for line in lines[0:4]:
#            '''
#            each line represents an analysis
#            cycles in column blocks 
#            '''
#            try:
#                int(line[0])
#            except ValueError:
#                continue
#            _blob_dict = self.get_peak_blobs(line)
#
#        return None, None

#    def get_peak_blobs(self, line):
#        '''
#            
#        '''
#        self.info('generating peak blobs')
#        numcycles = (len(line) - 2) / 25
#        signals_dict = dict(m40=[],
#                            m39=[],
#                            m38=[],
#                            m37=[],
#                            m36=[],
#                            )
#
#        mkey = ['m36', 'm37', 'm38', 'm39', 'm40']
#        for c in range(numcycles):
#            for i, k in enumerate(mkey):
#                pos = 25 * c + 5 * i
#                data = (float(line[3 + pos ]), float(line[4 + pos]))
#                signals_dict[k].append(data)
#
#        peakblob = dict()
#        for k in mkey:
#            v, t = transpose(signals_dict[k])
#            peakblob[k] = self._build_timeblob(t, v)
#        return peakblob
#    def load_peak_time_file(self, p, nsignals=2):
#        retiloadtxt(p, unpack=True)
#
#        return
#    def parse_(self, path, keys):
#        self.info('parsing %s' % path)
#        with open(path, 'r') as f:
#            reader = csv.reader(f)
#            header = reader.next()
#            results = []
#            for line in reader:
#                results.append(dict(zip(keys, line)))
#        return results
#    def parse_detectors(self, path):
#        self.info('parsing %s' % path)
#        detectors = []
#        with open(path, 'r') as f:
#            reader = csv.reader(f)
#            header = reader.next()
#            keys = ['Gain', 'DetectorTypeID']
#            for line in reader:
#                gains = [float(g) for g in line[:5]]
#                types = line[5:]
#                detectors.append([dict([(keys[i], attr) for i, attr in enumerate(det)])
#                            for det in zip(gains, types)])
#        return detectors
#
#    def parse_analyses(self, path):
#        self.info('parsing %s' % path)
#        with open(path, 'r') as f:
#            reader = csv.reader(f)
#            header = reader.next()
#            analyses = []
#            irrad_args = []
#            isotopes = [dict(Label = 'ar40'),
#                            dict(Label = 'ar39'),
#                            dict(Label = 'ar38'),
#                            dict(Label = 'ar37'),
#                            dict(Label = 'ar36'),
#                            ]
#            ikeys = ['RID', 'IrradiationPositionLevel', 'HoleNumber']
#            keys = ['RID', 'Tot40', 'Tot39', 'Tot38', 'Tot37', 'Tot36']
#            n = 2
#            for line in reader:
#                signals = [float(iso) for iso in line[n:n + 5]]
#                irrad_args.append(dict(zip(ikeys, line[:n + 1])))
#                analyses.append(dict(zip(keys, [line[0]] + signals)))
#
#        return zip(analyses, irrad_args)
#
#    def parse_projects(self, path):
#        keys = ['Project']
#        return self.parse_(path, keys)
#
#    def parse_samples(self, path):
#        keys = ['Sample', 'Project']
#        return self.parse_(path, keys)
#
#    def parse_irradiations(self, path):
#
#        keys = ['IrradiationLevel', 'HoleNumber', 'Material', 'Sample']
#        return self.parse_(path, keys)

#    def parse_and_write(self, paths):
#        path, detectorpath, irradiationpath, samplepath, projectpath = paths
#        self.info('uploading %s' % path)
#        sess = None
#        #save project info
#        for project in self.parse_projects(projectpath):
#            sess = self._db.add_project(project)
#        sess.commit()
#
#        #save sample info
#        for sample in self.parse_samples(samplepath):
#            sess = self._db.add_sample(sample, sess = sess)
#        sess.commit()
#
#        #save irradiation info
#        for irradiation in self.parse_irradiations(irradiationpath):
#            sess = self._db.add_irradiation_position(irradiation, sess = sess)
#        sess.commit()
#
#        #add an analysis and araranalysis
#        for analysis, irrad_args in self.parse_analyses(path):
#
#            RID = analysis['RID']
#            dbanalysis, sess = self._db.add_analysis(dict(RID = RID), irrad_args, sess = sess)
#            if dbanalysis is not None:
#                #dbanalysis is None if an analysis entry already exists
#                sess.commit()
#                sess = self._db.add_arar_analysis(analysis, sess = sess, dbanalysis = dbanalysis)
#
#                #save detector info
#                detector_ids = []
#                for detectors in self.parse_detectors(detectorpath):
#                    for i, d in enumerate(detectors):
#                        detector, sess = self._db.add_detector(None, d, sess = sess)
#                        #keep a list of the added detectorIDs
#                        #list will be in order from L2 to H2
#                        sess.commit()
#                        detector_ids.append(detector.DetectorID)
#
#                isotopes = [dict(Label = 'ar36', NumCnts = 10),
#                            dict(Label = 'ar38', NumCnts = 10),
#                            dict(Label = 'ar37', NumCnts = 10),
#                            dict(Label = 'ar39', NumCnts = 10),
#                            dict(Label = 'ar40', NumCnts = 10) ]
#    #           #add isotopes
#                t = range(10)
#                v = range(10)
#                for i, iso in enumerate(isotopes):
#                #requires reference to analyses, detector
#                    dbisotope, sess = self._db.add_isotope(detector_ids[i], None, iso, sess = sess, dbanalysis = dbanalysis)
#                    print dbisotope
#                    if dbisotope is not None:
#                        sess = self._db.add_peaktimeblob(None, self._build_timeblob(t, v),
#                                              sess = sess, dbisotope = dbisotope)
#        return sess
#def write_to_db(self, analysis, new = False):
#
#        self.info('WRITE TO DB')
#
#        dbanalysis, sess = self._db.get_analysis(analysis.rid)
#        if dbanalysis is not None:
#            analysis_id = dbanalysis.AnalysisID
#            self.info('found analysis_id %s, %s' % (analysis_id, analysis.rid))
#
#
##        self.info('save irradiation info')
##
##        self.info('save sample info')
##
##        self.info('save spectrometer parameters')
#
#        self.info('save unchangeable items')
#        if dbanalysis is None:
#            self.info('adding new analysis')
#            dbanalysis, sess = self._db.add_analysis(None, analysis, sess = sess)
#
##        self.info('save runid components')
##
##        self.info('save project id')
##
##        self.info('save user id')
##
##        self.info('save ref detector id')
##
##        self.info('save changeable items')
##
#        self.info('save raw signals')
#        #save the measurement data
#        args = ['Tot40', 'Tot39', 'Tot38', 'Tot37', 'Tot36']
#        args = dict(zip(args, analysis.signals[:5]))
#        self._db.add_arar_analysis(dbanalysis, args , sess = sess)
#
##        self.info('save baselines')
##
#        self.info('save isotope values')
#        for d, iso in enumerate(analysis.isotopes):
#            self._db.add_isotope(dbanalysis, 10000 + d, iso, sess = sess)
##        self.info('save ratios')
#
#        if sess is not None:
#            self.info('committing session')
#            sess.commit()
#           # sess.close()
#        self.info('finished')
