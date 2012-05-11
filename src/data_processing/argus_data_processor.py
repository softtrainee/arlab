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



#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================
import csv
import struct
import os
from pylab import transpose
#============= local library imports  ==========================
from src.database.nmgrl_database_adapter import NMGRLDatabaseAdapter
from src.loggable import Loggable

mkeys = ['l2 value', 'l1 value', 'ax value', 'h1 value', 'h2 value']

class ArgusDataProcessor(Loggable):
    '''
        this class takes an csw file from Imhotep preps it for 
        saving into a database
    '''
    _db = None



    def read_csv_file(self, path, **kw):
        '''
            
        '''
        with open(path, 'U') as f:
            reader = csv.reader(f, **kw)
            header = reader.next()
            lines = [line for line in reader]
            return header, lines
    def parse_imhootep_file(self, path):
        '''
            
        '''
        _header, lines = self.read_csv_file(path, delimiter='\t')
        for line in lines[0:4]:
            '''
            each line represents an analysis
            cycles in column blocks 
            '''
            try:
                int(line[0])
            except ValueError:
                continue
            _blob_dict = self.get_peak_blobs(line)

        return None, None

    def get_peak_blobs(self, line):
        '''
            
        '''
        self.info('generating peak blobs')
        numcycles = (len(line) - 2) / 25
        signals_dict = dict(m40=[],
                            m39=[],
                            m38=[],
                            m37=[],
                            m36=[],
                            )

        mkey = ['m36', 'm37', 'm38', 'm39', 'm40']
        for c in range(numcycles):
            for i, k in enumerate(mkey):
                pos = 25 * c + 5 * i
                data = (float(line[3 + pos ]), float(line[4 + pos]))
                signals_dict[k].append(data)

        peakblob = dict()
        for k in mkey:
            v, t = transpose(signals_dict[k])
            peakblob[k] = self.build_timeblob(t, v)
        return peakblob

    def parse_data_file(self, path):
        '''
            @type path: C{str}
            @param path:
        '''
        fail = None
        sess = None
        header, lines = self.read_csv_file(path)
        for l in lines:
            #make a dictionary of the values using header as keys
            analysis_args = dict(zip(header, l))
            #save project info
            if 'Project' in analysis_args:
                sess = self._db.add_project(dict(Project=analysis_args['Project']), sess=sess)
                sess.flush()
            #save sample info
            if 'Sample' in analysis_args:
                sess = self._db.add_sample(dict(Project=analysis_args['Project'],
                                                Sample=analysis_args['Sample']), sess=sess)
                sess.flush()

            #save irradiation info
            ikeys = ['IrradiationLevel', 'HoleNumber', 'Material', 'Sample']
            iargs = dict()
            for k in ikeys:
                if k not in analysis_args:
                    fail = 'Invalid irrad pos key {}'.format(k)
                    break
                iargs[k] = analysis_args[k]

            if fail:
                break

            dbirradiationpos, sess = self._db.add_irradiation_position(iargs, sess=sess)
            sess.flush()

            #add analysis and aranalysis
            if 'RID' in analysis_args:
                dbanalysis, new, sess = self._db.add_analysis(dict(RID=analysis_args['RID']),
                                             None, sess=sess, dbirradiationpos=dbirradiationpos)

                sess.flush()
            if not new:
                #get the isotopes and update
                isos, sess = self._db.get_isotopes(dbanalysis.AnalysisID, sess=sess)
                for i, iso in enumerate(isos):
                    iso.NumCnts += 1
                    #update peak time table
                    pk, sess = self._db.get_peaktimeblob(iso.IsotopeID, sess=sess)
                    ts, vs = self.parse_timeblob(pk.PeakTimeBlob)
                    vs.append(analysis_args[mkeys[i]])
                    ts.append(analysis_args['Time'])
                    pk.PeakTimeBlob = self.build_timeblob(ts, vs)

            else:
                #add the detector info
                detector_ids = []
                dkeys = [('l2 gain', 'l2 type'), ('l1 gain', 'l1 type'), ('ax gain', 'ax type'),
                       ('h1 gain', 'h1 type'), ('h2 gain', 'h2 type')]
                args = dict()
                for dk_1, dk_2 in dkeys:
                    if dk_1 in analysis_args and dk_2 in analysis_args:
                        args['Gain'] = analysis_args[dk_1]
                        args['DetectorTypeID'] = analysis_args[dk_2]
                        detector, sess = self._db.add_detector(None, args, sess=sess)
                        #keep a list of the added detectorIDs
                        #list will be in order from L2 to H2
                        sess.flush()
                        detector_ids.append(detector.DetectorID)
                    else:
                        fail = 'detector args %s %s' % (dk_1, dk_2)
                        break
                if fail:
                    break
                #update the isotope dict
                isotopes = [dict(Label='Ar36', NumCnts=1),
                            dict(Label='Ar38', NumCnts=1),
                            dict(Label='Ar37', NumCnts=1),
                            dict(Label='Ar39', NumCnts=1),
                            dict(Label='Ar40', NumCnts=1) ]

                #add the baselines

                #add isotopes
                for i, iso in enumerate(isotopes):
                #TODO add baseline ref.
                #requires reference to analyses, detector
                    dbisotope, sess = self._db.add_isotope(iso, sess=sess, dbanalysis=dbanalysis,
                                                           dbdetector=detector_ids[i])
                    if dbisotope is not None:
                #add the peak time series
                        v = [analysis_args[mkeys[i]]]
                        t = [analysis_args['Time']]
                        sess = self._db.add_peaktimeblob(None, self.build_timeblob(t, v),
                                              sess=sess, dbisotope=dbisotope)
                #add a araranalysis
                sess = self._db.add_arar_analysis(dict(), sess=sess, dbanalysis=dbanalysis)

        return sess, fail
    def test(self):
        '''
        '''

        #clear the tables


        return False
    def upload_data(self, path):
        '''
            @type path: C{str}
            @param path:
        '''
        if os.path.isfile(path):
            self.info('uploading %s' % path)
            #sess, fail = self.parse_data_file(path)
            sess, fail = self.parse_imhootep_file(path)
        else:
            self.warning('Invalid data path %s' % path)
            return

        if fail:
            self.info(fail)
            sess.rollback()
        else:
            if sess is not None:
                self.info('committing session')
                sess.commit()
                sess.close()

        self.info('upload finished')



    def connect(self):
        '''
            establish a database connection
            
            creates _db object 
        '''
        debug = True
        type = 'mysql'
        if debug:
            user = 'root'
            dbname = 'argustestdata'
            host = 'localhost'
            password = None
        else:
            user = 'massspec'
            dbname = 'Argustestdatabase'
            host = '129.138.12.131'
            password = 'DBArgon'
        self.info('connecting to %s@%s' % (dbname, host))

        self._db = NMGRLDatabaseAdapter(type, user, host, dbname, password)


    def build_timeblob(self, t, v):
        '''
            @type t: C{str}
            @param t:

            @type v: C{str}
            @param v:
        '''
        blob = ''
        for ti, vi in zip(t, v):
            blob += struct.pack('>ff', float(vi), float(ti))
        return blob

    def parse_timeblob(self, blob):
        '''
            @type blob: C{str}
            @param blob:
        '''
        v = []
        t = []
        for i in range(0, len(blob), 8):
            vi, ti = struct.unpack('>ff', blob[i:i + 8])
            v.append(vi)
            t.append(ti)

        return t, v

#============= EOF ====================================
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
#                        sess = self._db.add_peaktimeblob(None, self.build_timeblob(t, v),
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
