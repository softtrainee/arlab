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
from traits.api import on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin

class ExperimentUIPlugin(CoreUIPlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.experiment.ui'
    name = 'Experiment UI'

    def _action_sets_default(self):
        '''
        '''
        from experiment_action_set import ExperimentActionSet
        return [ExperimentActionSet]

#    def _views_default(self):
#        '''
#        '''
#        return [self._create_analysis_graph_view]


#    def _create_analysis_graph_view(self, **kw):
#        '''
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        app = self.application
##        obj = app.get_service('src.experiment.analysis_graph_view.AnalysisGraphView')
#        manager = app.get_service('src.experiment.experiments_manager.ExperimentsManager')
#        manager.on_trait_change(obj.update, 'selected')
#
#        args = dict(id='experiment.analysis.graph.view',
#                         name='GraphView',
#                         obj=obj
#                         )
#
#        return self.traitsuiview_factory(args, kw)

#    @on_trait_change('application.gui:started')
#    def _started(self, obj, name, old, new):
#        '''
#            @type obj: C{str}
#            @param obj:
#
#            @type name: C{str}
#            @param name:
#
#            @type old: C{str}
#            @param old:
#
#            @type new: C{str}
#            @param new:
#        '''
#        if new  is True:
#            app = self.application
#            window = app.workbench.active_window
#            manager = app.get_service('src.experiment.experiment_manager.ExperimentManager')
#            manager.window = window
#            manager.open_default()
#============= views ===================================
#============= EOF ====================================
