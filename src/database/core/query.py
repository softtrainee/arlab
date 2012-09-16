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
    Bool, cached_property
from traitsui.api import View, Item, EnumEditor, HGroup, Spring , spring
from src.helpers.datetime_tools import get_date
from datetime import datetime, timedelta
#============= standard library imports ========================
#============= local library imports  ==========================
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
    parameters = Property(depends_on='query_table')

    comparator = Str('=')
    comparisons = List(['=', '<', '>', '<=', '>=', '!=',
                         'like',
                         'contains'
                         ])
    criterion = String('')
    query_table = Any

    parent = Any
    add = Button('+')
    remove = Button('-')
    removable = Bool(True)
    date_str = 'rundate'

    def get_filter_str(self,):
        return self._get_filter_str(self.parameter, self.comparator, self.criterion)

    def _get_filter_str(self, param, comp, criteria):
        if self.date_str in param:
            c = criteria.replace('/', '-')
            if criteria == 'today':
                c = get_date()
            elif criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if '=' in comp:
                    d = d - timedelta(days=d.day)
                    c = self._between(param, today, d)
                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '{}'.format(c)
        elif 'runtime' in param:
            args = criteria.split(':')
            if len(args) in [1, 2] and comp == '=':
                base = ['00', ] * (3 - len(args))
                g = ':'.join(args + base)
                try:
                    a = [int(ai) + (1 if len(args) - 1 == i else 0)
                        for i, ai in enumerate(args)]
                except ValueError:
                    return None

                f = ':'.join(['{:n}', ] * (len(args)) + base)
                l = f.format(*a)
                c = self._between(param , l, g)
                return c
            else:
                c = ':'.join(args + ['00', ] * (3 - len(args)))
        else:
            #convert forgein key param
            if not '.' in param:
                param = '{}Table.id'.format(param)

            c = criteria

        if comp == 'like':
            c += '%'
        elif comp == 'contains':
            comp = 'like'
            c = '%' + c + '%'

        c = '"{}"'.format(c)
        return ' '.join((param, comp, c))

#===============================================================================
# private
#===============================================================================
    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

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

    @cached_property
    def _get_parameters(self):

        b = self.query_table
        params = [str(fi.column).split('.')[0].replace('Table', '').lower() for fi in b.__table__.foreign_keys]

        params += [str(col) for col in b.__table__.columns]
#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = list(f(b))
        if not self.parameter:
            self.parameter = params[0]
        return params

#===============================================================================
# handlers
#===============================================================================
    def _add_fired(self):

        g = TableSelector()
        info = g.edit_traits()
        if info.result:
            self.parent.add_query(g.parameter)

    def _remove_fired(self):
        self.parent.remove_query(self)

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
#============= EOF =============================================
