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



#============= enthought library imports =======================
from traits.api import HasTraits, Any, Instance, Str, List, Enum, Bool
from traitsui.api import View, Item, \
     TableEditor, EnumEditor, \
     HGroup, Label
from traitsui.table_column import ObjectColumn
from traitsui.table_filter import TableFilter
#============= standard library imports ========================
import datetime
#============= local library imports  ==========================
from src.managers.manager import Manager

class LogRecord(HasTraits):
    name = Str
    level = Str
    date = Str
    time = Str
    message = Str

class LogFilter(TableFilter):
    parent = Any
    name = Str
    names = List(['---'])
    level = Enum('---', 'INFO', 'WARNING', 'DEBUG')
    date = Str(enter_set=True, auto_set=False)
    time = Str(enter_set=True, auto_set=False)

    highlight = Bool

    dcomparator = Enum('=', '<', '>', '<=', '>=')
    tcomparator = Enum('=', '<', '>', '<=', '>=')
    message = Str(enter_set=True, auto_set=False)
    traits_view = View(Item('name', editor=EnumEditor(name='names')),
                       Item('level'),
                       HGroup(Label('Date'), Item('dcomparator', show_label=False), Item('date', show_label=False)),
                       HGroup(Label('Time'), Item('tcomparator', show_label=False), Item('time', show_label=False)),
                       HGroup(Label('Message = '), Item('message', show_label=False), Item('highlight'))

                       )

    def filter(self, obj):
        tname = self.name in ['All items', '---']

        if not tname:
            tname = obj.name == self.name

        tlevel = self.level in ['All items', '---']
        if not tlevel:
            tlevel = obj.level == self.level

        tdate = not self.date
        if not tdate:
            odate = datetime.date(*[int(i) for i in obj.date.split('-')])
            args = [int(i) for i in self.date.split('-')]
            if len(args) == 2:
                args += [odate.day]
            elif len(args) == 1:
                args += [odate.month, odate.day]

            fdate = datetime.date(*args)
            delta = odate - fdate
            delta = delta.total_seconds()

            if self.dcomparator == '=':
                tdate = delta == 0
            elif self.dcomparator == '<':
                tdate = delta < 0
            elif self.dcomparator == '>':
                tdate = delta > 0
            elif self.dcomparator == '<=':
                tdate = delta <= 0
            elif self.dcomparator == '>=':
                tdate = delta >= 0

        ttime = not self.time
        if not ttime:
            otime, micro = obj.time.split(',')

            args = [int(i) for i in otime.split(':')]
            otime = datetime.datetime(*[1, 1, 1] + args + [int(micro)])


            args = [int(i) for i in self.time.split(':')]
            if len(args) == 2:
                args += [otime.second, otime.microsecond]
            elif len(args) == 1:
                args += [otime.minute, otime.second, otime.microsecond]

            ftime = datetime.datetime(*[1, 1, 1] + args)
            delta = otime - ftime
            delta = delta.total_seconds()

            if self.tcomparator == '=':
                ttime = abs(delta) < 0.001
            elif self.tcomparator == '<':
                ttime = delta < 0
            elif self.tcomparator == '>':
                ttime = delta > 0.001
            elif self.tcomparator == '<=':
                ttime = delta <= 0.001
            elif self.tcomparator == '>=':
                ttime = delta >= 0.001

        tmsg = True
        if self.message:
            tmsg = self.message in obj.message
            if tmsg and self.highlight:
                self.parent.selected.append(obj)
            if self.highlight:
                tmsg = True
        else:
            self.parent.selected = []

        return (tname and
                tlevel and
                tdate and
                ttime and
                tmsg
                )

class LoggerManager(Manager):
    messages = List
    filter = Instance(LogFilter, ())
    selected = List
    path = Str
#    path = File
#    def _path_changed(self):
#        self.messages = []
#        self.load_file(self.path)

    def load_file(self, p):
        self.path = p
        self.filter.parent = self
        prev_msg = ''
        with open(p, 'r') as f:
            for line in f:
                args = ':'.join(line.split(':')[1:])
                args = args.split(' ')[1:]
                name = line.split(':')[0].strip()

                msg = ' '.join(args[3:])
                strip_decoration = True
                if strip_decoration:
                    msg = msg.strip()
                    if msg[:6] == '======' or msg[:6] == '******':
                        msg = msg[6:-6]

                if not args:
                    if prev_msg == '':
                        i = self.messages.pop(-1)
                        prev_msg = i.message + '\n' + line.strip()
                        prev_name = i.name
                    else:
                        prev_msg += '\n' + line.strip()
                else:
                    if prev_msg == '':
                        date = args[0]
                        ti = args[1]
                        level = args[2]
                        self.add_message(name, date, ti, level, msg.strip())

                    else:
                        self.add_message(prev_name, date, ti, level, prev_msg)
                        self.add_message(name, args[0], args[1], args[2], msg.strip())
                        prev_msg = ''

    def add_message(self, name, date, time, level, msg):
        self.messages.append(LogRecord(name=name,
                                       date=date,
                                       time=time,
                                       level=level,
                                       message=msg
                                       ))
        if name not in self.filter.names:
            self.filter.names.append(name)

    def traits_view(self):
        editor = TableEditor(columns=[ObjectColumn(name='name'),
                                        ObjectColumn(name='date'),
                                        ObjectColumn(name='time'),
                                        ObjectColumn(name='level'),
                                        ObjectColumn(name='message'),
                                        ],
                             editable=False,
                             selection_mode='rows',
                             selected='selected',
                             filter_name='filter',
                             filtered_indices='filtered_indices',
                             show_toolbar=True
                             )
        v = View(
                 Item('filter', show_label=False, style='custom'),
                 Item('path', style='readonly', show_label=False),
                 Item('messages', editor=editor, show_label=False),
                 width=700,
                 height=550,
                 resizable=True
                 )
        return v
if __name__ == '__main__':
    lm = LoggerManager()
    p = '/Users/Ross/Pychrondata_beta/logs/spectrometer560.log'
    lm.load_file(p)
#    lm.path = p
    lm.configure_traits()

#============= EOF =============================================
