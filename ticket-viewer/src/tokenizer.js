function newScanner(text) {
  var regexp = /"((?:\\.|[^"])*)"|:([^\s"]*)|(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([*+/A-Za-z_-]+)|([ \t]+)|(\r\n|\r|\n)|(.)/g;
  var line = 0;
  var column = 0;
  return {
    do_: function () {
      var retval = null;
      for (;;) {
        var g = regexp.exec(text);
        if (!g)
          return null;
        if (g[1]) {
          retval = ['string', g[1].replace(/\\(.)/g, '$1')];
        } else if (g[2]) {
          retval = ['symbol', g[2]];
        } else if (g[3]) {
          retval = ['number', parseFloat(g[3])];
        } else if (g[4]) {
          retval = ['command', g[4]];
        } else if (g[6]) {
          column = 0;
          line++;
          continue;
        } else if (g[7]) {
          throw new Error("TSE00001: Syntax error at column " + (column + 1) + " line " + (line + 1));
        }
        column += g[0].length;
        if (retval)
          break;
      }
      return retval;
    }
  };
}

exports.newScanner = newScanner;

function tokenize(text) {
  var retval = [];
  var scanner = newScanner(text);
  for (var token = null; token = scanner.do_();) {
    retval.push(token);
  }
  return retval;
}

exports.tokenize = tokenize;
