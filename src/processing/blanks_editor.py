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
from traits.api import HasTraits, Button, List, Str, Int, Instance, Property, Bool, Any
from traitsui.api import View, Item, VGroup, HGroup, Spring, Label, Group, \
    spring
#============= standard library imports ========================
#============= local library imports  ==========================
from src.helpers.traitsui_shortcuts import listeditor
from src.processing.blank_config import BlankConfig
from src.database.core.database_adapter import DatabaseAdapter
from src.database.orms.isotope_orm import proc_BlanksTable
from src.loggable import Loggable
from src.processing.analysis import Signal

#@todo: add notes to blanks history table
#@todo: save notes to blanks history table

class BlanksEditor(Loggable):

    db = Instance(DatabaseAdapter)
    workspace = None
    repo = None

    apply_blanks = Button
    fit_blanks = Button
    revert_blanks = Button
    save_blanks = Button

    blanks = List

#    note = Str
#    save_note = Button('Save')

    analyses = List
    saveable = Bool(False)
    appliable = Property(depends_on='blanks.save')

    def _get_appliable(self):
        return [s for s in self.blanks if s.save]
#    saveable = Property(depends_on='blanks.save')
#    def _get_saveable(self):
#        return [s for s in self.blanks if s.save]

    def add(self, iso_keys):
        self.blanks = [BlankConfig(label=iso)
                        for iso in iso_keys]

#===============================================================================
# handlers
#===============================================================================

    def _fit_blanks_fired(self):
        #open a figure with the default loaded blanks
        from figures.blanks_figure import BlanksFigure
        f = BlanksFigure(db=self.db,
                   workspace=self.workspace,
                   repo=self.repo)
        f.edit_traits()
        f.on_trait_change(self._fit_blanks, 'apply_blanks_event')

    def _fit_blanks(self):
        self.info('Applying blank fits to analyses')
        for a in self.analyses:
            an = a.dbresult

    def _revert_blanks_fired(self):
        pass

    def _save_blanks_fired(self):
        '''
             add new blank history
             add blanks row
        '''

        db = self.db
        self.info('committing blanks to db')
        db.commit()

    def _apply_blanks_fired(self):
        db = self.db
        for a in self.analyses:
            an = a.dbresult
            histories = an.blanks_histories
            phistory = histories[-1] if histories else None
            history = None
            for bci in self.blanks:
                if bci.save:
                    self.saveable = True
                    l = bci.label
                    uv = bci.value
                    ue = bci.error

                    a.signals['{}bl'.format(l)] = Signal(_value=uv, _error=ue)
                    a.age_dirty = True

                    if history is None:
                        self.info('adding blanks history for {}'.format(a.rid))
                        history = db.add_blanks_history(an)

                    db.add_blanks(history,
                                       isotope=l,
                                       use_set=False,
                                       user_value=uv, user_error=ue)
                    self.info('setting {} blank. {:0.5f} +/- {:0.5f}'.format(l, uv, ue))

                    #copy blanks from a previous history
                    for bi in phistory.blanks:
                        li = bi.isotope
                        if li == l:
                            continue

                        uv = bi.user_value
                        ue = bi.user_error
                        db.add_blanks(history,
                                      isotope=li,
                                      use_set=bi.use_set,
                                      user_value=uv,
                                      user_error=ue
                                      )
                        self.info('copying {} blank from previous history. {:0.5f} +/- {:0.5f}'.format(li, uv, ue))


#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        header = HGroup(Spring(springy=False, width=38),
                      Label('Value'),
                      Spring(springy=False, width=62),
                      Label('Error'),
                      Spring(springy=False, width=62),
                      Label('Save'),
                      )

        left = VGroup(
                     header,
                     listeditor('blanks', height=125),
                     )
        right = HGroup(
                       Item('apply_blanks',
                           enabled_when='appliable',
                           show_label=False),
                       Item('revert_blanks',
                                       enabled_when='0',
                                       show_label=False,
                                       ),
                      Item('save_blanks',
                           enabled_when='saveable',
                           show_label=False),
                      Item('fit_blanks', show_label=False)
                    )

        v = View(HGroup(left, right))
#        v = View(right)
        return v
#============= EOF =============================================
