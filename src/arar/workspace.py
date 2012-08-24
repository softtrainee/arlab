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
from traits.api import Str, List, Instance
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.arar.nodes.experiment import ExperimentNode
import os
from src.graph.graph import Graph
from src.database.core.database_adapter import DatabaseAdapter


class ArArWorkspace(Loggable):
    name = Str('Workspace')
    experiments = List(ExperimentNode)
    root = Str
    current_experiment = Instance(ExperimentNode)
    db = Instance(DatabaseAdapter)

    graph = Instance(Graph)

    def traits_view(self):
        v = View(
                 Item('name', show_label=False, style='readonly'),
                 )
        return v

    def init(self):
        self.info('initializing workspace {}'.format(self.root))
        if os.path.isdir(self.root):
            pass
#            if self.confirmation_dialog('Overwrite Directory {}'.format(self.root)):
#                pass
        else:
            os.mkdir(self.root)

    def new_experiment(self, name, kind):
        klass = '{}Node'.format(kind.capitalize())
        m = __import__('src.arar.nodes.{}'.format(kind), fromlist=[klass])
        cls = getattr(m, klass)
        exp = cls(name=name)
        self.current_experiment = exp
        self.experiments.append(exp)
        return exp

    def add_data(self, data):
        exp = self.current_experiment
        db = self.db
        for d in data:
            ref = db.get_analysis(d.rid)
            irrad_pos = db.get_irradiation_position(ref.IrradPosition)
#
            arar_analysis = ref.araranalyses[-1]
            rid = ref.RID
            kwargs = dict(
                        sample=ref.sample.Sample,
                        irradiation=irrad_pos.IrradiationLevel,
                        age=arar_analysis.Age,
                        age_err=arar_analysis.ErrAge
                        )
            exp.load_analysis_reference(ref, rid, kwargs)

            exp.load_series_reference('airs', ref, rid, kwargs)

#        #refresh the plot
#        self._selected_changed()
    def has_node(self, node):
        if node in self.experiments:
            return True
        else:
            for exp in self.experiments:
                if exp.has_node(node):
                    return True

#===============================================================================
# factories
#===============================================================================
    def _graph_factory(self, shape):
        g = Graph(container_dict=dict(type='g',
                                      shape=shape,
                                      bgcolor='gray',
                                      padding=10
                                      ),
                  )
        return g
#===============================================================================
# defaults
#===============================================================================

    def _graph_default(self):
        return self._graph_factory((1, 1))
#===============================================================================
# views
#===============================================================================
#    def configure_view(self):
#        v = View()
#        return v

    def graph_view(self):
        v = View(Item('graph',
                      show_label=False,
                      style='custom'))
        return v

#============= EOF =============================================
