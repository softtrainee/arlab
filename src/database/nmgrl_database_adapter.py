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

#=============enthought library imports=======================

#=============standard library imports ========================

# make a global session
from sqlalchemy.orm import sessionmaker
from src.database.nmgrl_orm import IsotopeResultsTable, \
    AnalysesChangeableItemsTable, BaselinesTable

Session = sessionmaker()

#=============local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from nmgrl_orm import  DetectorTable, \
     IsotopeTable, AnalysesTable, ArArAnalysisTable, \
    IrradiationPositionTable, MaterialTable, SampleTable, ProjectTable, \
    PeakTimeTable


class NMGRLDatabaseAdapter(DatabaseAdapter):
    def _get_tables(self):
        return globals()

    def clear_table(self, tablename):
        sess = self.get_session()
        try:
            table = globals()[tablename]
        except KeyError, e:
            print e
            a = None

        try:
            a = sess.query(table)
        except Exception, e:
            print e
            a = None
        if a is not None:
            a.delete()

    def get_rids(self, limit=1000):
        '''
        '''
#        if sess is None:
#            sess = self.session_factory()
        sess = self.get_session()
        q = sess.query(AnalysesTable.AnalysisID, AnalysesTable.RID)
        p = q.limit(limit)
        return p

    def get_project(self, project):
        '''
        '''
        return self._get_one(ProjectTable, dict(Project=project))

    def get_araranalysis(self, aid):
        '''
        '''
        return self._get_one(ArArAnalysisTable, dict(AnalysisID=aid))

    def get_araranalyses(self, aid):
        '''
        '''
        return self._get(ArArAnalysisTable, dict(AnalysisID=aid), func='all')

    def get_analysis(self, rid):
        '''
        '''
        sess = self.get_session()




        return self._get_one(AnalysesTable, dict(RID=rid))

    def get_analyses(self, **kw):
        '''
        '''
        table = AnalysesTable


#        return self._get_all((AnalysesTable.RID,))
#        if sess is None:
#            sess = self.session_factory()
#        p = sess.query(AnalysesTable.RID).all()

#        return p, sess

    def get_detector(self, did, sess=None):
        '''
        '''
        return self._get_one(DetectorTable, dict(DetectorID=did))

    def get_material(self, material, sess=None):
        '''
        '''
        return self._get_one(MaterialTable, dict(Material=material))

    def get_sample(self, sample, sess=None):
        '''
        '''
        return self._get_one(SampleTable, dict(Sample=sample))
#        if sess is None:
#            sess = self.session_factory()
#        try:
#            s = sess.query(SampleTable).filter_by(Sample=sample).one()
#        except:
#            s = None
#        return s, sess

    def get_isotopes(self, aid, sess=None):
        '''
        '''
#        return self._get_all((IsotopeTable.AnalysisID,))
#        if sess is None:
#            sess = self.session_factory()
        sess = self.get_session()
        isos = sess.query(IsotopeTable).filter_by(AnalysisID=aid).all()
        return isos

    def get_irradiation_position(self, irp):
        return self._get_one(IrradiationPositionTable, dict(IrradPosition=irp))
#    def get_irradiation_position(self, args, sess=None):
#        '''
#        '''
#
#        if sess is None:
#            sess = self.session_factory()
#        try:
#            if isinstance(args, tuple):
#                q = sess.query(IrradiationPositionTable)
#                s = q.filter_by(IrradiationLevel=args[0],
#                               HoleNumber=int(args[1])).one()
#            else:
#                IrradiationPosID = args
##                print 'asdgte', args
#                q = sess.query(IrradiationPositionTable)
#                s = q.filter_by(IrradPosition=IrradiationPosID).one()
##                print s
#        except Exception, e:
#            print e
#            s = None
#
#        return s, sess

    def get_peaktimeblob(self, isoid, sess=None):
        '''
        '''
        return self._get_one(PeakTimeTable, dict(IsotopeID=isoid))
#        if sess is None:
#            sess = self.session_factory()
#        try:
#            q = sess.query(PeakTimeTable)
#            ptb = q.filter_by(IsotopeID=IsotopeID).one()
#        except:
#            ptb = None
#        return ptb, sess

    def _get_record(self, record, func):
        '''
        '''
        if record is not None:
            if isinstance(record, (long, int)):
                record = getattr(self, func)(record)

        return record

    def _get(self, table, query_dict, func='one'):
        sess = self.get_session()
        q = sess.query(table)
#        print q
#        print query_dict
#        f=
        f = q.filter_by(**query_dict)
#        f = q.filter_by(RID='22027-03C')
        return getattr(f, func)()

    def _get_one(self, table, query_dict):
        sess = self.get_session()

        q = sess.query(table)
#        print q
#        print query_dict
#        f=
#        q.filter(like('fff'))
        f = q.filter_by(**query_dict)
#        f = q.filter_by(RID='22027-03C')
#        print f
        try:
            return f.one()
        except Exception, e:
#            pass
            print 'get_one', e

    def _get_all(self, query_args):
        sess = self.get_session()
        p = sess.query(*query_args).all()
        return p
#    def debug_delete_table(self, table, sess=None):
#        def _delete_table(t):
#            rows = sess.query(t).all()
#            for r in rows:
#                sess.delete(r)
#
#        if sess is None:
#            sess = self.session_factory()
#
#        if isinstance(table, list):
#            for ti in table:
#                _delete_table(ti)
#        else:
#            _delete_table(table)

#    def get_data_reduction_session_dates(self, data_reduction_id_list, sess = None):
#        if sess is None:
#            sess = Session()
#        p = sess.query(DataReductionSessionTable.SessionDate).filter(
#                                DataReductionSessionTable.DataReductionSessionID.in_(data_reduction_id_list)).order_by(DataReductionSessionTable.DataReductionSessionID).all()
#        return p, sess
#    def get_discrimination(self, detector_ids, sess = None):
#        if sess is None:
#            sess = Session()
#        p = sess.query(DetectorTable.DetectorID, DetectorTable.Disc).filter(DetectorTable.DetectorID.in_(detector_ids)).all()
#        return p, sess
#    def get_isotopes(self, iso_ids, sess = None):
#        if sess is None:
#            sess = Session()
#        p = sess.query(IsotopeResultsTable.IsotopeID,
#                     IsotopeResultsTable.Intercept,
#                     IsotopeResultsTable.Bkgd).filter(IsotopeResultsTable.IsotopeID.in_(iso_ids)).\
#        order_by(IsotopeResultsTable.DataReductionSessionID).\
#                     order_by(IsotopeResultsTable.IsotopeID).all()
#        return p, sess
#    def get_isotope_ids(self, aids, sess = None):
#        if sess is None:
#            sess = Session()
#
#        p = sess.query(IsotopeTable.IsotopeID,
#                    IsotopeTable.Label,
#                    IsotopeTable.DetectorID
#                     ).filter(IsotopeTable.AnalysisID.in_(aids)).all()
#        return p, sess
#    def get_analysis_by_ln(self, ln, sess = None):
#        '''
#        like syntax
#        % allows you to match any string of any length (including zero length)
#
#        _ allows you to match on a single character
#        '''
#        if sess is None:
#            sess = Session()
#
#        p = sess.query(AnalysesTable.AnalysisID,
#                     AnalysesTable.RID).filter(AnalysesTable.RID.like(ln)).all()
#        return p, sess
#    def get_analysis_by_rid(self, rid, sess = None):
#        if sess is None:
#            sess = Session()
#        p = sess.query(AnalysesTable.AnalysisID).filter_by(RID = rid).first()
#        return p, sess
#    def get_araranalysis_rids(self, run_list):
#        sess = Session()
#        p = sess.query(AnalysesTable.AnalysisID,
#                     AnalysesTable.RID
#                     ).filter(AnalysesTable.RID.in_(run_list)).all()
#        return p, sess
#    def get_araranalyses(self, aid_list, sess = None):
#        if sess is None:
#            sess = Session()
#        p = sess.query(ArArAnalysisTable.AnalysisID,
#                     ArArAnalysisTable.DataReductionSessionID,
#                     ArArAnalysisTable.Tot40,
#                     ArArAnalysisTable.Tot39,
#                     ArArAnalysisTable.Tot38,
#                     ArArAnalysisTable.Tot37,
#                     ArArAnalysisTable.Tot36,
#                     ArArAnalysisTable.Tot40Er,
#                     ArArAnalysisTable.Tot39Er,
#                     ArArAnalysisTable.Tot38Er,
#                     ArArAnalysisTable.Tot37Er,
#                     ArArAnalysisTable.Tot36Er,
#                     ArArAnalysisTable.JVal,
#                     ArArAnalysisTable.JEr,
#
#                     ).filter(ArArAnalysisTable.AnalysisID.in_(aid_list)).order_by(ArArAnalysisTable.DataReductionSessionID).\
#                     order_by(ArArAnalysisTable.AnalysisID).all()
#        return p, sess
#    def get_araranalysis(self,a_id,sess=None):
#        if sess is None:
#            sess=Session()
#        p=sess.query(ArArAnalysisTable.Tot40,
#                     ArArAnalysisTable.Tot39,
#                     ArArAnalysisTable.Tot38,
#                     ArArAnalysisTable.Tot37,
#                     ArArAnalysisTable.Tot36,
#                     ArArAnalysisTable.Tot40Er,
#                     ArArAnalysisTable.Tot39Er,
#                     ArArAnalysisTable.Tot38Er,
#                     ArArAnalysisTable.Tot37Er,
#                     ArArAnalysisTable.Tot36Er,
#                     ArArAnalysisTable.DataReductionSessionID,
#                     ).filter_by(AnalysisID=a_id).all()
#        return p,sess


#    def _add_tableitem(self, table):
#        sess = self.get_session()
#        sess.add(table)
#        return table
#
#    def add_baseline(self, args):
#        return self._add_tableitem(BaselinesTable(**args))
##        sess = self.get_session()
##        b = BaselinesTable(**args)
##        sess.add(b)
##
##        return b
#
#    def add_project(self, args):
#        '''
#        '''
#        p = self.get_project(args['Project'])
#        if p is None:
#            return self._add_tableitem(ProjectTable(**args))
##        if sess is None:
##            sess = self.session_factory()
#
##        p, sess = self.get_project(args['Project'], sess=sess)
##        if p is None:
##        p = ProjectTable(**args)
##        sess.add(p)
##        return p
#
#    def add_sample(self, args, project=None):
#        '''
#        '''
#        s = self.get_sample(args['Sample'])
#        if s is None:
#            p = self.get_project(project)
##            self._add_tableitem(SampleTable(**args))
#            if p is not None:
#                s = SampleTable(**args)
#                p.samples.append(s)
#
#        return s
##        if sess is None:
##            sess = self.session_factory()
##        #check to see if sample already exists
##        s, sess = self.get_sample(args['Sample'], sess=sess)
##        if s is None:
##            p, sess = self.get_project(args['Project'], sess=sess)
##
##            s = SampleTable(**args)
##            p.samples.append(s)
##            sess.add(s)
##        return s, sess
#
#    def add_material(self, args):
#        '''
#
#        '''
##        if sess is None:
##            sess = self.session_factory()
##        m = MaterialTable(**args)
##        sess.add(m)
##        return m, sess
#        return self._add_tableitem(MaterialTable(**args))
#
##    def add_irradiation_position(self, args):
##        '''
##        '''
##       
##
##        ip, sess = self.get_irradiation_position((args['IrradiationLevel'],
##                                                 args['HoleNumber']),
##                                                 sess=sess)
##        if ip is None:
##            material, sess = self.get_material(args['Material'], sess=sess)
##            #if the material doesnt exist add it
##            if material is None:
##                material, sess = self.add_material(dict(Material=args['Material']),
##                                                   sess=sess)
##            sample, sess = self.get_sample(args['Sample'], sess=sess)
##            args.pop('Sample')
##
##            ip = IrradiationPositionTable(**args)
##            sample.irradpositions.append(ip)
##            material.irradpositions.append(ip)
##
##        return ip, sess
#
##    def add_arar_analysis(self, args, dbanalysis=None):
##        '''
##
##        '''
##        if sess is None:
##            sess = self.session_factory()
##        if dbanalysis is None:
##            if 'RID' in args:
##                analysis, sess = self.get_analysis(args['RID'], sess=sess)
##            else:
##                analysis = None
##        else:
##            analysis = dbanalysis
##
##        if analysis is not None:
##            araranalysis, sess = self.get_araranalysis(analysis.AnalysisID,
##                                                       sess=sess)
##            if araranalysis is None:
###                args.pop('RID')
##                a = ArArAnalysisTable(**args)
##                analysis.araranalyses.append(a)
##        return sess
#
#    def add_analysis(self, args, dbirradiationpos=None, dbsample=None):
#        '''
#        '''
#
#        analysis = self.get_analysis(args['RID'])
#        new = False
#        if analysis is None:
#            analysis = AnalysesTable(**args)
#            irradpos = self._get_record(dbirradiationpos,
#                            'get_irradiation_position')
#
#            if irradpos is not None:
#                new = True
#                irradpos.analyses.append(analysis)
#                sample = self._get_record(dbsample, 'get_sample')
#                if sample is not None:
#                    sample.analyses.append(analysis)
#
#        return analysis, new
#
##    def add_detector(self, detector_id, kw, sess=None):
##        '''
##        '''
###        if sess is None:
###            sess = self.session_factory()
##
###        print det_args, sess, detector_id
##        if detector_id is not None:
###            #get the detector row
##            det, sess = self.get_detector(detector_id, sess=sess)
##            #print det
##            for a in kw:
##                setattr(det, a, kw[a])
##        else:
##            det = DetectorTable(**kw)
##            sess.add(det)
##
##        return det, sess
#    def add_detector(self, args):
#        return self._add_tableitem(DetectorTable(**args))
#
#    def add_analysis_changeable(self, args, dbanalysis=None):
#        anal = self._get_record(dbanalysis, 'get_analysis')
#        if anal:
#            c = AnalysesChangeableItemsTable(**args)
#            anal.changeable = c
#            return c
#
#    def add_isotope_result(self, args, dbisotope=None):
##        if sess is None:
##            sess = self.session_factory()
#
#        iso = self._get_record(dbisotope, 'get_isotope')
#        if iso is not None:
#            iso_result = IsotopeResultsTable(**args)
#            iso.results.append(iso_result)
#            return iso_result
#
#    def add_isotope(self, args, dbanalysis=None, dbdetector=None, dbbaseline=None):
#        '''
#
#        '''
##        if sess is None:
##            sess = self.session_factory()
#
#        analysis = self._get_record(dbanalysis, 'get_analysis')
#
#        if analysis is not None:
#            detector = self._get_record(dbdetector, 'get_detector')
#            if detector is not None:
#                iso = IsotopeTable(**args)
#
#                analysis.isotopes.append(iso)
#                detector.isotopes.append(iso)
#
#                return iso
#
#    def add_peaktimeblob(self, blob, dbisotope=None):
#        iso = self._get_record(dbisotope, 'get_isotope')
#        if iso is not None:
#            pk = PeakTimeTable(PeakTimeBlob=blob)
#            iso.peak_time_series.append(pk)
#            return pk
#
##    def add_peaktimeblob(self, iso_id, blob, dbisotope=None, sess=None):
##        '''
##        '''
###        if sess is None:
###            sess = self.session_factory()
##        
##        isotope = dbisotope
##        if dbisotope is None:
##            isotope, sess = self.get_isotope(iso_id, sess=sess)
##
##        if isotope is not None:
##            pk = PeakTimeTable(PeakTimeBlob=blob)
##            isotope.peak_time_series.append(pk)
##
##        return sess
