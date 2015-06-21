var express = require('express');
var app = express();

var error = {
  ok: 0,
  invalid_input: 1,
};

var g_cache = {};

app.get('/set', function (req, res) {
  var key = req.query.key;
  var value = req.query.value;
  if (key === undefined || value === undefined) {
    res.send(JSON.stringify({
      error_code: error.invalid_input
    }));
    return;
  }

  if (!(key in g_cache)) {
    g_cache[key] = {};
  }

  var entry = g_cache[key];
  entry.value = value;
  if ('callbacks' in entry) {
    var cbs = entry.callbacks;
    for (var i = 0; i < cbs.length; i++) {
      cbs[i]();
    }
    while (cbs.length > 0) {
      cbs.pop();
    }
  }
  res.send(JSON.stringify({
    error_code: error.ok
  }));
});


app.get('/get', function (req, res) {
  var key = req.query.key;
  if (key === undefined) {
    res.send(JSON.stringify({
      error_code: error.invalid_input
    }));
    return;
  }

  if (!(key in g_cache)) {
    g_cache[key] = {};
  }

  var entry = g_cache[key];
  if ('value' in entry) {
    res.send(JSON.stringify({
      error_code: error.ok,
      value: entry.value
    }));
  } else {
    if (!('callbacks' in entry)) {
      entry.callbacks = [];
    }
    entry.callbacks.push(function() {
      res.send(JSON.stringify({
        error_code: error.ok,
        value: entry.value
      }));
    });
  }
});

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;
  console.log('web server for long polling listening at http://%s:%s', host, port);
});
