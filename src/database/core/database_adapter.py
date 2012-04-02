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
from traits.api import Password, Bool, Str, on_trait_change, Any
from traitsui.api import View
#=============standard library imports ========================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#=============local library imports  ==========================

from src.loggable import Loggable
ATTR_KEYS = ['kind', 'user', 'host', 'dbname', 'password']
def create_url(kind, user, hostname, db, password=None):
    '''

    '''
    if password is not None:
        url = '%s://%s:%s@%s/%s' % (kind, user, password, hostname, db)
    else:
        url = '%s://%s@%s/%s' % (kind, user, hostname, db)
    return url


class DatabaseAdapter(Loggable):
    '''
    '''
    sess = None

    connected = Bool(False)
    kind = Str('mysql')
    user = Str('root')
    host = Str('localhost')
    dbname = Str('pychrondb')
    password = Password('Argon')
    use_db = Bool

#    window = Any

#    @on_trait_change('[user,host,password,dbname, use_db]')
#    def connect_attributes_changed(self, obj, name, old, new):
#        if name == 'use_db':
#            if new:
#                self.connect()
#            else:
#                self.connected = False
#        else:
#            self.connect()
#
#        #refresh the open database views
#        sess = None
#        if self.window:
#            for v in self.window.views:
#                if v.category == 'Database':
#                    sess = v.obj.load(sess=sess)
#
#        if sess is not None:
#            sess.close()

    def connect(self, test=True):
        '''
        '''
        args = []
        for a in ATTR_KEYS:
            args.append(getattr(self, a))

        self._new_engine(*tuple(args))
        self.info('connecting to database')

        self.session_factory = sessionmaker(bind=self.engine)
        if test:
            if self._test_db_connection():
                self.connected = True
            else:
                self.connected = False

    def _test_db_connection(self):
        self.connected = True
        sess = self.session_factory()
        self.info('testing database connection')
        try:
            connected = True
            if self.test_func is not None:
                getattr(self, self.test_func)
#                _users, sess = getattr(self, self.test_func)(sess=sess)

        except:
            self.warning('connection failed %s@%s/%s' % (self.user, self.host,
                                                        self.dbname))
            connected = False

        finally:
            if sess is not None:
                self.info('closing test session')
                sess.close()

        return connected

    def _new_engine(self, kind, user, host, db, password):
        '''

        '''

        url = create_url(kind, user, host, db, password=password)
        self.info('url = %s' % url)
        self.engine = create_engine(url)

    def _get_record(self, record, func, sess):
        '''
        '''
        if record is not None:
            result = None
            if isinstance(record, int) or isinstance(record, long):
                record = dict(id=record)

            if isinstance(record, dict):
                result, sess = getattr(self, func)(filter=record, sess=sess)
            else:
                result = record
            return result

    def get_session(self):
        '''
        '''
        if self.sess is None:
            self.sess = self.session_factory()

        return self.sess

    def delete(self, item):
        if self.sess is not None:
            self.sess.delete(item)

    def commit(self):
        if self.sess is not None:
            self.sess.commit()

    def flush(self):
        if self.sess is not None:
            self.sess.flush()

    def rollback(self):
        if self.sess is not None:
            self.sess.rollback()

    def close(self):
        if self.sess is not None:
            self.sess.close()

    def traits_view(self):
        v = View('user',
               'password',
               'host',
               'dbname'
               )
        return v
