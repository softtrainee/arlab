#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from xml_parser import XMLParser
class HWCParser(XMLParser):
    def get_class_attributes(self):
        r = []
        c = self._tree.find('class')
        for a in c.iter('attr'):
            name = a.get('name')
            attr = a.text
            r.append((name, attr))
        return r

    def get_functions(self):
        r = []
        for f in self._tree.iter('func'):
            name = f.find('name').text
            body = 'pass'
            args = 'a'
            args = ', '.join([a.text for a in f.findall('arg')])

            body = '''cmd='{command}'
        resp=self.ask(self._build_command(cmd))
        return self._parse_response(resp)
'''.format(command = f.find('command').text)


            kwargs = ', '
            for kw in f.findall('kwarg'):
                kwargs += '{}={}'.format(kw.get('name'),
                                       kw.text)
            if kwargs == ', ':
                kwargs = ''

            d = dict(name = name,
                   args = args,
                   kwargs = kwargs,
                   body = body
                   )
            r.append(d)

        return r
#============= EOF ====================================
