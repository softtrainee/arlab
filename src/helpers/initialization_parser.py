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
from xml_parser import XMLParser
import os
from src.helpers.paths import setup_dir
#============= standard library imports ========================
#============= local library imports  ==========================


class InitializationParser(XMLParser):
    def __init__(self, *args, **kw):
        p = os.path.join(setup_dir, 'initialization.xml')
        super(InitializationParser, self).__init__(p, *args, **kw)

    def add_plugin(self, category, name):

        tree = self._tree

        cat = tree.find(category)
        cat.append(self.new_element('plugin', name, enabled='false'))
        self.save()

    def get_plugins(self, category=None, all=False, element=False):
        tree = self._tree.find('plugins')
        print tree, category, all, element
        if category:
            cat = tree.find(category)
            if cat is not None:
                plugins = cat.findall('plugin')
        else:
            try:
                plugins = tree.iter(tag='plugin')
            except AttributeError:
                plugins = tree.getiterator(tag='plugin')

        return [p if element else p.text.strip()
                for p in plugins if all or p.get('enabled').lower() == 'true']

#    def get_plugins_as_elements(self, category):
#        tree = self._tree.find('plugins')
#        cat = tree.find(category)
#        if cat is not None:
#            return cat.findall('plugin')

    def get_plugin_groups(self):
        elem = self._tree.find('plugins')
        return [t.tag for t in list(elem)]

    def get_groups(self):
        tree = self._tree
        root = tree.getroot()
        return [t.tag for t in list(root)]

    def enable_manager(self, name, parent):
        plugin = self.get_plugin(parent)
        man = next((m for m in plugin.findall('manager') if m.text.strip() == name), None)
        man.set('enabled', 'true')
        self.save()

    def disable_manager(self, name, parent):
        plugin = self.get_plugin(parent)
        man = next((m for m in plugin.findall('manager') if m.text.strip() == name), None)
        man.set('enabled', 'false')
        self.save()

    def enable_device(self, name, plugin):
        dev = self.get_device(plugin, name, None, element=True)
        dev.set('enabled', 'true')
        self.save()

    def disable_device(self, name, plugin):
        dev = self.get_device(plugin, name, None, element=True)
        dev.set('enabled', 'false')
        self.save()

    def enable_plugin(self, name, category=None):
        plugin = self.get_plugin(name, category)
        plugin.set('enabled', 'true')
        self.save()

    def disable_plugin(self, name, category=None):
        plugin = self.get_plugin(name, category)
        plugin.set('enabled', 'false')
        self.save()

    def get_flags(self, manager, **kw):
        return self._get_paramater(manager, 'flag', **kw)

    def get_device(self, manager, devname, plugin, element=False):

        if plugin is None:
            man = self.get_plugin(manager)
        else:
            man = self.get_manager(manager, plugin)

        dev = next((d for d in man.findall('device')
                    if d.text.strip() == devname), None)
        if not element and dev:
            dev = dev.text.strip()
        return dev

    def get_devices(self, manager, **kw):
        return self._get_paramater(manager, 'device', **kw)

    def get_processor(self, manager, **kw):
        p = self._get_paramater(manager, 'processor', **kw)
        if p:
            return p[0]

    def get_processors(self):
#        ps = []
#        for p in self.get_plugins('Hardware'):
#            pp = self.get_processor(p)
#            if pp:
#                ps.append(pp)
        return [pi for pi in [self.get_processor(p)
                    for p in self.get_plugins('hardware', element=True)] if pi]

    def _get_paramater(self, subtree, tag, all=False, element=False):
        return [d if element else d.text.strip()
                for d in subtree.findall(tag)
                    if all or d.get('enabled').lower() == 'true']

    def get_managers(self, elem, all=False, element=False):
        return [m if element else m.text.strip()
                for m in elem.findall('manager')
                               if all or m.get('enabled').lower() == 'true']

    def get_plugin(self, name, category=None):
        if '_' in name:

            if 'co2' in name:
                name = name.split('_')[0].capitalize() + 'CO2'
            else:
                name = ''.join([a.capitalize() for a in name.split('_')])
        else:
            name = name[0].upper() + name[1:]

        return self._get_element(category, name)

    def get_manager(self, name, plugin):

        if 'Manager' in plugin:
            plugin = plugin.replace('Manager', '')
        p = self.get_plugin(plugin)

        man = next((pi for pi in p.findall('manager') if pi.text.strip() == name), None)

        return man

    def _get_element(self, category, name, tag='plugin'):
        tree = self._tree.find('plugins')
        if category is None:
            for p in tree.iter(tag=tag):
                if p.text.strip() == name:
                    return p
        else:
            cat = tree.find(category)
            for plugin in cat.findall(tag):
                if plugin.text.strip() == name:
                    return plugin

    def get_systems(self):
        p = self.get_plugin('ExtractionLine')
        return [(s.text.strip(), s.get('master_host')) for s in p.findall('system')]

#    def get_processors(self):
#
#        cat = self._tree.find('remotehardware')
#        pi = None
#        if cat is not None:
#            pi = cat.findall('processor')
#
#        return [pii.text.strip() for pii in (pi if pi else [])]
#============= EOF =============================================
