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


function loadText(url, success, error) {
  var xhr = XHR();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 200 || xhr.status == 0) {
        var txt = xhr.responseText;
        success(txt);
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

var seatDefaultStyle = {
  'fill': new Fashion.FloodFill(new Fashion.Color(255, 255, 255)),
  'stroke': new Fashion.Stroke(new Fashion.Color(0, 100, 200, 255), 2)
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
      shape.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(255, 203, 63)),
        'stroke': new Fashion.Stroke(new Fashion.Color(90, 190, 205, 255), 30)
      });
      break;

    case 'text':
      var xString = n.getAttribute('x');
      var yString = n.getAttribute('y');
      var widthString = n.getAttribute('width');
      var heightString = n.getAttribute('height');
      var fontSize = n.style.fontSize;
      var idString = n.getAttribute('id');
      shape = drawable.draw(
        new Fashion.Text(
          parseFloat(xString),
          parseFloat(yString),
          parseFloat(fontSize),
          n.firstChild.nodeValue));
      shape.id = idString;
      shape.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(0, 30, 60)),
      });
      break;

    case 'rect':
      var xString = n.getAttribute('x');
      var yString = n.getAttribute('y');
      var widthString = n.getAttribute('width');
      var heightString = n.getAttribute('height');
      var idString = n.getAttribute('id');
      shape = drawable.draw(
        new Fashion.Rect(
          parseFloat(xString),
          parseFloat(yString),
          parseFloat(widthString),
          parseFloat(heightString)));
      shape.seat = true;
      shape.id = idString;
      shape.style(seatDefaultStyle);
      break;
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
    d: null,
    originalStyles: {},
    shift: false
  },

  methods: {
    init : function(d) {
      this.d = d;
      this.mask = new Fashion.Rect(0,0,0,0);
      this.mask.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(0, 100, 255, 128)),
        'stroke': new Fashion.Stroke(new Fashion.Color(0, 128, 255, 255), 2)
      });
    },

    changeTool: function(type) {
      var self = this;

      var selectedSeatStyle = {
        'fill': new Fashion.FloodFill(new Fashion.Color(0, 155, 225, 255)),
        'stroke': new Fashion.Stroke(new Fashion.Color(255, 255, 255, 255), 3),
        'label': {
          'fill': new Fashion.FloodFill(new Fashion.Color(255, 255, 255))
        }
      };

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
                  if (i.selecting && !self.shift) {
                    i.style(seatDefaultStyle);
                    i.selecting = false;
                  } else {
                    i.style(selectedSeatStyle);
                    i.selecting = true;
                  }
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
                if (i.selecting && !self.shift) {
                  var originalStyle = self.originalStyles[i.id];
                  i.style(originalStyle);
                  if (i.label) {
                    i.label.style(originalStyle.label);
                  }
                  i.selecting = false;
                } else {
                  self.originalStyles[i.id] = {
                    fill: i.style().fill,
                    stroke: i.style().fill,
                    label: i.label.style()
                  };
                  i.style(selectedSeatStyle);
                  if (i.label) {
                    i.label.style(selectedSeatStyle.label);
                  }
                  i.selecting = true;
                }
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

function key(e) {
  var shift, ctrl;

  // Mozilla(Firefox, NN) and Opera
  if (e != null) {
    keycode = e.which;
    ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
    shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;
    // イベントの上位伝播を防止
    e.preventDefault();
    e.stopPropagation();
    // Internet Explorer
  } else {
    keycode = event.keyCode;
    ctrl    = event.ctrlKey;
    shift   = event.shiftKey;
    // イベントの上位伝播を防止
    event.returnValue = false;
    event.cancelBubble = true;
  }

  // キーコードの文字を取得
  keychar = String.fromCharCode(keycode).toUpperCase();

  return {
    ctrl:    (!!ctrl) || keycode === 17,
    shift:   (!!shift) || keycode === 16,
    keycode: keycode,
    keychar: keychar
  };

  // 27Esc
  // 8 BackSpace
  // 9 Tab
  // 32Space
  // 45Insert
  // 46Delete
  // 35End
  // 36Home
  // 33PageUp
  // 34PageDown
  // 38↑
  // 40↓
  // 37←
  // 39→

}

var drawable = null;
var manager = null;
