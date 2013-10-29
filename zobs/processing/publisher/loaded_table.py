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
from traits.api import List, Button, Any, Dict, cached_property, Property, \
    on_trait_change
from traitsui.api import View, Controller, UItem, \
    HGroup, spring, ListEditor
#============= standard library imports ========================
from functools import partial
#============= local library imports  ==========================
from src.processing.publisher.analysis import PubAnalysis, Marker
from src.pychron_constants import PLUSMINUS
from src.ui.tabular_editor import myTabularEditor
from traitsui.tabular_adapter import TabularAdapter
from pyface.action.menu_manager import MenuManager
from pyface.action.action import Action
from src.helpers.formatting import floatfmt


class LoadedTableAdapter(TabularAdapter):
    columns = Property(depends_on='visible_columns,visible_columns[]')
    visible_columns = List(['runid', 'status', 'age', 'age_error', 'k_ca'])
    column_m = {'runid': ('RunID', 'runid'),
                'status': ('Status', 'status'),
                'age': ('Age', 'age'),
                'age_error': (u'{}1s'.format(PLUSMINUS), 'age_error'),
                'k_ca': ('K/Ca', 'k_ca'),
                'labnumber': ('Lab. #', 'labnumber')
    }
    age_text = Property
    age_error_text = Property
    status_text = Property
    k_ca_text = Property

    def _get_k_ca_text(self):
        return floatfmt(self._get_nominal_value('k_ca'), n=2)

    def _get_status_text(self):
        s = self.item.status
        if s == 0 or s == '0':
            s = ''
        return s

    def _get_age_error_text(self):
        return self._get_std_dev('age')

    def _get_age_text(self):
        return self._get_nominal_value('age')

    def _get_nominal_value(self, attr):
        v = getattr(self.item, attr)
        if not isinstance(v, str):
            v = v.nominal_value
        return v

    def _get_std_dev(self, attr):
        v = getattr(self.item, attr)
        if not isinstance(v, str):
            v = v.std_dev
        return v

    @cached_property
    def _get_columns(self):
        cols = []
        visible_columns = self.visible_columns
        for attr in visible_columns:
            cols.append(self.column_m[attr])

        return cols


class ComputedValuesTabularAdapter(TabularAdapter):
    columns = [('Lab. #', 'labnumber'),
               ('Sample', 'sample'),
               ('Plateau', 'plateau_age'),
               ('{}1s'.format(PLUSMINUS), 'plateau_error'),
               ('Steps', 'plateau_steps'),
               ('Integrated', 'integrated_age'),
               ('{}1s'.format(PLUSMINUS), 'integrated_error'),
               ('Weighted Mean Age.', 'wm_age'),
    ]

    plateau_age_text = Property
    plateau_error_text = Property
    integrated_age_text = Property
    integrated_error_text = Property
    plateau_steps_text = Property

    def _get_plateau_steps_text(self):
        s = self.item.plateau_steps
        n = self.item.plateau_nsteps
        if n > 1:
            m = 'n= {}, {}'.format(n, s)
        else:
            m = ''
        return m

    def _get_plateau_error_text(self):
        return self._get_std_dev('plateau_age')

    def _get_plateau_age_text(self):
        return self._get_nominal_value('plateau_age')

    def _get_integrated_error_text(self):
        return self._get_std_dev('integrated_age')

    def _get_integrated_age_text(self):
        return self._get_nominal_value('integrated_age')

    def _get_nominal_value(self, attr):
        return self._get_value('nominal_value', attr, partial(floatfmt, n=8))

    def _get_std_dev(self, attr):
        return self._get_value('std_dev', attr, partial(floatfmt, n=9))

    def _get_value(self, key, attr, fmt):
        v = getattr(self.item, attr)
        if v is not None:
            v = getattr(v, key)
            if isinstance(fmt, str):
                m = fmt.format(v)
            else:
                m = fmt(v)
        else:
            m = ''
        return m

        # class MeanLoadedTableAdapter(LoadedTableAdapter):

#    visible_columns = ['labnumber', 'age']

class LoadedTableController(Controller):
    load_button = Button
    selected = Any
    columns_button = Button('Columns')
    columns = List
    column_dict = Dict({'RunID': 'runid',
                        'Age': 'age',
                        'AgeError': 'age_error',
                        'K/Ca': 'k_ca'
    })

    @on_trait_change('model:groups:right_clicked')
    def _right_clicked_handler(self, new):
        if self.selected:
            sel = self.selected.selected
        else:
            sel = self.model.groups[0].selected

        if not sel:
            return

        mm = self._menu_factory(sel)

        control = self.info.ui.control
        menu = mm.create_menu(control, None)
        menu.show()

    def _include(self, selected):
        def __include():
            print 'asdfasdfasdf', selected

        return __include

    def _menu_factory(self, selected):
        actions = [('Include', self._include(selected))]
        menu = [self._action_factory(*action)
                for action in actions]

        return MenuManager(*menu)

    def _action_factory(self, name, func, **kw):
        if isinstance(func, str):
            func = getattr(self, func)

        return Action(name=name,
                      on_perform=func,
                      #                   visible_when='0',
                      **kw)

    def controller_load_button_changed(self, info):
        p = '/Users/ross/Sandbox/autoupdate_stepheat_61526.txt'
        self.model.load(p)

    #    def controller_columns_button_changed(self, info):
    #        v = View(Item('controller.columns',
    #                      editor=SetEditor(ordered=True,
    #                                       values=['RunID', 'Age', 'AgeError', 'K/Ca']),
    #                      ),
    #                 buttons=['OK', 'Cancel'],
    #                 kind='livemodal'
    #                 )
    #        info = self.edit_traits(v)
    #        if info.result:
    #            cs = [self.column_dict[ci] for ci in self.columns]
    #            self._loaded_table_adapter.visible_columns = cs

    def traits_view(self):
    #        self._loaded_table_adapter = LoadedTableAdapter()
    #        self._mean_loaded_table_adapter = MeanLoadedTableAdapter()
        self._computed_values_adapter = ComputedValuesTabularAdapter()
        v = View(
            HGroup(UItem('controller.columns_button'),
                   spring, UItem('controller.load_button')),
            UItem('groups',
                  style='custom',
                  editor=ListEditor(use_notebook=True,
                                    page_name='.name',
                                    style='custom',
                                    selected='controller.selected'
                                    #                                                   editor=InstanceEditor()
                  )
            ),
            UItem('computed_values', editor=myTabularEditor(
                editable=False,
                adapter=self._computed_values_adapter)),

        )

        return v

        #============= EOF =============================================
