#!/usr/bin/env python
# -*- encoding: utf8 -*-

import csv
import codecs
import sys
import optparse
import os


class Review(object):
    def __init__(self, version, language, created_time, last_updated_time, stars, title, text, link):
        if not version:
            version = 0
        self.version = int(version)
        self.language = language
        self.created_time = int(created_time)
        self.last_updated_time = int(last_updated_time)
        self.stars = int(stars)
        self.title = title
        self.text = text
        self.link = link

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        return u'%s: %s' % (self.title, self.text)


def parse_logs(lines):
    '''
    |lines|: an iterator with unicode object.
    '''
    # The module csv expects the input is a file object
    # with content in utf-8 format. Need to convert |lines|.
    cr = csv.reader(line.encode('utf-8') for line in lines)
    result = []
    for line in cr:
        (pkg_name, version, language, device, _, created_time,
         _, last_updated_time, stars, title, text, _, _, _, link) = line
        if pkg_name == 'Package Name':
            # Skip the first line.
            continue
        if not title and not text:
            continue
        row = [version, language, created_time, last_updated_time, stars, title, text, link]
        row = [c.decode('utf-8') for c in row]
        result.append(Review(*row))
    return result

def parse_logs_by_filename(filename):
    # Python built-in csv module cannot handle utf-16.
    # Need to convert decode utf-16 first.
    f = codecs.open(filename, 'rU', 'utf-16')
    return parse_logs(f)

def main():
    '''\
    %prog [options] <directory>

    <directory>: the directory store reviews (in CSV format) fetched from Google Play.
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 1

    dir = args[0]
    all_reviews = []
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        rs = parse_logs_by_filename(path)
        all_reviews.extend(rs)

    # Count stars by versions.
    stars = {}
    for r in all_reviews:
        v = r.version
        if not v:
            continue
        if v not in stars:
            stars[v] = []
        stars[v].append(r.stars)

    result = [(v, sum(ss) / float(len(ss)), len(ss)) for v, ss in stars.items()]
    result.sort()
    print 'Stars of reiviews'
    print '-' * 60
    for v, s, n in result:
        print '%7s: %.1f (%5d reviews)' % (v, s, n)
    last_version = v

    # Count special words in reviews
    tmp = [r for r in all_reviews
           if r.language == 'en' and r.title and r.text and r.version == last_version]
    observered_words = [
        'crash',
        'freeze',
    ]

    counts = {}
    for w in observered_words:
        counts[w] = 0
    for r in tmp:
        title = r.title.lower()
        text = r.text.lower()
        for w in observered_words:
            if w in title or w in text:
                counts[w] += 1

    result = [(n, k) for k, n in counts.items()]
    result.sort(reverse=True)
    print '\nIssues'
    print '-' * 60
    for n, w in result:
        print '%10s: %5d' % (w, n)

    return 0

if __name__ == '__main__':
    sys.exit(main())
