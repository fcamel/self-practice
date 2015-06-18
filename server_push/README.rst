About
-----
Implement server push by long polling using tornado.
The server supports the following API:
* /get: use long polling.
* /set
* /clear

See push_test.py to learn the API details.


How to run
----------

Run the server listens to port 8888::

  $ python push.py


Run test
--------

After starting the server, run the test by::

  $ python push_test.py

