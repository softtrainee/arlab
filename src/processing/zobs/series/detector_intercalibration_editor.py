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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.series.fit_series_editor import FitSeriesEditor
from src.processing.figures.detector_intercalibration_figure import DetectorIntercalibrationFigure
from src.processing.series.detector_intercalibration_config import DetectorIntercalibrationConfig

class DetectorIntercalibrationEditor(FitSeriesEditor):
    config_klass = DetectorIntercalibrationConfig
    figure_klass = DetectorIntercalibrationFigure
    _series_name = 'detector_intercalibration'
#    _series_key = 'bg'
    _analysis_type = 'air'

    def _add_history(self, func, history, uv, ue, *args):
        func(history, user_value=uv, user_error=ue)

#============= EOF =============================================
