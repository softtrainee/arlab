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
from traits.api import HasTraits, String, Property, Str, List, Button, Any, \
    Bool
from traitsui.api import View, Item, EnumEditor, HGroup, Spring
from src.helpers.datetime_tools import get_date
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import and_
#============= standard library imports ========================
#============= local library imports  ==========================

def compile_query(query):
    from sqlalchemy.sql import compiler
    from MySQLdb.converters import conversions, escape

    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    enc = dialect.encoding
    params = []
    for k in comp.positiontup:
        v = comp.params[k]
        if isinstance(v, unicode):
            v = v.encode(enc)
        params.append(escape(v, conversions))

    comp = comp.string.encode(enc)
    comp = comp.replace('?', '%s')

    return (comp % tuple(params)).decode(enc)

class TableSelector(HasTraits):
    parameter = String
    parameters = Property

    def _get_parameters(self):
        params = [
                  'Analysis',
                'Material',
                'Sample',
                'Detector',
                'IrradiationPosition',
                ]
        self.parameter = params[0]
        return params

    def traits_view(self):
        v = View(Item('parameter',
                      show_label=False,
                       editor=EnumEditor(name='parameters')),
                 buttons=['OK', 'Cancel'],
                 kind='livemodal'
                 )
        return v

class Query(HasTraits):
    parameter = String
#    parameters = Property(depends_on='query_table')
    parameters = Property

    comparator = Str('=')
    comparisons = List(['=', '<', '>', '<=', '>=', 'not =',
                         'like',
                         'contains'
                         ])
    criterion = String('')
#    criterion = String('')
    criteria = Property(depends_on='parameter')
#    query_table = Any

    selector = Any
    add = Button('+')
    remove = Button('-')
    removable = Bool(True)
#    date_str = 'rundate'

    def assemble_filter(self, query, attr):
        comp = self.comparator
        if self.parameter == 'Run Date':
            query = self.date_query(query, attr)
        else:
            c = self.criterion
            if comp in ['like', 'contains']:
                if comp == 'like':
                    c += '%'
                elif comp == 'contains':
                    comp = 'like'
                    c = '%' + c + '%'
                query = query.filter(attr == c)
            else:
                comp = self._convert_comparator(comp)
                query = query.filter(getattr(attr, comp)(c))

        return query

    def date_query(self, query, attr):
        criterion = self.criterion
        comp = self.comparator
        c = criterion.replace('/', '-')
        if criterion == 'today':
            c = get_date()
        elif criterion == 'this month':
            d = datetime.today().date()
            today = get_date()
            if '=' in comp:
                d = d - timedelta(days=d.day)
                query = query.filter(and_(attr <= today,
                                   attr >= d
                                   ))
            else:
                comp = self._convert_comparator(comp)
                c = d - timedelta(days=d.day - 1)
                query = query.filter(getattr(attr, comp)(c))

#        c = '{}'.format(c)
        return query

#        elif 'runtime' in param:
#    def time_query(self):
#        args = criteria.split(':')
#        if len(args) in [1, 2] and comp == '=':
#            base = ['00', ] * (3 - len(args))
#            g = ':'.join(args + base)
#            try:
#                a = [int(ai) + (1 if len(args) - 1 == i else 0)
#                    for i, ai in enumerate(args)]
#            except ValueError:
#                return None
#
#            f = ':'.join(['{:n}', ] * (len(args)) + base)
#            l = f.format(*a)
#            c = self._between(param , l, g)
#            return c
#        else:
#            c = ':'.join(args + ['00', ] * (3 - len(args)))
#    def get_filter_str(self,):
#        return self._get_filter_str(self.parameter, self.comparator, self.criterion)
#
#    def _get_filter_str(self, param, comp, criteria):
#        if self.date_str in param:
#            c = criteria.replace('/', '-')
#            if criteria == 'today':
#                c = get_date()
#            elif criteria == 'this month':
#                d = datetime.today().date()
#                today = get_date()
#                if '=' in comp:
#                    d = d - timedelta(days=d.day)
#                    c = self._between(param, today, d)
#                    return c
#                else:
#                    c = d - timedelta(days=d.day - 1)
#            c = '{}'.format(c)
#        elif 'runtime' in param:
#            args = criteria.split(':')
#            if len(args) in [1, 2] and comp == '=':
#                base = ['00', ] * (3 - len(args))
#                g = ':'.join(args + base)
#                try:
#                    a = [int(ai) + (1 if len(args) - 1 == i else 0)
#                        for i, ai in enumerate(args)]
#                except ValueError:
#                    return None
#
#                f = ':'.join(['{:n}', ] * (len(args)) + base)
#                l = f.format(*a)
#                c = self._between(param , l, g)
#                return c
#            else:
#                c = ':'.join(args + ['00', ] * (3 - len(args)))
#        else:
#            #convert forgein key param
#            if not '.' in param:
#                param = '{}.id'.format(param)
#
#            c = criteria
#
#        if comp == 'like':
#            c += '%'
#        elif comp == 'contains':
#            comp = 'like'
#            c = '%' + c + '%'
#
#        c = '"{}"'.format(c)
#        return ' '.join((param, comp, c))

#===============================================================================
# private
#===============================================================================
#    def _between(self, p, l, g):
#        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _convert_comparator(self, c):
        if c == '=':
            c = '__eq__'
        elif c == '<':
            c = '__lt__'
        elif c == '>':
            c = '__gt__'
        elif c == '<=':
            c = '__le__'
        elif c == '>=':
            c = '__ge__'
        return c

#    @cached_property
    def _get_parameters(self):

#        b = self.query_table
#        params = [str(fi.column).split('.')[0].replace('Table', '').lower() for fi in b.__table__.foreign_keys]
#
#        params += [str(col) for col in b.__table__.columns]
##        f = lambda x:[str(col)
##                           for col in x.__table__.columns]
##        params = list(f(b))
        params = self.__params__
        if not self.parameter:
            self.parameter = params[0]

        return params

#===============================================================================
# handlers
#===============================================================================
    def _add_fired(self):

#        g = TableSelector()
#        info = g.edit_traits()
#        if info.result:
#            self.selector.add_query(g.parameter)
        self.selector.add_query('')

    def _remove_fired(self):
        self.selector.remove_query(self)

#    def _criterion_changed(self):
#        if self.criterion:
#            self.selector.execute_query()

#===============================================================================
# property get/set
#===============================================================================
    def _get_criteria(self):
        return []
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='parameters'),
                     width= -200
                     ),
                Spring(springy=False,
                       width=10),
                Item('comparator', editor=EnumEditor(name='comparisons')),
                Item('criterion'),
                Item('add'),
                Spring(springy=False,
                       width=50, visible_when='not removable'),
                Item('remove', visible_when='removable'),
                show_labels=False
                )
        v = View(qgrp)
        return v

class IsotopeQuery(Query):
    __params__ = ['Labnumber',
                'Irradiation',
                'Run Date/Time',
                'Irradiation Level',
                'Irradiation Position',
                'Sample',
                'Project',
                'Experiment'
                ]

class DeviceScanQuery(Query):
    __params__ = ['Run Date/Time', ]
class BakeoutQuery(Query):
    __params__ = ['Run Date/Time',
                  'Controller'
                  ]
#============= EOF =============================================
