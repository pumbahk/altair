var JSONParser = (function() {
  var _JSONParser = {};

  _JSONParser.decode = function(str) {
    var rt;
    eval("rt = "+str);
    return rt;
  };

  _JSONParser.encode = function(obj) {
    var self = _JSONParser.encode;
    var rt;

    var type = Object.prototype.toString.call(obj);
    switch (type) {
    case "[object Object]":
      rt = '{';
      var first = true;
      for (var i in obj) {
        if (obj.hasOwnProperty(i)) {
          rt += ((first) ? '"' : ', "') +i+'":'+self(obj[i]);
          first = false;
        }
      }
      rt += '}';
      break;

    case "[object Array]":
      var m = obj.length;
      rt = '[';
      if (m > 0) {
        rt += self(obj[0]);
        for (var j = 1; j<m; j++) {
          rt += ', ' + self(obj[j]);
        }
      }
      rt += ']';
      break;

    case "[object String]":
      rt = '"' + obj + '"';
      break;

    case "[object Number]":
      rt = obj + '';
      break;

    case "[object Null]":
      rt = 'null';
      break;

    default:
      _error();

    }

    return rt;
  }

  return _JSONParser;

})();