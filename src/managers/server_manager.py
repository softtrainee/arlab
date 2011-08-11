#============= enthought library imports =======================
from traits.api import List, Instance, Any
from traitsui.api import View, Item, Group, HGroup, VGroup, \
    ListEditor, TableEditor
from traitsui.table_column import ObjectColumn

#============= standard library imports ========================

import os
import ConfigParser
#============= local library imports  ==========================
#from globals import use_shared_memory
#if use_shared_memory:
#    from src.messaging.command_repeater import SHMCommandRepeater as CommandRepeater
#else:

from src.messaging.command_repeater import CommandRepeater

from src.messaging.remote_command_server import RemoteCommandServer

from src.managers.manager import Manager
from src.helpers.paths import initialization_dir

class ServerManager(Manager):
    '''
    '''
    # quit the program if this window is closed
    exit_on_close = True
    servers = List(RemoteCommandServer)
    repeater = Instance(CommandRepeater)
    selected = Any
    def load(self):
        '''
        '''

        names = self.read_configuration()
        if names:
            for s in names:
                e = RemoteCommandServer(name = s,
                               repeater = self.repeater,
                               configuration_dir_name = 'servers',
                               )

                e.bootstrap()
                self.servers.append(e)

    def read_configuration(self):
        '''
        '''

        config = ConfigParser.ConfigParser()
        path = os.path.join(initialization_dir, 'server_initialization.cfg')
        config.read(path)

        servernames = [s.strip() for s in self.config_get(config, 'General', 'servers').split(',')]
        return servernames

    def _repeater_default(self):
        '''
        '''
        c = CommandRepeater(name = 'repeater',
                               configuration_dir_name = 'servers')
        c.bootstrap()
        return c

    def traits_view(self):
        '''
        '''
        cols = [ObjectColumn(name = 'name'),
                ObjectColumn(name = 'klass', label = 'Class'),
                ObjectColumn(name = 'processor_type', label = 'Type'),
              ObjectColumn(name = 'host'),
              ObjectColumn(name = 'port')]
        tservers = Group(Item('servers', style = 'custom',
                      editor = TableEditor(columns = cols,
                                           selected = 'selected',
                                           editable = False),
                      show_label = False,
                      ),
                      show_border = True,
                      label = 'Servers'
                      )
        servers = Item('servers',
                       style = 'custom',
                       editor = ListEditor(use_notebook = True,
                                           page_name = '.name',
                                           selected = 'selected'), show_label = False)
        repeater = Group(Item('repeater', style = 'custom',
                              show_label = False),
                            show_border = True,

                         label = 'Repeater')
        v = View(HGroup(
                 VGroup(tservers, repeater),
                 servers
                 ),
                 title = 'Remote Hardware Server',
                 width = 700,
                 height = 360,
                 resizable = True,
                 handler = self.handler_klass
                 )

        return v

#============= EOF ====================================
