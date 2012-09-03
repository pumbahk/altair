/** @file main.js { */
var Fashion = (function() {
  var Fashion = this;

/** @file constants.js { */
this.DIRTY_TRANSFORM      = 0x00000001;
this.DIRTY_POSITION       = 0x00000002;
this.DIRTY_SIZE           = 0x00000004;
this.DIRTY_SHAPE          = 0x00000008;
this.DIRTY_ZINDEX         = 0x00000010;
this.DIRTY_STYLE          = 0x00000020;
this.DIRTY_VISIBILITY     = 0x00000040;
this.DIRTY_EVENT_HANDLERS = 0x00000080;
/** @} */

/** @file lib.js { */
var _lib = {};

/** @file browser.js { */
var detectBrowser = function(window) {
  if (!window) {
    return {
      name:             'unknown',
      identifier:       'unknown',
      version:          0,
      precise_version:  0,
      application_name: 'unknown',
      user_agent:       '-'
    };
  }

  var nVer = window.navigator.appVersion;
  var nAgt = window.navigator.userAgent;
  var browserName  = window.navigator.appName;
  var fullVersion  = ''+parseFloat(window.navigator.appVersion);
  var majorVersion = parseInt(window.navigator.appVersion,10);
  var nameOffset,verOffset,ix;
  var identifier;

  // In Opera, the true version is after "Opera" or after "Version"
  if ((verOffset=nAgt.indexOf("Opera"))!=-1) {
    browserName = "Opera";
    identifier = 'op';
    fullVersion = nAgt.substring(verOffset+6);
    if ((verOffset=nAgt.indexOf("Version"))!=-1)
      fullVersion = nAgt.substring(verOffset+8);
  }
  // In MSIE, the true version is after "MSIE" in userAgent
  else if ((verOffset=nAgt.indexOf("MSIE"))!=-1) {
    browserName = "Microsoft Internet Explorer";
    identifier = 'ie';
    fullVersion = nAgt.substring(verOffset+5);
  }
  // In Chrome, the true version is after "Chrome"
  else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
    browserName = "Chrome";
    identifier = 'ch';
    fullVersion = nAgt.substring(verOffset+7);
  }
  // In Safari, the true version is after "Safari" or after "Version"
  else if ((verOffset=nAgt.indexOf("Safari"))!=-1) {
    browserName = "Safari";
    identifier = 'saf';
    fullVersion = nAgt.substring(verOffset+7);
    if ((verOffset=nAgt.indexOf("Version"))!=-1)
      fullVersion = nAgt.substring(verOffset+8);
  }
  // In Firefox, the true version is after "Firefox"
  else if ((verOffset=nAgt.indexOf("Firefox"))!=-1) {
    browserName = "Firefox";
    identifier = 'fx';
    fullVersion = nAgt.substring(verOffset+8);
  }
  // In most other browsers, "name/version" is at the end of userAgent
  else if ((nameOffset=nAgt.lastIndexOf(' ')+1) < (verOffset=nAgt.lastIndexOf('/')))
  {
    identifier = 'other';
    browserName = nAgt.substring(nameOffset,verOffset);
    fullVersion = nAgt.substring(verOffset+1);
    if (browserName.toLowerCase()==browserName.toUpperCase()) {
      browserName = navigator.appName;
    }
  }
  // trim the fullVersion string at semicolon/space if present
  if ((ix=fullVersion.indexOf(";"))!=-1)
    fullVersion=fullVersion.substring(0,ix);
  if ((ix=fullVersion.indexOf(" "))!=-1)
    fullVersion=fullVersion.substring(0,ix);

  majorVersion = parseInt(''+fullVersion,10);
  if (isNaN(majorVersion)) {
    fullVersion  = ''+parseFloat(navigator.appVersion);
    majorVersion = parseInt(navigator.appVersion,10);
  }

  return {
    name:             browserName,
    identifier:       identifier,
    version:          majorVersion,
    precise_version:  fullVersion,
    application_name: navigator.appName,
    user_agent:       navigator.userAgent
  };
};

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
_lib.detectBrowser = detectBrowser;
var BROWSER = detectBrowser(typeof window == 'undefined' ? void(0): window);

/** @file assert.js { */
function __assert__(predicate) {
  if (!predicate)
    throw new AssertionFailure();
}
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
_lib.__assert__            = __assert__;

/** @file misc.js { */
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
/** @} */
_lib._atomic_p             = _atomic_p;
_lib._clone                = _clone;
_lib.xparseInt             = xparseInt;
_lib._repeat               = _repeat;
_lib._lpad                 = _lpad;
_lib._clip                 = _clip;
_lib.clipPoint             = _clipPoint;
_lib.addPoint              = _addPoint;
_lib.subtractPoint         = _subtractPoint;
_lib.escapeXMLSpecialChars = _escapeXMLSpecialChars;
_lib._bindEvent            = _bindEvent;
_lib._unbindEvent          = _unbindEvent;

/** @file error.js { */
var FashionError = function(message) {
  Error.apply(this, arguments);
  if (typeof Error.captureStackTrace !== 'undefined')
    Error.captureStackTrace(this, this.constructor);
  this.message = message;
};
FashionError.prototype = new Error();

var createExceptionClass = function(exceptionClassName) {
  var exceptionClass = function() { FashionError.apply(this, arguments); };
  exceptionClass.prototype = new FashionError();
  exceptionClass.prototype.name = exceptionClassName;
  return exceptionClass;
}
var NotImplemented   = createExceptionClass('NotImplemented');
var ValueError       = createExceptionClass('ValueError');
var PropertyError    = createExceptionClass('PropertyError');
var NotSupported     = createExceptionClass('NotSupported');
var ArgumentError    = createExceptionClass('ArgumentError');
var NotAttached      = createExceptionClass('NotAttached');
var NotFound         = createExceptionClass('NotFound');
var AlreadyExists    = createExceptionClass('AlreadyExists');
var DeclarationError = createExceptionClass('DeclarationError');
var AssertionFailure = createExceptionClass('AssertionFailure');
/** @} */
_lib.FashionError          = FashionError;
_lib.createExceptionClass  = createExceptionClass;
_lib.NotImplemented        = NotImplemented;
_lib.ValueError            = ValueError;
_lib.PropertyError         = PropertyError;
_lib.NotSupported          = NotSupported;
_lib.ArgumentError         = ArgumentError;
_lib.NotAttached           = NotAttached;
_lib.NotFound              = NotFound;
_lib.AlreadyExists         = AlreadyExists;

/** @file classify.js { */
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
/** @} */
_lib._class = _class;
/** @} */
  Fashion._lib = _lib;

  var _window = typeof window == 'undefined' ? void(0): window;
  var _Image = _window && typeof _window.Image !== 'undefined' ? _window.Image: null;

  this.browser = detectBrowser(_window);
  this.window = _window;

  var determineImplementation = function determineImplementation(priority) {
    for (var i = 0, l = priority.length; i < l; i++) {
      var target = priority[i].toLowerCase();
      if (target === 'svg' && Fashion.Backend.SVG)
        return Fashion.Backend.SVG;
      else if (target === 'vml' && Fashion.Backend.VML)
        return Fashion.Backend.VML;
      else if (target === 'canvas' && Fashion.Backend.Canvas)
        return Fashion.Backend.Canvas;
    }
    
    function unsupported() {
      throw new NotSupported('Browser is not supported');
    }
    
    return {
      Shape    : unsupported,
      Circle   : unsupported,
      Rect     : unsupported,
      Path     : unsupported,
      Text     : unsupported,
      Drawable : unsupported
    };
  };

  var onceOnLoad = (function () {
    var pending = [];
    var loaded = false;

    if (_window) {
      _bindEvent(_window, 'load', function () {
        loaded = true;
        _unbindEvent(_window, 'load', arguments.callee);
        while (pending.length)
          (pending.shift())();
      });
    
      return function onceOnLoad(f) {
        if (loaded)
          f();
        else
          pending.push(f);
      };
    } else {
      return function onceOnLoad(f) {
        f();
      }
    }
  })();

/** @file Matrix.js { */
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
        if (offset ===  void(0))
          return { x: this.e, y: this.f };
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
/** @} */
  this.Matrix = Matrix;

/** @file backend.js { */
var Backend = (function() {
/** @file Refresher.js { */
var Refresher = _class("Refresher", {
  props: {
    _preHandler: null,
    _postHandler: null,
    _handlers: []
  },

  methods: {
    init: function (original) {
      if (original instanceof this.constructor) {
        this._preHandler = original._preHandler;
        this._postHandler = original._postHandler;
        this._handlers = original._handlers.slice(0);
      }
    },

    setup: function(args) {
      for (var i in args)
        this[i].call(this, args[i]);
      return this;
    },

    preHandler: function(pre) {
      this._preHandler = pre;
    },

    postHandler: function(post) {
      this._postHandler = post;
    },

    handlers: function(pairs) {
      this._handlers = pairs;
    },

    moreHandlers: function(pairs) {
      this._handlers = this._handlers.concat(pairs);
    },

    add: function(pair) {
      this._handlers.push(pair);
    },

    call: function (target, dirty) {
      var originalDirty = dirty;
      if (this._preHandler) {
        var _dirty = this._preHandler.call(target, dirty);
        if (_dirty !== void(0))
          dirty = _dirty;
      }
      if (dirty) {
        for (var i = 0; i < this._handlers.length; i++) {
          var pair = this._handlers[i];
          if (dirty & pair[0])
            pair[1].call(target, dirty);
        }
      }
      this._postHandler && this._postHandler.call(target, dirty, originalDirty);
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file TransformStack.js { */
var TransformStack = _class("TransformStack", {
  props: {
    stack: [],
    pairs: {},
    endOfFirst: 0,
    beginningOfLast: 0
  },

  methods: {
    init: function () {
    },

    add: function (disposition, key, matrix) {
      var pair = this.pairs[key];
      if (pair) {
        pair[1] = matrix;
        return false;
      }
      switch (disposition.toLowerCase()) {
      case 'first':
        pair = [key, matrix];
        this.pairs[key] = pair;
        this.stack.unshift(pair);
        this.endOfFirst++;
        this.beginningOfLast++;
        break;
      case 'afterfirst':
        pair = [key, matrix];
        this.pairs[key] = pair;
        this.stack.splice(this.endOfFirst, 0, pair);
        this.beginningOfLast++;
        break;
      case 'beforelast':
        pair = [key, matrix];
        this.pairs[key] = pair;
        this.stack.splice(this.beginningOfLast, 0, pair);
        this.beginningOfLast++;
        break;
      case 'last':
        pair = [key, matrix];
        this.pairs[key] = pair;
        this.stack.push(pair);
        break;
      default:
        throw new Fashion.ArgumentError("Invalid disposition: " + disposition);
      }
      return true;
    },

    remove: function (key) {

      if (!(key in this.pairs)) return;

      var i = 0;
      for (;;) {
        if (i >= this.stack.length)
          throw new Fashion.NotFound("???"); // should not happen
        if (this.stack[i][0] == key)
          break;
        i++;
      }
      this.stack.splice(i, 1);
      if (i < this.endOfFirst)
        this.endOfFirst--;
      if (i < this.beginningOfLast)
        this.beginningOfLast--;
      delete this.pairs[key];
    },

    get: function () {
      if (this.stack.length == 0)
        return null;
      var matrix = this.stack[0][1];
      for (var i = 1; i < this.stack.length; i++)
        matrix = matrix.multiply(this.stack[i][1]);
      return matrix;
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */

  var getDomOffsetPosition = (function () {
    var support_box_model =  (_window && _window.document.compatMode === "CSS1Compat");

    var contains = (function() {
      if ( _window && _window.document.documentElement.contains ) {
        return function( a, b ) {
          return a !== b && (a.contains ? a.contains(b) : true);
        };

      } else if ( _window && _window.document.documentElement.compareDocumentPosition ) {
        return function( a, b ) {
          return !!(a.compareDocumentPosition(b) & 16);
        };

      } else {
        return function() {
          return false;
        };
      }
    })();

    if ( _window && "getBoundingClientRect" in _window.document.documentElement ) {
      return function getDomOffsetPosition_boundingClientRect(elem, doc, docElem, box ) {
        doc = document; docElem = document.documentElement;

        try {
          box = elem.getBoundingClientRect();
        } catch(e) {}

        if ( !box || !contains( docElem, elem ) ) {
          return box ? { top: box.top, left: box.left } : { top: 0, left: 0 };
        }

        var body = doc.body,
        clientTop  = docElem.clientTop  || body.clientTop  || 0,
        clientLeft = docElem.clientLeft || body.clientLeft || 0,
        scrollTop  = _window.pageYOffset || support_box_model && docElem.scrollTop  || body.scrollTop,
        scrollLeft = _window.pageXOffset || support_box_model && docElem.scrollLeft || body.scrollLeft,
        top  = box.top  + scrollTop  - clientTop,
        left = box.left + scrollLeft - clientLeft;

        return { x: left, y: top };
      };
    } else {
      return function getDomOffsetPosition(elem) {
        var curleft = 0, curtop = 0;
        if (elem.offsetParent) {
          do {
            curleft += elem.offsetLeft;
            curtop += elem.offsetTop;

          } while (elem = elem.offsetParent);
        }
        return {x: curleft, y: curtop};
      };
    }
  })();


  return {
    Refresher      : Refresher,
    TransformStack : TransformStack,
    getDomOffsetPosition: getDomOffsetPosition
  };

})();
/** @} */
  this.Backend = Backend;

/** @file Color.js { */
var Color = (function() {
  var color_code_table = {
    aliceblue: [240, 248, 255, 255], 
    antiquewhite: [250, 235, 215, 255], 
    aqua: [0, 255, 255, 255], 
    aquamarine: [127, 255, 212, 255], 
    azure: [240, 255, 255, 255], 
    beige: [245, 245, 220, 255], 
    bisque: [255, 228, 196, 255], 
    black: [0, 0, 0, 255], 
    blanchedalmond: [255, 235, 205, 255], 
    blue: [0, 0, 255, 255], 
    blueviolet: [138, 43, 226, 255], 
    brown: [165, 42, 42, 255], 
    burlywood: [222, 184, 135, 255], 
    cadetblue: [95, 158, 160, 255], 
    chartreuse: [127, 255, 0, 255], 
    chocolate: [210, 105, 30, 255], 
    coral: [255, 127, 80, 255], 
    cornflowerblue: [100, 149, 237, 255], 
    cornsilk: [255, 248, 220, 255], 
    crimson: [220, 20, 60, 255], 
    cyan: [0, 255, 255, 255], 
    darkblue: [0, 0, 139, 255], 
    darkcyan: [0, 139, 139, 255], 
    darkgoldenrod: [184, 134, 11, 255], 
    darkgray: [169, 169, 169, 255], 
    darkgreen: [0, 100, 0, 255], 
    darkgrey: [169, 169, 169, 255], 
    darkkhaki: [189, 183, 107, 255], 
    darkmagenta: [139, 0, 139, 255], 
    darkolivegreen: [85, 107, 47, 255], 
    darkorange: [255, 140, 0, 255], 
    darkorchid: [153, 50, 204, 255], 
    darkred: [139, 0, 0, 255], 
    darksalmon: [233, 150, 122, 255], 
    darkseagreen: [143, 188, 143, 255], 
    darkslateblue: [72, 61, 139, 255], 
    darkslategray: [47, 79, 79, 255], 
    darkslategrey: [47, 79, 79, 255], 
    darkturquoise: [0, 206, 209, 255], 
    darkviolet: [148, 0, 211, 255], 
    deeppink: [255, 20, 147, 255], 
    deepskyblue: [0, 191, 255, 255], 
    dimgray: [105, 105, 105, 255], 
    dimgrey: [105, 105, 105, 255], 
    dodgerblue: [30, 144, 255, 255], 
    firebrick: [178, 34, 34, 255], 
    floralwhite: [255, 250, 240, 255], 
    forestgreen: [34, 139, 34, 255], 
    fuchsia: [255, 0, 255, 255], 
    gainsboro: [220, 220, 220, 255], 
    ghostwhite: [248, 248, 255, 255], 
    gold: [255, 215, 0, 255], 
    goldenrod: [218, 165, 32, 255], 
    gray: [128, 128, 128, 255], 
    green: [0, 128, 0, 255], 
    greenyellow: [173, 255, 47, 255], 
    grey: [128, 128, 128, 255], 
    honeydew: [240, 255, 240, 255], 
    hotpink: [255, 105, 180, 255], 
    indianred: [205, 92, 92, 255], 
    indigo: [75, 0, 130, 255], 
    ivory: [255, 255, 240, 255], 
    khaki: [240, 230, 140, 255], 
    lavender: [230, 230, 250, 255], 
    lavenderblush: [255, 240, 245, 255], 
    lawngreen: [124, 252, 0, 255], 
    lemonchiffon: [255, 250, 205, 255], 
    lightblue: [173, 216, 230, 255], 
    lightcoral: [240, 128, 128, 255], 
    lightcyan: [224, 255, 255, 255], 
    lightgoldenrodyellow: [250, 250, 210, 255], 
    lightgray: [211, 211, 211, 255], 
    lightgreen: [144, 238, 144, 255], 
    lightgrey: [211, 211, 211, 255], 
    lightpink: [255, 182, 193, 255], 
    lightsalmon: [255, 160, 122, 255], 
    lightseagreen: [32, 178, 170, 255], 
    lightskyblue: [135, 206, 250, 255], 
    lightslategray: [119, 136, 153, 255], 
    lightslategrey: [119, 136, 153, 255], 
    lightsteelblue: [176, 196, 222, 255], 
    lightyellow: [255, 255, 224, 255], 
    lime: [0, 255, 0, 255], 
    limegreen: [50, 205, 50, 255], 
    linen: [250, 240, 230, 255], 
    magenta: [255, 0, 255, 255], 
    maroon: [128, 0, 0, 255], 
    mediumaquamarine: [102, 205, 170, 255], 
    mediumblue: [0, 0, 205, 255], 
    mediumorchid: [186, 85, 211, 255], 
    mediumpurple: [147, 112, 219, 255], 
    mediumseagreen: [60, 179, 113, 255], 
    mediumslateblue: [123, 104, 238, 255], 
    mediumspringgreen: [0, 250, 154, 255], 
    mediumturquoise: [72, 209, 204, 255], 
    mediumvioletred: [199, 21, 133, 255], 
    midnightblue: [25, 25, 112, 255], 
    mintcream: [245, 255, 250, 255], 
    mistyrose: [255, 228, 225, 255], 
    moccasin: [255, 228, 181, 255], 
    navajowhite: [255, 222, 173, 255], 
    navy: [0, 0, 128, 255], 
    oldlace: [253, 245, 230, 255], 
    olive: [128, 128, 0, 255], 
    olivedrab: [107, 142, 35, 255], 
    orange: [255, 165, 0, 255], 
    orangered: [255, 69, 0, 255], 
    orchid: [218, 112, 214, 255], 
    palegoldenrod: [238, 232, 170, 255], 
    palegreen: [152, 251, 152, 255], 
    paleturquoise: [175, 238, 238, 255], 
    palevioletred: [219, 112, 147, 255], 
    papayawhip: [255, 239, 213, 255], 
    peachpuff: [255, 218, 185, 255], 
    peru: [205, 133, 63, 255], 
    pink: [255, 192, 203, 255], 
    plum: [221, 160, 221, 255], 
    powderblue: [176, 224, 230, 255], 
    purple: [128, 0, 128, 255], 
    red: [255, 0, 0, 255], 
    rosybrown: [188, 143, 143, 255], 
    royalblue: [65, 105, 225, 255], 
    saddlebrown: [139, 69, 19, 255], 
    salmon: [250, 128, 114, 255], 
    sandybrown: [244, 164, 96, 255], 
    seagreen: [46, 139, 87, 255], 
    seashell: [255, 245, 238, 255], 
    sienna: [160, 82, 45, 255], 
    silver: [192, 192, 192, 255], 
    skyblue: [135, 206, 235, 255], 
    slateblue: [106, 90, 205, 255], 
    slategray: [112, 128, 144, 255], 
    slategrey: [112, 128, 144, 255], 
    snow: [255, 250, 250, 255], 
    springgreen: [0, 255, 127, 255], 
    steelblue: [70, 130, 180, 255], 
    tan: [210, 180, 140, 255], 
    teal: [0, 128, 128, 255], 
    thistle: [216, 191, 216, 255], 
    tomato: [255, 99, 71, 255], 
    turquoise: [64, 224, 208, 255], 
    violet: [238, 130, 238, 255], 
    wheat: [245, 222, 179, 255], 
    white: [255, 255, 255, 255], 
    whitesmoke: [245, 245, 245, 255], 
    yellow: [255, 255, 0, 255], 
    yellowgreen: [154, 205, 50, 255]
  };

  return _class('Color', {
    props: {
      r: 0,
      g: 0,
      b: 0,
      a: 255
    },

    methods: {
      init: function Color_init() {
        switch (arguments.length) {
        case 0:
          break;
        case 1:
          return this.initWithColorCode(arguments[0]);
        case 3:
        case 4:
          return this.initWithRGBA.apply(this, arguments);
        default:
          throw new ArgumentError("constructor expects 0, 1, 3 or 4 arguments, got " + arguments.length);
        }
      },

      initWithColorCode: function Color_initWithColorCode(str) {
        var rt;
        if (!(rt = color_code_table[str])) {
          var g = /^\s*(?:#(?:([0-9A-Fa-f])([0-9A-Fa-f])([0-9A-Fa-f])|([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})?)|rgb\(([^)]*)\)|rgba\(([^)]*)\))\s*$/.exec(str);
          if (!g)
            throw new ValueError("Invalid color specifier: " + str);

          rt = [0, 0, 0, 255];
          if (g[1]) {
            for (var i = 1; i <= 3; i++) {
              var v = xparseInt(g[i], 16);
              rt[i - 1] = v | (v << 4);
            }
          } else if (g[4]) {
            for (var i = 4; i <= 7 && g[i]; i++)
              rt[i - 4] = xparseInt(g[i], 16);
          } else if (g[8]) {
            var s = g[8].split(/\s*,\s*/);
            if (s.length != 3)
              throw new ValueError("Invalid color specifier: " + str);
            for (var i = 0; i < 3; i++)
              rt[i] = xparseInt(s[i]);
          } else if (g[9]) {
            var s = g[9].split(/\s*,\s*/);
            if (s.length != 4)
              throw new ValueError("Invalid color specifier: " + str);
            for (var i = 0; i < 4; i++)
              rt[i] = xparseInt(s[i]);
          }
        }

        this.r = 0|rt[0];
        this.g = 0|rt[1];
        this.b = 0|rt[2];
        this.a = 0|rt[3];
      },

      initWithRGBA: function Color_initWithRGBA(r, g, b, a) {
        this.r = 0|r;
        this.g = 0|g;
        this.b = 0|b;
        if (a === null)
          this.a = null;
        else if (a !== void(0))
          this.a = 0|a;
      },

      replace: function(r, g, b, a) {
        return new this.constructor(
            r !== null ? r: this.r,
            g !== null ? g: this.g,
            b !== null ? b: this.b,
            a !== null ? a: this.a);
      },

      toString: function(without_alpha) {
        return this._toString(without_alpha);
      },

      _toString: function(without_alpha) {
        return '#' + _lpad(this.r.toString(16), 2, '0')
                   + _lpad(this.g.toString(16), 2, '0')
                   + _lpad(this.b.toString(16), 2, '0')
                   + (this.a !== null && !without_alpha ?
                      _lpad(this.a.toString(16), 2, '0'): '');
      },

      valueOf: function() {
        return this.toString();
      }
    }
  });
})();
/** @} */
  this.Color = Color;

/** @file Stroke.js { */
var Stroke = (function() {
  var predefined_patterns = {
    'solid':  [],
    'dotted': [1, 1],
    'dashed': [2, 2],
    'double': []
  };

  return _class("Stroke", {
    props: {
      color: null,
      width: null,
      pattern: null
    },
 
    class_methods: {
      parseDashString: function Stroke_parseDashString(str) {
        var retval;
        if ((retval = predefined_patterns[str]))
          return retval;

        retval = [];
        var last = '-';
        var segment_length = 0;
        for (var i in str) {
          var c = str[i];
          if (c != '-' && c != '_')
            throw new ValueError("Invalid character: '" + c + "' occurred in " + str);
          if (last != str[i]) {
            retval.push(segment_length);
            segment_length = 0;
            last = c;
          }
          segment_length++;
        }
        retval.push(segment_length);
        return retval;
      }
    },

    methods: {
      init: function Stroke_init() {
        switch (arguments.length) {
        case 0:
          break;
        case 1:
          if (typeof arguments[0] == 'string' || arguments[0] instanceof String) {
            this.initWithString.apply(this, arguments);
            break;
          }
          /* fall throigh */
        case 2:
        case 3:
          this.initWithArguments.apply(this, arguments);
          break;
        default:
          throw new ArgumentError("constructor expects 0, 1, 2 or 3 arguments, got " + arguments.length);
        }
      },
  
      initWithArguments: function Stroke_initWithArguments(color, width, pattern) {
        this.color = color;
        this.width = width === void(0) ? null: width;
        this.pattern = pattern === void(0) ? null: pattern;
      },
  
      initWithString: function Stroke_initWithString(str) {
        var rt = null;
  
        var tokens = str.split(/\s+/);
        if (tokens[0] == '')
          tokens.shift();
        if (tokens[tokens.length - 1] == '')
          tokens.pop();
        if (tokens.length == 0 || tokens.length > 3)
          throw new ValueError("Invalid number of tokens: " + str);
  
        this.initWithArguments(
          new Color(tokens[0]),
          tokens.length >= 2 ? xparseInt(tokens[1]): null,
          tokens.length >= 3 ? this.constructor.parseDashString(tokens[2]): null
        );
      }
    }
  });
})();

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
  this.Stroke = Stroke;

/** @file Fill.js { */
var Fill = _class("Fill", {
  props: {},
  methods: {}
});

var FloodFill = _class("FloodFill", {
  parent: Fill,

  props: {
    color: new Color()
  },

  methods: {
    init: function(color) {
      this.color = color;
    }
  }
});

var GradientFill = _class("GradientFill", {
  parent: Fill,

  props: {
    colors: []
  },

  methods: {
    init: function(colors) {
      this.colors = colors;
    }
  }
});

var LinearGradientFill = _class("LinearGradientFill", {
  parent: GradientFill,

  props: {
    angle: 0
  },

  methods: {
    init: function(colors, angle) {
      this.__super__().init.call(this, colors);
      this.angle = angle;
    }
  }
});

var RadialGradientFill = _class("RadialGradientFill", {
  parent: GradientFill,

  props: {
    focus: { x: "50%", y: "50%" }
  },

  methods: {
    init: function(colors, focus) {
      this.__super__().init.call(this, colors);
      this.focus = focus;
    }
  }
});

var ImageTileFill = _class("ImageTileFill", {
  parent: Fill,

  props: {
    url: null,
    imageData: null
  },

  methods: {
    init: function(imageData) {
      this.imageData = imageData;
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
  this.Fill = Fill;
  this.FloodFill = FloodFill;
  this.GradientFill = GradientFill;
  this.LinearGradientFill = LinearGradientFill;
  this.RadialGradientFill = RadialGradientFill;
  this.ImageTileFill = ImageTileFill;

/** @file ImageData.js { */
var ImageData = _class('ImageData', {
  props: {
    url: null,
    node: null,
    _size: null,
    callbacks: null
  },

  methods: {
    init: function ImageData_init(url) {
      this.url = url;
      this.node = new _Image();

      this.callbacks = [];
      var self = this;
      onceOnLoad(function () {
        self._size = { width: self.node.width, height: self.node.height };
        while (self.callbacks.length)
          (self.callbacks.shift())(self._size);
      });

      this.node.src = url;
    },

    size: function ImageData_size(f) {
      if (this._size !== null)
        f(this._size);
      else
        this.callbacks.push(f);
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
  this.ImageData = ImageData;

/** @file PathData.js { */
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
      var x = this.parseNumber(arr[i]) + this.last.x, y = this.parseNumber(arr[i + 1]) + this.last.y;
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
        var rx = this.parseNumber(arr[j]), ry = this.parseNumber(arr[j + 1]);
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
        var rx = this.parseNumber(arr[j]), ry = this.parseNumber(arr[j + 1]);
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
          if (!(op = OPERATORS[seg[0]]))
            throw new ValueError('Unexpected operator "' + arr[i] + '"');
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
/** @} */
  this.PathData = PathData;

/** @file MouseEvt.js { */
var MouseEvt = _class("MouseEvt", {

  props: {
    type: null,
    target: null,
    logicalPosition:   { x: 0, y: 0 },
    physicalPosition:  { x: 0, y: 0 },
    screenPosition:    { x: 0, y: 0 },
    offsetPosition:    { x: 0, y: 0 },
    left:            false,
    middle:          false,
    right:           false
  },

  methods: {}
});
/** @} */
  this.MouseEvt = MouseEvt;

/** @file VisualChangeEvt.js { */
var VisualChangeEvt = _class("VisualChangeEvt", {
  props: {
    type: 'visualchange',
    target: null,
    dirty: 0
  },

  methods: {}
});

/** @} */
  this.VisualChangeEvt = VisualChangeEvt;

/** @file ScrollEvt.js { */
var ScrollEvt = _class("ScrollEvt", {

  props: {
    type: 'scroll',
    target: null,
    logicalPosition:   { x: 0, y: 0 },
    physicalPosition:  { x: 0, y: 0 }
  },

  methods: {}
});
/** @} */
  this.ScrollEvt = ScrollEvt;

/** @file MouseEventsHandler.js { */
var MouseEventsHandler = _class("MouseEventsHandler", {
  props : {
    _handlersMap: {},
    _target: null
  },

  methods: {
    init: function(target, events) {
      this._target = target;
      for (var i in events)
        this._handlersMap[events[i]] = [];
    },

    getHandlerFunctionsFor: function(type) {
      var funcs = this._handlersMap[type];
      if (!funcs)
        throw new NotSupported("Unexpected keyword '" + type + "'.");
      return funcs;
    },

    add: function(type, h) {
      if (arguments.length == 2 && typeof h == 'function') {
        var handlers = this._handlersMap[type];
        if (!handlers)
          throw new NotSupported("Unsupported event type: '" + type + "'.");
        if (_indexOf(handlers, h) >= 0)
          return false;
        handlers.push(h);
        return true;
      } else if (arguments.length == 1) {
        for (var _type in type)
          this.add(_type, type[_type]);
        return true;
      } else {
        throw new ArgumentError("Unexpected argument: " + type);
      }
    },

    remove: function(type, h) {
      var handlers = this._handlersMap[type];
      var i = _indexOf(handlers, h);
      if (i < 0)
        throw new NotFound("The function is not Found in this Handler.");
      handlers.splice(i, 1);
    },

    removeAll: function (types) {
      var l = arguments.length;
      if (l == 0) {
        for (var i in this._handlersMap) this._handlersMap[i] = [];
      } else {
        for (var i = 0; i < l; i++) {
          this._handlersMap[arguments[i]] = [];
        }
      }
    },

    dispatch: function (evt) {
      var handlers = this._handlersMap[evt.type];
      if (handlers === void(0))
        return false;
      for (var i = 0; i < handlers.length; i++)
        handlers[i].call(this._target, evt);
      return true;
    },

    handles: function (type) {
      var handlers = this._handlersMap[type];
      return handlers && handlers.length > 0;
    }
  }
});
/** @} */
  this.MouseEventsHandler = MouseEventsHandler;

/** @file BatchUpdater.js { */
var BatchUpdater = _class('BatchUpdater', {
  methods: {
    schedule: function (shape, updateFunc) {}
  }
});

var BasicBatchUpdater = _class('BasicBatchUpdater', {
  interfaces: [BatchUpdater],

  props: {
    queue: []
  },

  methods: {
    schedule: function (shape, updateFunc) {
      for (var i = 0; i < this.queue.length; i++) {
        if (this.queue[i][0] === shape &&
            this.queue[i][1] === updateFunc) {
          this.queue.splice(i, 1);
          break;
        }
      }
      this.queue.push([shape, updateFunc]);
    },

    update: function () {
      for (var i = 0; i < this.queue.length; i++) {
        var entry = this.queue[i];
        entry[1].call(entry[0]);
      }
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
  this.BatchUpdater = BatchUpdater;
  this.BasicBatchUpdater = BasicBatchUpdater;

/** @file Base.js { */
var Base = _class("Base", {
  props: {
    id: null,
    impl: null,
    drawable: null,
    handler: null,
    _position: { x: 0, y: 0 },
    _size: { x: 0, y: 0 },
    _style: { fill: null, stroke: null },
    _zIndex: 0,
    _transform: null,
    _dirty: Fashion.DIRTY_POSITION | Fashion.DIRTY_SIZE | Fashion.DIRTY_ZINDEX ,
    _visibility: true
  },

  methods: {
    init: function (values) {
      if (values) {
        for (var i in values) {
          switch (typeof this[i]) {
          case 'function':
            this[i](values[i]);
            break;
          default:
            throw new ArgumentError('Invalid keyword argument: ' + i);
          }
        }
      }
    },

    position: function(value) {
      if (value) {
        this._position = value;
        this._dirty |= Fashion.DIRTY_POSITION;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._position;
    },

    size: function(value) {
      if (value) {
        this._size = value;
        this._dirty |= Fashion.DIRTY_SIZE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._size;
    },

    zIndex: function(value) {
      if (value !== void(0)) {
        this._zIndex = value;
        this._dirty |= Fashion.DIRTY_ZINDEX;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._zIndex;
    },

    transform: function(value) {
      if (value !== void(0)) {
        this._transform = value;
        this._dirty |= Fashion.DIRTY_TRANSFORM;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._transform;
    },

    style: function(value) {
      if (value !== void(0)) {
        this._style = value;
        this._dirty |= Fashion.DIRTY_STYLE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._style;
    },

    _attachTo: function(drawable) {
      this.drawable = drawable;
      this.impl = new drawable.backend[this.constructor.impl](this);
    },

    captureMouse: function() {
      if (!this.drawable)
        throw new NotAttached("This Shape is not attached any Drawable yet.");
      this.drawable.impl.captureMouse(this.impl);
    },

    releaseMouse: function() {
      if (!this.drawable)
        throw new NotAttached("This Shape is not attached any Drawable yet.");
      this.drawable.impl.releaseMouse(this.impl);
    },

    addEvent: function(type, h) {
      if (this.handler === null) {
        this.handler = new MouseEventsHandler(
          this,
          ['mousedown', 'mouseup', 'mousemove', 'mouseover', 'mouseout']
        );
      }
      this.handler.add.apply(this.handler, arguments);
      this._dirty |= Fashion.DIRTY_EVENT_HANDLERS;
      if (this.drawable)
        this.drawable._enqueueForUpdate(this);
    },

    removeEvent: function(type, h) {
      if (this.handler === null) return;
      var arglen = arguments.length;
      if (arglen === 0) {
        this.handler.removeAll();
      } else if (arglen == 1) {
        this.handler.removeAll.apply(this.handler, type);
      } else if (arguments.length < 3) {
        this.handler.remove(type, h);
      }
      this._dirty |= Fashion.DIRTY_EVENT_HANDLERS;
      if (this.drawable)
        this.drawable._enqueueForUpdate(this);
    },

    _refresh: function () {
      this.impl.refresh(this._dirty);
      this._dirty = 0;
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */

/** @file Circle.js { */
var Circle = _class("Circle", {
  parent: Base,
  class_props: { impl: 'Circle' }
});
/** @} */
/** @file Rect.js { */
var Rect = _class("Rect", {
  parent: Base,
  class_props: { impl: 'Rect' },
  props: {
    _corner: { x: 0, y: 0 }
  },
  methods: {
    corner: function(value) {
      if (value !== void(0)) {
        this._corner = value;
        this._dirty |= Fashion.DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._corner;
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file Path.js { */
var Path = _class("Path", {
  parent: Base,
  class_props: { impl: 'Path' },
  props: {
    _points: [],
    _position_matrix: new Matrix()
  },
  methods: {
    points: function(points) {
      if (points !== void(0)) {
        this._points = points;
        this._dirty |= Fashion.DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._points;
    }
  }
});
/** @} */
/** @file Drawable.js { */
var Drawable = _class("Drawable", {
  props: {
    backend: null,
    impl: null,
    handler: null,
    batchUpdater: null,
    target: null,
    _id_acc: 0,
    _elements: {},
    _capturing_elements: {},
    _numElements: 0,
    _anchor: 'left-top',
    _content_size:      { x: 0, y: 0 },
    _viewport_size:     { x: 0, y: 0 },
    _offset_position:      null,
    _transform: null,
    _inverse_transform: null,
    _dirty: 0
  },
  methods: {
    init: function(target, options) {
      this.backend = options && options.backend || Fashion.getBackend();
      this.target = target;
      this.impl = new this.backend.Drawable(this);
      this.transform(Matrix.scale(1.));
      if (options && options.viewportSize) {
        this.viewportSize(options.viewportSize);
      } else {
        var self = this;
        if (_window) {
          onceOnLoad(function () {
            var size = { x: target.clientWidth, y: target.clientHeight };
            self.viewportSize(size);
            if (!options || !options.contentSize)
              self.contentSize(size);
          });
        }
      }
      if (options) {
        if (options.contentSize)
          this.contentSize(options.contentSize);
        else if (options.viewportSize)
          this.contentSize(options.viewportSize);
      }
    },

    dispose: function () {
      this.impl.dispose();
    },

    viewportSize: function(size) {
      if (size) {
        this._viewport_size = size;
        this._dirty |= Fashion.DIRTY_SIZE;
        this._enqueueForUpdate(this);
      }
      return this._viewport_size;
    },

    viewportInnerSize: function () {
      return this.impl._viewportInnerSize;
    },

    contentSize: function(size) {
      if (size) {
        this._content_size = size;
        this._dirty |= Fashion.DIRTY_TRANSFORM;
        this._enqueueForUpdate(this);
      }
      return this._content_size;
    },

    scrollPosition: function(position) {
      if (position)
        return this.impl.scrollPosition(position);
      else
        return this.impl.scrollPosition();
    },

    transform: function (value) {
      if (value) {
        this._transform = value;
        this._inverse_transform = value.invert();
        this._dirty |= Fashion.DIRTY_TRANSFORM;
        this._enqueueForUpdate(this);
      }
      return this._transform;
    },

    gensym: function() {
      var sym = "G" + (++this._id_acc);
      return sym;
    },

    numElements: function() {
      return this._numElements;
    },

    each: function(func) {
      var elems = this._elements;
      for (var i in elems) {
        if (elems.hasOwnProperty(i)) {
          func.call(this, elems[i], i);
        }
      }
    },

    find: function(func) {
      var rt = null;
      this.each(function(elem, i) {
        if (rt || !func.call(this, elem, i)) return;
        rt = elem;
      });
      return rt;
    },

    collect: function(func) {
      var rt = [];
      this.each(function(elem, i) {
        if (func.call(this, elem, i)) rt.push(elem);
      });
      return rt;
    },

    map: function(func) {
      var elems = this._elements;
      this.each(function(elem, i) { elems[i] = func.call(this, elem); });
      return this;
    },

    anchor: function(d) {
      if (d) {
        this._anchor = d;
        this.impl.anchor(d);
      }
      return this._anchor;
    },

    draw: function(shape) {
      var id = this.gensym();
      shape.id = id;
      shape._attachTo(this);
      this.impl.append(shape.impl);
      shape.impl.refresh(shape._dirty);
      this._elements[id] = shape;
      this._numElements++;
      return shape;
    },

    drawAll: function(shapes) {
      for(var i=0,l=shapes.length; i<l; i++) {
        shapes[i] = this.draw(shapes[i]);
      }
      return shapes;
    },

    erase: function(shape) {
      var id = shape.id;

      if (id && (id in this._elements)) {
        shape.drawable = null;
        shape._dirty = ~0;
        shape.id = null;
        this.impl.remove(shape.impl);
        delete this._elements[id];
        this._numElements--;
      } else {
        throw new NotSupported("Shape " + shape + " is not added yet");
      }
      return shape;
    },

    captureMouse: function() {
      this.impl.captureMouse(this.impl);
    },

    releaseMouse: function() {
      this.impl.releaseMouse(this.impl);
    },

    addEvent: function(type, h) {
      if (this.handler === null) {
        this.handler = new MouseEventsHandler(
          this,
          ['mousedown', 'mouseup', 'mousemove', 'mouseover', 'mouseout',
           'scroll', 'visualchange']
        );
      }
      this.handler.add.apply(this.handler, arguments);
      this._dirty |= Fashion.DIRTY_EVENT_HANDLERS;
      this._enqueueForUpdate(this);
    },

    removeEvent: function(type, h) {
      if (this.handler === null) return;
      var arglen = arguments.length;
      if (arglen === 0) {
        this.handler.removeAll();
      } else if (arglen == 1) {
        this.handler.removeAll.apply(this.handler, type);
      } else if (arguments.length < 3) {
        this.handler.remove(type, h);
      }
      this._dirty |= Fashion.DIRTY_EVENT_HANDLERS;
      if (this.drawable)
        this.drawable._enqueueForUpdate(this);
    },

    _refresh: function () {
      this.impl.refresh(this._dirty);
      this._dirty = 0;
    },

    _enqueueForUpdate: function (shape) {
      if (this.batchUpdater) {
        this.batchUpdater.schedule(shape, shape._refresh);
      } else {
        shape._refresh();
      }
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file Text.js { */
var Text = (function() {
  var ANCHOR_SYMS = {
    'left': 'left',
    'center': 'center',
    'right': 'right',
    'start': 'left',
    'middle': 'center',
    'end': 'right'
  };
  return _class("Text", {
    parent: Base,
    class_props: { impl: 'Text' },
    props: {
      _text: '',
      _fontFamily: 'Sans',
      _fontSize: 10,
      _anchor: 'left'
    },
    methods: {
      fontFamily: function(value) {
        if (value) {
          this._fontFamily = value
          this._dirty |= Fashion.DIRTY_SHAPE;
          if (this.drawable)
            this.drawable._enqueueForUpdate(this);
        }
        return this._fontFamily;
      },

      fontSize: function(value) {
        if (value) {
          this._fontSize = value;
          this._dirty |= Fashion.DIRTY_SHAPE;
          if (this.drawable)
            this.drawable._enqueueForUpdate(this);
        };
        return this._fontSize;
      },

      text: function (value) {
        if (value) {
          this._text = value;
          this._dirty |= Fashion.DIRTY_SHAPE;
          if (this.drawable)
            this.drawable._enqueueForUpdate(this);
        };
        return this._text;
      },

      anchor: function (value) {
        if (value) {
          var _value = ANCHOR_SYMS[value.toLowerCase()];
          if (_value === void(0))
            throw new ValueError('Invalid anchor type: ' + _value);
          this._anchor = _value;
          this._dirty |= Fashion.DIRTY_SHAPE;
          if (this.drawable)
            this.drawable._enqueueForUpdate(this);
        };
        return this._anchor;
      }
    }
  });
})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file Image.js { */
var Image = _class('Image', {
  parent: Base,
  class_props: { impl: 'Image' },
  props: {
    _imageData: null
  },
  methods: {
    imageData: function (value) {
      if (value !== void(0)) {
        this._imageData = value;
        this._dirty |= Fashion.DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._imageData;
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */

  this.Base     = Base;
  this.Circle   = Circle;
  this.Rect     = Rect;
  this.Path     = Path;
  this.Text     = Text;
  this.Image    = Image;
  this.Drawable = Drawable;

/** @file conf.js { */
var DEBUG_MODE = true;

var DEFAULT_PRIORITY = ['svg', 'vml', 'canvas'];

var SEPARATOR = /\s|,/;

var DEFAULT_STYLE = {
  fill: {
    color: new Color(),
    rule: "nonzero",
    none: true
  },
  stroke: {
    color: new Color(),
    width: 1,
    none: false
  },
  visibility: true,
  cursor: "default"
};
/** @} */

  Fashion.getBackend = function getBackend() {
    return determineImplementation(DEFAULT_PRIORITY);
  };

  return this;
}).call(typeof exports !== 'undefined' ? exports: {});
/** @} */
