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

#============= enthought library imports =======================

#============= standard library imports ========================
from src.helpers.xml_parser import XMLParser
#============= local library imports  ==========================


class CanvasParser(XMLParser):
    '''
    '''
#    def get_valves(self, group=None, element=True):
#        return self._get_elements(group, element, 'valve')
##        if group is None:
##            group = self._tree
##        return [v if element else v.text.strip()
##                for v in group.findall('valve')]
#
#    def get_stages(self, group=None, element=True):
#        return self._get_elements(group, element, 'stage')
##        if group is None:
##            group = self._tree
##        return [v if element else v.text.strip()
##                for v in group.findall('stage')]
#
#    def get_connections(self, group=None, element=True):
#        return self._get_elements(group, element, 'connection')
##        if group is None:
##            group = self._tree
##        return [v if element else v.text.strip()
##                for v in group.findall('connection')]
#    def get_spectrometers(self, group=None, element=True):
#        return self._get_elements(group, element, 'spectrometer')
#
#    def get_turbos(self, group=None, element=True):
#        return self._get_elements(group, element, 'turbo')
#
#    def get_labels(self, group=None, element=True):
#        return self._get_elements(group, element, 'label')
#
#    def get_getters(self, group=None, element=True):
#        return self._get_elements(group, element, 'getter')

    def get_elements(self, name):
        return self._get_elements(None, True, name)

    def _get_elements(self, group, element, name):
        if group is None:
            group = self._tree
        return [v if element else v.text.strip()
                for v in group.findall(name)]

#============= EOF ====================================
