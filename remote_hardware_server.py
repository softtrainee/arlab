#!/Library/Frameworks/Python.framework/Versions/Current/bin/python
#============= enthought library imports =======================
#============= standard library imports ========================
import os
import sys
#============= local library imports  ==========================
#add src to the path
root = os.path.basename(os.path.dirname(__file__))
if 'pychron' not in root:
    root = 'pychron'
src = os.path.join(os.path.expanduser('~'),
                   'Programming',
                   root
                   )
sys.path.append(src)

from src.helpers.logger_setup import setup
from src.managers.server_manager import ServerManager

if __name__ == '__main__':
    '''
        use a Server Manager
    '''


    setup('server')
    s = ServerManager()
    s.load()
    s.configure_traits()

#    launch()
#============= EOF ====================================
#
#def read_configuration():
#    '''
#         read the server initialization file in the initialization dir. 
#         
#         ex
#         [General]
#         servers= server_names
#         
#         server names refer to server configuration files
#    '''
#
#    config = ConfigParser.ConfigParser()
#    path = os.path.join(initialization_dir, 'server_initialization.cfg')
#    config.read(path)
#
#    servernames = config.get('General', 'servers').split(',')
#    return servernames
#
#def launch():
#    '''
#    
#    launch the application
#
#    '''
#
#    #create a new CommandRepeater to repeat commands to the ExtractionLine Program on
#    #on the specified port
#    repeater = CommandRepeater(name = 'repeater',
#                              configuration_dir_name = 'servers'
#                              )
#    repeater.bootstrap()
#
#    servers = []
#    for server_name in read_configuration():
#        
#        #create a new RemoteCommandServer to handle TCP or UDP Protocol based commands
#        e = RemoteCommandServer(name = server_name,
#                               repeater = repeater,
#                               configuration_dir_name = 'servers',
#                               )
#
#        e.bootstrap()
#        servers.append(e)
#
#    try:
#        while 1:
#        #serve infinitely
#            pass
#    except KeyboardInterrupt:
#        for s in servers:
#            if s is not None:
#                s._server.shutdown()
#        os._exit(0)
