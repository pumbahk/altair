function XHR() {
  return Fashion.browser.identifier == 'ie' ?
    new ActiveXObject("Msxml2.XMLHTTP"):
    new XMLHttpRequest();
}

function loadXml(url, success, error) {
  var xhr = XHR();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200 || xhr.status == 0) {
        var xml = xhr.responseXML;
        if ((!xml || !xml.documentElement) && xhr.responseText) {
          if (window.DOMParser) {
            var parser = window.DOMParser();
            xml = parser.parseFromString(xhr.responseText);
          } else {
            var xml = new ActiveXObject("Microsoft.XMLDOM");
            xml.async = false;
            xml.loadXML(xhr.responseText);
          }
        }
        success(xml);
      } else {
        error();
      }
    }
  };
  xhr.open("GET", url, true);
  xhr.send();
}

var parseCSSRules = (function () {
  var regexp_for_rules = /\s*(-?(?:[_a-z\u00a0-\u10ffff]|\\[^\n\r\f#])(?:[\-_A-Za-z\u00a0-\u10ffff]|\\[^\n\r\f])*)\s*:\s*((?:(?:(?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+|"(?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*"|'(?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*')(?:\s+|(?=;|$)))+)(?:;|$)/g;

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

  return function parseCSSRules(str) {
    var retval = {};
    var r = str.replace(regexp_for_rules, function (_, k, v) {
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

function parseCSSAsSvgStyle(str) {
  var rules = parseCSSRules(str);
  var fill = null;
  var fillString = rules['fill'];
  var fillOpacity = null;
  var fillOpacityString = rules['fill-opacity'];
  var stroke = null;
  var strokeString = rules['stroke'];
  var strokeWidth = null;
  var strokeWidthString = rules['stroke-width'];
  var strokeOpacity = null;
  var strokeOpacityString = rules['stroke-opacity'];
  if (fillString) {
    if (fillString[0] == 'none')
      fill = false;
    else
      fill = new Fashion.Color(fillString[0]);
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
      new Fashion.FloodFill(
        svgStyle.fill.replace(
          null, null, null,
          svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255)):
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

function appendShapes(drawable, svgStyle, nodeList) {
  for (var i = 0; i < nodeList.length; i++) {
    var n = nodeList[i];
    if (n.nodeType != 1) continue;
    var styleString = n.getAttribute('style');
    var currentSvgStyle =
      styleString ?
      mergeSvgStyle(svgStyle, parseCSSAsSvgStyle(styleString)):
      svgStyle;
    var shape = null;
    var shape2 = null;
    switch (n.nodeName) {
    case 'g':
      appendShapes(drawable, currentSvgStyle, n.childNodes);
      break;
    case 'path':
      var pathDataString = n.getAttribute('d');
      if (!pathDataString)
        throw "Pathdata is not provided for the path element";
      shape = drawable.draw(new Fashion.Path(new Fashion.PathData(pathDataString)));
      break;
    case 'rect':
      var xString = n.getAttribute('x');
      var yString = n.getAttribute('y');
      var widthString = n.getAttribute('width');
      var heightString = n.getAttribute('height');
      shape = drawable.draw(
        new Fashion.Rect(
          parseFloat(xString),
          parseFloat(yString),
          parseFloat(widthString),
          parseFloat(heightString)));
      shape2 = drawable.draw(
        new Fashion.Text(
          parseFloat(xString),
          parseFloat(yString) + (parseFloat(heightString) * 0.75),
          (parseFloat(widthString) * 0.75),
          "ぴ"));
      shape.seat = true;
      break;
    }
    if (shape !== null) {
      var x = parseFloat(n.getAttribute('x')),
      y = parseFloat(n.getAttribute('y'));
      shape.style(buildStyleFromSvgStyle(currentSvgStyle));
    }
    if (shape2 !== null) {
      shape2.style(buildStyleFromSvgStyle(currentSvgStyle));
    }
  }
}

function parseSvg(xml, targetNode) {
  var viewBoxString = xml.documentElement.getAttribute('viewBox');
  var widthString = xml.documentElement.getAttribute('width');
  var heightString = xml.documentElement.getAttribute('height');
  var viewBox = viewBoxString ? viewBoxString.split(/\s+/): null;
  var size =
    viewBox ?
    {
      width: parseFloat(viewBox[2]),
      height: parseFloat(viewBox[3])
    }
  :
  widthString ?
    heightString ?
    {
      width: parseFloat(widthString),
      height: parseFloat(heightString)
    }
  :
  {
    width: parseFloat(widthString),
    height: parseFloat(widthString)
  }
  :
  heightString ?
    {
      width: parseFloat(heightString),
      height: parseFloat(heightString)
    }
  :
  null
  ;
  var drawable = new Fashion.Drawable(targetNode, { content: size });
  appendShapes(
    drawable,
    { fill: false, fillOpacity: false,
      stroke: false, strokeOpacity: false },
    xml.documentElement.childNodes);

  return drawable;
}

function makeTester(a) {
  var pa = a.position(),
  sa = a.size(),
  ax0 = pa.x,
  ax1 = pa.x + sa.width,
  ay0 = pa.y,
  ay1 = pa.y + sa.height;

  return function(b) {
    var pb = b.position(),
    sb = b.size(),
    bx0 = pb.x,
    bx1 = pb.x + sb.width,
    by0 = pb.y,
    by1 = pb.y + sb.height;

    return ((((ax0 < bx0) && (bx0 < ax1)) || (( ax0 < bx1) && (bx1 < ax1)) || ((bx0 < ax0) && (ax1 < bx1))) && // x
            (((ay0 < by0) && (by0 < ay1)) || (( ay0 < by1) && (by1 < ay1)) || ((by0 < ay0) && (ay1 < by1))));  // y
  }
};


var DemoManager = Fashion._lib._class("DemoManager", {

  props: {
    dragging: false,
    start_pos: {x:0,y:0},
    mask: null,
    d: null
  },

  methods: {
    init : function(d) {
      this.d = d;
      this.mask = new Fashion.Rect(0,0,0,0);
      this.mask.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(255, 0, 0, 128)),
        'stroke': new Fashion.Stroke(new Fashion.Color(255, 0, 0, 255), 2)
      });
    },

    changeTool: function(type) {
      var self = this;

      if (this.d.handler)
        this.d.removeEvent("mousedown", "mouseup", "mousemove");

      switch(type) {
      case 'select1':
        this.d.addEvent({
          mousedown: function(evt) {
            var pos = evt.contentPosition;
            self.d.each(function(i) {
              if (i.seat) {
                var p = i.position(), s = i.size();
                if (p.x < pos.x && pos.x < (p.x + s.width) &&
                    p.y < pos.y && pos.y < (p.y + s.height)) {
                  i.style({
                    'fill': new Fashion.FloodFill(new Fashion.Color(255, 0, 255, 128)),
                    'stroke': new Fashion.Stroke(new Fashion.Color(255, 0, 0, 255), 2)
                  });
                }
              }
            });
          }
        });

        break;
      case 'select':
        this.d.addEvent({
          mousedown: function(evt) {
            self.start_pos = evt.contentPosition;
            self.mask.position({x: self.start_pos.x, y: self.start_pos.y});
            self.mask.size({width: 0, height: 0});
            self.d.draw(self.mask);
            self.dragging = true;
          },
          mouseup: function(evt) {
            self.dragging = false
            var hitTest = makeTester(self.mask);
            self.d.each(function(i) {
              if (i.seat && hitTest(i)) {
                i.style({
                  'fill': new Fashion.FloodFill(new Fashion.Color(255, 0, 255, 128)),
                  'stroke': new Fashion.Stroke(new Fashion.Color(255, 0, 0, 255), 2)
                });
              }
            });
            self.d.erase(self.mask);
          },
          mousemove: function(evt) {
            if (self.dragging) {
              var pos = evt.contentPosition;
              var w = Math.abs(pos.x - self.start_pos.x);
              var h = Math.abs(pos.y - self.start_pos.y);

              var origin = {
                x: (pos.x < self.start_pos.x) ? pos.x : self.start_pos.x,
                y: (pos.y < self.start_pos.y) ? pos.y : self.start_pos.y
              };

              if (origin.x !== self.start_pos.x || origin.y !== self.start_pos.y)
                self.mask.position(origin);

              self.mask.size({width: w, height: h});
            }
          }
        });

        break;
      case 'zoomin':
        this.d.addEvent({
          mouseup: function(evt) {
            this.zoom(this.zoom()*1.2, evt.contentPosition);
          }
        });
        break;
      case 'zoomout':
        this.d.addEvent({
          mouseup: function(evt) {
            this.zoom(this.zoom()/1.2, evt.contentPosition);
          }
        });
        break;
      }
    }
  }
});


var drawable = null;
var manager = null;