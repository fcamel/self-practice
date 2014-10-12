#!/usr/bin/env python
# -*- encoding: utf8 -*-

'''
Show recent popular movies with IMDB scores.

Practice:
* Download web content by requests.
* Extract html content by lxml CSS path.
* Using multiprocessing to download web pages concurrently.
'''

import datetime
import sys
import optparse
import multiprocessing
import urllib

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
        return lxml.html.fromstring(u'')

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

    search_url = ('http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=tt'
                  '' % urllib.quote(query_name.encode('utf8')))
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
                         '' % (query_name, search_url, str(e)))
        return '', ''

def _get_imdb_score(link, dom):
    if not link:
        return -1.0

    try:
        target = dom.cssselect('.star-box-giga-star')[0]
        return float(target.text)
    except Exception, e:
        sys.stderr.write('ERROR: _get_imdb_score_by_dom: link=%s e=%s\n' % (link, e))
        return -1.0

# A simple check about whether this movie is what we're looking for.
# If it's not released in this or last year, it probably is not our target.
# Test case:
# * 桃蛙源記    The Frogville
# * 迴光奏鳴曲  Exit
def _verify_movie(chinese_name, english_name, dom):
    this_year = int(datetime.datetime.now().strftime('%Y'))
    try:
        tmp = dom.cssselect('#title-overview-widget .header .nobr')[0]
        target = tmp.getchildren()[0]
        year = int(target.text)
        return year == this_year or year == this_year - 1
    except Exception, e:
        sys.stderr.write('ERROR: _verify_movie: chinese_name=%s english_name=%s e=%s\n'
                         '' % (chinese_name, english_name, e))
        return False

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

def _get_movie(chinese_name, link):
    english_name = _get_english_name(link)
    _, imdb_link = _get_imdb_link(english_name)
    dom = _get_web_page(imdb_link)
    if _verify_movie(chinese_name, english_name, dom):
        score = _get_imdb_score(link, dom)
    else:
        score = -1.0
        imdb_link = ''
    return Movie(chinese_name, english_name, score, imdb_link)

def _get_movies(popular_movies):
    result = []
    for chinese_name, link in popular_movies:
        print 'Processing %s ...' % chinese_name.encode('utf8'),
        movie = _get_movie(chinese_name, link)
        print ' score=%.1f' % movie.score
        result.append(movie)
    return result

def _get_movie_and_save_in_queue(row):
    chinese_name, link, queue = row
    print 'Processing %s ...' % chinese_name.encode('utf8'),
    movie = _get_movie(chinese_name, link)
    print ' score=%.1f' % movie.score
    queue.put(movie)


def _get_movies_in_parallel(popular_movies):
    manager = multiprocessing.Manager()
    pool = multiprocessing.Pool(processes=10)
    queue = manager.Queue()
    data = [(chinese_name, link, queue) for chinese_name, link in popular_movies]
    pool.map(_get_movie_and_save_in_queue, data)
    result = []
    while not queue.empty():
        result.append(queue.get())
    return result

def print_text(result):
    for movie in result:
        out = ('%.1f: %s (%s) %s'
               '' % (movie.score, movie.chinese_name,
                     movie.english_name, movie.imdb_link))
        print out.encode('utf8')

def print_html(result, filename):
    with open(filename, 'w') as fw:
        updated_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        fw.write('''<!DOCTYPE>
<html>
<head>
<title>台灣近期電影排行榜 (依IMDB分數)</title>
<meta content="text/html; charset=UTF-8" http-equiv="Content-Type"/>
<style>
th, td {
    border: 1px solid grey;
}
.heading {
    background-color: orange;
}
.odd {
    background-color: rgb(190, 216, 190);
}
.even {
    background-color: rgb(255, 255, 255);
}
</style>
</head>
<body>
<h4>最後更新時間: %s</h4>
<table>\n''' % updated_time)
        fw.write('<tr class="heading"><th>中文片名</th><th>英文片名</th><th>IMDB 分數</th></tr>\n')
        cls = 'odd'
        for movie in result:
            out = ('<tr class="%s"><td>%s</td><td>%s</td><td><a href="%s">%.1f</a></td></tr>'
                   '' % (cls, movie.chinese_name, movie.english_name,
                         movie.imdb_link, movie.score))
            fw.write(out.encode('utf8') + '\n')
            cls = 'even' if cls == 'odd' else 'odd'
        fw.write('''</table>
</body>
</html>\n''')


def main():
    '''\
    %prog [options]
    '''
    parser = optparse.OptionParser(usage=main.__doc__)
    parser.add_option('-H', '--html', dest='html',
                      type='string', default='',
                      help='Output in HTML format to the target file.')
    options, args = parser.parse_args()

    if len(args) != 0:
        parser.print_help()
        return 1

    popular_movies = _get_popular_movies()
    #result = _get_movies(popular_movies)
    result = _get_movies_in_parallel(popular_movies)
    result.sort()
    print '\n---- DONE ----\n'
    if options.html:
        print_html(result, options.html)
    else:
        print_text(result)
    return 0


if __name__ == '__main__':
    sys.exit(main())
