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
  var styles = parseCSSStyleText(str);
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
  if (fillString) {
    if (fillString[0] == 'none') {
      fill = false;
    } else {
      var g = /url\(#([^)]*)\)/.exec(fillString[0]);
      if (g) {
        fill = defs[g[1]];
        if (!fill)
          throw new Error();
      } else {
        fill = new Fashion.Color(fillString[0]);
      }
    }
  }
  if (fillOpacityString) {
    fillOpacity = parseFloat(fillOpacityString[0]);
  }
  if (strokeString) {
    if (strokeString[0] == 'none')
      stroke = false;
    else
      stroke = new Fashion.Color(strokeString[0]);
  }
  if (strokeWidthString) {
    strokeWidth = parseFloat(strokeWidthString[0]);
  }
  if (strokeOpacityString) {
    strokeOpacity = parseFloat(strokeOpacityString[0]);
  }
  return {
    fill: fill,
    fillOpacity: fillOpacity,
    stroke: stroke,
    strokeWidth: strokeWidth,
    strokeOpacity: strokeOpacity
  };
}

function mergeSvgStyle(origStyle, newStyle) {
  return {
    fill: newStyle.fill !== null ? newStyle.fill: origStyle.fill,
    fillOpacity: newStyle.fillOpacity !== null ? newStyle.fillOpacity: origStyle.fillOpacity,
    stroke: newStyle.stroke !== null ? newStyle.stroke: origStyle.stroke,
    strokeWidth: newStyle.strokeWidth !== null ? newStyle.strokeWidth: origStyle.strokeWidth,
    strokeOpacity: newStyle.strokeOpacity !== null ? newStyle.strokeOpacity: origStyle.strokeOpacity
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
  if (shape instanceof Fashion.Path) {
    return new Fashion.Path({ points: shape.points(), style:shape.style() });
  } else if (shape instanceof Fashion.Rect) {
    return new Fashion.Rect({ position: shape.position(), size: shape.size() });
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
