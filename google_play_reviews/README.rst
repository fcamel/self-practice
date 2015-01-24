Usage
=====

analyze_reviews.py
------------------
Goal: fetch reviews and find out hot keywords.
http://fcamel-life.blogspot.tw/2015/01/app-google-play.html


cluster ratings
---------------
( crawl_ratings.py, cluster.py, cluster_ratings.py )

Goal: cluster ratings of similar apps and see which apps
have similar ratings.

1. crawl:
# Update __main__ in crawl_ratings.py
# Then run it.
$ python crawl_ratings.py > in

2. cluster:
$ python cluster_ratings in 2

For example:
$ python cluster_ratings example.in 2
