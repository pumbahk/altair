(function () {
var __LIBS__ = {};
__LIBS__['LDP932QNAP6SEFRN'] = (function (exports) { (function () { 

/************** util.js **************/
exports.eventKey = function Util_eventKey(e) {
  var shift, ctrl;
  // Mozilla
  if (e != null) {
    keycode = e.which;
    ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
    shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;

  }
  // ie
  else {
    keycode = event.keyCode;
    ctrl    = event.ctrlKey;
    shift   = event.shiftKey;

  }

  keychar = String.fromCharCode(keycode).toUpperCase();

  return {
    ctrl:    (!!ctrl) || keycode === 17,
    shift:   (!!shift) || keycode === 16,
    keycode: keycode,
    keychar: keychar
  };
};

exports.convertToFashionStyle = function Util_convertToFashionStyle(style, gradient) {
  var fill = function(fill) {
    switch (fill.type) {
    case 'flood':
    default:
      if (gradient) {
        return new Fashion.LinearGradientFill(
          [
            [0, new Fashion.Color("#fff")],
            [1, new Fashion.Color(fill.color || "#fff")]
          ], .125);
      } else {
        return new Fashion.FloodFill(new Fashion.Color(fill.color));
      }
    case 'linear':
      return new Fashion.LinearGradientFill(_map(fill.colors, function (c) { return new Fashion.Color(c); }), fill.angle);
    case 'radial':
      return new Fashion.LinearGradientFill(_map(fill.colors, function (c) { return new Fashion.Color(c); }), fill.focus);
    case 'tile':
      return new Fashion.ImageTileFill(fill.imageData);
    }
    return null;
  };

  var stroke = function(stroke) {
    return new Fashion.Stroke(
            [(style.stroke.color || "#000"),
             (style.stroke.width ? style.stroke.width: 1),
             (style.stroke.pattern || "solid")].join(' '));
  };

  return {
    "fill": style.fill ? fill(style.fill): null,
    "stroke": style.stroke ? stroke(style.stroke): null
  };
};

exports.convertFromFashionStyle = function (style) {
  return {
    text: null,
    text_color: null,
    fill: 
      style.fill instanceof Fashion.FloodFill ?
        { type: 'flood', color: style.fill.color._toString() }:
      style.fill instanceof Fashion.LinearGradientFill ?
        { type: 'linear', colors: _map(style.fill.colors, function (c) { return c._toString() }),
          angle: style.fill.angle }:
      style.fill instanceof Fashion.RadialGradientFill ?
        { type: 'radial', colors: _map(style.fill.colors, function (c) { return c._toString() }),
          focus: style.fill.focus }:
      style.fill instanceof Fashion.ImageTileFill ?
        { type: 'tile', imageData: style.imageData }:
      null,
    stroke:
      style.stroke ?
        { color: style.stroke.color._toString(), width: style.stroke.width,
          pattern: style.stroke.pattern }:
        null
  };
};

exports.allAttributes = function Util_allAttributes(el) {
  var rt = {}, attrs = el.attributes;
  for (var i = 0, l = attrs.length; i < l; i++) {
    var attr = attrs[i];
    rt[attr.namespaceURI ? ('{' + attr.namespaceURI + '}') + attr.nodeName.replace(/^[^:]*:/, ''): attr.nodeName] = attr.nodeValue;
  }
  return rt;
};

exports.makeHitTester = function Util_makeHitTester(a) {
  var leftTop = a.position(), sa = a.size();
  var rightBottom = { x: leftTop.x + sa.x, y: leftTop.y + sa.y };
  if (a.transform()) {
    leftTop = a.transform().apply(leftTop); 
    rightBottom = a.transform().apply(rightBottom);
  }

  return function(b) {
    var targetLeftTop = b.position(), sa = b.size();
    var targetRightBottom = { x: targetLeftTop.x + sa.x, y: targetLeftTop.y + sa.y };
    if (b.transform()) {
      targetLeftTop = b.transform().apply(targetLeftTop); 
      targetRightBottom = b.transform().apply(targetRightBottom);
    }

    return ((((leftTop.x < targetLeftTop.x) && (targetLeftTop.x < rightBottom.x)) ||
             ((leftTop.x < targetRightBottom.x) && (targetRightBottom.x < rightBottom.x)) ||
             ((targetLeftTop.x < leftTop.x) && (rightBottom.x < targetRightBottom.x))) && // x
            (((leftTop.y < targetLeftTop.y) && (targetLeftTop.y < rightBottom.y)) ||
             ((leftTop.y < targetRightBottom.y) && (targetRightBottom.y < rightBottom.y)) ||
             ((targetLeftTop.y < leftTop.y) && (rightBottom.y < targetRightBottom.y))));  // y
  }
};
 })(); return exports; })({});
__LIBS__['y_K1P6ML4QFP4RY3'] = (function (exports) { (function () { 

/************** CONF.js **************/
exports.DEFAULT = {
  ZOOM_RATIO: 0.8,
  STYLES: {
    label: {
      fill: new Fashion.Color('#000'),
      stroke: null
    },
    seat: {
      fill: new Fashion.Color('#fff'),
      stroke: new Fashion.Color('#000')
    },
    glayout: {
      fill: new Fashion.FloodFill(new Fashion.Color('#ccc')),
      stroke: new Fashion.Stroke(new Fashion.Color('#999'), 2)
    }
  },

  MASK_STYLE: {
    fill:   new Fashion.FloodFill(new Fashion.Color("#0064ff80")),
    stroke: new Fashion.Stroke(new Fashion.Color("#0080FF"), 2)
  },

  SEAT_STYLE: {
    text_color: "#000",
    fill:   { color: "#fff" }
  },

  OVERLAYS: {
    highlighted: {
      fill: null,
      stroke: { color: "#F63", width: 3, pattern: 'solid' }
    },
    highlighted_block: {
      fill: null,
      stroke: { color: "#F44", width: 5, pattern: 'solid' }
    }
  },

  AUGMENTED_STYLE: {
    selected: {
      text_color: "#FFF",
      fill:   { color: "#009BE1" },
      stroke: { color: "#FFF", width: 3 }
    },
    unselectable: {
      text_color: "#888",
      fill:   { color: "#eee" },
      stroke: { color: "#ccc" }
    }
  }
};
 })(); return exports; })({});
__LIBS__['C1BYIORY9CY2K_QX'] = (function (exports) { (function () { 

/************** seat.js **************/
var util = __LIBS__['LDP932QNAP6SEFRN'];
var CONF = __LIBS__['y_K1P6ML4QFP4RY3'];

function clone(obj) {
  return $.extend({}, obj);
}

function mergeStyle(a, b) {
  return {
    text: (b.text ? b.text: a.text) || null,
    text_color: (b.text_color ? b.text_color: a.text_color) || null,
    fill: (b.fill ? b.fill: a.fill) || null,
    stroke: (b.stroke ? b.stroke: a.stroke) || null
  };
}

function copyShape(shape) {
  if (shape instanceof Fashion.Path) {
    return new Fashion.Path({ points: shape.points(), style: shape.style(), transform: shape.transform() });
  } else if (shape instanceof Fashion.Rect) {
    return new Fashion.Rect({ position: shape.position(), size: shape.size(), transform: shape.transform() });
  }
  return null;
}

var Seat = exports.Seat = function Seat () {
  this.id = null;
  this.editor = null;
  this.type = null;
  this.floor = null;
  this.gate = null;
  this.block = null;
  this.events = {};
  this._styleTypes = [];
  this.mata = null;
  this.shape = null;
  this.originalStyle = null;
  this._highlightedSeats = [];
  this._selected = false;
  this.label = null;
  this._overlays = {};

  this.init.apply(this, arguments);
};

Seat.prototype.init = function Seat_init(id, meta, parent, events) {
  var self    = this;
  this.id     = id;
  this.parent = parent;
  this.meta   = meta;

  this.type = this.parent.stockTypes[meta.stock_type_id];

  this.originalStyle = this.defaultStyle();

  if (events) {
    for (var i in events) {
      (function(i) {
        self.events[i] = function(evt) {
          if (self.parent.dragging || self.parent.animating)
            return;
          events[i].apply(self, arguments);
        };
      }).call(this, i);
    }
  }

  this.refresh();
};

Seat.prototype.defaultStyle = function Seat_defaultStype() {
  var style = CONF.DEFAULT.SEAT_STYLE;

  if (this.shape)
    style = mergeStyle(style, util.convertFromFashionStyle(this.shape.style()));

  if (this.type)
    style = mergeStyle(style, this.type.style);

  return style;
}

Seat.prototype.attach = function Seat_attach(shape) {
  this.shape = shape;
  this.originalStyle = this.defaultStyle();
  this.refresh();
  shape.addEvent(this.events);
};

Seat.prototype.detach = function Seat_detach(shape) {
  if (this.shape)
    this.shape.removeEvent();
};

Seat.prototype.stylize = function Seat_stylize() {
  if (!this.shape)
    return;
  var style = this.originalStyle;
  for (var i = 0; i < this._styleTypes.length; i++) {
    var styleType = this._styleTypes[i];
    style = mergeStyle(style, CONF.DEFAULT.AUGMENTED_STYLE[styleType]);
  }
  this.shape.style(util.convertToFashionStyle(style));

  if (style.text) {
    if (!this.label) {
      var p = this.shape.position(),
          s = this.shape.size();
      this.label = this.parent.drawable.draw(
        new Fashion.Text({
          position: {
            x: p.x,
            y: p.y + (s.y * 0.75)
          },
          fontSize: (s.y * 0.75),
          text: style.text,
          style: { fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) }
        })
      );
      this.label.addEvent(this.events);
    } else {
      this.label.text(style.text);
      this.label.style({ fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) });
    }
  } else {
    if (this.label) {
      this.parent.drawable.erase(this.label);
      this.label = null;
    }
  }
};

Seat.prototype.addOverlay = function Seat_addOverlay(value) {
  if (!(value in this._overlays)) {
    var shape = copyShape(this.shape)
    shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS[value]));
    this._overlays[value] = shape;
    this.parent.drawable.draw(shape);
  }
};

Seat.prototype.removeOverlay = function Seat_removeOverlay(value) {
  var shape = this._overlays[value];
  if (shape !== void(0)) {
    this.parent.drawable.erase(shape);
    delete this._overlays[value];
  }
};

Seat.prototype.addStyleType = function Seat_addStyleType(value) {
  this._styleTypes.push(value);
  this.stylize();
};

Seat.prototype.removeStyleType = function Seat_removeStyleType(value) {
  for (var i = 0; i < this._styleTypes.length;) {
    if (this._styleTypes[i] == value)
      this._styleTypes.splice(i, 1);
    else
      i++;
  }
  this.stylize();
};

Seat.prototype.refreshDynamicStyle = function Seat_refreshDynamicStyle() {
  if (!this.selectable())
    this.addStyleType('unselectable');
  else
    this.removeStyleType('unselectable');
};

Seat.prototype.refresh = function Seat_refresh() {
  this.refreshDynamicStyle();
  this.stylize();
};

Seat.prototype.__selected = function Seat___selected() {
  this.addStyleType('selected');
  this._selected = true;
};

Seat.prototype.__unselected = function Seat___unselected() {
  this.removeStyleType('selected');
  this._selected = false;
};

Seat.prototype.selected = function Seat_selected(value) {
  if (value !== void(0))
    this.parent._select(this, value);
  return this._selected;
};

Seat.prototype.selectable = function Seat_selectable() {
  return !this.parent.callbacks.selectable ||
    this.parent.callbacks.selectable(this.parent, this);
};

var SeatAdjacencies = exports.SeatAdjacencies = function SeatAdjacencies(parent) {
  this.tbl = [];
  this.src = parent.dataSource.seatAdjacencies;
  this.availableAdjacencies = parent.availableAdjacencies;
  this.callbacks = parent.callbacks;
};

SeatAdjacencies.prototype.getCandidates = function SeatAdjacencies_getCandidates(id, length, next, error) {
  if (length == 1)
    return next([[id]]);

  var tbl = this.tbl[length];
  if (tbl !== void(0)) {
    next(tbl[id] || []);
    return;
  }
  this.callbacks.loadstart && this.callbacks.loadstart('seatAdjacencies');
  var self = this;
  this.src(function (data) {
    var _data;
    if (data === void(0) || (_data = data[length]) === void(0)) {
      error("Invalid adjacency data");
      return;
    }
    tbl = self.tbl[length] = self.convertToTable(length, _data);
    next(tbl[id] || []);
  }, error, length);
};

SeatAdjacencies.prototype.convertToTable = function SeatAdjacencies_convertToTable(len, src) {
  var rt = {};

  for (var i = 0, l = src.length; i < l; i++) {
    // sort by string.
    src[i] = src[i].sort();
    for (var j = 0;j < len;j++) {
      var id  =  src[i][j];
      if (!rt[id]) rt[id] = [];
      rt[id].push(src[i]);
    }
  }

  // sort by string-array.
  for (var i in rt) rt[i].sort().reverse();

  return rt;
};

/*
// test code
// ad == ad2

var ad = new SeatAdjacencies({"3": [["A1", "A2", "A3"], ["A2", "A3", "A4"], ["A3", "A4", "A5"], ["A4", "A5", "A6"]]});
var ad2 = new SeatAdjacencies({"3": [["A1", "A3", "A2"], ["A2", "A3", "A4"], ["A4", "A3", "A5"], ["A6", "A5", "A4"]]});
console.log(ad);
console.log(ad2);
*/
/*
 * vim: sts=2 sw=2 ts=2 et
 */
 })(); return exports; })({});


/************** venue-viewer.js **************/
(function ($) {



/************** classify.js **************/


/************** misc.js **************/
// detect atomic or not
function _atomic_p(obj) {
  var t;
  return ( obj === null || obj === void(0) ||
           (t = typeof obj) === 'number' ||
           t === 'string' ||
           t === 'boolean' ||
           ((obj.valueOf !== Object.prototype.valueOf) &&
            !(obj instanceof Date)));
};


// make deep clone of the object
function _clone(obj, target) {
  if (_atomic_p(obj)) return obj;

  // if target is given. clone obj properties into it.
  var clone, p;
  if (obj instanceof Date) {
    clone = new Date(obj.getTime());
    if (target instanceof Date) {
      for (p in target) if (target.hasOwnProperty(p)) clone[p] = _clone(target[p], clone[p]);
    }
  } else if (typeof obj === 'function') {
    clone = function(){return obj.apply(this, arguments);};
    if (typeof target === 'function') {
      for (p in target) if (target.hasOwnProperty(p)) clone[p] = _clone(target[p], clone[p]);
    }
  } else {
    clone = (!_atomic_p(target) && typeof target !== 'function') ?
      target : new obj.constructor();
  }

  for (p in obj)
    if (obj.hasOwnProperty(p))
      clone[p] = _clone(obj[p], clone[p]);

  return clone;
};

function xparseInt(str, radix) {
  var retval = parseInt(str, radix);
  if (isNaN(retval))
    throw new ValueError("Invalid numeric string: " + str);
  return retval;
};

function _repeat(str, length) {
  var retval = '';
  while (length) {
    if (length & 1)
      retval += str;
    str += str;
    length >>= 1;
  }
  return retval;
};

function _lpad(str, length, pad) {
  return _repeat(pad, length - str.length) + str;
};

function _bindEvent(target, type, f) {
  if (typeof BROWSER == 'undefined')
    return;

  if (BROWSER.identifier == 'ie' && BROWSER.version < 9)
    target.attachEvent('on' + type, f);
  else
    target.addEventListener(type, f, false);
}

function _unbindEvent(target, type, f) {
  if (typeof BROWSER == 'undefined')
    return;

  if (BROWSER.identifier == 'ie' && BROWSER.version < 9)
    target.detachEvent('on' + type, f);
  else
    target.removeEventListener(type, f, false);
}

var _escapeXMLSpecialChars = (function () {
  var specials = new RegExp("[<>&'\"]"),
      map = ['', '&lt;', '&gt;', '&amp;', '&apos;', '&quot;', ''];
  return function (str) {
    if (typeof str != 'string')
      str = str.toString();
    return str.replace(specials, function(x) { return map[special.source.indexOf(x)] });
  };
})();

function _clip(target, min, max) {
  return Math.min(Math.max(target, min), max);
}

function _clipPoint(target, min, max) {
  return { x: _clip(target.x, min.x, max.x),
           y: _clip(target.y, min.y, max.y) };
}

function _addPoint(lhs, rhs) {
  return { x: lhs.x + rhs.x, y: lhs.y + rhs.y };
}

function _subtractPoint(lhs, rhs) {
  return { x: lhs.x - rhs.x, y: lhs.y - rhs.y };
}

function _indexOf(array, elem, fromIndex) {
  if (array instanceof Array && 'indexOf' in Array.prototype) {
    return array.indexOf(elem, fromIndex);
  }
  for (var i = Math.max(fromIndex || 0, 0); i < array.length; i++) {
    if (array[i] === elem)
      return i;
  }
  return -1;
}

var _class = (function() {
  function __super__() {
    return this.constructor.__super__.prototype;
  }

  function inherits(_class, parent) {
    _class.__super__ = parent;

    var f = function() {};
    f.prototype = parent.prototype;
    f.prototype.constructor = parent;
    _class.prototype = new f();
    _class.prototype.__super__ = __super__;

    var iiop = _class['%%INIT_INSTANCE_ORIGIN_PROPS'];

    _class['%%INIT_INSTANCE_ORIGIN_PROPS'] = function(inst) {
      var parent_iiop = parent['%%INIT_INSTANCE_ORIGIN_PROPS'];
      if (parent_iiop) parent_iiop(inst);
      iiop(inst);
    };

    return _class;

  };

  function method(_class, name, func) {
    func.__class__ = _class;
    _class.prototype[name] = func;
  };

  var genclassid = (function() {
    var id = 0;
    return function getclassid() {
      var ret = "%%ANONYMOUS_CLASS_"+id+"%%"; ++id;
      return ret;
    };
  })();

  function mixin(_class, include) {
    var incproto = include.prototype;
    for (var i in incproto) {
      if (i == 'init') {
        _class.prototype['init%%' + include['%%CLASSNAME%%']] = incproto[i];
      } else if (i !== "__super__" && i !== "constructor") {
        _class.prototype[i] = incproto[i];
      }
    }

    var iiop = _class['%%INIT_INSTANCE_ORIGIN_PROPS'];
    _class['%%INIT_INSTANCE_ORIGIN_PROPS'] = function(inst) {
      var include_iiop = include['%%INIT_INSTANCE_ORIGIN_PROPS'];
      if (include_iiop) include_iiop(inst);
      iiop(inst);
    };
  };

  function check_interface(_class, impl) {
    for (var i in impl.prototype) {
      if (impl.prototype.hasOwnProperty(i)) {
        if (!_class.prototype.hasOwnProperty(i)) {
          throw new DeclarationError(
              'The class \'' + _class['%%CLASSNAME%%'] +
              '\' must provide property or method \'' + i +
              '\' imposed by \'' + impl['%%CLASSNAME%%'] +'".');
        }
      }
    }
  };

  return function _class(name, definition) {
    var __class__, i, j, l, c, def, type;

    var props = {};
    var class_props = {};
    var methods = {};
    var class_methods = {};
    var parent = Object;
    var mixins = [];
    var interfaces = [];

    for (i in definition) {
      switch (i) {
      case "props":
        def = definition[i];
        for (j in def) {
          if (def.hasOwnProperty(j))
            props[j] = def[j];
        }
        break;
      case "class_props":
        class_props = definition[i];
        break;
      case "methods":
        methods = definition[i];
        break;
      case "class_methods":
        class_methods = definition[i];
        break;
      case "parent":
        parent = definition[i];
        break;
      case "interfaces":
        interfaces = definition[i];
        break;
      case "mixins":
        mixins = definition[i];
        break;
      default:
        throw new ArgumentError(
            'You gave \'' + i + '\' as definition, but the _class() excepts' +
            ' only \'props\',\'class_props\',\'methods\',\'class_methods\',\'parent\',\'interfaces\',\'mixins\'.');

      }
    }

    __class__ = function __Class__(arg) {
      __class__['%%INIT_INSTANCE_ORIGIN_PROPS'](this);
      if (this.init) this.init.apply(this, arguments);
      else           _clone(arg, this);
    };

    __class__['%%INIT_INSTANCE_ORIGIN_PROPS'] =
      function(inst) {
        for (var p in props) {
          inst[p] = _clone(props[p]);
        }
      };

    inherits(__class__, parent);

    for (j = 0, l = mixins.length; j < l; j++) {
      mixin(__class__, mixins[j]);
    }

    for (i in methods) {
      if (methods.hasOwnProperty(i)) {
        method(__class__, i, methods[i]);
      }
    }
    __class__.prototype.constructor = __class__;

    __class__['%%CLASSNAME%%'] = name || genclassid();
    for (i in class_methods) {
      __class__[i] = class_methods[i];
    }

    for (j=0, l=interfaces.length; j<l; j++) {
      check_interface(__class__, interfaces[j]);
    }

    for (i in class_props) {
      __class__[i] = class_props[i];
    }

    class_methods['init'] && class_methods.init.call(__class__);

    return __class__;
  };

})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** helpers.js **************/
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

  var CONF = __LIBS__['y_K1P6ML4QFP4RY3'];
  var seat = __LIBS__['C1BYIORY9CY2K_QX'];
  var util = __LIBS__['LDP932QNAP6SEFRN'];

  var StoreObject = _class("StoreObject", {
    props: {
      store: {}
    },
    methods: {
      save: function(id, data) {
        if (!this.store[id]) this.store[id] = data;
      },
      restore: function(id) {
        var rt = this.store[id];
        delete this.store[id];
        return rt;
      },
      clear: function() {
        for (var id in this.store) {
          delete this.store[id];
        }
      }
    }
  });

  var VenueViewer = _class("VenueViewer", {

    props: {
      canvas: null,
      callbacks: {
        uimodeselect: null,
        load: null,
        loadPartStart: null,
        loadPartEnd: null,
        loadAbort: null,
        click: null,
        selectable: null,
        select: null,
        pageChanging: null,
        messageBoard: null,
        zoomRatioChanging: null,
        zoomRatioChange: null
      },
      dataSource: null,
      zoomRatio: CONF.DEFAULT.ZOOM_RATIO,
      contentOriginPosition: {x: 0, y: 0},
      dragging: false,
      startPos: { x: 0, y: 0 },
      rubberBand: new Fashion.Rect({
        position: {x: 0, y: 0},
        size: {x: 0, y: 0}
      }),
      drawable: null,
      availableAdjacencies: [ 1 ],
      originalStyles: new StoreObject(),
      overlayShapes: new StoreObject(),
      shift: false,
      keyEvents: null,
      uiMode: 'select1',
      shapes: null,
      link_pairs: null,
      seats: null,
      selection: {},
      selectionCount: 0,
      highlighted: {},
      animating: false,
      _adjacencyLength: 1,
      currentPage: null,
      rootPage: null,
      _history: [],
      seatTitles: {},
      optionalViewportSize: null,
      loading: false,
      loadAborted: false,
      loadAbortionHandler: null
    },

    methods: {
      init: function VenueViewer_init(canvas, options) {
        this.canvas = canvas;
        this.stockTypes = null;
        if (options.callbacks) {
          for (var k in this.callbacks)
            this.callbacks[k] = options.callbacks[k] || function () {};
        }
        this.dataSource = options.dataSource;
        if (options.zoomRatio) zoom(options.zoomRatio);
        this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
        canvas.empty();
        this.optionalViewportSize = options.viewportSize;
      },

      load: function VenueViewer_load() {
        this.loading = true;
        this.seatAdjacencies = null;
        var self = this;

        self.callbacks.loadPartStart.call(self, 'pages');
        self.initBlocks(self.dataSource.pages, function() {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          self.callbacks.loadPartEnd.call(self, 'pages');
          self.currentPage = self.rootPage;
          self.loading = true;
          self.callbacks.loadPartStart.call(self, 'stockTypes');
          self.dataSource.stockTypes(function (data) {
            self.loading = false;
            if (self.loadAborted) {
              self.loadAborted = false;
              self.loadAbortionHandler && self.loadAbortionHandler.call(self);
              self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
              return;
            }
            self.loading = true;
            self.callbacks.loadPartEnd.call(self, 'stockTypes');
            self.stockTypes = data;
            self.callbacks.loadPartStart.call(self, 'info');
            self.dataSource.info(function (data) {
              self.loading = false;
              if (self.loadAborted) {
                self.loadAborted = false;
                self.loadAbortionHandler && self.loadAbortionHandler.call(self);
                self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
                return;
              }
              self.loading = true;
              self.callbacks.loadPartEnd.call(self, 'info');
              if (!'available_adjacencies' in data) {
                self.callbacks.message.call(self, "Invalid data");
                return;
              }
              self.availableAdjacencies = data.available_adjacencies;
              self.seatAdjacencies = new seat.SeatAdjacencies(self);
              self.callbacks.loadPartStart.call(self, 'seats');
              self.initSeats(self.dataSource.seats, function () {
                self.loading = false;
                if (self.loadAborted) {
                  self.loadAborted = false;
                  self.loadAbortionHandler && self.loadAbortionHandler.call(self);
                  self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
                  return;
                }
                self.loading = true;
                self.callbacks.loadPartEnd.call(self, 'seats');
                if (self.currentPage) {
                  self.loadDrawing(self.currentPage, function () {
                    self.callbacks.load.call(self, self);
                  });
                } else {
                  self.callbacks.load.call(self, self);
                }
              });
            }, self.callbacks.message);
          }, self.callbacks.message);
        });
      },

      loadDrawing: function (page, next) {
        var self = this;
        this.callbacks.loadPartStart.call(this, this, 'drawing');
        this.initDrawable(page, function () {
          next();
          self.callbacks.pageChanging.call(self, page);
          self.callbacks.loadPartEnd.call(self, self, 'drawing');
        });
      },

      cancelLoading: function VenueViewer_cancelLoading(next) {
        if (this.loading) {
          this.loadAborted = true;
          this.loadAbortionHandler = next;
        } else {
          next.call(this);
        }
      },

      dispose: function VenueViewer_dispose(next) {
        var self = this;
        this.cancelLoading(function () {
          self.removeKeyEvent();
          if (self.drawable) {
            self.drawable.dispose();
            self.drawable = null;
          }
          self.seats = null;
          self.selection = null;
          self.highlighted = null;
          self.availableAdjacencies = [1];
          self.shapes = null;
          self.link_pairs = null;
          self.selection = {};
          self.selectionCount = 0;
          self.highlighted = {};
          self.animating = false;
          self._adjacencyLength = 1;
          self.currentPage = null;
          self.rootPage = null;
          self._history = [];
          self.seatTitles = {};
          next && next.call(self);
        });
      },

      initDrawable: function VenueViewer_initDrawable(page, next) {
        if (this.link_pairs) {
          for (var i = this.link_pairs.length; --i >= 0; )
            this.link_pairs[i][0].removeEvent();
        }

        if (this.drawable)
          this.drawable.dispose();

        this.originalStyles.clear();
        this.overlayShapes.clear();

        this.currentPage = page;

        var self = this;
        var currentFocusedIds = (function () {
          var retval = {};
          var focused_ids = self.pages[page]['focused_ids'];
          if (focused_ids) {
            for (var i = focused_ids.length; --i >= 0; )
              retval[focused_ids[i]] = true;
          }
          return retval;
        })();

        var isFocused = function isFocused(id){
          return currentFocusedIds[id];
        };

        var dataSource = this.dataSource.drawing(page);

        dataSource(function (drawing) {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          var attrs = util.allAttributes(drawing.documentElement);
          var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
          var vb = null;
          if (attrs['viewBox']) {
            var comps = attrs['viewBox'].split(/\s+/);
            vb = new Array(comps.length);
            for (var i = 0; i < comps.length; i++)
              vb[i] = parseFloat(comps[i]);
          }

          var size = ((vb || w || h) ? {
            x: ((vb && vb[2]) || w || h),
            y: ((vb && vb[3]) || h || w)
          } : null);

          var drawable = new Fashion.Drawable( self.canvas[0], {
            contentSize: size ? {x: size.x, y: size.y}: null,
            viewportSize: self.optionalViewportSize
          });

          var shapes = {}, link_pairs = [];
          var styleClasses = CONF.DEFAULT.STYLES;

          var leftTop = null, rightBottom = null;

          (function iter(context, nodeList) {
            outer:
            for (var i = 0; i < nodeList.length; i++) {
              var n = nodeList[i];
              if (n.nodeType != 1) continue;

              var attrs = util.allAttributes(n);
              var xlink = context.xlink;
              var focused = context.focused || (attrs.id && isFocused(attrs.id));
              var transform = attrs["transform"] ?
                context.transform.multiply(parseTransform(attrs["transform"])):
                context.transform;
              var shape = null;

              { // stylize
                var currentSvgStyle = context.svgStyle;
                if (attrs.style)
                  currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, context.defs));
                if (attrs['class']) {
                  var style = styleClasses[attrs['class']];
                  if (style) currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
                }
                currentSvgStyle = mergeSvgStyle(currentSvgStyle, svgStylesFromMap(attrs));
              }

              switch (n.nodeName) {
              case 'defs':
                parseDefs(n, context.defs);
                break;

              case 'a':
                xlink = attrs['{http://www.w3.org/1999/xlink}href'];
                /* fall-through */
              case 'g': {
                arguments.callee.call(
                  self,
                  {
                    svgStyle: currentSvgStyle,
                    transform: transform,
                    defs: context.defs,
                    focused: focused,
                    xlink: xlink
                  },
                  n.childNodes);
                continue outer;
              }

              case 'path':
                if (!attrs.d) throw new Error("Pathdata is not provided for the path element");
                shape = new Fashion.Path({
                  points: new Fashion.PathData(attrs.d)
                });
                break;

              case 'text':
                if (n.firstChild) {
                  shape = new Fashion.Text({
                    text: collectText(n),
                    anchor: currentSvgStyle.textAnchor,
                    transform: _transform
                  });
                }
                break;

              case 'symbol':
                break;

              case 'rect':
                var _transform = attrs.transform || null;
                shape = new Fashion.Rect({
                  size: {
                    x: parseFloat(attrs.width),
                    y: parseFloat(attrs.height)
                  },
                  corner: {
                    x: parseFloat(attrs.rx || 0),
                    y: parseFloat(attrs.ry || 0)
                  },
                  transform: _transform,
                  zIndex: -10
                });
                for (var j=0,ll=n.childNodes.length; j<ll; j++) {
                  if (n.childNodes[j].nodeName == "title") {
                    self.seatTitles[attrs.id] = n.childNodes[j].childNodes[0].nodeValue;
                    break;
                  }
                }
                break;

              default:
                continue outer;
              }

              if (shape !== null) {
                var x = parseFloat(attrs.x),
                    y = parseFloat(attrs.y);

                if (!isNaN(x) && !isNaN(y)) {

                  if (focused) {
                    leftTop = leftTop ? {
                      x: Math.min(leftTop.x, x),
                      y: Math.min(leftTop.y, y)
                    }: { x: x, y: y };
                    rightBottom = rightBottom ? {
                      x: Math.max(rightBottom.x, x),
                      y: Math.max(rightBottom.y, y)
                    }: { x: x, y: y };
                  }
                  shape.position({ x: x, y: y });
                }
                shape.style(buildStyleFromSvgStyle(currentSvgStyle));
                shape.transform(transform);
                if (shape instanceof Fashion.Text) {
                  shape.fontSize(currentSvgStyle.fontSize);
                }
                drawable.draw(shape);
              }
              if (attrs.id) {
                shapes[attrs.id] = shape;
                var seat = self.seats[attrs.id];
                if (seat)
                  seat.attach(shape);
              }
              if (xlink)
                link_pairs.push([shape, xlink])
            }
          }).call(
            self,
            {
              svgStyle: {
                fill: false, fillOpacity: false,
                stroke: false, strokeOpacity: false,
                fontSize: 10
              },
              transform: new Fashion.Matrix(),
              defs: {},
              focused: false,
              xlink: null
            },
            drawing.documentElement.childNodes);

          self.drawable = drawable;
          self.shapes = shapes;
          self.link_pairs = link_pairs;

          if (!leftTop)
            leftTop = { x: 0, y: 0 };
          if (!rightBottom)
            rightBottom = size;

          var center = {
            x: (leftTop.x + rightBottom.x) / 2,
            y: (leftTop.x + rightBottom.y) / 2
          };

          var focusedRegionSize = {
            x: (rightBottom.x - leftTop.x) / 0.8,
            y: (rightBottom.y - leftTop.y) / 0.8
          };
          var focusedRegionOffset = {
            x: center.x - (focusedRegionSize.x / 2),
            y: center.y - (focusedRegionSize.y / 2)
          };

          var vs = drawable.viewportSize();
          var wr = vs.x / focusedRegionSize.x;
          var hr = vs.y / focusedRegionSize.y;
          var r = (wr < hr) ? wr : hr;
          var origin = {
            x: (wr < hr) ? focusedRegionOffset.x : center.x - ((vs.x/2)/hr),
            y: (wr < hr) ? center.y - ((vs.y/2)/wr) : focusedRegionOffset.y
          };
          self.zoomRatioMin = r;
          self.contentOriginPosition = origin;

          drawable.transform(
            Fashion.Matrix.scale(self.zoomRatio)
              .translate({x: -origin.x, y: -origin.y}));

          drawable.contentSize({x: (vs.x/r) + origin.x, y: (vs.y/r) + origin.y});

          function getSiblings(link) {
            var rt = [];
            for (var i = self.link_pairs.length; --i >= 0;) {
              var shape_and_link = self.link_pairs[i];
              if (shape_and_link[1] == link)
                rt.push(shape_and_link[0]);
            }
            return rt;
          }

          for (var i = 0; i < self.link_pairs.length; i++) {
            (function (shape, link) {
              var siblings = getSiblings(link);
              shape.addEvent({
                mouseover: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = copyShape(siblings[i]);
                      if (shape) {
                        shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                        self.drawable.draw(shape);
                        self.overlayShapes.save(siblings[i].id, shape);
                      }
                    }
                    self.callbacks.messageBoard.up.call(self, self.pages[link].name);
                  }
                },
                mouseout: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = self.overlayShapes.restore(siblings[i].id);
                      if (shape)
                        self.drawable.erase(shape);
                    }
                    self.callbacks.messageBoard.down.call(self);
                  }
                },
                mousedown: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    self.callbacks.messageBoard.down.call(self);
                    self.navigate(link);
                  }
                }
              });
            }).apply(self, self.link_pairs[i]);
          }

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      navigate: function (page) {
        if (!(page in this.pages))
          return;
        var previousPage = this.currentPage;
        var self = this;
        this.loadDrawing(page, function () {
          if (self._history.length > 0 && self._history[self._history.length - 1] == page)
            self._history.pop();
          else
            self._history.push(previousPage);
        });
      },

      history: function () {
        return this._history;
      },

      initBlocks: function VenueViewer_initBlocks(dataSource, next) {
        var self = this;

        dataSource(function (pages) {
          self.pages = pages;
          for (var page in pages) {
            if (pages[page].root)
              self.rootPage = page;
          }
          next.call(self);
        }, self.callbacks.message);
      },

      initSeats: function VenueViewer_initSeats(dataSource, next) {
        var self = this;
        dataSource(function (seatMeta) {
          var seats = {};
          for (var id in seatMeta) {
            seats[id] = new seat.Seat(id, seatMeta[id], self, {
              mouseover: function(evt) {
                if (self.uiMode == 'select')
                  return;
                self.callbacks.messageBoard.up(self.seatTitles[this.id]);
                self.seatAdjacencies.getCandidates(this.id, self.adjacencyLength(), function (candidates) {
                  if (candidates.length == 0)
                    return;
                  var candidate = null;
                  for (var i = 0; i < candidates.length; i++) {
                    candidate = candidates[i];
                    for (var j = 0; j < candidate.length; j++) {
                      if (!seats[candidate[j]].selectable()) {
                        candidate = null;
                        break;
                      }
                    }
                    if (candidate) {
                      break;
                    }
                  }
                  if (!candidate)
                    return;
                  for (var i = 0; i < candidate.length; i++) {
                    var seat = seats[candidate[i]];
                    seat.addOverlay('highlighted');
                    self.highlighted[seat.id] = seat;
                  }
                }, self.callbacks.message);
              },
              mouseout: function(evt) {
                if (self.uiMode == 'select')
                  return;
                self.callbacks.messageBoard.down.call(self);
                var highlighted = self.highlighted;
                self.highlighted = {};
                for (var i in highlighted)
                  highlighted[i].removeOverlay('highlighted');
              },
              mousedown: function(evt) {
                self.callbacks.click(self, self, self.highlighted);
              }
            });
          }

          self.seats = seats;
          next.call(self);
        }, self.callbacks.message);
      },

      refresh: function VenueViewer_refresh() {
        for (var id in this.seats) this.seats[id].refresh();
      },

      addKeyEvent: function VenueViewer_addKeyEvent() {
        if (this.keyEvents) return;
        var self = this;
        this.keyEvents = {
          down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
          up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
        };

        $(document).bind('keydown', this.keyEvents.down);
        $(document).bind('keyup',   this.keyEvents.up);
      },

      removeKeyEvent: function VenueViewer_removeKeyEvent() {
        if (!this.keyEvents) return;

        $(document).unbind('keydown', this.keyEvents.down);
        $(document).unbind('keyup',   this.keyEvents.up);
      },

      changeUIMode: function VenueViewer_changeUIMode(type) {
        if (this.drawable) {
          var self = this;
          this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

          switch(type) {
          case 'move':
            var mousedown = false, scrollPos = null;
            this.drawable.addEvent({
              mousedown: function (evt) {
                if (self.animating) return;
                mousedown = true;
                scrollPos = self.drawable.scrollPosition();
                self.startPos = evt.logicalPosition;
              },

              mouseup: function (evt) {
                if (self.animating) return;
                mousedown = false;
                if (self.dragging) {
                  self.drawable.releaseMouse();
                  self.dragging = false;
                }
              },

              mousemove: function (evt) {
                if (self.animating) return;
                if (!self.dragging) {
                  if (mousedown) {
                    self.dragging = true;
                    self.drawable.captureMouse();
                  } else {
                    return;
                  }
                }
                var newScrollPos = Fashion._lib.subtractPoint(
                  scrollPos,
                  Fashion._lib.subtractPoint(
                    evt.logicalPosition,
                    self.startPos));
                scrollPos = self.drawable.scrollPosition(newScrollPos);
              }
            });
            break;

          case 'select1':
            /* this.drawable.addEvent({
              mousedown: {
              }
            });
            */
            break;

          case 'select':
            this.drawable.addEvent({
              mousedown: function(evt) {
                if (self.animating) return;
                self.startPos = evt.logicalPosition;
                self.rubberBand.position({x: self.startPos.x,
                                          y: self.startPos.y});
                self.rubberBand.size({x: 0, y: 0});
                self.drawable.draw(self.rubberBand);
                self.dragging = true;
                self.drawable.captureMouse();
              },

              mouseup: function(evt) {
                if (self.animating) return;
                self.drawable.releaseMouse();
                self.dragging = false;
                var selection = [];
                var hitTest = util.makeHitTester(self.rubberBand);
                for (var id in self.seats) {
                  var seat = self.seats[id];
                  if (seat.shape && (hitTest(seat.shape) || (self.shift && seat.selected())) &&
                      (!self.callbacks.selectable
                       || self.callbacks.selectable(this, seat))) {
                    selection.push(seat);
                  }
                }
                self.unselectAll();
                self.drawable.erase(self.rubberBand);
                for (var i = 0; i < selection.length; i++)
                  selection[i].selected(true);
                self.callbacks.select(self, selection);
              },

              mousemove: function(evt) {
                if (self.animating) return;
                if (self.dragging) {
                  var pos = evt.logicalPosition;
                  var w = Math.abs(pos.x - self.startPos.x);
                  var h = Math.abs(pos.y - self.startPos.y);

                  var origin = {
                    x: (pos.x < self.startPos.x) ? pos.x : self.startPos.x,
                    y: (pos.y < self.startPos.y) ? pos.y : self.startPos.y
                  };

                  if (origin.x !== self.startPos.x || origin.y !== self.startPos.y)
                    self.rubberBand.position(origin);

                  self.rubberBand.size({x: w, y: h});
                }
              }
            });
            break;

          case 'zoomin':
            this.drawable.addEvent({
              mouseup: function(evt) {
                self.zoom(self.zoomRatio * 1.2, evt.logicalPosition);
              }
            });
            break;

          case 'zoomout':
            this.drawable.addEvent({
              mouseup: function(evt) {
                self.zoom(self.zoomRatio / 1.2, evt.logicalPosition);
              }
            });
            break;

          default:
            throw new Error("Invalid ui mode: " + type);
          }
        }
        this.uiMode = type;
        this.callbacks.uimodeselect(this, type);
      },

      zoom: function(ratio, center) {
        if (isNaN(ratio))
          return;
        var previousRatio = this.zoomRatio;
        if (this.callbacks.zoomRatioChanging) {
          var corrected = this.callbacks.zoomRatioChanging(ratio);
          if (corrected === false)
            return;
          if (corrected)
            ratio = corrected;
        }
        if (!this.drawable) {
          this.zoomRatio = ratio;
          this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange(ratio);
          return;
        }

        if (!center) {
          var vs = this.drawable.viewportSize();
          var logicalSize = {
            x: vs.x / previousRatio,
            y: vs.y / previousRatio
          };
          var scroll = this.drawable.scrollPosition();
          center = {
            x: scroll.x + (logicalSize.x / 2),
            y: scroll.y + (logicalSize.y / 2)
          }
        }

        this.drawable.transform(Fashion.Matrix.scale(ratio)
                                .translate({x: -this.contentOriginPosition.x,
                                            y: -this.contentOriginPosition.y}));

        var vs = this.drawable.viewportSize();

        var logicalSize = {
          x: vs.x / ratio,
          y: vs.y / ratio
        };

        var logicalOrigin = {
          x: center.x - (logicalSize.x / 2),
          y: center.y - (logicalSize.y / 2)
        };

        this.drawable.scrollPosition(logicalOrigin);
        this.zoomRatio = ratio;
        this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange(ratio);
      },

      unselectAll: function VenueViewer_unselectAll() {
        var prevSelection = this.selection;
        this.selection = {};
        for (var id in prevSelection) {
          this.seats[id].__unselected();
        }
        this.selectionCount = 0;
      },

      _select: function VenueViewer__select(seat, value) {
        if (value) {
          if (!(seat.id in this.selection)) {
            this.selection[seat.id] = seat;
            this.selectionCount++;
            seat.__selected();
          }
        } else {
          if (seat.id in this.selection) {
            delete this.selection[seat.id];
            this.selectionCount--;
            seat.__unselected();
          }
        }
      },

      adjacencyLength: function VenueViewer_adjacencyLength(value) {
        if (value !== void(0)) {
          this._adjacencyLength = value;
        }
        return this._adjacencyLength;
      },

      scrollTo: function VenueViewer_scrollTo(leftTopCorner) {
        if (this.animating) return;
        var scrollPos = this.drawable.scrollPosition();
        leftTopCorner = { x: leftTopCorner.x, y: leftTopCorner.y };
        var contentSize = this.drawable.contentSize();
        var rightBottomCorner = Fashion._lib.addPoint(
          leftTopCorner,
          this.drawable._inverse_transform.apply(
            this.drawable.viewportInnerSize()));
        if (rightBottomCorner.x > contentSize.x)
          leftTopCorner.x += contentSize.x - rightBottomCorner.x;
        if (rightBottomCorner.y > contentSize.y)
          leftTopCorner.y += contentSize.y - rightBottomCorner.y;
        leftTopCorner.x = Math.max(leftTopCorner.x, 0);
        leftTopCorner.y = Math.max(leftTopCorner.y, 0);

        this.animating = true;
        var self = this;
        var t = setInterval(function () {
          var delta = Fashion._lib.subtractPoint(
            leftTopCorner,
            scrollPos);
          if (Math.sqrt(delta.x * delta.x + delta.y * delta.y) < 1) {
            clearInterval(t);
            self.animating = false;
            return;
          }
          delta = { x: delta.x / 2, y: delta.y / 2 };
          scrollPos = Fashion._lib.addPoint(scrollPos, delta);
          self.drawable.scrollPosition(scrollPos);
        }, 50);
      },

      back: function VenueViewer_back() {
        if (this._history.length > 0)
          this.navigate(this._history[this._history.length - 1]);
      }
    }
  });

  /* main */

  $.fn.venueviewer = function (options) {
    var aux = this.data('venueviewer');

    if (!options)
      throw new Error("Options must be given");
    if (typeof options == 'object') {
      if (!options.dataSource || typeof options.dataSource != 'object')
        throw new Error("Required option missing: dataSource");
      var self = this;
      function init() {
        var _options = $.extend({}, options);

        var createMetadataLoader = (function () {
          var conts = {}, allData = null, first = true;
          return function createMetadataLoader(key) {
            return function metadataLoader(next, error) {
              conts[key] = { next: next, error: error };
              if (first) {
                $.ajax({
                  url: options.dataSource.metadata,
                  dataType: 'json',
                  success: function(data) {
                    allData = data;
                    var _conts = conts;
                    conts = {};
                    for (var k in _conts)
                      _conts[k].next(data[key]);
                  },
                  error: function(xhr, text) {
                    var message = "Failed to load " + key + " (reason: " + text + ")";
                    var _conts = conts;
                    conts = {};
                    for (var k in _conts)
                      _conts[k] && _conts[k].error(message);
                  }
                });
                first = false;
                return;
              } else {
                if (allData) {
                  conts[key].next(allData[key]);
                  delete conts[key];
                }
              }
            };
          };
        })();

        $.each(
          [
            [ 'stockTypes', 'stock_types' ],
            [ 'seats', 'seats' ],
            [ 'areas', 'areas' ],
            [ 'info', 'info' ],
            [ 'seatAdjacencies', 'seat_adjacencies' ],
            [ 'pages', 'pages' ]
          ],
          function(n, k) {
            _options.dataSource[k[0]] =
              typeof options.dataSource[k[0]] == 'function' ?
                options.dataSource[k[0]]:
                createMetadataLoader(k[1]);
          }
        );
        aux = new VenueViewer(self, _options),
        self.data('venueviewer', aux);

        if (options.uimode) aux.changeUIMode(options.uimode);
      }
      if (aux)
        aux.dispose(init);
      else
        init();
    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        if (aux)
          aux.dispose();
        this.empty();
        this.data('venueviewer', null);
      } else {
        if (!aux)
          throw new Error("Command issued against an uninitialized element");
        switch (options) {
        case 'load':
          aux.load();
          break;

        case 'uimode':
          if (arguments.length >= 2)
            aux.changeUIMode(arguments[1]);
          else
            return aux.uiMode;
          break;

        case 'selection':
          return aux.selection;

        case 'unselectAll':
          return aux.unselectAll();

        case 'refresh':
          return aux.refresh();

        case 'adjacency':
          aux.adjacencyLength(arguments[1]|0);
          break;

        case 'root':
          return aux.rootPage;

        case 'back':
          aux.back();
          break;

        case 'zoom':
          aux.zoom(arguments[1]);
          break;

        case 'navigate':
          aux.navigate(arguments[1]);
          break;
        }
      }
    }

    return this;
  };

})(jQuery);
/*
 * vim: sts=2 sw=2 ts=2 et
 */
})();
