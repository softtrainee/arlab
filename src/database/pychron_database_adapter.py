#'''
#Copyright 2011 Jake Ross
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#'''
##=============enthought library imports=======================
#
##=============standard library imports ========================
#
## make a global session
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.orm.exc import NoResultFound
#import struct
#
#Session = sessionmaker()
#
##=============local library imports  ==========================
#from src.database.core.database_adapter import DatabaseAdapter
#
#from pychron_orm import Detectors, Spectrometers, Analyses, Samples, Signals, \
#    Irradiations, Reactors, IrradiationTrays
#
#class PychronDatabaseAdapter(DatabaseAdapter):
#    def add_sample(self, irradiation=None, **kw):
#        row = Samples(**kw)
#        self.add_item(row, [(Irradiations, irradiation, 'samples')])
#        return row
#
#    def add_detector(self, spectrometer=None, ** kw):
#        if 'gain' in kw:
#            kw['gain'] = float(kw['gain'])
#
#        row = Detectors(**kw)
#        self.add_item(row, [(Spectrometers, spectrometer, 'detectors')])
#        return row
#
#    def add_analysis(self, sample=None, **kw):
#        row = Analyses(**kw)
#        self.add_item(row, [(Samples, sample, 'analyses')])
#        return row
#
#    def add_signal(self, analysis=None, detector=None, **kw):
#
#        #convert to blobs
#        if 'times' in kw:
#            kw['times'] = ''.join([struct.pack('>d', ti) for ti in kw['times']])
#            '''
#                unpack
#                width=8
#                vs=[]
#                for i in range(len(blob),width):
#                    v=struct.unpack('>d',blob[i:i+width])[0]
#                    vs.append(v)
#                or
#                
#                vs=[struct.unpack('>d',blob[i:i+width])[0] for i in range(0,len(blob),width)] 
#                    
#            '''
#        if 'intensities' in kw:
#            kw['intensities'] = ''.join([struct.pack('>d', ti) for ti in kw['intensities']])
#
#        row = Signals(**kw)
#        self.add_item(row, [(Analyses, analysis, 'signals'),
#                                   (Detectors, detector, 'signals')
#                                   ])
#        return row
#
#    def add_irradiation(self, **kw):
#        row = Irradiations(**kw)
#        self.add_item(row, None)
#        return row
#
#    def add_irradiation_tray(self, irradiation=None, **kw):
#        row = IrradiationTrays(**kw)
#        self.add_item(row, [(Irradiations, irradiation, 'trays')])
#        return row
#
#    def add_reactor(self, **kw):
#        row = Reactors(**kw)
#        self.add_item(row, None)
#        return row
#
#    def add_item(self, obj, parent_args):
#        sess = self.get_session()
#        if parent_args is None:
#            sess.add(obj)
#        else:
#            for parent_klass, parent, relation in parent_args:
#                if parent is not None:
#                    if isinstance(parent, (dict, str)):
#                        parent = self.get_item(parent_klass, filter_clause=parent)
#
#                    if parent:
#                        getattr(parent, relation).append(obj)
#
#        sess.commit()
#
#    def get_reactors(self):
#        return self.get_items(Reactors)
#
#    def get_irradiation(self, filter):
#        return self.get_item(Irradiations, filter_clause=filter)
#
#    def get_irradiations(self):
#        return self.get_items(Irradiations)
#
#    def get_samples(self):
#        return self.get_items(Samples)
#
#    def get_sample(self, filter):
#        return self.get_item(Samples, filter_clause=filter)
#
#    def get_spectrometer(self, filter):
#        return self.get_item(Spectrometers, filter_clause=filter)
#
#    def get_analysis(self, filter):
#        return self.get_item(Analyses, filter_clause=filter)
#
#    def get_signal(self, filter):
#        return self.get_item(Signals, filter_clause=filter)
#
#    def get_item(self, *args, **kw):
#        return self.get_items(func='one', *args, **kw)
#
#    def get_items(self, klass, filter_clause=None, func='all'):
#        sess = self.get_session()
#        query = sess.query(klass)
#        items = None
#        if filter_clause is not None:
#
#            if isinstance(filter_clause, str):
#                filter_clause = dict(name=filter_clause)
#
#            try:
#                q = query.filter_by(**filter_clause)
#                items = getattr(q, func)()
#            except NoResultFound, e:
#                self.warning(e)
#        else:
#            items = query.all()
#
#        return items
#
#    def get_session(self):
#        sess = self.sess
#        if sess is None:
#            self.sess = sess = self.session_factory()
#        return sess
##==================== EOF ===========================
##
##class PychronDatabaseAdapter(DatabaseAdapter):
##    test_func = 'get_users'
##    def add_analysis(self, args, dbsample = None, sess = None, dbexperiment = None):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type dbsample: C{str}
##            @param dbsample:
##
##            @type sess: C{str}
##            @param sess:
##        '''
##        return self._add_(Analyses, args, sess,
##                          relations = [(dbsample, 'get_samples', 'analyses'),
##                                       (dbexperiment, 'get_experiments', 'analyses')]
##                          )
##
##    def add_irradiation(self, args, **kw):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return  self._add_(Irradiations, args, **kw)
##    def add_user(self, args, sess = None, **kw):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._add_(Users, args, sess, **kw)
##
##    def add_project(self, args, sess = None, **kw):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._add_(Projects, args, sess, **kw)
##
##    def add_sample(self, args, sess = None, dbproject = None,
##                                            dbirradiation = None):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type dbproject: C{str}
##            @param dbproject:
##
##            @type : C{str}
##            @param :
##        '''
##        return self._add_(Samples, args, sess,
##                   relations = [(dbproject, 'get_projects', 'samples'),
##                                (dbirradiation, 'get_irradiations', 'samples')
##                                ])
##
##
##    def add_detector(self, args, sess = None,):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type : C{str}
##            @param :
##        '''
##        return self._add_(Detectors, args, sess)
##
##    def add_signal(self, args, sess = None, dbanalysis = None,
##                                         dbdetector = None
##                   ):
##        '''
##            @type args: C{str}
##            @param args:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type dbanalysis: C{str}
##            @param dbanalysis:
##
##            @type : C{str}
##            @param :
##        '''
##
##
##        return self._add_(Signals, args, sess,
##                          relations = [
##                                     (dbanalysis, 'get_analyses', 'signals'),
##                                     (dbdetector, 'get_detectors', 'signals'),
##                                     ])
##    def add_ararage(self, args, sess = None, dbanalysis = None):
##        return self._add_(ArArAges, args, sess, relations = (dbanalysis, 'get_analyses', 'ararages'))
##    def add_experiment(self, args, sess = None):
##        return self._add_(Experiments, args, sess)
##
##    def add_corrected_signal(self, args, sess = None, dbsignal = None):
##        return self._add_(CorrectedSignals, args, sess, relations = (dbsignal, 'get_signals', 'corrected_signal'))
##
##    def add_irradiation_production_ratios(self, args, sess = None, dbirradiation = None):
##        return self._add_(IrradiationProductionRatios, args, sess, relations = (dbirradiation, 'get_irradiations', 'production_ratios'))
##
##    def _get_rows(self, klass, id = None, filter = None, **kw):
##
##        self._make_filter_clause(id, kw)
##        self._make_filter_clause(filter, kw)
##        return self._get_(klass, **kw)
##
##    def get_analyses(self, id = None, filter = None, **kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._get_rows(Analyses, id = id, filter = filter, **kw)
###        self._make_filter_clause(id, kw)
###        self._make_filter_clause(filter, kw)
###        return self._get_(Analyses, **kw)
##
##    def get_detectors(self, id = None, filter = None, **kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
###        self._make_filter_clause(id, kw)
###        self._make_filter_clause(filter, kw)
###        return self._get_(Detectors, **kw)
##        return self._get_rows(Detectors, id = id, filter = filter, **kw)
##
##    def get_experiments(self, id = None, filter = None, **kw):
##        return self._get_rows(Experiments, id = id, filter = filter, **kw)
##
##    def get_irradiation_production_ratioss(self, id = None, filter = None, **kw):
##        return self._get_rows(IrradiationProductionRatios, id = id, filter = filter, **kw)
##
##
##    def get_irradiations(self, id = None, filter = None, **kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._get_rows(Irradiations, id = id, filter = filter, **kw)
###        self._make_filter_clause(id, kw)
###        self._make_filter_clause(filter, kw)
###        return self._get_(Irradiations, **kw)
##
##    def get_users(self, id = None, filter = None, **kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._get_rows(Users, id = id, filter = filter, **kw)
###        self._make_filter_clause(id, kw)
###        self._make_filter_clause(filter, kw)
###        return self._get_(Users, **kw)
##
##    def get_projects(self, id = None, filter = None, **kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type **kw: C{str}
##            @param **kw:
##        '''
##        return self._get_rows(Projects, id = id, filter = filter, **kw)
###        self._make_filter_clause(id, kw)
###        self._make_filter_clause(filter, kw)
###        return self._get_(Projects, **kw)
##
##    def get_samples(self, id = None, filter = None , ** kw):
##        '''
##            @type id: C{str}
##            @param id:
##
##            @type filter: C{str}
##            @param filter:
##
##            @type ** kw: C{str}
##            @param ** kw:
##        '''
##        return self._get_rows(Samples, id = id, filter = filter, **kw)
###        self._make_filter_clause(filter, kw)
###        self._make_filter_clause(id, kw)
###        return self._get_(Samples, **kw)
##
##    def _make_filter_clause(self, d, kw):
##        '''
##            @type d: C{str}
##            @param d:
##
##            @type kw: C{str}
##            @param kw:
##        '''
##        filter_clause = None
##        if isinstance(d, dict):
##            filter_clause = d
##        elif isinstance(d, tuple):
##            filter_clause = dict(*d)
##        elif isinstance(d, int):
##            filter_clause = dict(id = d)
##
##        if filter_clause is not None:
##            if kw.has_key('filter_clause'):
##                kw['filter_clause'] += filter_clause
##            else:
##                kw['filter_clause'] = filter_clause
##
##    def _add_(self, klass, args, sess, relations = None):
##        '''
##        '''
##        def _add_to_relation(r, obj):
##            dbr = self._get_record(*r[:2], sess = sess)
##            if dbr:
##                rel = getattr(dbr, r[2])
##                try:
##                    rel.append(obj)
##                except AttributeError:
##                    #this is one to one relationship
##                    setattr(dbr, r[2], obj)
##        if self.connected:
##            sess = self._get_session(sess)
##            k = klass(**args)
##            if relations is None:
##                sess.add(k)
##            elif isinstance(relations, list):
##                for r in relations:
##                    _add_to_relation(r, k)
##            else:
##                _add_to_relation(relations, k)
##            return k, sess
##        else:
##            return None, None
##
##    def _get_(self, klass, filter_clause = None, sess = None, id = None, func = 'one'):
##        '''
##            @type klass: C{str}
##            @param klass:
##
##            @type filter_clause: C{str}
##            @param filter_clause:
##
##            @type sess: C{str}
##            @param sess:
##
##            @type id: C{str}
##            @param id:
##
##            @type func: C{str}
##            @param func:
##        '''
##        if self.connected:
##            sess = self._get_session(sess)
##            try:
##                query = sess.query(klass)
##            except:
##                import sys
##                print sys.exc_info()
##
##            items = None
##            if filter_clause is not None:
##                #print filter_clause, klass, func
##                try:
##                    q = query.filter_by(**filter_clause)
##                    func = getattr(q, func)
##                    items = func()
##                except NoResultFound, e:
##                    self.warning(e)
##
##
##            elif id is None:
##                items = query.all()
##
##            return items, sess
##        else:
##            return None, None
##    def get_irradiation(self, **kw):
##        return self.get_irradiations(**kw)
##
##    def get_user(self, uid, **kw):
##        return self.get_users(uid = int(uid), **kw)
##
##    def get_project(self, **kw):
##        return self.get_projects(**kw)
##
##    def get_sample(self, **kw):
##        return self.get_samples(**kw)
