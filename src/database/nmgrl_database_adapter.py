
#=============enthought library imports=======================

#=============standard library imports ========================

# make a global session
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

#=============local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
from nmgrl_orm import  DetectorTable, \
     IsotopeTable, AnalysesTable, ArArAnalysisTable, \
    IrradiationPositionTable, MaterialTable, SampleTable, ProjectTable, \
    PeakTimeTable

class NMGRLDatabaseAdapter(DatabaseAdapter):
    def add_project(self, args, sess = None):
        '''
      
        '''
        if sess is None:
            sess = self.session_factory()

        p, sess = self.get_project(args['Project'], sess = sess)
        if p is None:
            p = ProjectTable(**args)
        sess.add(p)
        return sess

    def add_sample(self, args, sess = None):
        '''

        '''
        if sess is None:
            sess = self.session_factory()
        #check to see if sample already exists
        s, sess = self.get_sample(args['Sample'], sess = sess)
        if s is None:
            p, sess = self.get_project(args['Project'], sess = sess)

            s = SampleTable(**args)
            p.samples.append(s)
            sess.add(s)
        return s, sess

    def add_material(self, args, sess = None):
        '''

        '''
        if sess is None:
            sess = self.session_factory()
        m = MaterialTable(**args)
        sess.add(m)
        return m, sess

    def add_irradiation_position(self, args, sess = None):
        '''
        '''
        if sess is None:
            sess = self.session_factory()

        ip, sess = self.get_irradiation_position((args['IrradiationLevel'],
                                                 args['HoleNumber']),
                                                 sess = sess)
        print ip
        if ip is None:
            material, sess = self.get_material(args['Material'], sess = sess)
            #if the material doesnt exist add it
            if material is None:
                material, sess = self.add_material(dict(Material = args['Material']), sess = sess)
            sample, sess = self.get_sample(args['Sample'], sess = sess)
            args.pop('Sample')

            ip = IrradiationPositionTable(**args)
            sample.irradpositions.append(ip)
            material.irradpositions.append(ip)

        return ip, sess

    def add_arar_analysis(self, args, sess = None, dbanalysis = None):
        '''

        '''
        if sess is None:
            sess = self.session_factory()
        if dbanalysis is None:
            if 'RID' in args:
                analysis, sess = self.get_analysis(args['RID'], sess = sess)
            else:
                analysis = None
        else:
            analysis = dbanalysis

        if analysis is not None:
            araranalysis, sess = self.get_araranalysis(analysis.AnalysisID, sess = sess)
            if araranalysis is None:
#                args.pop('RID')
                a = ArArAnalysisTable(**args)
                analysis.araranalyses.append(a)
        return sess

    def add_analysis(self, kw, sess = None, dbirradiationpos = None,
                     dbsample = None):
        '''
            
        '''
        if sess is None:
            sess = self.session_factory()

        analysis, sess = self.get_analysis(kw['RID'], sess = sess)
        new = False
        if analysis is None:
            irradpos = self._get_record(dbirradiationpos, 'get_irradiation_position', sess)
            if irradpos is not None:
                sample = self._get_record(dbsample, 'get_sample', sess)
                if sample is not None:
                        analysis = AnalysesTable(**kw)
                        irradpos.analyses.append(analysis)
                        sample.analyses.append(analysis)
                        new = True

        return analysis, new, sess

    def add_detector(self, detector_id, kw, sess = None):
        '''
            
        '''
        if sess is None:
            sess = self.session_factory()

#        print det_args, sess, detector_id
        if detector_id is not None:
#            #get the detector row
            det, sess = self.get_detector(detector_id, sess = sess)
            #print det
            for a in kw:
                setattr(det, a, kw[a])
        else:
            det = DetectorTable(**kw)
            sess.add(det)

        return det, sess
    def add_isotope(self, args, sess = None, dbanalysis = None,
                    dbdetector = None, dbbaseline = None):
        '''
            
        '''
        if sess is None:
            sess = self.session_factory()

        iso = None
        analysis = self._get_record(dbanalysis, 'get_analysis', sess)

        if analysis is not None:
            detector = self._get_record(dbdetector, 'get_detector', sess)
            if detector is not None:
                iso = IsotopeTable(**args)

                analysis.isotopes.append(iso)
                detector.isotopes.append(iso)

        return iso, sess

    def add_peaktimeblob(self, IsotopeID, blob, dbisotope = None, sess = None):
        '''
            
        '''
        if sess is None:
            sess = self.session_factory()

        isotope = dbisotope
        if dbisotope is None:
            isotope, sess = self.get_isotope(IsotopeID, sess = sess)

        if isotope is not None:
            pk = PeakTimeTable(PeakTimeBlob = blob)
            isotope.peak_time_series.append(pk)

        return sess

    def get_rids(self, sess = None):
        '''
          
        '''
        if sess is None:
            sess = self.session_factory()

        p = sess.query(AnalysesTable.AnalysisID, AnalysesTable.RID).limit(1000)
        return p, sess
    def get_project(self, project, sess = None):
        '''
           
        '''
        if sess is None:
            sess = self.session_factory()
        try:
            p = sess.query(ProjectTable).filter_by(Project = project).one()
        except:
            p = None
        return p, sess

    def get_araranalysis(self, aid, sess = None):
        '''
        
        '''
        if sess is None:
            sess = self.session_factory()
        try:
            a = sess.query(ArArAnalysisTable).filter_by(AnalysisID = aid).one()
        except:
            a = None
        return a, sess

    def get_analysis(self, rid, sess = None):
        '''
        
        '''
        if sess is None:
            sess = self.session_factory()
        try:
            a = sess.query(AnalysesTable).filter_by(RID = rid).one()
        except:
            a = None
        return a, sess
    def get_analyses(self, sess = None):
        '''
            
        '''
        if sess is None:
            sess = self.session_factory()
        p = sess.query(AnalysesTable.RID).all()

        return p, sess

    def get_detector(self, id, sess = None):
        '''
            @type id: C{str}
            @param id:

            @type sess: C{str}
            @param sess:
        '''
        if sess is None:
            sess = self.session_factory()

        d = sess.query(DetectorTable).filter_by(DetectorID = id).one()
        return d, sess

    def get_material(self, material, sess = None):
        '''
    
        '''
        if sess is None:
            sess = self.session_factory()
        try:
            m = sess.query(MaterialTable).filter_by(Material = material).one()
        except:
            m = None
        return m, sess
    def get_sample(self, sample, sess = None):
        '''

        '''
        if sess is None:
            sess = self.session_factory()
        try:
            s = sess.query(SampleTable).filter_by(Sample = sample).one()
        except:
            s = None
        return s, sess
    def get_isotopes(self, AnalysisID, sess = None):
        '''
  
        '''
        if sess is None:
            sess = self.session_factory()

        isos = sess.query(IsotopeTable).filter_by(AnalysisID = AnalysisID).all()
        return isos, sess
    def get_irradiation_position(self, args, sess = None):
        '''
     
        '''

        if sess is None:
            sess = self.session_factory()
        try:
            if isinstance(args, tuple):
                s = sess.query(IrradiationPositionTable).filter_by(IrradiationLevel = args[0],
                                                                   HoleNumber = int(args[1]),
                                                                   ).one()
            else:
                IrradiationPosID = args
                s = sess.query(IrradiationPositionTable).filter_by(IrradPos = IrradiationPosID).one()
        except:
            s = None

        return s, sess

    def get_peaktimeblob(self, IsotopeID, sess = None):
        '''
     
        '''
        if sess is None:
            sess = self.session_factory()
        try:
            ptb = sess.query(PeakTimeTable).filter_by(IsotopeID = IsotopeID).one()
        except:
            ptb = None
        return ptb, sess

    def _get_record(self, record, func, sess):
        '''
       
        '''
        if record is not None:
            if isinstance(record, int):
                record, sess = getattr(self, func)(record, sess = sess)

        return record
    def debug_delete_table(self, table, sess = None):
        def _delete_table(t):
            rows = sess.query(t).all()
            for r in rows:
                sess.delete(r)

        if sess is None:
            sess = self.session_factory()



        if isinstance(table, list):
            for ti in table:
                _delete_table(ti)
        else:
            _delete_table(table)

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