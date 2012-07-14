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
import sqlalchemy

#============= enthought library imports =======================

#============= standard library imports ========================
#============= local library imports  ==========================

def add(func):
    def _add(obj, *args, **kw):

        kwargs = kw.copy()
        for key in ['unique', 'commit']:
            try:
                kwargs.pop(key)
            except KeyError:
                pass

        sess = obj.get_session()
        dbr = None
        if sess:
            dbr = func(obj, *args, **kwargs)
            if dbr:
                sess.add(dbr)

                try:
                    if kw['commit']:
                        sess.commit()
                except KeyError:
                    pass

        return dbr

    return _add


def get_one(func):
    def __get_one(obj, name, *args, **kw):
        return _get_one(func, obj, name, *args, **kw)
    return __get_one

def _get_one(func, obj, name, *args, **kw):
    params = func(obj, name, *args, **kw)
    if isinstance(params, tuple):
        table, attr = params
    else:
        table = params
        attr = 'name'

    sess = obj.get_session()
    q = sess.query(table)
    q = q.filter(getattr(table, attr) == name)

    try:
        return q.one()
    except sqlalchemy.exc.SQLAlchemyError, e:
        print e

def delete_one(func):
    def _delete_one(obj, name, *args, **kw):
        sess = obj.get_session()
        dbr = _get_one(func, obj, name, *args, **kw)
        sess.delete(dbr)
        sess.commit()


    return _delete_one

def sql_retrieve(func):
    try:
        return func()
    except sqlalchemy.exc.SQLAlchemyError, e:
        print e
#============= EOF =============================================
