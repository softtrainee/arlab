#============= enthought library imports =======================
from traits.api import Any, List, HasTraits, Bool, Str, on_trait_change
from traitsui.api import View, Item, TableEditor, ListEditor
from apptools.preferences.ui.api import PreferencesPage
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.helpers.paths import setup_dir
from src.helpers.initialization_parser import InitializationParser
class Plugin(HasTraits):
    '''
    '''
    name = Str
    enabled = Bool
    category = Str

class PluginCategory(HasTraits):
    plugins = List
    name = Str
    parser = Any

    @on_trait_change('plugins:enabled')
    def _update(self, obj, name, old, new):
        '''
        '''
        parser = self.parser
        if obj.enabled:
            parser.enable_plugin(obj.name, category = obj.category)
        else:
            parser.disable_plugin(obj.name, category = obj.category)

    def traits_view(self):
        cols = [
                CheckboxColumn(name = 'enabled'),
                ObjectColumn(name = 'name', editable = False)]
        editor = TableEditor(columns = cols)

        return View(Item('plugins', editor = editor, show_label = False))

class PychronWorkbenchPreferencesPage(PreferencesPage):
    '''
    '''
    categories = List(transient = True)
    preferences_path = 'pychron.workbench'
    name = 'Plugins'

    def __init__(self, *args, **kw):
        super(PychronWorkbenchPreferencesPage, self).__init__(*args, **kw)
        p = os.path.join(setup_dir, 'initialization.xml')
        self.parser = InitializationParser(p)

    def _categories_default(self):
        '''
        '''
        parser = self.parser
        cats = []
        for g in parser.get_groups():
            ps = parser.get_plugins_as_elements(g)
            plugins = []
            for pi in ps:
                plugin = Plugin(name = pi.text.strip(),
                              enabled = True if pi.get('enabled').lower() == 'true' else False,
                              category = g
                              )
                plugins.append(plugin)

            cat = PluginCategory(name = g.capitalize(),
                                 plugins = plugins,
                                 parser = self.parser
                                 )
            cats.append(cat)

        return cats


    def traits_view(self):
        '''
        '''
        editor = ListEditor(use_notebook = True,
                            dock_style = 'tab',
                            page_name = '.name'
                            )
        v = View(Item('categories', editor = editor,
                       show_label = False,
                       style = 'custom'
                       ))
        return v
#============= views ===================================
#============= EOF ====================================
