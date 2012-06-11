"use strict";
var fs = require('fs');

// detect atomic or not
function _atomic_p(obj) {
  var t = typeof obj;
  return ( !(obj instanceof Date) &&
           ( obj === null || obj === void(0) ||
             t === 'boolean' || t === 'number' || t === 'string' ||
             obj.valueOf !== Object.prototype.valueOf));
};


// make deep clone of the object
function _clone(obj, target) {
  if (_atomic_p(obj)) return obj;

  // if target is given. clone obj properties into it.
  var clone, p;
  if (obj instanceof Date) {
    clone = new Date((typeof obj.getTime === 'function') ? obj.getTime() : obj);
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
      target :
      new obj.constructor()
  }

  for (p in obj)
    if (obj.hasOwnProperty(p))
      clone[p] = _clone(obj[p], clone[p]);

  return clone;
};


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

    var iiop = _class['%%INIT_INSTANCE_ORIGN_PROPS'];

    _class['%%INIT_INSTANCE_ORIGN_PROPS'] = function(inst) {
      var parent_iiop = parent['%%INIT_INSTANCE_ORIGN_PROPS'];
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

    var iiop = _class['%%INIT_INSTANCE_ORIGN_PROPS'];
    _class['%%INIT_INSTANCE_ORIGN_PROPS'] = function(inst) {
      var include_iiop = include['%%INIT_INSTANCE_ORIGN_PROPS'];
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

    __class__ = function(arg) {
      __class__['%%INIT_INSTANCE_ORIGN_PROPS'](this);
      if (this.init)
        this.init.apply(this, arguments);
      else
        _clone(arg, this); 
    };

    __class__['%%INIT_INSTANCE_ORIGN_PROPS'] =
      function(inst) {
        for (var p in props) {
          if (props.hasOwnProperty(p)) {
            inst[p] = _clone(props[p]);
          }
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

var Matrix = (function() {

  var PI = Math.PI;

  var norm = function(a) {
    return ( a[0] * a[0] ) + ( a[1] * a[1] );
  };

  var normalize = function(a) {
    var mag = Math.sqrt(norm(a));
    a[0] && (a[0] /= mag);
    a[1] && (a[1] /= mag);
  };

  var _Matrix = _class("Matrix", {
    props: {
      a: 1, c: 0, e: 0,
      b: 0, d: 1, f: 0
    },

    class_methods: {
      translate: function (offset) {
        return new this(1, 0, 0, 1, offset.x, offset.y)
      },

      scale: function (degree, anchor) {
        if (anchor) {
          return new this(degree, 0, 0, degree, anchor.x, anchor.y)
                     .multiplyI(1, 0, 0, 1, -anchor.x, -anchor.y);
        } else {
          return new this(degree, 0, 0, degree, 0, 0);
        }
      },

      rotate: function (r, anchor) {
        var cos = Math.cos(r), sin = Math.sin(r);
        if (anchor) {
          return new this(cos, sin, -sin, cos, anchor.x, anchor.y)
                     .multiplyI(1, 0, 0, 1, -anchor.x, -anchor.y);
        } else {
          return new this(cos, sin, -sin, cos, 0, 0);
        }
      }
    },

    methods: {
      init: function (a, b, c, d, e, f) {
        if (arguments.length == 6) {
          this.a = +a; this.c = +c; this.e = +e;
          this.b = +b; this.d = +d; this.f = +f;
        } else if (arguments.length != 0) {
          throw new ArgumentError("0 or 6 arguments expected");
        }
      },

      multiplyI: function (a2, b2, c2, d2, e2, f2) {
        return new this.constructor(
          this.a * a2 + this.c * b2,
          this.b * a2 + this.d * b2,
          this.a * c2 + this.c * d2,
          this.b * c2 + this.d * d2,
          this.a * e2 + this.c * f2 + this.e,
          this.b * e2 + this.d * f2 + this.f
        );
      },

      multiply: function (that) {
        return new this.constructor(
          this.a * that.a + this.c * that.b,
          this.b * that.a + this.d * that.b,
          this.a * that.c + this.c * that.d,
          this.b * that.c + this.d * that.d,
          this.a * that.e + this.c * that.f + this.e,
          this.b * that.e + this.d * that.f + this.f
        );
      },

      invert: function () {
        var me = this,
        x = me.a * me.d - me.b * me.c;
        return new this.constructor(
          me.d / x, -me.b / x, -me.c / x,
          me.a / x, (me.c * me.f - me.d * me.e) / x, (me.b * me.e - me.a * me.f) / x);
      },

      translate: function (offset) {
        return this.multiplyI(1, 0, 0, 1, offset.x, offset.y);
      },

      scale: function (degree, anchor) {
        if (anchor) {
          return this.multiplyI(degree, 0, 0, degree, anchor.x, anchor.y)
                     .multiplyI(1, 0, 0, 1, -cx, -cy);
        } else {
          return this.multiplyI(degree, 0, 0, degree, 0, 0);
        }
      },

      rotate:  function (r, anchor) {
        var cos = Math.cos(r), sin = Math.sin(r);
        if (anchor) {
          return this.multiplyI(cos, sin, -sin, cos, x, y)
                     .multiplyI(1, 0, 0, 1, -x, -y);
        } else {
          return this.multiplyI(cos, sin, -sin, cos, 0, 0);
        }
      },

      isUnit: function () {
        return this.a == 1 && this.b == 0 && this.c == 0 && this.d == 1;
      },

      isScaling: function() {
        return this.b == 0 && this.c == 0 && { x: this.a, y: this. d } || null;
      },

      apply: function(p) {
        return { x: (p.x * this.a) + (p.y * this.c) + this.e,
                 y: (p.x * this.b) + (p.y * this.d) + this.f };
      },

      get: function (i) {
        return this[String.fromCharCode(97 + i)];
      },

      toString: function () {
        return '{ ' + this.a + ', ' + this.b + ', ' + this.e + 
               '  ' + this.c + ', ' + this.d + ', ' + this.f + ' }';
      },

      offset: function () {
        return { x: this.e, y: this.f };
      },

      split: function () {
        var out = {};
        // translation
        out.dx = this.e;
        out.dy = this.f;

        // scale and shear
        var row = [[this.a, this.c], [this.b, this.d]];
        out.scalex = Math.sqrt(norm(row[0]));
        normalize(row[0]);

        out.shear = row[0][0] * row[1][0] + row[0][1] * row[1][1];
        row[1] = [row[1][0] - row[0][0] * out.shear, row[1][1] - row[0][1] * out.shear];

        out.scaley = Math.sqrt(norm(row[1]));
        normalize(row[1]);
        out.shear /= out.scaley;

        // rotation
        var sin = -row[0][1],
        cos = row[1][1];
        if (cos < 0) {
          out.rotate = R.deg(Math.acos(cos));
          if (sin < 0) {
            out.rotate = 360 - out.rotate;
          }
        } else {
          out.rotate = R.deg(Math.asin(sin));
        }

        out.isSimple = !+out.shear.toFixed(FLOAT_ACCURACY_ACCURATE) && (out.scalex.toFixed(FLOAT_ACCURACY_ACCURATE) == out.scaley.toFixed(FLOAT_ACCURACY_ACCURATE) || !out.rotate);
        out.isSuperSimple = !+out.shear.toFixed(FLOAT_ACCURACY_ACCURATE) && out.scalex.toFixed(FLOAT_ACCURACY_ACCURATE) == out.scaley.toFixed(FLOAT_ACCURACY_ACCURATE) && !out.rotate;
        out.noRotation = !+out.shear.toFixed(FLOAT_ACCURACY_ACCURATE) && !out.rotate;
        return out;
      },

      toTransformString: function (shorter) {
        var s = shorter || this[split]();
        if (s.isSimple) {
          s.scalex = +s.scalex.toFixed(FLOAT_ACCURACY);
          s.scaley = +s.scaley.toFixed(FLOAT_ACCURACY);
          s.rotate = +s.rotate.toFixed(FLOAT_ACCURACY);
          return  (s.dx || s.dy ? "t" + [s.dx, s.dy] : E) +
            (s.scalex != 1 || s.scaley != 1 ? "s" + [s.scalex, s.scaley, 0, 0] : E) +
            (s.rotate ? "r" + [s.rotate, 0, 0] : E);
        } else {
          return "m" + [this.get(0), this.get(1), this.get(2), this.get(3), this.get(4), this.get(5)];
        }
      }
    }
  });

  return _Matrix;

})();

var PathData = (function() {
  /**
   * M   moveto                           (x y)+
   * Z   closepath                        (none)
   * L   lineto                           (x y)+
   * H   horizontal lineto                x+
   * V   vertical lineto                  y+
   * C   curveto                          (x1 y1 x2 y2 x y)+
   * S   smooth curveto                   (x2 y2 x y)+
   * Q   quadratic Bezier curveto         (x1 y1 x y)+
   * T   smooth quadratic Bezier curveto  (x y)+
   * A   elliptical arc                   (rx ry x-axis-rotation large-arc-flag sweep-flag x y)+
   * R   Catmull-Rom curveto*x1 y1        (x y)+
   *
   **/
  var OPERATORS = {
    'Z': 'Z',
    'z': 'Z',
    'closePath': 'Z',
    'H': 'H',
    'h': 'h',
    'horizontalLineTo': 'H',
    'horizontalLineToRel': 'h',
    'V': 'V',
    'v': 'v',
    'verticalLineTo': 'V',
    'verticalLineToRel': 'v',
    'M': 'M',
    'm': 'm',
    'moveTo': 'M',
    'moveToRel': 'm',
    'L': 'L',
    'l': 'l',
    'lineTo': 'L',
    'lineToRel': 'l',
    'T': 'T',
    't': 't',
    'curveToSmoothQB': 'T',
    'curveToSmoothQBRel': 't',
    'R': 'R',
    'r': 'r',
    'curveToCR': 'R',
    'curveToCRRel': 'r',
    'S': 'S',
    's': 's',
    'curveToSmooth': 'S',
    'curveToSmoothRel': 's',
    'Q': 'Q',
    'q': 'q',
    'curveToQB': 'Q',
    'curveToQBRel': 'q',
    'C': 'C',
    'c': 'c',
    'curveTo': 'C',
    'curveToRel': 'c',
    'A': 'A',
    'a': 'a',
    'arc': 'A',
    'arcRel': 'a'
  };

  function PathDataBuilder(data) {
    this.data = data;
    this.last = { x: 0., y: 0. };
  };

  PathDataBuilder.prototype.parseNumber = function(v) {
    var retval = parseFloat(v);
    if (isNaN(retval))
      throw new ValueError("Invalid argument: " + v);
    return retval;
  };

  PathDataBuilder.prototype.addSegments = function(arr, i, l, op) {
    var arg_len = 0;
    switch (op) {
    case 'Z':
      if (l != 0)
        throw new ValueError("closePath takes no arguments, " + l + " given: " + arr.join(" "));
      this.data.push(['Z']); 
      break;

    case 'H':
      if (l == 0)
        throw new ValueError("horizontalLineTo takes at least 1 argument" + arr.join(" "));
      var x = 0.;
      for (var j = 0; j < l; j++) {
        x = this.parseNumber(arr[i + j]);
        this.data.push(['M', x, this.last.y]);
      }
      this.last.x = x;
      break;

    case 'h':
      if (l == 0)
        throw new ValueError("horizontalLineToRel takes at least 1 argument:" + arr.join(" "));
      var x = this.last.x;
      for (var j = 0; j < l; j++) {
        x += this.parseNumber(arr[i + j]);
        this.data.push(['M', x, this.last.y]);
      }
      this.last.x = x;
      break;

    case 'V':
      if (l == 0)
        throw new ValueError("verticalLineTo takes at least 1 argument: " + arr.join(" "));
      var y = 0.;
      for (var j = 0; j < l; j++) {
        y = this.parseNumber(arr[i + j]);
        this.data.push(['M', this.last.x, y]);
      }
      this.last.y = y;
      break;

    case 'v':
      if (l == 0)
        throw new ValueError("verticalLineToRel takes at least 1 argument: " + arr.join(" "));
      var y = this.last.y;
      for (var j = 0; j < l; j++) {
        y += this.parseNumber(arr[i + j]);
        this.data.push(['M', this.last.x, y]);
      }
      this.last.y = y;
      break;

    case 'M':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("moveTo takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.parseNumber(arr[i]), y = this.parseNumber(arr[i + 1]);
      this.data.push(['M', x, y]);
      for (var j = i + 2, n = i + l; j < n ; j += 2) {
        x = this.parseNumber(arr[j]), y = this.parseNumber(arr[j + 1]);
        this.data.push(['L', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'm':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("moveToRel takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x + this.parseNumber(arr[i]), y = this.last.y + this.parseNumber(arr[i + 1]);
      this.data.push(['M', x, y]);
      for (var j = i + 2, n = i + l; j < n ; j += 2) {
        x += this.parseNumber(arr[j]), y += this.parseNumber(arr[j + 1]);
        this.data.push(['L', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'L':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("lineTo takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j < n ; j += 2) {
        x = this.parseNumber(arr[j]), y = this.parseNumber(arr[j + 1]);
        this.data.push(['L', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'l':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("lineTo takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 2) {
        x += this.parseNumber(arr[j]), y += this.parseNumber(arr[j + 1]);
        this.data.push(['L', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'T':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("curveToSmoothQB takes 2 * n arguments, " + l + " given:" + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 2) {
        x = this.parseNumber(arr[j]), y = this.parseNumber(arr[j + 1]);
        this.data.push(['T', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 't':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("curveToSmoothQBRel takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 2) {
        x += this.parseNumber(arr[j]), y += this.parseNumber(arr[j + 1]);
        this.data.push(['T', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'R':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("curveToCR takes 2 * n arguments, " + l + " given:" + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 2) {
        x = this.parseNumber(arr[j]), y = this.parseNumber(arr[j + 1]);
        this.data.push(['R', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'r':
      if (l == 0 || l % 2 != 0)
        throw new ValueError("curveToCRRel takes 2 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 2) {
        x += this.parseNumber(arr[j]), y += this.parseNumber(arr[j + 1]);
        this.data.push(['R', x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'S':
      if (l == 0 || l % 4 != 0)
        throw new ValueError("curveToSmooth takes 4 * n arguments, " + l + " given: " + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 4) {
        var x2 = this.parseNumber(arr[j]), y2 = this.parseNumber(arr[j + 1]);
        x = this.parseNumber(arr[j + 2]), y = this.parseNumber(arr[j + 3]);
        this.data.push(['S', x2, y2, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 's':
      if (l == 0 || l % 4 != 0)
        throw new ValueError("curveToSmooth takes 4 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 4) {
        var x2 = x + this.parseNumber(arr[j]), y2 = y + this.parseNumber(arr[j + 1]);
        x += this.parseNumber(arr[j + 2]), y += this.parseNumber(arr[j + 3]);
        this.data.push(['S', x2, y2, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'Q':
      if (l == 0 || l % 4 != 0)
        throw new ValueError("curveToQB takes 4 * n arguments, " + l + " given: " + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 4) {
        var x1 = this.parseNumber(arr[j]), y1 = this.parseNumber(arr[j + 1]);
        x = this.parseNumber(arr[j + 2]), y = this.parseNumber(arr[j + 3]);
        this.data.push(['Q', x1, y1, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'q':
      if (l == 0 || l % 4 != 0)
        throw new ValueError("curveToQBRel takes 4 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 4) {
        var x1 = x + this.parseNumber(arr[j]), y1 = y + this.parseNumber(arr[j + 1]);
        x += this.parseNumber(arr[j + 2]), y += this.parseNumber(arr[j + 3]);
        this.data.push(['Q', x1, y1, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'C':
      if (l == 0 || l % 6 != 0)
        throw new ValueError("curveTo takes 6 * n arguments, " + l + " given: " + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 6) {
        var x1 = this.parseNumber(arr[j]), y1 = this.parseNumber(arr[j + 1]);
        var x2 = this.parseNumber(arr[j + 2]), y2 = this.parseNumber(arr[j + 3]);
        x = this.parseNumber(arr[j + 4]), y = this.parseNumber(arr[j + 5]);
        this.data.push(['C', x1, y1, x2, y2, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'c':
      if (l == 0 || l % 6 != 0)
        throw new ValueError("curveToRel takes 6 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 6) {
        x1 = x + this.parseNumber(arr[j]), y1 = y + this.parseNumber(arr[j + 1]);
        x2 = x + this.parseNumber(arr[j + 2]), y2 = y + this.parseNumber(arr[j + 3]);
        x += this.parseNumber(arr[j + 4]), y += this.parseNumber(arr[j + 5]);
        this.data.push(['C', x1, y1, x2, y2, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'A':
      if (l == 0 || l % 7 != 0)
        throw new ValueError("arc takes 7 * n arguments, " + l + " given: " + arr.join(" "));
      var x = 0., y = 0.;
      for (var j = i, n = i + l; j <n ; j += 7) {
        var rx = this.parseNumber(arr[j]), ry = y + this.parseNumber(arr[j + 1]);
        var x_axis_rotation = this.parseNumber(arr[j + 2]);
        var large_arc_flag = this.parseNumber(arr[j + 3]);
        var sweep_flag = this.parseNumber(arr[j + 4]);
        var x = this.parseNumber(arr[j + 5]), y = this.parseNumber(arr[j + 6]);
        this.data.push(['A', rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;

    case 'a':
      if (l == 0 || l % 7 != 0)
        throw new ValueError("arcRel takes 7 * n arguments, " + l + " given: " + arr.join(" "));
      var x = this.last.x, y = this.last.y;
      for (var j = i, n = i + l; j <n ; j += 7) {
        var rx = x + this.parseNumber(arr[j]), ry = y + this.parseNumber(arr[j + 1]);
        var x_axis_rotation = this.parseNumber(arr[j + 2]);
        var large_arc_flag = this.parseNumber(arr[j + 3]);
        var sweep_flag = this.parseNumber(arr[j + 4]);
        x += this.parseNumber(arr[j + 5]), y += this.parseNumber(arr[j + 6]);
        this.data.push(['A', rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y]);
      }
      this.last.x = x, this.last.y = y;
      break;
    }
  };

  return _class('PathData', {
    props: {
      length: 0
    },

    methods: {
      init: function PathData_init(points) {
        if (typeof points === 'string' || points instanceof String) {
          this.initWithString(points);
        } else if (points instanceof Array) {
          this.initWithArray(points);
        }
      },

      initWithString: function PathData_initWithString(str) {
        var x, atom, arglen_now, seg, last_idt;
        var arr = str.match(/-?((?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|[A-Za-z_]+/g);
        var builder = new PathDataBuilder(this);
        for (var i = 0, n; i < arr.length; i = n) {
          var op;
          if (!(op = OPERATORS[arr[i]]))
            throw new ValueError('Unexpected operator "' + arr[i] + '"');

          i++;

          n = i;
          while (n < arr.length && !(arr[n] in OPERATORS)) n++;
          builder.addSegments(arr, i, n - i, op);
        }
      },

      initWithArray: function PathData_initWithArray(arr) {
        var builder = new PathDataBuilder(this);
        for (var i = 0; i < arr.length; i++) {
          var seg = arr[i];
          var op;
          if (!(op = operators[seg[0]]))
            throw new valueerror('unexpected operator "' + arr[i] + '"');
          builder.addSegments(arr, 1, seg.length, op);
        }
      },

      applyMatrix: function PathData_applyMatrix(matrix) {
        var x = 0, y = 0;
        for (var i = 0; i < this.length; i++) {
          var seg = this[i];
          switch (seg[0]) {
          case 'Z':
            break;

          case 'M':
          case 'L':
          case 'T':
          case 'R':
            var p = matrix.apply({ x: seg[1], y: seg[2] });
            seg[1] = p.x, seg[2] = p.y;
            break;

          case 'S':
          case 'Q':
            var p = matrix.apply({ x: seg[1], y: seg[2] });
            seg[1] = p.x, seg[2] = p.y;
            var q = matrix.apply({ x: seg[3], y: seg[4] });
            seg[3] = q.x, seg[4] = q.y;
            break;

          case 'C':
            var p = matrix.apply({ x: seg[1], y: seg[2] });
            seg[1] = p.x, seg[2] = p.y;
            var q = matrix.apply({ x: seg[3], y: seg[4] });
            seg[3] = q.x, seg[4] = q.y;
            var r = matrix.apply({ x: seg[5], y: seg[6] });
            seg[5] = r.x, seg[6] = r.y;
            break;

          case 'A':
            var p = matrix.apply({ x: seg[1], y: seg[2] });
            seg[1] = p.x, seg[2] = p.y;
            var q = matrix.apply({ x: seg[7], y: seg[8] });
            seg[7] = q.x, seg[8] = q.y;
            break;
          }
        }
      },

      push: Array.prototype.push,

      join: Array.prototype.join,

      slice: Array.prototype.slice
    }
  });
})();

var commandMap = {
    'Z': 'h',
    'M': 'm',
    'L': 'l',
    'C': 'c'
};

fs.readFile(process.argv[2], 'utf-8', function(err, pathstr) {
    if (err) throw err;
    var pathData = new PathData(pathstr);
    pathData.applyMatrix(Matrix.translate({ x:112, y:0 }).scale(0.14));
    var out = ['1e-3', 'S'];
    for (var i = 0; i < pathData.length; i++) {
        for (var j = 1; j < pathData[i].length; j++) {
            out.push((pathData[i][j] * 1000).toFixed(0));
        }
        out.push(commandMap[pathData[i][0]]);
    }
    console.log(out.join(" "));
});
