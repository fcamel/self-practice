#!/usr/bin/env python
# -*- encoding: utf8 -*-

import socket
import sys
import optparse
import os


def process(sock):
    while True:
        raw_data = sock.recv(65536)
        print '[server] get data: %s' % raw_data
        try:
            vol = int(raw_data)
        except Exception, e:
            print '[server] %s is not a number. End this connection.' % raw_data
            break

        print '[server] will set volume to %d.' % vol
        os.system('nircmd setsysvolume %d' % vol)
        print '[server] did set volume to %d.' % vol
    print '[server] did end connection.'

def start(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('0.0.0.0', port))
    serversocket.listen(5)

    while True:
        print '[server] waiting for next connection'
        (clientsocket, address) = serversocket.accept()
        print '[server] get a new connection'
        clientsocket.settimeout(5.0)  # 5s
        process(clientsocket)


def main():
    '''\
    %prog [options] <port>
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 1

    try:
        port = int(args[0])
    except Exception, e:
        print '%s is not a number' % args[0]
        return 1

    start(port)

    return 0


if __name__ == '__main__':
    sys.exit(main())
