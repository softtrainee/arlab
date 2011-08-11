#============= enthought library imports =======================
from traits.api import Instance, Button
from traitsui.api import View, Item
from src.managers.manager import Manager

#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
class DBDataManager(Manager):
    database = Instance(DatabaseAdapter)

    #host = DelegatesTo('database')
    #dbname = DelegatesTo('database')
    #password = DelegatesTo('database')
    #user = DelegatesTo('database')
    #kind = DelegatesTo('database')
    #connected = DelegatesTo('database')
    #use_db = DelegatesTo('database')
    importbutton = Button('Import')
    def _importbutton_fired(self):
        self._import_()

    def _import_(self):
        pass


    def traits_view(self):

        v = View(Item('importbutton', show_label = False),
                 Item('database', style = 'custom', show_label = False)
                 )
        return v



#============= EOF ====================================
