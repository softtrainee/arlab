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

#=============enthought library imports=======================
from traits.api import Password, Bool, Str, on_trait_change, Any
from traitsui.api import View
#=============standard library imports ========================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#=============local library imports  ==========================

from src.loggable import Loggable
from src.helpers.datetime_tools import get_datetime
import os
from sqlalchemy.sql.expression import asc, desc
ATTR_KEYS = ['kind', 'user', 'host', 'dbname', 'password']
def create_url(kind, user, hostname, db, password=None):
    '''

    '''
    if kind == 'mysql':
        if password is not None:
            url = 'mysql://{}:{}@{}/{}'.format(user, password, hostname, db)
        else:
            url = 'mysql://{}@{}/{}'.format(user, hostname, db)
    else:
        url = 'sqlite:///{}'.format(db)

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

    selector_klass = Any

    session_factory = None

    application = Any
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

        return self.connected

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
            if self.session_factory is not None:
                self.sess = self.session_factory()
            else:
                self.warning_dialog('Not connect to the database {}'.format(self.dbname))

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
            self.sess = None

    def traits_view(self):
        v = View('user',
               'password',
               'host',
               'dbname'
               )
        return v

    def _get_tables(self):
        pass

    def get_results(self, tablename, **kw):
        tables = self._get_tables()
        table = tables[tablename]
        sess = self.get_session()
        q = sess.query(table)
        if kw:

            for k, (cp, val) in kw.iteritems():

                d = getattr(table, k)
                func = getattr(d, cp)
                q = q.filter(func(val))

        return q.all()

    def _get_query(self, klass, join_table=None, filter_str=None, *args, **clause):
        sess = self.get_session()
        q = sess.query(klass)

        if join_table is not None:
            q = q.join(join_table)

        if filter_str:
            q = q.filter(filter_str)
        else:
            q = q.filter_by(**clause)
        return q

    def _add_item(self, obj, commit):
        sess = self.get_session()
        sess.add(obj)
        if commit:
            sess.commit()

    def _add_timestamped_item(self, klass, commit, **kw):
        d = get_datetime()

#        args = dict(rundate=str(d.date()),
#                    runtime=str(d.time()))
#        args = dict(rundate=d.date(),
#                    runtime=d.time())
        kw['rundate'] = d.date()
        kw['runtime'] = d.time()
        obj = klass(**kw)
        self._add_item(obj, commit)
        return obj

    def _get_path_keywords(self, path, args):
        n = os.path.basename(path)
        r = os.path.dirname(path)
        args['root'] = r
        args['filename'] = n
        return args

    def _get_items(self, table, gtables,
                   join_table=None, filter_str=None,
                   limit=None,
                   order=None):
        try:
            if isinstance(join_table, str):
                join_table = gtables[join_table]

            q = self._get_query(table, join_table=join_table,
                                 filter_str=filter_str)
            if order:
                for o in order \
                        if isinstance(order, list) else [order]:
                    q = q.order_by(o)

            if limit:
                q = q.limit(limit)

            #reorder based on id
            if order:
                q = q.from_self()
                q = q.order_by(table.id)

            res = q.all()
            return res

        except Exception, e:
            print e


    def open_selector(self):
        s = self._selector_factory()
        if s:
            s.edit_traits()

    def _selector_factory(self):
        if self.selector_klass:
            s = self.selector_klass(_db=self)
            s.load_recent()
            return s


class PathDatabaseAdapter(DatabaseAdapter):
    path_table = None
    def add_path(self, rec, path, commit=False, **kw):
        if self.path_table is None:
            raise NotImplementedError
        kw = self._get_path_keywords(path, kw)
        p = self.path_table(**kw)
        rec.path = p
        if commit:
            self.commit()
        return p

#============= EOF =============================================

