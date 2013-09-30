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
import os
from traits.api import HasTraits, Instance

#============= standard library imports ========================
#============= local library imports  ==========================
from src.canvas.canvas2D.extraction_line_canvas2D import ExtractionLineCanvas2D
from src.canvas.canvas2D.scene.canvas_parser import CanvasParser
from src.canvas.canvas2D.scene.extraction_line_scene import ExtractionLineScene
from src.canvas.canvas2D.scene.primitives.valves import Valve


class Designer(HasTraits):
    scene = Instance(ExtractionLineScene, ())
    canvas = Instance(ExtractionLineCanvas2D)

    def _canvas_default(self):
        canvas = ExtractionLineCanvas2D(active=False)
        return canvas

    def save_xml(self, p):
        if self.scene:
            # sync the canvas_parser with the
            # current scene and save
            if os.path.isfile(p):
                self._save_xml(p)
            else:
                self._construct_xml()

    def _save_xml(self, p):
        cp = CanvasParser(p)
        scene = self.scene
        for tag in ('laser', 'stage', 'spectrometer'):
            for ei in cp.get_elements(tag):
                name = ei.text.strip()
                obj = scene.get_item(name)
                if obj is not None:
                    color = ei.find('color')
                    if color is not None:
                        c = ','.join(map(lambda x: str(x),
                                         obj.default_color.toTuple()
                        ))
                        color.text = c
                    trans = ei.find('translation')
                    if trans is not None:
                        trans.text = '{},{}'.format(obj.x, obj.y)

        p = os.path.join(os.path.dirname(p, ), 'test.xml')
        cp.save(p)

    def _construct_xml(self):
        tags = {Valve: 'valve'}
        cp = CanvasParser()
        for elem in self.scene.iteritems():
            if type(elem) in tags:
                tag = tags[type(elem)]
                print tag, elem
            elif hasattr(elem, 'type_tag'):
                print elem.type_tag, elem

    def open_xml(self, p):
        #cp=CanvasParser(p)
        #print cp

        scene = ExtractionLineScene(canvas=self.canvas)
        self.canvas.scene = scene
        cp = os.path.join(os.path.dirname(p), 'canvas_config.xml')
        scene.load(p, cp)

        self.scene = scene

    #============= EOF =============================================
