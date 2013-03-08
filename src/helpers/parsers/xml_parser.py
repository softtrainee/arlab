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

#============= standard library imports ========================
from xml.etree.ElementTree import ElementTree, Element, ParseError
from pyface.message_dialog import warning
#============= local library imports  ==========================
class XMLParser(object):
    '''
        wrapper for ElementTree
    '''
    _tree = None
    def __init__(self, path, *args, **kw):
        if path:
            self._path = path
            try:
                self._parse_file(path)
            except ParseError, e:
                warning(None, str(e))


    def _parse_file(self, p):
        tree = ElementTree()
        tree.parse(p)
        self._tree = tree
        return tree
    def get_tree(self):
        return self._tree
    def save(self):
        self.indent(self._tree.getroot())
        self._tree.write(self._path)

    def indent(self, elem, level=0):
        i = '\n' + level * '  '
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def new_element(self, tag, value, ** kw):
        e = Element(tag, attrib=kw)
        e.text = value
        return e
#============= EOF ====================================
