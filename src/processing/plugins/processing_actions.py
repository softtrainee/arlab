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
from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager
from pyface.image_resource import ImageResource
from src.paths import paths
# from src.envisage.core.action_helper import open_manager
# from globals import globalv
#============= standard library imports ========================

#============= local library imports  ==========================
# EXPERIMENT_MANAGER_PROTOCOL =

class AgeCalculator(Action):
    accelerator = 'Ctrl+='

    def perform(self, event):
        app = event.window.application
        manager = app.get_service('src.processing.age_calculator.AgeCalculator')
        open_manager(app, manager)

class ProcessingAction(Action):
    def _get_manager(self, event):
        app = event.window.application
        manager = app.get_service('src.processing.processing_manager.ProcessingManager')
        return manager

class FitIsotopesAction(ProcessingAction):
    def perform(self, event):
        man = self._get_manager(event)
        man.fit_isotopes()

#===============================================================================
# find
#===============================================================================
class OpenSelectorAction(ProcessingAction):
    accelerator = 'Ctrl+f'
    def perform(self, event):
        man = self._get_manager(event)
        man.open_search()

class OpenFiguresAction(ProcessingAction):
    accelerator = 'Ctrl+Shift+f'
    def perform(self, event):
        man = self._get_manager(event)
        man.open_figures()

class SaveFigureAction(ProcessingAction):
    def perform(self, event):
        man = self._get_manager(event)
        man.save_figure()

class ExportCSVFigureTableAction(ProcessingAction):
    def perform(self, event):
        man = self._get_manager(event)
        man.export_figure_table(kind='csv')

class ExportPDFFigureTableAction(ProcessingAction):
    accelerator = 'Ctrl+shift+e'
    def perform(self, event):
        man = self._get_manager(event)
        man.export_figure_table(kind='pdf')

class ExportPDFFigureAction(ProcessingAction):
    def perform(self, event):
        man = self._get_manager(event)
        man.export_figure(kind='pdf')

# class ViewAnalysisTableAction(ProcessingAction):
#    accelerator = 'Ctrl+t'
#    def perform(self, event):
#        man = self._get_manager(event)
#        man.open_table()
#===============================================================================
# display
#===============================================================================
import os
ICON_PATH = os.path.join(os.path.dirname(__file__), 'images')
class NewSeriesAction(ProcessingAction):
    accelerator = 'Ctrl+k'
    def _image_default(self):
        im = ImageResource('series.gif',
                           search_path=[ICON_PATH])
        return im
    def perform(self, event):
        man = self._get_manager(event)
        man.new_series()

class NewIdeogramAction(ProcessingAction):
    accelerator = 'Ctrl+j'
    def _image_default(self):
        im = ImageResource('ideogram.gif',
                           search_path=[ICON_PATH])
        return im

    def perform(self, event):
        man = self._get_manager(event)
        man.new_ideogram()

class NewSpectrumAction(ProcessingAction):
    def _image_default(self):
        im = ImageResource('spectrum.gif',
                           search_path=[ICON_PATH])
        return im

    accelerator = 'Ctrl+u'
    def perform(self, event):
        man = self._get_manager(event)
        man.new_spectrum()

class NewInverseIsochronAction(ProcessingAction):
    accelerator = 'Ctrl+i'
    def _image_default(self):
        im = ImageResource('isochron.gif',
                           search_path=[ICON_PATH])
        return im
    def perform(self, event):
        man = self._get_manager(event)
        man.new_isochron()

#===============================================================================
# calculations
#===============================================================================
class CalculateFluxAction(ProcessingAction):
    accelerator = 'Ctrl+g'
    def perform(self, event):
        man = self._get_manager(event)
        man.calculate_flux()
#===============================================================================
# corrections
#===============================================================================

class ApplyBlankAction(ProcessingAction):
    accelerator = 'Ctrl+Shift+b'
    def perform(self, event):
        man = self._get_manager(event)
        man.apply_blank_correction()

class ApplyBackgroundAction(ProcessingAction):
    accelerator = 'Ctrl+Shift+n'
    def perform(self, event):
        man = self._get_manager(event)
        man.apply_background_correction()

class ApplyDetectorIntercalibrationAction(ProcessingAction):
    accelerator = 'Ctrl+Shift+d'
    def perform(self, event):
        man = self._get_manager(event)
        man.apply_detector_intercalibration_correction()

#===============================================================================
#
#===============================================================================
class ProjectViewAction(ProcessingAction):
    accelerator = 'Ctrl+p'
    def perform(self, event):
        man = self._get_manager(event)
        man.open_project_view()

class OpenRecentTableAction(ProcessingAction):
    description = 'Open the Recent Analysis Table'
    name = 'Lab Table'
    accelerator = 'Ctrl+R'

    def perform(self, event):
        manager = self._get_manager(event)
        manager.open_recent()


class DatabasePlotAction(ProcessingAction):
    def perform(self, event):
        manager = self._get_manager(event)
        manager.database_plot()

#============= EOF ====================================
