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
from envisage.ui.tasks.task_factory import TaskFactory
from pyface.tasks.action.schema_addition import SchemaAddition
from envisage.ui.tasks.task_extension import TaskExtension
# from pyface.action.group import Group
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
# from src.experiment.signal_calculator import SignalCalculator
# from src.experiment.image_browser import ImageBrowser
# from src.experiment.tasks.experiment_task import ExperimentEditorTask
# from src.experiment.tasks.experiment_preferences import ExperimentPreferencesPane
# from src.experiment.tasks.experiment_actions import NewExperimentQueueAction, \
#     OpenExperimentQueueAction, SaveExperimentQueueAction, \
#     SaveAsExperimentQueueAction, SignalCalculatorAction, \
#     UpdateDatabaseAction, DeselectAction, SendTestNotificationAction, \
#     NewPatternAction, OpenPatternAction, ResetQueuesAction
# from src.experiment.tasks.constants_preferences import ConstantsPreferencesPane
# from src.database.isotope_database_manager import IsotopeDatabaseManager
from src.loading.load_task import LoadingTask
from src.loading.actions import SaveLoadingAction
from src.loading.loading_preferences import LoadingPreferencesPane

class LoadingPlugin(BaseTaskPlugin):
    id = 'pychron.loading'
    def _my_task_extensions_default(self):
        return [
                TaskExtension(task_id='pychron.loading',
                               actions=[SchemaAddition(id='save_loading_figure',
                                                       factory=SaveLoadingAction,
                                                       path='MenuBar/File')
                                        ],
                              ),
                ]

    def _tasks_default(self):
        return [
                TaskFactory(id='pychron.loading',
                            factory=self._load_task_factory,
                            name='Loading',
                            accelerator='Ctrl+Y',
                            task_group='experiment'
                            )
                ]

    def _load_task_factory(self):
        return LoadingTask()

    def _preferences_panes_default(self):
        return [
                LoadingPreferencesPane
                ]
#============= EOF =============================================
