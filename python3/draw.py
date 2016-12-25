# Require Python 3.5

import sys
import optparse
import random
import typing

def draw(t: int, n: int, k: int) -> bool:
    '''
    Given |n| items, draw |t| times and return True if there are at least |k| different items.
    '''
    result = set()
    for _ in range(t):
        result.add( random.randrange(0, n) )
    return len(result) >= k

def test(nround: int, t: int, n: int, k: int) -> float:
    '''
    Try |nround| rounds and return the percentage of success.
    Each round is successful if there are at least |k| different items among |n| items
    by drawing |t| times.
    '''
    success = 0
    for _ in range(nround):
        success += int(draw(t, n, k))
    return float(success) / nround

def main() -> int:
    '''\
    %prog [options] <nround> <ntimes> <nitem> <kitem>

    Try |nround| rounds and print the percentage of success.
    Each round is successful if there are at least |kitem| different items among |nitem| items
    by drawing |ntime| times.

    Example of usage:

        # Based on 10000 trials, the success rate is 90% that
        # you'll have at least 3 different items among 5 by drawing 5 times
        $ python3 draw.py 10000 5 5 3
        0.9010

        # Based on 10000 trials, the success rate is 42% that
        # you'll have at least 4 different items among 5 by drawing 5 times
        $ python3 draw.py 10000 5 5 4
        0.4221

        # Based on 10000 trials, the success rate is 94% that
        # you'll have at least 4 different items among 5 by drawing 5 times
        $ python3 draw.py 10000 10 5 4
        0.9398

        # Based on 10000 trials, the success rate is 52% that
        # you'll have at least 4 different items among 5 by drawing 5 times
        $ python3 draw.py 10000 10 5 5
        0.5205

        # Based on 10000 trials, the success rate is 94% that
        # you'll have at least 4 different items among 5 by drawing 5 times
        $ python3 draw.py 10000 20 5 5
        0.9422
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 4:
        parser.print_help()
        return 1

    new_args = map(int, args)
    percentage = test(*new_args)
    print("%.04f" % percentage)

    return 0


if __name__ == '__main__':
    sys.exit(main())
