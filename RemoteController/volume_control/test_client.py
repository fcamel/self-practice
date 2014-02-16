#!/usr/bin/env python
# -*- encoding: utf8 -*-

import socket
import sys
import time
import optparse
import os

def start(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', port))

    for i in range(0, 65536, 1000):
        print 'i: %d' % i
        sock.send(str(i))
        time.sleep(1)


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
