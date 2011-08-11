
#============= enthought library imports =======================

#============= standard library imports ========================
from xml.etree.ElementTree import ElementTree, Element
#============= local library imports  ==========================
class XMLParser(object):
    '''
        wrapper for ElementTree
    '''
    def __init__(self, path, *args, **kw):
        self._path = path
        self._parse_file(path)

    def _parse_file(self, p):
        tree = ElementTree()
        tree.parse(p)
        self._tree = tree
        return tree

    def save(self):
        self.indent(self._tree.getroot())
        self._tree.write(self._path)

    def indent(self, elem, level = 0):
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
        e = Element(tag, attrib = kw)
        e.text = value
        return e
#============= EOF ====================================
