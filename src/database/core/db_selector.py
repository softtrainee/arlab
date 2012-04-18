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
from traits.api import HasTraits, Str, String, Button, List, Any, Long, Event, \
    Date, Time, Instance, Dict, DelegatesTo, Property

from traitsui.api import View, Item, TabularEditor, EnumEditor, \
    HGroup, VGroup, Group, spring
from traitsui.tabular_adapter import TabularAdapter
from datetime import datetime, timedelta

from src.helpers.datetime_tools import  get_date

from src.loggable import Loggable
from src.database.core.database_adapter import DatabaseAdapter


class DBResult(HasTraits):
    _id = Long
    _db_result = Any

class DBSelector(Loggable):
    parameter = String
    _parameters = Property
    comparator = Str('=')
#    _comparisons = List(COMPARISONS['num'])
    _comparisons = List(['=', '<', '>', '<=', '>=', '!=', 'like', 'contains'])
    criteria = Str('this month')
    comparator_types = Property
    search = Button
    results = List

    _db = DatabaseAdapter

    dclicked = Event
    selected = Any

    wx = 0.4
    wy = 0.1
    opened_windows = Dict
    title = 'Recall'

    def _search_fired(self):
        self._search_()

    def _search_(self):
        pass
    def _get_comparator_types(self):
        return ['=', '<', '>', '<=', '>=', '!=', 'like']

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

    def _between(self, p, l, g):
        return '{}<="{}" AND {}>="{}"'.format(p, l, p, g)

    def _get_filter_str(self):

        if self.date_str in self.parameter:
            c = self.criteria.replace('/', '-')
            if self.criteria == 'today':
                c = get_date()
            elif self.criteria == 'this month':
                d = datetime.today().date()
                today = get_date()
                if '=' in self.comparator:
                    d = d - timedelta(days=d.day)
                    c = self._between(self.parameter, today, d)
                    return c
                else:
                    c = d - timedelta(days=d.day - 1)
            c = '{}'.format(c)
        elif 'runtime' in self.parameter:
            args = self.criteria.split(':')
            if len(args) in [1, 2] and self.comparator == '=':
                base = ['00', ] * (3 - len(args))
                g = ':'.join(args + base)
                try:
                    a = [int(ai) + (1 if len(args) - 1 == i else 0)
                        for i, ai in enumerate(args)]
                except ValueError:
                    return None

                f = ':'.join(['{:n}', ] * (len(args)) + base)
                l = f.format(*a)
                c = self._between(self.parameter, l, g)
                return c
            else:
                c = ':'.join(args + ['00', ] * (3 - len(args)))
        else:
            c = self.criteria


        c = '{}'.format(c)
        s = ''.join((self.parameter,
                   self.comparator,
                   c))
        return s
    def traits_view(self):

        qgrp = HGroup(
                Item('parameter', editor=EnumEditor(name='_parameters')),
                Item('comparator', editor=EnumEditor(name='_comparisons')),
                Item('criteria'),
                show_labels=False
                )


        editor = TabularEditor(adapter=self.tabular_adapter(),
                               dclicked='object.dclicked',
                               selected='object.selected',
                               editable=False,
                               multi_select=True
                               )
        v = View(

                 Item('results', style='custom',
                      editor=editor,
                      show_label=False
                      ),
                 qgrp,
                 HGroup(spring, Item('search', show_label=False)),


                 resizable=True,
                 width=500,
                 height=500,
                 x=0.1,
                 y=0.1,
                 title=self.title
                 )
        return v
