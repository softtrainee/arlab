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
#============= standard library imports ========================
#============= local library imports  ==========================
from reportlab.platypus.flowables import Flowable


class GraphFlowable(Flowable):
    '''
        use this class to add a Chaco Graph (src.graph.graph.Graph) to a 
        PDF document
        
        ...
        gf=GraphFlowable(graph)
        doc.build([gf,...,])
        
    '''
    def __init__(self, graph, scale=1.0, align='left'):
        self._graph = graph
        self._scale = scale
        self._size = graph.plotcontainer.width * self._scale
        self._xoffset = 0
        self._align = align

    def wrap(self, *args):
        return (self._xoffset, self._size)

    def draw(self):
        if self._align == 'center':
            self.canv.translate(self._xoffset + self._size, 0)  # , -self.size)
        self.canv.scale(self._scale, self._scale)
        self._graph.render_to_pdf(canvas=self.canv)
#============= EOF =============================================
