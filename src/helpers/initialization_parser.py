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
#============= standard library imports ========================
#============= local library imports  ==========================

class InitializationParser(XMLParser):
    def add_plugin(self, category, name):
        tree = self._tree

        cat = tree.find(category)
        cat.append(self.new_element('plugin', name, enabled='false'))
        self.save()

    def get_plugins(self, category=None, all=False):
        tree = self._tree

        if category:
            cat = tree.find(category)
            if cat is not None:
                plugins = cat.findall('plugin')
        else:
            try:
                plugins = tree.iter(tag='plugin')
            except AttributeError:
                plugins = tree.getiterator(tag='plugin')

        return [p.text.strip() for p in plugins if all or p.get('enabled').lower() == 'true']

    def get_plugins_as_elements(self, category):
        tree = self._tree

        cat = tree.find(category)
        return cat.findall('plugin')

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

    def enable_device(self, name, manager):

        dev = self.get_device(manager, name, True, element=True)
        if dev is None:
            dev = self.get_device(manager, name, False, element=True)

        dev.set('enabled', 'true')
        self.save()

    def disable_device(self, name, manager):
        dev = self.get_device(manager, name, True, element=True)
        if dev is None:
            dev = self.get_device(manager, name, False, element=True)

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

    def get_device(self, manager, name, plugin, element=False):
        if plugin is None:
            man = self.get_plugin(manager)
        else:
            man = self.get_manager(manager, plugin)

        dev = next((d for d in man.findall('device') if d.text.strip() == name), None)
        if not element and dev:
            dev = dev.text.strip()
        return dev

    def get_devices(self, manager, all=False, element=False):
        return [d if element else d.text.strip()  for d in manager.findall('device')
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

        return self._get_element(category, name)

    def get_manager(self, name, plugin):

        if 'Manager' in plugin:
            plugin = plugin.replace('Manager', '')
        p = self.get_plugin(plugin)

        man = next((pi for pi in p.findall('manager') if pi.text.strip() == name), None)

        return man

    def _get_element(self, category, name, tag='plugin'):
        tree = self._tree
        if category is None:
            for p in tree.iter(tag=tag):
                if p.text.strip() == name:
                    return p
        else:
            cat = tree.find(category)
            for plugin in cat.findall(tag):
                if plugin.text.strip() == name:
                    return plugin
#============= EOF =============================================
