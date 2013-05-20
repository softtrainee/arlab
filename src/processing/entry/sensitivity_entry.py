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
from traits.api import HasTraits, Any, List, Button, Property, Str, Int
from traitsui.api import View, Item, TabularEditor, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================
from src.paths import paths
from src.experiment.entry.db_entry import DBEntry
from traitsui.tabular_adapter import TabularAdapter

class SensitivityAdapter(TabularAdapter):
    columns = [('', 'placeholder'),
               ('Spectrometer', 'spectrometer'),
               ('Sensitivity', 'sensitivity'), ('User', 'user'),
               ('Date', 'create_date'),
               ('Note', 'note')]
    placeholder_text = Str('')
    placeholder_width = Int(2)
#    mass_spectrometer_width = Int(40)

class SensitivityRecord(HasTraits):
    dbrecord = Any
    spectrometer = Property
    _spectrometer = Str

    def _get_spectrometer(self):

        if self._spectrometer:
            return self._spectrometer

        if self.dbrecord:
            return self.dbrecord.mass_spectrometer.name

    def _set_spectrometer(self, v):
        self._spectrometer = v

    def __getattr__(self, attr):
        if hasattr(self.dbrecord, attr):
            return getattr(self.dbrecord, attr)

    def sync(self, spec):
        attrs = ['sensitivity', 'note', 'user']
        for ai in attrs:
            v = getattr(self, ai)
            setattr(self.dbrecord, ai, v)

        self.dbrecord.mass_spectrometer = spec


class SensitivityEntry(DBEntry):
    records = Property(List(SensitivityRecord),
                       depends_on='_records'
                       )
    _records = List
    add_button = Button('+')
    save_button = Button('save')

#===============================================================================
# handlers
#===============================================================================
    def _add_button_fired(self):
        s = SensitivityRecord()
        self._records.append(s)
#        self.records_dirty = True
    def _save_button_fired(self):
        db = self.db
        for si in self.records:
#            print si.note, si.dbrecord.
            if si.dbrecord is None:
                user = si.user
                if user == 'None':
                    user = db.save_username
                db.add_sensitivity(si.spectrometer,
                                   user=user, note=si.note, sensitivity=si.sensitivity)
            else:
                spec = db.get_mass_spectrometer(si.spectrometer)
                si.sync(spec)
#                for ai in ['sensitivity','']



        db.commit()
#===============================================================================
# property get/set
#===============================================================================
    def _get_records(self):
        if not self._records:
            recs = self.db.get_sensitivities()
            self._records = [SensitivityRecord(dbrecord=ri) for ri in recs]
        return self._records

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(Item('records', show_label=False,
                      editor=TabularEditor(adapter=SensitivityAdapter(),
                                           operations=['edit'],
                                           editable=True,
                                           )
                      ),

                 HGroup(Item('add_button', show_label=False),
                        Item('save_button', show_label=False)),
                 resizable=True,
                 width=500,
                 height=200,
                 title='Sensitivity Table'
                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    paths.build('_experiment')

    logging_setup('runid')
    m = SensitivityEntry()
    m.configure_traits()
#============= EOF =============================================
