(function () {
var __LIBS__ = {};
__LIBS__['NR41EIISSYMO7J58'] = (function (exports) { (function () { 

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
      } else if(fill.color) {
        return new Fashion.FloodFill(new Fashion.Color(fill.color));
      } else {
        return null;
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
__LIBS__['a0X2EMD4_UNVR4TS'] = (function (exports) { (function () { 

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
__LIBS__['w_SSALS7ENCRK43R'] = (function (exports) { (function () { 

/************** seat.js **************/
var util = __LIBS__['NR41EIISSYMO7J58'];
var CONF = __LIBS__['a0X2EMD4_UNVR4TS'];

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
  if (this.shape === shape)
    return;
  if (this.shape !== shape)
    this.detach();

  this.shape = shape;
  this.originalStyle = this.defaultStyle();
  this.refresh();
  if (shape)
    shape.addEvent(this.events);
};

Seat.prototype.detach = function Seat_detach(shape) {
  if (!this.shape)
    return;

  if (this.label) {
    this.parent.drawable.erase(this.label);
    this.label = null;
  }
  this.shape.removeEvent();
  this.shape = null;
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
    if (this.shape) {
      var shape = copyShape(this.shape)
      shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS[value]));
      this._overlays[value] = shape;
      this.parent.drawable.draw(shape);
    }
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
  var regexp_for_values = /(?:((?:[^;\\"'(]|\([^)]*\)|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+)|"((?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)"|'((?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)')(?:\s+|$)/g;

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
    var retval = [];
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
      retval.push([k, values]);
      return '';
    });
    if (r != '')
      throw new ValueError("Invalid CSS rule string: " + str);
    return retval;
  };
})();

var expandFontProperty = (function () {
  var props = [
    [/normal|italic|oblique|inherit/, function (z) { this.push(['font-style', z]); }],
    [/normal|small-caps|inherit/, function (z) { this.push(['font-variant', z]); }],
    [/normal|bold|bolder|lighter|100|200|300|400|500|600|700|800|900|inherit/, function (z) { this.push(['font-weight', z]); }],
    [/((?:(?:(?:[1-9][0-9]*|0)(?:\.[0-9]*)?)|(?:\.[0-9]+))(?:px|pt|et|ex|%))(?:\/((?:(?:(?:[1-9][0-9]*|0)(?:\.[0-9]*)?)|(?:\.[0-9]+))(?:px|pt|et|ex|%)))?/, function (_, a, b) {
      this.push(['font-size', a]);
      if (b) {
        this.push(['line-height', b]); 
      }
    }]
  ];
  return function expandFontProperty(values) {
    var retval = [];
    var i = 0, j = 0;
    for (; i < values.length && j < props.length; i++) {
      for (; j < props.length; j++) {
        var prop = props[j];
        var g = prop[0].exec(values[i]);
        if (g) {
          prop[1].apply(retval, g);
          break;
        }
      }
    }
    retval.push(['font-family', values.slice(i).join(' ')]);
    return retval;
  };
})();

function coerceCSSStyleIntoMap(styles) {
  var retval = {};

  var props = [];
  for (var i = 0; i < styles.length; i++) {
    var k = styles[i][0], v = styles[i][1];
    switch (k) {
    case 'font':
      expanded = expandFontProperty(v);
      if (expanded) {
        for (var j = 0; j < expanded.length; j++) {
          retval[expanded[j][0]] = expanded[j][1];
        }
        continue;
      }
      break;
    }
    retval[k] = v;
  }
  return retval;
}

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
        var styles = coerceCSSStyleIntoMap(parseCSSStyleText(node.getAttribute('style')));
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
  return svgStylesFromMap(coerceCSSStyleIntoMap(parseCSSStyleText(str)), defs);
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
  var strokeDashArray = null;
  var strokeDashArrayString = styles['stroke-dasharray'];
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
  if (strokeDashArrayString) {
    if (strokeDashArrayString instanceof Array)
      strokeDashArrayString = strokeDashArrayString[0];
    if (strokeDashArrayString.indexOf(',') != -1)
      strokeDashArray = strokeDashArrayString.split(/,/);
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
    strokeDashArray: strokeDashArray,
    fontSize: fontSize,
    textAnchor: textAnchor
  };
}

function mergeSvgStyle(origStyle, newStyle) {
  var copied = { };
  for (var k in origStyle) {
    copied[k] = origStyle[k];
  }
  for (var k in newStyle) {
    if (newStyle[k] !== null) {
      copied[k] = newStyle[k];
    }
  }
  return copied;
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
      svgStyle.strokeDashArray ? svgStyle.strokeDashArray: (svgStyle.strokePattern ? svgStyle.strokePattern: null)):
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
  } else if (shape instanceof Fashion.Path) {
    return new Fashion.Path({ points: shape.points(),transform: shape.transform() });
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
        if (args.length == 1)
            args[1] = 0;
        else if (args.length != 2)
            throw new Error("invalid number of arguments for translate()")
        return Fashion.Matrix.translate({ x:parseFloat(args[0]), y:parseFloat(args[1]) });
    case 'scale':
        if (args.length == 1)
            args[1] = 0;
        else if (args.length != 2)
            throw new Error("invalid number of arguments for scale()");
        return new Fashion.Matrix(parseFloat(args[0]), 0, 0, parseFloat(args[1]), 0, 0);
    case 'rotate':
        if (args.length == 1)
            args[1] = 0;
        else if (args.length != 2)
            throw new Error("invalid number of arguments for rotate()");
        return Fashion.Matrix.rotate(parseFloat(args[0]) * Math.PI / 180);
    case 'skewX':
        if (args.length == 1)
            args[1] = 0;
        else if (args.length != 2)
            throw new Error('invalid number of arguments for skewX()');
        var t = parseFloat(args[0]) * Math.PI / 180;
        var ta = Math.tan(t);
        return new Fashion.Matrix(1, 0, ta, 1, 0, 0);
    case 'skewY':
        if (args.length == 1)
            args[2] = 0;
        else if (args.length != 2)
            throw new Error('invalid number of arguments for skewX()');
        var t = parseFloat(args[0]) * Math.PI / 180;
        var ta = Math.tan(t);
        return new Fashion.Matrix(1, ta, 0, 1, 0, 0);
    }
    throw new Error('invalid transform function: ' + f);
}

  var CONF = __LIBS__['a0X2EMD4_UNVR4TS'];
  var seat = __LIBS__['w_SSALS7ENCRK43R'];
  var util = __LIBS__['NR41EIISSYMO7J58'];

  var VenueViewer = _class("VenueViewer", {

    props: {
      canvas: null,
      callbacks: {
        uimodeselect: function () {},
        load: function () {},
        loadPartStart: function () {},
        loadPartEnd: function () {},
        loadAbort: function () {},
        click: function () {},
        selectable: function () {},
        select: function () {},
        pageChanging: function () {},
        message: function () {},
        messageBoard: function () {},
        zoomRatioChanging: function () {},
        zoomRatioChange: function () {},
        queryAdjacency: null
      },
      dataSource: null,
      zoomRatio: CONF.DEFAULT.ZOOM_RATIO,
      contentOriginPosition: {x: 0, y: 0},
      dragging: false,
      startPos: { x: 0, y: 0 },
      drawable: null,
      overlayShapes: {},
      shift: false,
      keyEvents: null,
      uiMode: 'select',
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
      pageBeingLoaded: false,
      pagesCoveredBySeatData: null, 
      loadAborted: false,
      loadAbortionHandler: null,
      _smallTextsShown: true,
      nextSingleClickAction: null,
      doubleClickTimeout: 400,
      mouseUpHandler: null,
      onMouseUp: null,
      onMouseMove: null,
      deferSeatLoading: false
    },

    methods: {
      init: function VenueViewer_init(canvas, options) {
        this.canvas = canvas;
        this.stockTypes = null;
        for (var k in this.callbacks) {
          if (options.callbacks[k])
            this.callbacks[k] = options.callbacks[k];
        }
        this.dataSource = options.dataSource;
        if (options.zoomRatio) zoom(options.zoomRatio);
        canvas.empty();
        this.optionalViewportSize = options.viewportSize;
        this.deferSeatLoading = !!options.deferSeatLoading;
        var self = this;
        this.mouseUpHandler = function() {
          if (self.onMouseUp) {
            self.onMouseUp.call(self);
          }
        };
        $(document.body).bind('mouseup', this.mouseUpHandler);
        this.mouseMoveHandler = function(evt) {
          if (self.onMouseMove) {
            var fasevt = new Fashion.MouseEvt();
            var physicalPagePosition = { x: evt.pageX, y: evt.pageY };
            var screenPosition = Fashion._lib.subtractPoint(physicalPagePosition, self.drawable.impl.getViewportOffset());
            var physicalPosition = Fashion._lib.addPoint(self.drawable.impl.convertToPhysicalPoint(self.drawable.impl.scrollPosition()), screenPosition);
            fasevt.logicalPosition = self.drawable.impl.convertToLogicalPoint(physicalPosition);
            self.onMouseMove.call(self, fasevt);
            evt.stopImmediatePropagation();
            evt.stopPropagation();
            evt.preventDefault();
            return false;
          }
        };
        $(document.body).bind('mousemove', this.mouseMoveHandler);
      },

      load: function VenueViewer_load() {
        this.loading = true;
        var self = this;

        self.callbacks.loadPartStart.call(self, self, 'pages');
        self.initBlocks(self.dataSource.pages, function() {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          self.callbacks.loadPartEnd.call(self, self, 'pages');
          self.currentPage = self.rootPage;
          self.loading = true;
          self.callbacks.loadPartStart.call(self, self, 'stockTypes');
          self.dataSource.stockTypes(function (data) {
            self.loading = false;
            if (self.loadAborted) {
              self.loadAborted = false;
              self.loadAbortionHandler && self.loadAbortionHandler.call(self);
              self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
              return;
            }
            self.loading = true;
            self.callbacks.loadPartEnd.call(self, self, 'stockTypes');
            self.stockTypes = data;
            self.callbacks.loadPartStart.call(self, self, 'info');
            self.dataSource.info(function (data) {
              self.loading = false;
              if (self.loadAborted) {
                self.loadAborted = false;
                self.loadAbortionHandler && self.loadAbortionHandler.call(self);
                self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
                return;
              }
              self.loading = true;
              self.callbacks.loadPartEnd.call(self, self, 'info');
              if (self.currentPage) {
                self.loadDrawing(self.currentPage, function () {
                  self.callbacks.load.call(self, self);
                  self.zoomAndPan(self.zoomRatioMin, { x: 0., y: 0. });
                });
              } else {
                self.callbacks.load.call(self, self);
              }
              if (!self.deferSeatLoading)
                self.loadSeats(function () { onDrawingOrSeatsLoaded('seats'); });
            }, self.callbacks.message);
          }, self.callbacks.message);
        });
      },

      loadDrawing: function (page, next) {
        var self = this;
        this.callbacks.loadPartStart.call(self, self, 'drawing');
        var _this = this;
        setTimeout(function() {
          _this.initDrawable(page, function () {
            if (self.pagesCoveredBySeatData && (self.pagesCoveredBySeatData === 'all-in-one' || page in self.pagesCoveredBySeatData)) {
              for (var id in self.seats) {
                var shape = self.shapes[id];
                if (shape)
                  self.seats[id].attach(shape);
              }
            }
            self.callbacks.pageChanging.call(self, page);
            self.callbacks.loadPartEnd.call(self, self, 'drawing');
            next.call(self);
          });
        }, 50);
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
          $(document.body).unbind('mouseup', self.mouseUpHandler);
          self.removeKeyEvent();
          if (self.drawable) {
            self.drawable.dispose();
            self.drawable = null;
          }
          self.seats = null;
          self.selection = null;
          self.highlighted = null;
          self.shapes = null;
          self.small_texts = [ ];
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

        this.overlayShapes = {};

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
        self.pageBeingLoaded = page;
        dataSource(function (drawing) {
          self.loading = false;
          self.pageBeingLoaded = null;
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
            viewportSize: self.optionalViewportSize             // fixed parameter
          });

          /*
          var frame = new Fashion.Rect({
                  size: { x: size.x, y: size.y },
                  position: { x: (vb && vb[0]) || 0, y: (vb && vb[1]) || 0 },
                  corner: { x: 0, y: 0 },
                  transform: null,
                  zIndex: -10
              });
          frame.style({ fill: new Fashion.FloodFill(new Fashion.Color("#ff000080")) });
          drawable.draw(frame);
          */

          var shapes = {}, link_pairs = [];
          var small_texts = [];
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
              var px = parseFloat(attrs.x),
                  py = parseFloat(attrs.y);
              var position = (!isNaN(px) && !isNaN(py)) ? { x: px, y: py } : context.position;
              var transform = attrs["transform"] ?
                context.transform.multiply(parseTransform(attrs["transform"])):
                context.transform;
              var shape = null;

              { // stylize
                var currentSvgStyle = context.svgStyle;
                // 1st: find style by class attribute
                if (attrs['class']) {
                  var style = styleClasses[attrs['class']];
                  if (style) currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
                }
                // 2nd: overwrite by style attribute (css like string)
                if (attrs.style)
                  currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, context.defs));
                // 3rd: overwrite by some kinds of attributes
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
              case 'tspan':
                if (n.childNodes.length==1 && n.firstChild.nodeType == /* Node.TEXT_NODE */ 3) {
                  shape = new Fashion.Text({
                    text: collectText(n),
                    anchor: currentSvgStyle.textAnchor,
                    fontSize: currentSvgStyle.fontSize,
                    position: position || null,
                    transform: transform || null
                  });
                } else if (n.nodeName == 'text') {
                  arguments.callee.call(
                    self,
                    {
                      svgStyle: currentSvgStyle,
                      position: position,
                      transform: transform,
                      defs: context.defs,
                      focused: focused,
                      xlink: xlink
                    },
                    n.childNodes);
                  continue outer;
                }
                break;

              case 'symbol':
                break;

              case 'rect':
                shape = new Fashion.Rect({
                  size: {
                    x: parseFloat(attrs.width),
                    y: parseFloat(attrs.height)
                  },
                  corner: {
                    x: parseFloat(attrs.rx || 0),
                    y: parseFloat(attrs.ry || 0)
                  },
                  transform: transform || null,
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
                  if (currentSvgStyle.fontSize <= 10) {
                    if (!self._smallTextsShown)
                      shape.visibility(false);
                    small_texts.push(shape);
                  }
                }
                drawable.draw(shape);
              }
              if (attrs.id) {
                shapes[attrs.id] = shape;
              }
              if (xlink)
                link_pairs.push([shape, xlink])
            }
          }).call(
            self,
            {
              svgStyle: {
                fill: false, fillOpacity: false,
                stroke: false, strokeOpacity: false, strokeDashArray: false,
                fontSize: 10, textAnchor: false
              },
              position: null,
              transform: new Fashion.Matrix(),
              defs: {},
              focused: false,
              xlink: null
            },
            drawing.documentElement.childNodes);

          self.drawable = drawable;
          self.shapes = shapes;
          self.small_texts = small_texts;
          self.link_pairs = link_pairs;

          if (!leftTop)
            leftTop = { x: (vb && vb[0]) || 0, y: (vb && vb[1]) || 0 };
          if (!rightBottom)
            rightBottom = { x: leftTop.x + size.x, y: leftTop.y + size.y };

          var center = {
            x: (leftTop.x + rightBottom.x) / 2,
            y: (leftTop.y + rightBottom.y) / 2
          };
          var focusedRegionSize = {
            x: (rightBottom.x - leftTop.x),
            y: (rightBottom.y - leftTop.y)
          };
          var focusedRegionOffset = {
            x: center.x - (focusedRegionSize.x / 2),
            y: center.y - (focusedRegionSize.y / 2)
          };

          var margin = { x: 20, y: 20 };  /* width of zoom slider and height of map selector */
          var vs = drawable.viewportSize();
          vs = { x: vs.x-margin.x, y: vs.y-margin.y };

          var xr = vs.x / focusedRegionSize.x * 0.9;
          var yr = vs.y / focusedRegionSize.y * 0.9;
          var r = (xr < yr) ? xr : yr;

          var origin = {
            x: center.x - (vs.x/2+margin.x)/r, y: center.y - (vs.y/2+margin.y)/r
          };
          self.zoomRatioMin = r;
          self.contentOriginPosition = origin;

          drawable.transform(
            Fashion.Matrix.scale(self.zoomRatioMin)
              .translate({ x: -origin.x, y: -origin.y })
          );
          drawable.contentSize({
            x: origin.x + vs.x/r, y: origin.y + vs.y/r
          });

          function getSiblings(link) {
            var rt = [];
            for (var i = self.link_pairs.length; --i >= 0;) {
              var shape_and_link = self.link_pairs[i];
              if (shape_and_link[1] == link)
                rt.push(shape_and_link[0]);
            }
            return rt;
          }

          var drawableMouseDown = false;
          var clickTimer = 0;

          for (var i = 0; i < self.link_pairs.length; i++) {
            (function (shape, link) {
              var siblings = getSiblings(link);
              shape.addEvent({
                mouseover: function(evt) {
                  if (self.pages) {
                    for (var i = siblings.length; --i >= 0;) {
                      var id = siblings[i].id;
                      if (self.overlayShapes[id] === void(0)) {
                        var overlayShape = copyShape(siblings[i]);
                        if (overlayShape) {
                          overlayShape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                          self.drawable.draw(overlayShape);
                          self.overlayShapes[id] = overlayShape;
                        }
                      }
                    }
                    var pageAndAnchor = link.split('#');
                    var page = pageAndAnchor[0];
                    if (page == '')
                      page = self.currentPage;
                    self.callbacks.messageBoard.up.call(self, self.pages[page].name);
                    self.canvas.css({ cursor: 'pointer' });
                  }
                },
                mouseout: function(evt) {
                  self.canvas.css({ cursor: 'default' });
                  for (var i = siblings.length; --i >= 0;) {
                    var id = siblings[i].id;
                    var overlayShape = self.overlayShapes[id];
                    if (overlayShape !== void(0)) {
                      self.drawable.erase(overlayShape);
                      delete self.overlayShapes[id];
                    }
                  }
                  self.callbacks.messageBoard.down.call(self);
                },
                mouseup: function(evt) {
                  if (self.pages) {
                    self.navigate(link);
                  }
                }
              });
            }).apply(self, self.link_pairs[i]);
          }

          (function () {
            var scrollPos = null;

            function drawableMouseUp() {
              self.onMouseUp = null;
              self.onMouseMove = null;
              $(self.canvas[0]).find('div').css({ overflow: 'scroll' });
              drawableMouseDown = false;
              if (self.dragging) {
                self.drawable.releaseMouse();
                self.dragging = false;
              }
            }

            function drawableMouseMove(evt) {
                if (clickTimer) {
                  singleClickFulfilled();
                }
                if (self.animating) return;
                if (!self.dragging) {
                  if (drawableMouseDown) {
                    self.dragging = true;
                    self.drawable.captureMouse();
                    $(self.canvas[0]).find('div').css({ overflow: 'hidden' });
                    self.callbacks.messageBoard.down.call(self);
                  } else {
                    return;
                  }
                }
                var newScrollPos = Fashion._lib.subtractPoint(
                  scrollPos,
                  Fashion._lib.subtractPoint(
                    evt.logicalPosition,
                    self.startPos));
                self.drawable.scrollPosition(newScrollPos);
                scrollPos = newScrollPos;
                return false;
            }

            function singleClickFulfilled() {
              clearTimeout(clickTimer);
              clickTimer = 0;
              var nextSingleClickAction = self.nextSingleClickAction;
              self.nextSingleClickAction = null;
              if (nextSingleClickAction)
                nextSingleClickAction.call(self);
            }

            self.drawable.addEvent({
              mousedown: function (evt) {
                if (self.animating) return;
                switch (self.uiMode) {
                case 'zoomin': case 'zoomout':
                  break;
                default:
                  drawableMouseDown = true;
                  self.onMouseUp = drawableMouseUp;
                  self.onMouseMove = drawableMouseMove;
                  if (!clickTimer) {
                    scrollPos = self.drawable.scrollPosition();
                    self.startPos = evt.logicalPosition;
                    clickTimer = setTimeout(singleClickFulfilled,
                                            self.doubleClickTimeout);
                  } else {
                    if (!self.dragging) {
                      // double click
                      clearTimeout(clickTimer);
                      clickTimer = 0;
                      self.drawableMouseDown = false;
                      var e = self.zoomRatio * 2;
                      self.zoom(e, evt.logicalPosition);
                      /*
                      self.animating = true;
                      var t = setInterval(function () {
                        var newZoomRatio = Math.min(e, self.zoomRatio * 1.2);
                        if (e - self.zoomRatio < self.zoomRatio * 1e-5 || newZoomRatio - self.zoomRatio > self.zoomRatio * 1e-5) {
                          self.animating = false;
                          clearInterval(t);
                        }
                      }, 50);
                      */
                    }
                  }
                  break;
                }
              },

              mouseup: function (evt) {
                drawableMouseUp(evt);
                if (self.animating) return;
                switch (self.uiMode) {
                case 'zoomin':
                  self.zoom(self.zoomRatio * 1.2, evt.logicalPosition);
                  break;
                case 'zoomout':
                  self.zoom(self.zoomRatio / 1.2, evt.logicalPosition);
                  break;
                default:
                  break;
                }
              },

              mouseout: function (evt) {
/*
                if (clickTimer) {
                  singleClickFulfilled();
                }
*/
                self.canvas.css({ cursor: 'default' });
                self.callbacks.messageBoard.down.call(self);
              },

              mousemove: function (evt) {
                drawableMouseMove(evt);
              }
            });
          })();

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      zoomOnShape: function (shape) {
        if (!this.drawable)
          return;
        var position = shape.position();
        var size = shape.size();
        var p0 = shape._transform.apply(position);
        var p1 = shape._transform.apply({ x: position.x, y: position.y+size.y });
        var p2 = shape._transform.apply({ x: position.x+size.x, y: position.y });
        var p3 = shape._transform.apply({ x: position.x+size.x, y: position.y+size.y });
        var rp = { x: Math.min(p0.x, p1.x, p2.x, p3.x), y: Math.min(p0.y, p1.y, p2.y, p3.y) };
        var rs = { x: Math.max(p0.x, p1.x, p2.x, p3.x)-rp.x, y: Math.max(p0.y, p1.y, p2.y, p3.y)-rp.y };
        var vs = this.drawable.viewportSize();
        var margin = 0.10;
        var ratio = Math.min(vs.x*(1-margin) / rs.x, vs.y*(1-margin) / rs.y);
        // FIXME: ratioが上限を超えないようにしないと、対象オブジェクトがセンターにこない
        var scrollPos = {
          x: Math.max(rp.x - (vs.x/ratio-rs.x)/2, 0),
          y: Math.max(rp.y - (vs.y/ratio-rs.y)/2, 0)
        };
        this.zoomAndPan(ratio, scrollPos);
      },

      navigate: function (pageUrlOrPageInfo) {
        var previousPageInfo = {
          page: this.currentPage,
          zoomRatio: this.zoomRatio,
          scrollPosition: this.drawable ? this.drawable.scrollPosition() : null
        };
        var self = this;
        if (typeof pageUrlOrPageInfo == 'string' || pageUrlOrPageInfo instanceof String) {
          // page can be
          // - page.svg
          // - page.svg#id
          // - page.svg#__FIXED__
          // - #id
          var comps = pageUrlOrPageInfo.split('#');
          var anchor = null;
          page = comps[0];
          if (comps.length > 1)
            anchor = comps[1];
          if (page == '')
            page = this.currentPage;
          var afterthings = function () {
            self._history.push(previousPageInfo);
            if (anchor == '__FIXED__') {
              self.zoomAndPan(previousPageInfo.zoomRatio,
                              previousPageInfo.scrollPosition);
            } else {
              var shape = self.shapes[anchor];
              if (shape !== void(0) && shape instanceof Fashion.Rect) {
                self.zoomOnShape(shape);
              } else {
                self.zoomAndPan(self.zoomRatioMin, { x: 0., y: 0. });
              }
            }
          }
          this._loadPage({ page: page }, afterthings);
        } else {
          this._loadPage(pageUrlOrPageInfo, function () {
            self._history.push(previousPageInfo);
          });
        }
      },

      _loadPage: function (pageInfo, next) {
        var self = this;
        var afterthings = function () {
          if (pageInfo.zoomRatio && pageInfo.scrollPosition) {
            self.zoomAndPan(pageInfo.zoomRatio,
                            pageInfo.scrollPosition);
          }
          if (next)
            next.call(self, pageInfo);
        };
        if (!pageInfo)
          return;
        if (!(pageInfo.page in this.pages))
          return;
        this.canvas.css({ cursor: 'default' });
        this.callbacks.messageBoard.down.call(this);
        if (this.currentPage != pageInfo.page) {
          this.loadDrawing(pageInfo.page, function () {
            self.callbacks.load.call(self, self);
            afterthings();
          });
        } else {
          afterthings();
        }
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

      loadSeats: function(next) {
        var self = this;
        self.callbacks.loadPartStart.call(self, self, 'seats');
        self.loading = true;
        self.initSeats(self.dataSource.seats, function () {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self, self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          if (!self.pageBeingLoaded && self.currentPage && (self.pagesCoveredBySeatData === 'all-in-one' || self.currentPage in self.pagesCoveredBySeatData)) {
            for (var id in self.seats) {
              var shape = self.shapes[id];
              if (shape)
                self.seats[id].attach(shape);
            }
          }
          self.callbacks.loadPartEnd.call(self, self, 'seats');
          if (next)
            next();
        });
      },

      initSeats: function VenueViewer_initSeats(dataSource, next) {
        var self = this;
        dataSource(function (seatMeta) {
          var seats = {};
          for (var id in seatMeta) {
            var seat_ = seats[id] = new seat.Seat(id, seatMeta[id], self, {
              mouseover: function(evt) {
                self.callbacks.messageBoard.up.call(self, self.seatTitles[this.id]);
                self.queryAdjacency(this.id, self.adjacencyLength(), function (candidates) {
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
                var highlighted = self.highlighted;
                self.highlighted = {};
                for (var i in highlighted)
                  highlighted[i].removeOverlay('highlighted');
              },
              mousedown: function(evt) {
                self.nextSingleClickAction = function () {
                  self.callbacks.click.call(self, self, self.highlighted);
                };
              }
            });
          }

          for (var id in self.seats)
            self.seats[id].detach();
          self.seats = seats;
          self.pagesCoveredBySeatData = 'all-in-one'; // XXX
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

          switch(type) {
          case 'select': case 'move': case 'zoomin': case 'zoomout':
            break;
          default:
            throw new Error("Invalid ui mode: " + type);
          }
        }
        this.uiMode = type;
        this.callbacks.uimodeselect.call(this, this, type);
      },

      zoom: function(ratio, anchor) {
        if (!this.drawable)
          return;
        var vs = this.drawable.viewportSize();
        var scrollPos = this.drawable.scrollPosition();
        var previousRatio = this.zoomRatio;

        var previousLogicalSize = {
          x: vs.x / previousRatio,
          y: vs.y / previousRatio
        };

        if (!anchor) {
          anchor = {
            x: scrollPos.x + (previousLogicalSize.x / 2),
            y: scrollPos.y + (previousLogicalSize.y / 2)
          }
        }

        var physicalOffset = {
          x: (anchor.x - scrollPos.x) * previousRatio,
          y: (anchor.y - scrollPos.y) * previousRatio 
        };
        var logicalSize = {
          x: vs.x / ratio,
          y: vs.y / ratio
        };

        var logicalOrigin = {
          x: anchor.x - (physicalOffset.x / ratio),
          y: anchor.y - (physicalOffset.y / ratio)
        };

        this.zoomAndPan(ratio, logicalOrigin);
      },

      zoomAndPan: function(ratio, scrollPos) {
        if (isNaN(ratio))
          return;
        var previousRatio = this.zoomRatio;
        if (this.callbacks.zoomRatioChanging) {
          var corrected = this.callbacks.zoomRatioChanging.call(this, ratio);
          if (corrected === false)
            return;
          if (corrected)
            ratio = corrected;
        }
        if (!this.drawable) {
          this.zoomRatio = ratio;
          this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange.call(this, ratio);
          return;
        }
        this.drawable.transform(Fashion.Matrix.scale(ratio)
                                .translate({x: -this.contentOriginPosition.x,
                                            y: -this.contentOriginPosition.y}));

        this.drawable.scrollPosition(scrollPos);
        this.zoomRatio = ratio;
        this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange.call(this, ratio);
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
          this._loadPage(this._history.pop());
      },

      showSmallTexts: function VenueViewer_showSmallTexts() {
        if (!this._smallTextsShown) {
          for(var i = this.small_texts.length; --i >= 0;)
            this.small_texts[i].visibility(true);
          this._smallTextsShown = true
        }
      },

      hideSmallTexts: function VenueViewer_hideSmallTexts() {
        if (this._smallTextsShown) {
          for(var i = this.small_texts.length; --i >= 0;)
            this.small_texts[i].visibility(false);
          this._smallTextsShown = false;
        }
      },

      queryAdjacency: function VenueViewer_queryAdjacency(id, adjacency, success, failure) {
        if (this.callbacks.queryAdjacency)
          return this.callbacks.queryAdjacency(id, adjacency, success, failure);
        success([[id]]);
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
                  error: function(xhr, text, status) {
                    var message = "Failed to load " + key + " (reason: " + text + " - " + status + ")";
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

        case 'loadSeats':
          aux.loadSeats(arguments[1]);
          break;

        case 'showSmallTexts':
          aux.showSmallTexts();
          break;
        case 'hideSmallTexts':
          aux.hideSmallTexts();
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
