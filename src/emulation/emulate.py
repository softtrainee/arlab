'''
Pychron_beta Package contains

G{packagetree }

'''

import sys
from src.emulation.emulation_server import LinkServer, Server
from src.emulation.emulator import LinkHandler, BaseHandler
def start_emulation():
    args = sys.argv[1:]

    portn = 1059
    if len(args) == 1:
        portn = int(args[0])

    s = Server()
    s.start_server('localhost', portn, BaseHandler)

#    ls = LinkServer()
#    ls.start_server('localhost', 1070, LinkHandler())

if __name__ == '__main__':
    start_emulation()
