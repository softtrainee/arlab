#===============================================================================
# Copyright 2013 Jake Ross
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
from pyface.message_dialog import information, warning
from traits.api import HasTraits, List, Any, Str, Enum, Bool, Button, \
    Int

#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.browser.table_configurer import TableConfigurer


class AnalysisTable(HasTraits):
    analyses = List
    oanalyses = List
    selected = Any
    dclicked = Any

    analysis_filter = Str
    analysis_filter_values = List
    analysis_filter_comparator = Enum('=', '<', '>', '>=', '<=', 'not =', 'startswith')
    analysis_filter_parameter = Str('Record_id')
    analysis_filter_parameters = List(['Record_id', 'Tag',
                                       'Age', 'Labnumber', 'Aliquot', 'Step'])

    omit_invalid = Bool(True)
    configure_analysis_filter = Button

    forward = Button
    backward = Button
    limit = Int
    page = Int

    db = Any

    def _forward_fired(self):
        db = self.db
        print db

    def _backward_fired(self):
        pass

    def set_analyses(self, ans):
        self.analyses = ans
        self.oanalyses = ans

    def _analysis_filter_changed(self, new):
        if new:
            name = self.analysis_filter_parameter
            comp = self.analysis_filter_comparator
            if name == 'Step':
                new = new.upper()

            self.analyses = filter(self._filter_func(new, name, comp), self.oanalyses)
        else:
            self.analyses = self.oanalyses

    def _configure_analysis_filter_fired(self):
        #msg = 'Advanced search not implemented yet!'
        #warning(None, msg)

        #self.information_dialog()
        c = TableConfigurer(adapter=self.tabular_adapter,
                            title='Configure Analysis Table')
        c.edit_traits()


    def _get_analysis_filter_parameter(self):
        p = self.analysis_filter_parameter
        return p.lower()

    def _analysis_filter_comparator_changed(self):
        self._analysis_filter_changed(self.analysis_filter)

    def _analysis_filter_parameter_changed(self, new):
        if new:
            vs = []
            p = self._get_analysis_filter_parameter()
            for si in self.oanalyses:
                v = getattr(si, p)
                if not v in vs:
                    vs.append(v)

            self.analysis_filter_values = vs

#============= EOF =============================================
        #def filter_invalid(self, ans):
        #    if self.omit_invalid:
        #        ans = filter(self._omit_invalid_filter, ans)
        #    return ans

        #def _omit_invalid_filter(self, x):
        #    return x.tag != 'invalid'

        #def _omit_invalid_changed(self, new):
        #    if new:
        #        self._
        #        self.analyses = filter(self._omit_invalid_filter, self.oanalyses)
        #    else:
        #        self.analyses = self.oanalyses
