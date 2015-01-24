import multiprocessing
import sys
import os
import Queue

import requests
import lxml
import lxml.html


DEBUG = False

MAX_ALL_RATINGS = 1000
N_PROCESS = 20


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

def _get_app_name(root):
    try:
        return list(root.cssselect('.document-title')[0])[0].text
    except Exception, e:
        return ''

def _get_ratings(root):
    try:
        ratings = [int(s.text.replace(',', ''))
                   for s in root.cssselect('.bar-number')]
    except Exception, e:
        return [0] * 5
    return ratings

def _get_similar_apps(root):
    try:
        cs = root.cssselect('.rec-cluster')[0].cssselect('.card-click-target')
    except Exception, e:
        return set()
    return set('https://play.google.com%s' % c.attrib['href'] for c in cs)

class ScopeLock(object):
    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, type, value, traceback):
        self._lock.release()

def _do_parse_url(lock, queue, s_all_ratings, s_active_workers, has_increased_active_workers):
    while True:
        msg = ('pid=%d: queue.get() (#=%df), all_ratings=%d\n'
               '' % (os.getpid(), queue.qsize(), len(s_all_ratings)))
        sys.stderr.write(msg)
        url = queue.get()
        msg = 'pid=%d: url=%s\n' % (os.getpid(), url)
        sys.stderr.write(msg)
        if url is None:
            break

        with ScopeLock(lock):
            s_active_workers.value += 1
            has_increased_active_workers = True

        root = _get_web_page(url)
        app_name = _get_app_name(root)
        ratings = _get_ratings(root)
        links = _get_similar_apps(root)

        with ScopeLock(lock):
            s_all_ratings[url] = [app_name, ratings]

        for link in links:
            with ScopeLock(lock):
                if len(s_all_ratings) + queue.qsize() > MAX_ALL_RATINGS:
                    break
                if link not in s_all_ratings:
                    queue.put(link)

        with ScopeLock(lock):
            s_active_workers.value -= 1
            has_increased_active_workers = False

def _parse_url(lock, queue, s_all_ratings, s_active_workers):
    has_increased_active_workers = False
    try:
        _do_parse_url(lock, queue, s_all_ratings, s_active_workers, has_increased_active_workers)
    except Exception, e:
        pass
    if has_increased_active_workers:
        # Must reset the state; otherwise, the main process won't stop.
        with ScopeLock(lock):
            s_active_workers.value -= 1


def _put_links(queue, app_links):
    for link in app_links:
        msg = 'pid=%d: put link=%s\n' % (os.getpid(), link)
        sys.stderr.write(msg)
        queue.put(link)

def get_app_review_in_parallel(app_links):
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    all_ratings = manager.dict()
    active_workers = manager.Value('i', 0)
    queue = manager.Queue()

    # Use a separated process to not block the main process.
    # Note that queue.put() may be blocked if the queue is full.
    init_producer = multiprocessing.Process(
        target=_put_links, args=(queue, app_links))
    init_producer.start()

    # Start workers (consumer & producer).
    processes = []
    for i in xrange(N_PROCESS):
        args = (lock, queue, all_ratings, active_workers)
        p = multiprocessing.Process(target=_parse_url, args=args)
        p.start()
        processes.append(p)

    # Wait the init producer to stop.
    init_producer.join()

    # Wait all workers (consumer & producer) to stop.
    while processes:
        for p in list(processes):
            if not p.is_alive():
                processes.remove(p)
                continue

            msg = (
                'pid=%d: main: # of process=%d, queue.qsize=%d, '
                'active_workers=%d, # of all_ratings=%d\n'
                '' % (os.getpid(), len(processes), queue.qsize(),
                      active_workers.value, len(all_ratings))
            )
            sys.stderr.write(msg)
            p.join(0.1)

            if queue.empty() and not active_workers.value:
                # No input. Ask all processes to stop.
                for _ in xrange(len(processes)):
                    queue.put(None)

    return all_ratings

if __name__ == '__main__':
    seed_urls = [
        'https://play.google.com/store/apps/details?id=com.cloudmosa.puffinFree&hl=en'
    ]

    all_ratings = get_app_review_in_parallel(seed_urls)
    for url, value in all_ratings.items():
        app_name, ratings = value
        ss = [app_name, url] + map(str, ratings)
        print (u'\t'.join(ss)).encode('utf8')
