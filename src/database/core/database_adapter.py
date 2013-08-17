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
from traits.api import Password, Bool, Str, on_trait_change, Any, Property, cached_property
#=============standard library imports ========================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, StatementError
import os
#=============local library imports  ==========================

from src.loggable import Loggable
from src.database.core.base_orm import MigrateVersionTable
from src.deprecate import deprecated
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import weakref
ATTR_KEYS = ['kind', 'username', 'host', 'name', 'password']


# def create_url(kind, user, hostname, db, password=None):

#    if kind == 'mysql':
#        if password is not None:
#            url = 'mysql://{}:{}@{}/{}?connect_timeout=3'.format(user, password, hostname, db)
#        else:
#            url = 'mysql://{}@{}/{}?connect_timeout=3'.format(user, hostname, db)
#    else:
#        url = 'sqlite:///{}'.format(db)
#
#    return url


class DatabaseAdapter(Loggable):
    '''
    '''
    sess = None

    connected = Bool(False)
    kind = Str  # ('mysql')
    username = Str  # ('root')
    host = Str  # ('localhost')
#    name = Str#('massspecdata_local')
    password = Password  # ('Argon')

    selector_klass = Any

    session_factory = None

    application = Any

    test_func = 'get_migrate_version'

    selector = Any

    # name used when writing to database
    save_username = Str
    connection_parameters_changed = Bool

    url = Property(depends_on='connection_parameters_changed')

    @property
    def enabled(self):
        return self.kind in ['mysql', 'sqlite']

    @on_trait_change('username,host,password,name')
    def reset_connection(self, obj, name, old, new):
        self.connection_parameters_changed = True

    def isConnected(self):
        return self.connected

    def reset(self):
        if self.sess:
            self.info('clearing current session. uncommitted changes will be deleted')

            self.sess.expunge_all()
            self.sess.close()

            self.sess = None

#             import gc
#             gc.collect()


    def connect(self, test=True, force=False, warn=True):
        '''
        '''
        if force:
            self.debug('forcing database connection')
        if self.connection_parameters_changed:
            force = True

#        print not self.isConnected() or force, self.connection_parameters_changed
        if not self.isConnected() or force:
            self.connected = True if self.kind == 'sqlite' else False
            if self.kind == 'sqlite':
                test = False

            if self.enabled:
                url = self.url
                if url is not None:
                    self.info('connecting to database {}'.format(url))
                    engine = create_engine(url, echo=False)
                    self.session_factory = sessionmaker(bind=engine,
                                                        autoflush=False)
                    if test:
                        self.connected = self._test_db_connection()
                    else:
                        self.connected = True

                    if self.connected:
                        self.info('connected to db')
                        self.initialize_database()
                    elif warn:
                        self.warning_dialog('Not Connected to Database {}.\nAccess Denied for user= {} \
host= {}\nurl= {}'.format(self.name, self.username, self.host, self.url))

        self.connection_parameters_changed = False
        return self.connected

    def new_session(self):
        sess = self.session_factory()
#         sess = scoped_session(self.session_factory)
        return sess

    def initialize_database(self):
        pass

    def get_query(self, table):
        sess = self.get_session()
        if sess:
            q = sess.query(table)
            return q

    def get_session(self):
        '''
        '''
        if self.sess is None:
            if self.session_factory is not None:
                self.sess = self.new_session()

        return self.sess

    def expire(self):
        if self.sess is not None:
            self.sess.expire_all()

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

    def get_migrate_version(self):
        sess = self.get_session()
        q = sess.query(MigrateVersionTable)
        mv = q.one()
        self.close()
        return mv

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

    @cached_property
    def _get_url(self):
        kind = self.kind
        password = self.password
        user = self.username
        host = self.host
        name = self.name
        if kind == 'mysql':
            # add support for different mysql drivers
            driver = self._import_mysql_driver()
            if driver is None:
                return

            if password is not None:
                url = 'mysql+{}://{}:{}@{}/{}?connect_timeout=3'.format(driver, user, password, host, name)
            else:
                url = 'mysql+{}://{}@{}/{}?connect_timeout=3'.format(driver, user, host, name)
        else:
            url = 'sqlite:///{}'.format(name)

        return url

    def _import_mysql_driver(self):
        try:
            '''
                pymysql
                https://github.com/petehunt/PyMySQL/
            '''
            import pymysql
            driver = 'pymysql'
        except ImportError:
            try:
                import _mysql
                driver = 'mysqldb'
            except ImportError:
                self.warning_dialog('A mysql driver was not found. Install PyMySQL or MySQL-python')
                return

        self.info('using {}'.format(driver))
        return driver

    def _test_db_connection(self):
        try:
            connected = False
            if self.test_func is not None:
                self.sess = None
                self.get_session()
#                sess = self.session_factory()
                self.info('testing database connection')
                getattr(self, self.test_func)()
                connected = True

        except Exception, e:
            print e

            self.warning('connection failed to {}'.format(self.url))
            connected = False

        finally:
            if self.sess is not None:
                self.info('closing test session')
                self.sess.close()

        return connected

    @deprecated
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

    def _get_tables(self):
        pass

    def _add_item(self, obj):
        sess = self.get_session()
        if sess is not None:
            sess.add(obj)

    def _add_unique(self, item, attr, name):
        # test if already exists
        nitem = getattr(self, 'get_{}'.format(attr))(name)
        if nitem is None:  # or isinstance(nitem, (str, unicode)):
            self.info('adding {}= {}'.format(attr, name))
            self._add_item(item)
            nitem = item
            self.flush()
            self.debug('add unique flush')
#            self.info('{}= {} already exists'.format(attr, name))
        return nitem


    def _get_path_keywords(self, path, args):
        n = os.path.basename(path)
        r = os.path.dirname(path)
        args['root'] = r
        args['filename'] = n
        return args

    def _retrieve_items(self, table,
                        joins=None,
                        filters=None,
                        limit=None, order=None):
        sess = self.get_session()
        if sess is not None:
            q = sess.query(table)

            if joins:
                try:
                    for ji in joins:
                        if ji != table:
                            q = q.join(ji)
                except InvalidRequestError:
                    pass

            if filters is not None:
                for fi in filters:
                    q = q.filter(fi)

            if order is not None:
                q = q.order_by(order)

            if limit is not None:
                q = q.limit(limit)
            return q.all()

    def _retrieve_first(self, table, value, key='name', order_by=None):
        if not isinstance(value, (str, int, unicode, long, float)):
            return value
        sess = self.get_session()
        if sess is None:
            return

        q = sess.query(table)
        q = q.filter(getattr(table, key) == value)
        try:
            if order_by is not None:
                q = q.order_by(order_by)
            return q.first()
        except SQLAlchemyError, e:
            print e
            return

    def _retrieve_item(self, table, value, key='name', last=None):
        sess = self.get_session()
        if sess is None:
            return
        if not isinstance(value, (str, int, unicode, long, float, list, tuple)):
            return value

        if not isinstance(value, (list, tuple)):
            value = (value,)
        if not isinstance(key, (list, tuple)):
            key = (key,)

        def __retrieve():
            q = sess.query(table)
            for k, v in zip(key, value):
                q = q.filter(getattr(table, k) == v)

            if last:
                q = q.order_by(last)

            try:
                return q.one()

            except StatementError:
                import traceback
                self.debug(traceback.format_exc())
                sess.rollback()
#                 return __retrieve()

            except MultipleResultsFound:
                self.debug('multiples row found for {} {} {}. Trying to get last row'.format(table.__tablename__, key, value))
                try:
                    if hasattr(table, 'id'):
                        q = q.order_by(table.id.desc())
                    return q.limit(1).all()[-1]

                except (SQLAlchemyError, IndexError, AttributeError), e:
                    self.debug('no rows for {} {} {}'.format(table.__tablename__, key, value))

            except NoResultFound:
                self.debug('no row found for {} {} {}'.format(table.__tablename__, key, value))

        # no longer true: __retrieve is recursively called if a StatementError is raised
        return __retrieve()

    @deprecated
    def _get_items(self, table, gtables,
                   join_table=None, filter_str=None,
                   limit=None,
                   order=None,
                   key=None
                   ):

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

        # reorder based on id
        if order:
            q = q.from_self()
            q = q.order_by(table.id)

        res = q.all()
        if key:
            return [getattr(ri, key) for ri in res]
        return res



    def _selector_default(self):
        return self._selector_factory()

#    def open_selector(self):
#        s = self._selector_factory()
#        if s:
#            s.edit_traits()
#            self.

    def selector_factory(self, **kw):
        sel = self._selector_factory(**kw)
        self.selector = weakref.ref(sel)()
        return self.selector

#    def new_selector(self, **kw):
#        if self.selector_klass:
#            s = self.selector_klass(_db=self, **kw)
#            return s

    def _selector_factory(self, **kw):
        if self.selector_klass:
            s = self.selector_klass(db=self, **kw)
#            s.load_recent()
            return s

#    def _get(self, table, query_dict, func='one'):
#        sess = self.get_session()
#        q = sess.query(table)
#        f = q.filter_by(**query_dict)
#        return getattr(f, func)()

#    def _get_one(self, table, query_dict):
#        sess = self.get_session()
#        q = sess.query(table)
#        f = q.filter_by(**query_dict)
#        try:
#            return f.one()
#        except Exception, e:
#            print 'get_one', e
#
#    def _get_all(self, query_args):
#        sess = self.get_session()
#        p = sess.query(*query_args).all()
#        return p

class PathDatabaseAdapter(DatabaseAdapter):
    path_table = None
    def add_path(self, rec, path, **kw):
        if self.path_table is None:
            raise NotImplementedError
        kw = self._get_path_keywords(path, kw)
        p = self.path_table(**kw)
        rec.path = p
        return p

#============= EOF =============================================

