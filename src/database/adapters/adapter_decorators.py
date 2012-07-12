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
#============= standard library imports ========================
import sqlalchemy
#============= local library imports  ==========================

def commit(func):
    def _func(obj, params, * args, **kw):
        return _commit(lambda a, b, c:True, obj, func, params, args, kw)
    return _func

def _commit(hook, obj, func, params, args, kw):
#    kwargs = kw.copy()
#    try:
#        kwargs.pop('commit')
#        kwargs.pop('unique')
#    except KeyError:
#        pass

    dbr = func(obj, *args, **params)

    sess = obj.get_session()
    if sess:
        if not hook(sess, dbr, kw):
            return

        try:
            if kw['commit']:
                sess.commit()
        except KeyError:
            pass

    return dbr


def add(func):
    def _func(obj, params, *args, **kw):
        def add_hook(sess, dbr, kwargs):
            add = True
            if (kw['unique'] if kw.has_key('unique') else True):
                cls = dbr.__class__
                q = sess.query(cls)

                try:
                    name = func.__name__.replace('add_', '')
                    print name
                    f = getattr(obj, '_{}_unique_filter_hook'.format(name))
#                    q = f(q, cls, dbr)
                except AttributeError:
                    f = None

                q = obj.filter(q, f, cls, dbr, kwargs)

                add = not bool(q.count())
                print q.count(), add, 'count'

            if add:
                print 'asess add'
#                sess.add(dbr)
                return True
            else:
                return False

        return _commit(add_hook, obj, func, params, args, kw)

    return _func

def get_query(obj, name, func):
    sess = obj.get_session()

    tablename = func.__name__.replace('get_', '')
    table = obj.tables[tablename]
    return sess.query(table).filter(table.name == name)

def get_one(func):
    def _get(obj, name, *args, **kw):
        q = get_query(obj, name, func)
        try:
            return q.one()
        except sqlalchemy.exc.SQLAlchemyError:
            pass

    return _get

def get_all(func):
    def _get(obj, name, *args, **kw):
        q = get_query(obj, name, func)
        return q.all()

    return _get
#============= EOF =============================================
