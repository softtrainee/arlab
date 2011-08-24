import socket


import os


def server(kind, addr):
    if kind == 'inet':
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(addr)
        except:
            print 'remove %s' % addr

    s.bind(addr)
    s.listen(1)
#    while 1:
    con, addr = s.accept()
    while 1:
        data = con.recv(1024)
        #print 'rec %s' % data
        if not data:break
        con.send(data)
    con.close()

if __name__ == '__main__':
    addr = '127.0.0.1', 1054
    addr = '/tmp/hardware'
    server('unix', addr)