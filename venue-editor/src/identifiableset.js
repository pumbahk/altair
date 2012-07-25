var IdentifiableSet = exports.IdentifiableSet = function IdentifiableSet(options) {
  this.idAttribute = options && options.idAttribute || 'id';
  this.items = {};
  this.length = 0;
};

IdentifiableSet.prototype.add = function IdentifiableSet_add(item) {
  var id = item[this.idAttribute];
  if (!(id in this.items)) {
    this.items[id] = item;
    this.length++;
    return true;
  } else {
    return false;
  }
};

IdentifiableSet.prototype.remove = function IdentifiableSet_remove(item) {
  var id = item[this.idAttribute];
  if (id in this.items) {
    delete this.items[id];
    this.length--;
    return true;
  } else {
    return false;
  }
};

IdentifiableSet.prototype.contains = function IdentifiableSet_contains(item) {
  return item[this.idAttribute] in this.items;
};

IdentifiableSet.prototype.clear = function IdentifiableSet_clear() {
  this.items = {};
  this.length = 0;
};

IdentifiableSet.prototype.each = function IdentifiableSet_each(f) {
  for (var id in this.items)
    f(this.items[id]);
};

/*
 * vim: sts=2 sw=2 ts=2 et
 */
