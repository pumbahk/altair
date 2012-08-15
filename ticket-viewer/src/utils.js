function convertToUserUnit(value, unit) {
  if (value === null || value === void(0))
    return null;
  if (typeof value != 'string' && !(value instanceof String)) {
    var degree = value;
    switch (unit || 'px') {
    case 'pt':
      return degree * 1.25;
    case 'pc':
      return degree * 15;
    case 'mm':
      return degree * 90 / 25.4;
    case 'cm':
      return degree * 90 / 2.54;
    case 'in':
      return degree * 90.;
    case 'px':
      return degree;
    }
    throw new Error("Unsupported unit: " + unit);
  }
  var spec = /(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px)?/.exec(value);
  if (!spec)
    throw new Error('Invalid length / size specifier: ' + value)
  return convertToUserUnit(parseFloat(spec[1]), spec[2]);
}

exports.convertToUserUnit = convertToUserUnit;

function serializeStyleDef(obj) {
  var retval = [];
  for (var k in obj) {
    var v = obj[k];
    retval.push(k);
    retval.push(':');
    if (typeof v == 'number' || v instanceof Number) {
      retval.push(v);
    } else if (k == 'font-family') {
      retval.push("'" + v + "'");
    } else {
      retval.push(v);
    }
    retval.push(';');
  }
  return retval.join('');
}

exports.serializeStyleDef = serializeStyleDef;

function parseHtml(html) {
  var parser = new window.DOMParser();
  return parser.parseFromString(html, "text/xml");
}

exports.parseHtml = parseHtml;
