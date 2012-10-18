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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.processing.series.fit_series_editor import FitSeriesEditor
from src.experiment.processing.figures.detector_intercalibration_figure import DetectorIntercalibrationFigure
from src.experiment.processing.series.detector_intercalibration_config import DetectorIntercalibrationConfig

class DetectorIntercalibrationEditor(FitSeriesEditor):
    config_klass = DetectorIntercalibrationConfig
    figure_klass = DetectorIntercalibrationFigure
    _series_name = 'detector_intercalibration'
#    _series_key = 'bg'
    _analysis_type = 'air'

    def _apply(self, analysis):
        sn = self._series_name
        db = self.db

        an = analysis.dbresult
#        histories = getattr(an, '{}_histories'.format(sn))
#        phistory = histories[-1] if histories else None
        history = None

        funchist = getattr(db, 'add_{}_history'.format(sn))
        func = getattr(db, 'add_{}'.format(sn))
        for ci in self.configs:
            if ci.save:
                self.saveable = True
                l = ci.label
                uv = ci.value
                ue = ci.error
#                k = '{}{}'.format(l, self._series_key)
#                analysis.signals[k] = Signal(_value=uv, error=ue)
                if history is None:
                    self.info('adding {} history for {}'.format(sn, analysis.rid))
                    history = funchist(an)

                func(history, user_value=uv, user_error=ue)
                self.info('setting {} {}. {:0.5f} +/- {:0.5f}'.format(l, sn, uv, ue))

#                self._copy_from_previous(phistory, history, l)

#============= EOF =============================================
