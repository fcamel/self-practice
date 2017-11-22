#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import optparse

class Result(object):
    def __init__(self, bytes_, time_):
        self.bytes_ = bytes_
        self.time_ = time_

STATE_BEGIN = 0
STATE_SYN1 = 1
STATE_SYN2 = 2
STATE_CONNECTED = 3
STATE_FIN1 = 4
STATE_FIN2 = 5

def error(state, line):
    print('parse errors: state=%d, line=%s' % (state, line))

def parse(port, lines):
    results = []
    state = STATE_BEGIN
    begin_time = None
    bytes_ = 0
    for line in lines:
        line = line.strip()
        tokens = line.split()
        packet_byte = int(tokens[6])
        from_port = int(tokens[7])
        if from_port == port:
            bytes_ += packet_byte

        if state == STATE_BEGIN:
            if 'SYN' in line:
                state = STATE_SYN1
            else:
                error(state, line)
        elif state == STATE_SYN1:
            if 'SYN' in line:
                state = STATE_SYN2
            else:
                error(state, line)
        elif state == STATE_SYN2:
            if 'ACK' in line:
                state = STATE_CONNECTED
            else:
                error(state, line)
            if 'PSH' in line:
                begin_time = float(tokens[1])
        elif state == STATE_CONNECTED:
            if 'PSH' in line and begin_time is None:
                begin_time = float(tokens[1])
            if 'FIN' in line:
                end_time = float(tokens[1])
                results.append(Result(bytes_, end_time - begin_time))
                bytes_ = 0
                begin_time = None

                state = STATE_FIN1
        elif state == STATE_FIN1:
            if 'FIN' in line:
                state = STATE_FIN2
        elif state == STATE_FIN2:
            if 'ACK' in line:
                state = STATE_BEGIN
        else:
            error(state, line)

    return results


def main():
    '''\
    %prog [options] <server-port> <log.txt>
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        return 1

    port = int(args[0])
    results = parse(port, open(args[1]))
    print('bytes sent from port %d:' % port)
    print('\t'.join(str(r.bytes_) for r in results))
    print('duration in seconds from the first send() to the first FIN:')
    print('\t'.join(str(r.time_) for r in results))

    return 0


if __name__ == '__main__':
    sys.exit(main())
