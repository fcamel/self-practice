var Queue = function() {
  this._stack = [];
  this._queue = [];
  this.length = 0;  // O(1) operation.
};

// O(1) operation.
Queue.prototype.push = function(element) {
  this._stack.push(element);
  this.length = this._stack.length + this._queue.length;
};

// O(1) operation (amortized time).
Queue.prototype.pop = function() {
  var ret = undefined;
  if (this._queue.length === 0) {
    while (this._stack.length > 0) {  
      this._queue.push(this._stack.pop());
    }
  }
  if (this._queue.length > 0) {
    ret = this._queue.pop();
    this.length = this._stack.length + this._queue.length;
  }
  return ret;
};


/*
  Test codes:

var q = new Queue();
console.log(q.length, q.pop());
q.push('a');
q.push('b');
q.push('c');
console.log(q.length, q.pop());
q.push('d');
q.push('e');
console.log(q.length, q.pop());
console.log(q.length, q.pop());
q.push('f');
console.log(q.length, q.pop());
console.log(q.length, q.pop());
console.log(q.length, q.pop());
console.log(q.length, q.pop());

*/
