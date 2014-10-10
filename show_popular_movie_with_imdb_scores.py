#!/usr/bin/env python
# -*- encoding: utf8 -*-

import sys
import optparse
import requests
import lxml.html

DEBUG = False

class Movie(object):
    def __init__(self, chinese_name, english_name, score, imdb_link):
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.score = score
        self.imdb_link = imdb_link

    # The highest score is the first.
    def __cmp__(self, other):
        return cmp(other.score, self.score)


def _get_web_page(link):
    if not link:
        return u''
    try:
        r = requests.get(link)
        content = r.content.decode('utf8')
        if DEBUG:
            sys.stderr.write('Get content of link %s: %s' % (link, content[:50]))
        return lxml.html.fromstring(content)
    except Exception, e:
        if DEBUG:
            sys.stderr.write('Fail to get content of link: %s' % link)
        return u''

def _get_text_and_link(element):
    name = element.text.strip()
    link = ''
    for attr, value in element.items():
        if attr.lower() == 'href':
            link = value
            break
    return name, link

def _get_imdb_link(query_name):
    if not query_name:
        return '', ''

    search_url = 'http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=tt' % query_name.replace(' ', '+')
    try:
        dom = _get_web_page(search_url)
        rs = dom.cssselect('.result_text')
        r = rs[0]
        target = r.getchildren()[0]
        name, link = _get_text_and_link(target)
        if link and link.startswith('/'):
            link = 'http://www.imdb.com' + link
        return name, link
    except Exception, e:
        sys.stderr.write('ERROR: _get_imdb_link: query_name=%s search_url=%s e=%s\n'
                         '' % (query_name, search_url, e))
        return '', ''

def _get_imdb_score(link):
    if not link:
        return -1.0

    try:
        dom = _get_web_page(link)
        target = dom.cssselect('.star-box-giga-star')[0]
        return float(target.text)
    except Exception, e:
        sys.stderr.write('ERROR: _get_imdb_score: link=%s e=%s\n' % (link, e))
        return -1.0

def _get_popular_movies():
    link_prefix = 'http://app.atmovies.com.tw/movie/'
    weekend_link = link_prefix + 'movie.cfm?action=boxoffice&bo_code=TWWeekend'
    dom = _get_web_page(weekend_link)
    rs = dom.cssselect('.at11')
    result = []
    for r in rs:
        try:
            target = r.getchildren()[0]
            name, link = _get_text_and_link(target)
            if not link.startswith('http'):
                link = link_prefix + link
            result.append((name, link))
        except Exception, e:
            if DEBUG:
                sys.stderr.write('Fail to get the data: %s' % e)
    return result

def _get_english_name(link):
    try:
        dom = _get_web_page(link)
        rs = dom.cssselect('.at12b_gray')
        target = rs[0]
        return target.text
    except Exception, e:
        return ''

def main():
    '''\
    %prog [options]
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 1

    result = []
    popular_movies = _get_popular_movies()
    for chinese_name, link in popular_movies:
        print u'Processing %s ...' % chinese_name,
        english_name = _get_english_name(link)
        name, imdb_link = _get_imdb_link(english_name)
        score = _get_imdb_score(imdb_link)
        print ' score=%.1f' % score
        result.append(Movie(chinese_name, english_name, score, imdb_link))

    result.sort()
    for movie in result:
        print (u'%.1f: %s (%s) %s'
               '' % (movie.score, movie.chinese_name,
                     movie.english_name, movie.imdb_link))

    return 0


if __name__ == '__main__':
    sys.exit(main())

