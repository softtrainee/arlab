#============= enthought library imports =======================

#============= standard library imports ========================
import socket
import SocketServer
import select
import sys
#============= local library imports  ==========================


class Server(object):
    def start_server(self, host, port, handler_klass):
        print 'Starting server {} {}'.format(host, port)
        server = SocketServer.TCPServer((host, port), handler_klass)
        server.allow_reuse_address = True
        server.serve_forever()

class LinkServer(object):
    def start_server(self, host, port, handler_klass):
        print 'Link Starting server {} {}'.format(host, port)
#        backlog = 5
#        size = 1024
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(5)
        input = [server, sys.stdin]
        running = 1
#        handler = LinkEmulator()
        handler = handler_klass()
        while running:
            inputready, _outputready, _exceptready = select.select(input, [], [])
            for s in inputready:

                if s == server:
                    # handle the server socket
                    client, _address = server.accept()
                    input.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    _junk = sys.stdin.readline()
                    running = 0

                else:
                    # handle all other sockets

                    handler.request = s
                    data = handler.handle()
                    if data:
                        try:
                            s.send(data)
                        except socket.error:
                            pass
                    else:
                        s.close()
                        input.remove(s)
        server.close()
#============= EOF =============================================
