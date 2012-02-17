'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from src.helpers.xml_parser import XMLParser

class SceneParser(XMLParser):
    def _get_top(self):
        return self._tree.find('extraction_line')

    def get_sections(self):
        el = self._get_top()
        return el.findall('section')

    def get_valves(self, section):
        return section.findall('valve')

    def get_bellows(self, section):
        return section.findall('bellows')

    def get_spectrometers(self):
        return self._get_components('spectrometer')

    def get_swcs(self):
        return self._get_components('swc')

    def get_turbos(self):
        return self._get_components('turbo')

    def get_elbows(self):
        return self._get_components('elbow')

    def get_flexes(self):
        return self._get_components('flex')

    def get_show_origin(self):
        elem = self._tree.find('view')

        a = elem.get('show_origin')
        so = False
        if a is not None:
            so = True if a.lower() == 'true' else False

        return so

    def get_show_grid(self):
        elem = self._tree.find('view')
        a = elem.get('show_grid')

        so = False
        if a is not None:
            so = True if a.lower() == 'true' else False

        return so


    def _get_components(self, name):
        el = self._get_top()
        return el.findall(name)
#============= EOF ============================================

