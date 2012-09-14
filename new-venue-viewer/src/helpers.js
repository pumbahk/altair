var parseCSSStyleText = (function () {
  var regexp_for_styles = /\s*(-?(?:[_a-z\u00a0-\u10ffff]|\\[^\n\r\f#])(?:[\-_A-Za-z\u00a0-\u10ffff]|\\[^\n\r\f])*)\s*:\s*((?:(?:(?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+|"(?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*"|'(?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*')(?:\s+|(?=;|$)))+)(?:;|$)/g;
  var regexp_for_values = /(?:((?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+)|"((?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)"|'((?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)')(?:\s+|$)/g;

  function unescape(escaped) {
    return escaped.replace(/(?:\\(0{0,2}d[89ab][0-9A-Fa-f]{2})(?:\r\n|[ \n\r\t\f])?)?\\([0-9A-Fa-f]{1,6})(?:\r\n|[ \n\r\t\f])?|\\([^\n\r\f0-9A-Fa-f])/g, function(_, a, b, c) {
      if (a !== void(0)) {
        var c2 = parseInt(b, 16) ;
        if (c2 < 0xdc00 || c2 > 0xdfff)
          throw new ValueError("Invalid surrogate pair");
        return String.fromCharCode((((parseInt(a, 16) & 0x3ff) << 10) | (c2 & 0x3ff)) + 0x10000);
      } else if (b !== void(0)) {
        return String.fromCharCode(parseInt(b, 16));
      } else if (c !== void(0)) {
        return c;
      }
    });
  }

  return function parseCSSStyleText(str) {
    var retval = {};
    var r = str.replace(regexp_for_styles, function (_, k, v) {
      var values = [];
      var r = v.replace(regexp_for_values, function (_, a, b, c) {
        if (a !== void(0)) {
          values.push(unescape(a));
        } else if (b !== void(0)) {
          values.push(unescape(b));
        } else if (c !== void(0)) {
          values.push(unescape(c));
        }
        return '';
      });
      if (r != '')
        throw new ValueError("Invalid CSS rule string: " + str);
      retval[k] = values;
      return '';
    });
    if (r != '')
      throw new ValueError("Invalid CSS rule string: " + str);
    return retval;
  };
})();

function parseDefs(node, defset) {
  function parseStops(def) {
    var ref = typeof def.getAttributeNS == 'function' ?
      def.getAttributeNS('http://www.w3.org/1999/xlink', 'href'):
      def.getAttribute("xlink:href");
    if (ref) {
      if (typeof def.ownerDocument.getElementById == 'function')
        def = def.ownerDocument.getElementById(ref.substring(1));
      else
        def = def.ownerDocument.selectSingleNode("*//*[@id='" + ref.substring(1) + "']");
    }
    var stops = def.childNodes;
    var colors = [];
    for (var i = 0; i < stops.length; i++) {
      var node = stops[i];
      if (node.nodeType != 1)
        continue;
      if (node.nodeName == 'stop') {
        var styles = parseCSSStyleText(node.getAttribute('style'));
        colors.push([
          parseFloat(node.getAttribute('offset')),
          new Fashion.Color(styles['stop-color'][0])]);
      }
    }
    return colors;
  }

  var defs = node.childNodes;
  for (var i = 0; i < defs.length; i++) {
    var def = defs[i];
    if (def.nodeType != 1)
      continue;
    var id = def.getAttribute('id');
    switch (def.nodeName) {
    case 'linearGradient':
      var x1 = parseFloat(def.getAttribute("x1")), y1 = parseFloat(def.getAttribute("y1")),
      x2 = parseFloat(def.getAttribute("x2")), y2 = parseFloat(def.getAttribute("y2"));
      var r = Math.acos((x2 - x1) / Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))) + (y2 - y1 < 0 ? Math.PI: 0);
      defset[id] = new Fashion.LinearGradientFill(parseStops(def), r / (Math.PI * 2));
      break;
    case 'radialGradient':
      defset[id] = new Fashion.RadialGradientFill(parseStops(def),
                                                  { x: def.getAttribute('fx') || '50%', y: def.getAttribute('fy') || '50%' });
      break;
    }
  }
}

function parseCSSAsSvgStyle(str, defs) {
  return svgStylesFromMap(parseCSSStyleText(str), defs);
}

function svgStylesFromMap(styles, defs) {
  var fill = null;
  var fillString = styles['fill'];
  var fillOpacity = null;
  var fillOpacityString = styles['fill-opacity'];
  var stroke = null;
  var strokeString = styles['stroke'];
  var strokeWidth = null;
  var strokeWidthString = styles['stroke-width'];
  var strokeOpacity = null;
  var strokeOpacityString = styles['stroke-opacity'];
  var fontSize = null;
  var fontSizeString = styles['font-size'];
  var textAnchor = null;
  var textAnchorString = styles['text-anchor'];
  if (fillString) {
    if (fillString instanceof Array)
      fillString = fillString[0];
    if (fillString == 'none') {
      fill = false;
    } else {
      var g = /url\(#([^)]*)\)/.exec(fillString);
      if (g) {
        fill = defs[g[1]];
        if (!fill)
          throw new Error();
      } else {
        fill = new Fashion.Color(fillString);
      }
    }
  }
  if (fillOpacityString) {
    if (fillOpacityString instanceof Array)
      fillOpacityString = fillOpacityString[0];
    fillOpacity = parseFloat(fillOpacityString);
  }
  if (strokeString) {
    if (strokeString instanceof Array)
      strokeString = strokeString[0];
    if (strokeString == 'none')
      stroke = false;
    else
      stroke = new Fashion.Color(strokeString);
  }
  if (strokeWidthString) {
    if (strokeWidthString instanceof Array)
      strokeWidthString = strokeWidthString[0];
    strokeWidth = parseFloat(strokeWidthString);
  }
  if (strokeOpacityString) {
    if (strokeOpacityString instanceof Array)
      strokeOpacityString = strokeOpacityString[0];
    strokeOpacity = parseFloat(strokeOpacityString);
  }
  if (fontSizeString) {
    if (fontSizeString instanceof Array)
      fontSizeString = fontSizeString[0];
    fontSize = parseFloat(fontSizeString);
  }
  if (textAnchorString) {
    if (textAnchorString instanceof Array)
      textAnchorString = textAnchorString[0];
    textAnchor = textAnchorString;
  }
  return {
    fill: fill,
    fillOpacity: fillOpacity,
    stroke: stroke,
    strokeWidth: strokeWidth,
    strokeOpacity: strokeOpacity,
    fontSize: fontSize,
    textAnchor: textAnchor
  };
}

function mergeSvgStyle(origStyle, newStyle) {
  return {
    fill:          newStyle.fill !== null ? newStyle.fill: origStyle.fill,
    fillOpacity:   newStyle.fillOpacity !== null ? newStyle.fillOpacity: origStyle.fillOpacity,
    stroke:        newStyle.stroke !== null ? newStyle.stroke: origStyle.stroke,
    strokeWidth:   newStyle.strokeWidth !== null ? newStyle.strokeWidth: origStyle.strokeWidth,
    strokeOpacity: newStyle.strokeOpacity !== null ? newStyle.strokeOpacity: origStyle.strokeOpacity,
    fontSize:      newStyle.fontSize !== null ? newStyle.fontSize: origStyle.fontSize,
    textAnchor:    newStyle.textAnchor !== null ? newStyle.textAnchor: origStyle.textAnchor
  };
}

function buildStyleFromSvgStyle(svgStyle) {
  return {
    fill:
    svgStyle.fill ?
      (svgStyle.fill instanceof Fashion.Color ?
       new Fashion.FloodFill(
         svgStyle.fill.replace(
           null, null, null,
           svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255)):
       svgStyle.fill):
    null,
    stroke: 
    svgStyle.stroke ? new Fashion.Stroke(
      svgStyle.stroke.replace(
        null, null, null,
        svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255),
      svgStyle.strokeWidth ? svgStyle.strokeWidth: 1,
      svgStyle.strokePattern ? svgStyle.strokePattern: null):
    null,
    visibility: true
  };
}

function collectText(node) {
  var children = node.childNodes;
  for (var i=0, l=children.length, rt=""; i<l; i++) {
    var n = children[i];
    var name = n.nodeName;
    if (name === '#text'){
      rt += n.nodeValue;
    } else {
      rt += collectText(n);
    }
  }
  return rt;
}

function copyShape(shape) {
  if (shape instanceof Fashion.Rect) {
    return new Fashion.Rect({ position: shape.position(), size: shape.size(), transform: shape.transform() });
  }
  return null;
}

function _map(arr, fn) {
  var retval = new Array(arr.length);
  for (var i = 0; i < arr.length; i++) {
    retval[i] = fn(arr[i]);
  }
  return retval;
}

function parseTransform(transform_str) {
    var g = /\s*([A-Za-z_-][0-9A-Za-z_-]*)\s*\(\s*((?:[^\s,]+(?:\s*,\s*|\s+))*[^\s,]+)\s*\)\s*/.exec(transform_str);

    var f = g[1];
    var args = g[2].replace(/(?:^\s+|\s+$)/, '').split(/\s*,\s*|\s+/);

    switch (f) {
    case 'matrix':
        if (args.length != 6)
            throw new Error("invalid number of arguments for matrix()")
        return new Fashion.Matrix(
            parseFloat(args[0]), parseFloat(args[1]),
            parseFloat(args[2]), parseFloat(args[3]),
            parseFloat(args[4]), parseFloat(args[5]));
    case 'translate':
        if (args.length != 2)
            throw new Error("invalid number of arguments for translate()")
        return Fashion.Matrix.translate({ x:parseFloat(args[0]), y:parseFloat(args[1]) });
    case 'scale':
        if (args.length != 2)
            throw new Error("invalid number of arguments for scale()");
        return new Fashion.Matrix(parseFloat(args[0]), 0, 0, parseFloat(args[1]), 0, 0);
    case 'rotate':
        if (args.length != 1)
            throw new Error("invalid number of arguments for rotate()");
        return Fashion.Matrix.rotate(parseFloat(args[0]) * Math.PI / 180);
    case 'skewX':
        if (args.length != 1)
            throw new Error('invalid number of arguments for skewX()');
        var t = parseFloat(args[0]) * Math.PI / 180;
        var ta = Math.tan(t);
        return new Fashion.Matrix(1, 0, ta, 1, 0, 0);
    case 'skewY':
        if (args.length != 1)
            throw new Error('invalid number of arguments for skewX()');
        var t = parseFloat(args[0]) * Math.PI / 180;
        var ta = Math.tan(t);
        return new Fashion.Matrix(1, ta, 0, 1, 0, 0);
    }
    throw new Error('invalid transform function: ' + f);
}
