

/************** src/main.js **************/
var Fashion = (function() {
  var Fashion = this;



/************** src/constants.js **************/
var DIRTY_TRANSFORM      = 0x00000001;
var DIRTY_POSITION       = 0x00000002;
var DIRTY_SIZE           = 0x00000004;
var DIRTY_SHAPE          = 0x00000008;
var DIRTY_ZINDEX         = 0x00000010;
var DIRTY_STYLE          = 0x00000020;
var DIRTY_VISIBILITY     = 0x00000040;
var DIRTY_EVENT_HANDLERS = 0x00000080;



/************** src/lib/lib.js **************/
var _lib = {};



/************** src/lib/browser.js **************/
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
_lib.detectBrowser = detectBrowser;
var BROWSER = detectBrowser(typeof window == 'undefined' ? void(0): window);



/************** src/lib/assert.js **************/
function __assert__(predicate) {
  if (!predicate)
    throw new AssertionFailure();
}
/*
 * vim: sts=2 sw=2 ts=2 et
 */



/************** src/lib/misc.js **************/
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
_lib._atomic_p             = _atomic_p;
_lib._clone                = _clone;
_lib.xparseInt             = xparseInt;
_lib._repeat               = _repeat;
_lib._lpad                 = _lpad;
_lib._clip                 = _clip;



/************** src/lib/error.js **************/
var FashionError = this.Error = function(message) {
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
  this[exceptionClassName] = exceptionClass;
  return exceptionClass;
}
var NotImplemented   = createExceptionClass.call(this, 'NotImplemented');
var ValueError       = createExceptionClass.call(this, 'ValueError');
var PropertyError    = createExceptionClass.call(this, 'PropertyError');
var NotSupported     = createExceptionClass.call(this, 'NotSupported');
var ArgumentError    = createExceptionClass.call(this, 'ArgumentError');
var NotAttached      = createExceptionClass.call(this, 'NotAttached');
var NotFound         = createExceptionClass.call(this, 'NotFound');
var AlreadyExists    = createExceptionClass.call(this, 'AlreadyExists');
var DeclarationError = createExceptionClass.call(this, 'DeclarationError');
var AssertionFailure = createExceptionClass.call(this, 'AssertionFailure');
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



/************** src/lib/classify.js **************/
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
/*
 * vim: sts=2 sw=2 ts=2 et
 */
_lib._class = _class;



/************** src/lib/MultipleKeyHash.js **************/
var MultipleKeyHash = _class("MultipleKeyHash", {
  props: {
    _eql: function(key1, key2) { return key1 === key2 },
    _src: []
  },

  methods: {

    init: function(eql) {
      if (eql && typeof eql === 'function') this._eql = eql;
    },

    put: function(key, value) {
      var r = {};
      if (this.exist_p(key, r)) {
        r['ref']['value'] = value;
      }
      this._src.push({key: key, value: value});
    },

    get: function(key) {
      var r = {};
      if (this.exist_p(key, r)) return r['ref']['value'];
      return null;
    },

    pop: function(key) {
      var rt = this.get(key);
      if (rt !== null) this.erace(key);
      return rt;
    },

    erace: function(keys) {
      if (arguments.length > 0) {
        keys = Array.prototype.slice.call(arguments);

        for (var i=0, l=keys.length; i<l; i++) {
          var key = keys[i];
          var r = {};
          if (this.exist_p(key, r)) {
            this._src.splice(r.idx, 1);
          } else {
            throw new NotFound("the object is not found. key = " + key.toString());
          }
        }

      } else {
        for (var l=this._src.length; 0<l; l--) {
          this._src.pop();
        }
      }
    },

    exist_p: function(key, obj) {
      for (var i=0, l=this._src.length; i<l; i++) {
        if (this._eql(this._src[i]['key'], key)) {
          if (obj) {
            obj['ref'] = this._src[i];
            obj['idx'] = i;
          }
          return true;
        }
      }
      return false;
    },

    getAllKeys: function() {
      var rt = [];
      for (var l=this._src.length; 0<l; l--) rt.unshift(this._src[l-1].key);
      return rt;
    },

    getAllValues: function() {
      var rt = [];
      for (var l=this._src.length; 0<l; l--) rt.unshift(this._src[l-1].value);
      return rt;
    },

    forEach: function(fn, self) {
      self = self || this;
      for (var i=0, l=this._src.length; i<l; i++) {
        var item = this._src[i];
        fn.call(self, item.key, item.value, item);
      }
    },

    length: function() {
      return this._src.length;
    }
  }
});_lib.MultipleKeyHash = MultipleKeyHash;
  Fashion._lib = _lib;

  var _window = typeof window == 'undefined' ? void(0): window;
  var _Image = _window && typeof _window.Image !== 'undefined' ? _window.Image: null;

  BROWSER = detectBrowser(_window);
  Fashion.browser = BROWSER;



/************** src/util/util.js **************/
var Util = (function() {

  var Util = {};



/************** src/util/Matrix.js **************/
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
        return new this(0, 0, 0, 0, offset.x, offset.y)
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

  Util.Matrix = Matrix;

  return Util;

})();
  Fashion.Util = Util;



/************** src/../backends/backend.js **************/
var Backend = (function() {


/************** src/../backends/UtilImpl.js **************/
// utils for Impl

var UtilImpl = {
  DomEvt: _class("Impl.UtilImpl.DomEvt", {

    class_methods: {
      addEvt: ((_window && (_window.document.addEventListener)) ?
               function(elem, type, func){ return elem.addEventListener(type, func, false); } :
               ((_window && (_window.document.attachEvent)) ?
                function(elem, type, func) { return elem.attachEvent('on' + type, func); } :
                function() { throw new NotSupported("This Browser is not Supported add Event to a DomElement."); })),

      remEvt: ((_window && (_window.document.removeEventListener)) ?
               function(elem, type, func) { return elem.removeEventListener(type, func, false); } :
               ((_window && (_window.document.detachEvent)) ?
                 function(elem, tyoe, func) { return elem.detachEvent('on' + type, func); } :
                function() { throw new NotSupported("This Browser is not Supported add Event to a DomElement."); }))
    },

    methods: {
      convertToMouseEvt: function convertToMouseEvt(dom_evt) {
        return this;
      }
    }
  }),

  getDomOffsetPosition: (function () {
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
          console.log('here');
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
  })()

};



/************** src/../backends/Refresher.js **************/
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
      this._postHandler && this._postHandler.call(target, dirty);
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/TransformStack.js **************/
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
        throw new ArgumentError("Invalid disposition: " + disposition);
      }
      return true;
    },

    remove: function (key) {

      if (!(key in this.pairs)) return;

      var i = 0;
      for (;;) {
        if (i >= this.stack.length)
          throw new NotFound("???"); // should not happen
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


/************** src/../backends/VisualObject.js **************/
var VisualObject = _class("VisualObject", {
  methods: {
    refresh: function(dirty) {},
    dispose: function() {}
  }
});


/************** src/../backends/DrawableImpl.js **************/
/*
 * interface class.
 */
var DrawableImpl = _class("DrawableImpl", {
  methods: {
    append: function(shape)       {},
    remove: function(shape)       {},
    anchor: function(position)    {},
    captureMouse: function(shape) {},
    releaseMouse: function(shape) {}
  }
});



/************** src/../backends/svg/svg.js **************/
var SVG = (function() {
  // checking browser.
  if ((BROWSER.identifier === 'ie' && BROWSER.version < 9)) return null;

  var SVG_NAMESPACE = "http://www.w3.org/2000/svg";
  var XLINK_NAMESPACE = "http://www.w3.org/1999/xlink";

  function newElement(element_name) {
    return _window.document.createElementNS(SVG_NAMESPACE, element_name);
  }

  function newTextNode(text) {
    return _window.document.createTextNode(text);
  }

  function matrixString(m) {
    return "matrix(" + [m.get(0), m.get(1), m.get(2), m.get(3), m.get(4), m.get(5)].join() + ")";
  }

  function pathString(pathData) {
    return pathData.join(' ').replace(/,/g, ' ');
  }

  function buildMouseEvt(impl, domEvt) {
    var retval = new MouseEvt();
    retval.type = domEvt.type;
    retval.target = impl.wrapper;
    var which = domEvt.which;
    var button = domEvt.button;
    if (!which && button !== void(0)) {
      which = ( button & 1 ? 1 : ( button & 2 ? 3 : ( button & 4 ? 2 : 0 ) ) );
    }
    switch(which) {
    case 0: retval.left = retval.middle = retval.right = false; break;
    case 1: retval.left = true; break;
    case 2: retval.middle = true; break;
    case 3: retval.right = true; break;
    }

    var physicalPagePosition;
    if (typeof domEvt.pageX != 'number' && typeof domEvt.clientX == 'number') {
      var eventDoc = domEvt.target.ownerDocument || _window.document;
      var doc = eventDoc.documentElement;
      var body = eventDoc.body;
      physicalPagePosition = {
        x: domEvt.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0),
        y: domEvt.clientY + (doc && doc.scrollTop  || body && body.scrollTop  || 0) - (doc && doc.clientTop  || body && body.clientTop  || 0)
      };
    } else {
      physicalPagePosition = { x: domEvt.pageX, y: domEvt.pageY };
    }
    if (impl instanceof Drawable) {
      retval.screenPosition   = _subtractPoint(physicalPagePosition, impl.getViewportOffset());
      retval.logicalPosition  = impl.convertToLogicalPoint(retval.screenPosition);
      retval.physicalPosition = impl.convertToPhysicalPoint(retval.screenPosition);
    } else {
      retval.screenPosition   = _subtractPoint(physicalPagePosition, impl.drawable.getViewportOffset());
      retval.logicalPosition  = impl.drawable.convertToLogicalPoint(retval.screenPosition);
      retval.physicalPosition = impl.drawable.convertToPhysicalPoint(retval.screenPosition);
      retval.offsetPosition   = _subtractPoint(retval.logicalPosition, impl.wrapper._position);
    }

    return retval;
  }



/************** src/../backends/svg/Base.js **************/
var Base = _class("BaseSVG", {
  interfaces: [VisualObject],

  props : {
    drawable: null,
    _elem: null,
    def: null,
    wrapper: null,
    _handledEvents: {
      mousedown: null,
      mouseup:   null,
      mousemove: null,
      mouseover: null,
      mouseout:  null
    },
    _eventFunc: null,
    _refresher: null,
    _transformStack: null,
    _transformUpdated: false
  },

  class_props: {
    _refresher: new Refresher().setup({
      preHandler: function() {
        if (!this.drawable)
          return;
        if (!this._elem) {
          this._elem = this.newElement();
          this.drawable._vg.appendChild(this._elem);
        }
      },

      postHandler: function () {
        this._updateTransform();
      },

      handlers: [
        [
          DIRTY_ZINDEX,
          function () {
            this.drawable._depthManager.add(this);
          }
        ],
        [
          DIRTY_TRANSFORM,
          function () {
            if (this.wrapper._transform)
              this._transformStack.add('last', 'wrapper', this.wrapper._transform);
            else
              this._transformStack.remove('wrapper');
            this._transformUpdated = true;
          }
        ],
        [
          DIRTY_STYLE,
          function () {
            var elem = this._elem;
            var style = this.wrapper._style;
            if (style.fill) {
              if (style.fill instanceof FloodFill) {
                elem.setAttribute('fill', style.fill.color.toString(true));
                elem.setAttribute('fill-opacity', style.fill.color.a / 255.0);
              } else if (style.fill instanceof LinearGradientFill
                  || style.fill instanceof RadialGradientFill
                  || style.fill instanceof ImageTileFill) {
                var def = this.drawable._defsManager.get(style.fill);
                elem.setAttribute('fill', "url(#" + def.id + ")");
                if (this.def)
                  this.def.delRef();
                this.def = def;
                def.addRef();
              }
            } else {
              elem.setAttribute('fill', 'none');
            }

            if (style.stroke) {
              elem.setAttribute('stroke', style.stroke.color.toString(true));
              elem.setAttribute('stroke-opacity', style.stroke.color.a / 255.0);
              elem.setAttribute('stroke-width', style.stroke.width);
              if (style.stroke.pattern && style.stroke.pattern.length > 1)
                elem.setAttribute('stroke-dasharray', style.stroke.pattern.join(' '));
            } else {
              elem.setAttribute('stroke', 'none');
            }
            elem.style.cursor = style.cursor;
          }
        ],
        [
          DIRTY_VISIBILITY,
          function () {
            this._elem.style.display = this.wrapper._visibility ? 'block' : 'none'
          }
        ],
        [
          DIRTY_EVENT_HANDLERS,
          function () {

            if (!this.wrapper.handler) return;

            for (var type in this._handledEvents) {
              var handled = this.wrapper.handler.handles(type);
              var eventFunc = this._handledEvents[type];
              if (!eventFunc && handled) {
                this._elem.addEventListener(type, this._eventFunc, false);
                this._handledEvents[type] = this._eventFunc;
              } else if (eventFunc && !handled) {
                this._elem.removeEventListener(type, eventFunc, false);
                this._handledEvents[type] = null;
              }
            }
          }
        ]
      ]
    })
  },

  methods: {
    init: function (wrapper) {
      this.wrapper = wrapper;
      this._refresher = this.constructor._refresher;
      this._transformStack = new TransformStack();
      var self = this;
      this._eventFunc = function(domEvt) {
        if (self.drawable._capturingShape &&
            self.drawable._capturingShape != self)
          return true;
        self.wrapper.handler.dispatch(buildMouseEvt(self, domEvt));
        return false;
      };
    },

    dispose: function() {
      if (this.drawable)
        this.drawable.remove(this);
      else
        this._removed();
    },

    _removed: function () {
      if (this.def) {
        this.def.delRef();
        this.def = null;
      }
      this._elem = null;
      this.drawable = null;
    },

    newElement: function() { return null; },

    refresh: function(dirty) {
      this._refresher.call(this, dirty);
    },

    _updateTransform: function () {
      if (!this._transformUpdated)
        return;
      var transform = this._transformStack.get();
      if (transform) {
        this._elem.setAttribute('transform', matrixString(transform));
      } else {
        this._elem.removeAttribute('transform');
      }
      this._transformUpdated = false;
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Circle.js **************/
var Circle = _class("CircleSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION | DIRTY_SIZE,
          function() {
            var position = this.wrapper._position, size = this.wrapper._size;
            this._elem.setAttribute('rx', (size.x / 2) + 'px');
            this._elem.setAttribute('ry', (size.y / 2) + 'px');
            this._elem.setAttribute('cx', (position.x + (size.x / 2))+'px');
            this._elem.setAttribute('cy', (position.y + (size.y / 2))+'px');
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function() {
      return newElement('ellipse');
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Rect.js **************/
var Rect = _class("RectSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.setAttribute('x', position.x + 'px');
            this._elem.setAttribute('y', position.y + 'px');
          }
        ],
        [
          DIRTY_SIZE,
          function () {
            var size = this.wrapper._size;
            this._elem.setAttribute('width', size.x + 'px');
            this._elem.setAttribute('height', size.y + 'px');
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function() {
      return newElement('rect');
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Path.js **************/
var Path = _class("PathSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_SHAPE,
          function () {
            this._elem.setAttribute('d', pathString(this.wrapper._points));
          }
        ],
        [
          DIRTY_POSITION,
          function () {
            this._transformStack.add('first', 'path-position', Util.Matrix.translate(this.wrapper.position));
            this._transformUpdated = true;
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function() {
      return newElement('path');
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Text.js **************/
var Text = _class("TextSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.setAttribute('x', position.x + 'px');
            this._elem.setAttribute('y', position.y + 'px');
          }
        ],
        [
          DIRTY_SIZE,
          function () {
            var size = this.wrapper._size;
            this._elem.setAttribute('width', size.x + 'px');
            this._elem.setAttribute('height', size.y + 'px');
          }
        ],
        [
          DIRTY_SHAPE,
          function () {
            this._elem.setAttribute('font-size', this.wrapper._fontSize + 'px'); 
            this._elem.setAttribute('font-family', this.wrapper._fontFamily);
            if (this._elem.firstChild)
              this._elem.removeChild(this._elem.firstChild);
            this._elem.appendChild(newTextNode(this.wrapper._text));
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function() {
      return newElement('text');
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/DefsManager.js **************/
function createForeignNode(xml) {
  return new DOMParser().parseFromString(
    '<?xml version="1.0" ?>'
    + '<svg xmlns="' + SVG_NAMESPACE + '" '
    + 'xmlns:xlink="' + XLINK_NAMESPACE + '">'
    + xml + '</svg>', "text/xml").documentElement.firstChild;
}

var Def = _class('Def', {
  props: {
    manager: null,
    id: null,
    node: null,
    xml: null,
    refcount: 1
  },

  methods: {
    init: function(manager, node, xml, id) {
      this.manager = manager;
      this.node = node;
      this.xml = xml;
      this.id = id;
    },

    dispose: function() {
      if (this.manager)
        this.manager.remove(this);
      this.manager = null;
      this.xml = null;
      this.node = null;
      this.id = null;
    },

    addRef: function() {
      ++this.refcount;
    },

    delRef: function() {
      if (--this.refcount <= 0)
        this.dispose();
    }
  }
});

var DefsManager = (function() {
  var serializers = {
    LinearGradientFill: function(obj) {
      var tmp = obj.angle % 1;
      var real_angle = tmp < 0 ? 1 + tmp: tmp;
      var angle_in_radian = Math.PI * real_angle * 2;
      var vx = Math.cos(angle_in_radian),
          vy = Math.sin(angle_in_radian);
      if (obj.angle < 0.125 || obj.angle >= 0.875) {
        vy /= vx;
        vx = 1;
      } else if (obj.angle >= 0.125 && obj.angle < 0.375) {
        vx /= vy;
        vy = 1;
      } else if (obj.angle >= 0.375 && obj.angle < 0.625) {
        vy /= -vx;
        vx = -1;
      } else if (obj.angle >= 0.625 && obj.angle < 0.875) {
        vx /= vy;
        vy = -1;
      }
      var v2x = vx / 2 + .5, v2y = vy / 2 + .5;
      var v1x = -v2x + 1, v1y = -v2y + 1;
      var chunks = [
        '<linearGradient',
        ' x1="', v1x * 100, '%"',
        ' y1="', v1y * 100, '%"',
        ' x2="', v2x * 100, '%"',
        ' y2="', v2y * 100, '%"',
        ' gradientUnits="objectBoundingBox">'
      ];
      var colors = obj.colors;
      for (var i = 0; i < colors.length; i++) {
        chunks.push('<stop offset="', colors[i][0] * 100, '"',
                    ' stop-color="', colors[i][1].toString(true), '"',
                    ' stop-opacity="', colors[i][1].a / 255.0, '"',
                    ' />');
      }
      chunks.push('</linearGradient>');
      return [ chunks.join(''), null ];
    },
    RadialGradientFill: function(obj) {
      var chunks = [
        '<radialGradient cx="50%" cy="50%" r="50%"',
        ' fx="', obj.focus.x, '"',
        ' fy="', obj.focus.y, '"',
        ' gradientUnits="objectBoundingBox">'
      ];
      var colors = obj.colors;
      for (var i = 0; i < colors.length; i++) {
        chunks.push('<stop offset="', colors[i][0] * 100, '"',
                    ' stop-color="', colors[i][1].toString(true), '"',
                    ' stop-opacity="', colors[i][1].a / 255.0, '"',
                    ' />');
      }
      chunks.push('</radialGradient>');
      var xml = chunks.join('');
      return [ xml, null ];
    },
    ImageTileFill: function(obj) {
      var xml = [
        '<pattern width="0" height="0" patternUnits="userSpaceOnUse">',
        '<image xlink:href="', _escapeXMLSpecialChars(obj.imageData.url), '" width="0" height="0" />',
        '</pattern>'
      ].join('');
      return [
        xml,
        function(n) {
          obj.imageData.size(function(size) {
            n.setAttribute("width", size.width);
            n.setAttribute("height", size.height);
            n.firstChild.setAttribute("width", size.width);
            n.firstChild.setAttribute("height", size.width);
          });
        }
      ];
    }
  };

  return _class("DefsManager", {
    props: {
      node: null,
      nodes: {},
      dynamicNodes: {}
    },

    methods: {
      init: function(node) {
        this.node = node;
      },

      nextId: function() {
        var id;
        do {
          id = "__svg__def" + (Math.random() * 2147483648 | 0);
        } while (this.node.ownerDocument.getElementById(id));
        return id;
      },

      get: function(def) {
        var className = def.constructor['%%CLASSNAME%%'];
        var serializer = serializers[className];
        if (!serializer)
          throw new NotSupported(className + " is not supported by SVG backend");
        var pair = serializer(def);
        var def = this.nodes[pair[0]];
        if (!def) {
          var id = this.nextId();
          var n = createForeignNode(pair[0]);
          if (pair[1]) pair[1](n);
          n.setAttribute("id", id);
          n = this.node.ownerDocument.adoptNode(n);
          def = new Def(this, n, pair[0], id);
          this.node.appendChild(n);
          this.nodes[pair[0]] = def;
        }
        return def;
      },

      remove: function(def) {
        delete this.nodes[def.xml];
      }
    }
  });
})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/DepthManager.js **************/
var DepthManager = _class("DepthManager", {
  props: {
    root: null,
    depth: []
  },

  methods: {
    init: function(root) {
      this.root = root;
    },

    add: function(shape) {
      var s = 0, e = this.depth.length;
      while (s != e) {
        var c = (s + e) >> 1;
        if (this.depth[c].wrapper._zIndex < shape.wrapper._zIndex) {
          s = c + 1;
        } else {
          e = c;
        }
      }
      var exists = false;
      while (s < this.depth.length && this.depth[s].wrapper._zIndex == shape.wrapper._zIndex) {
        if (this.depth[s].wrapper.id == shape.wrapper.id) {
          exists = true;
          break;
        }
        s++;
      }
      this.depth.splice(s, exists, shape);
      if (shape._elem) {
        var beforeChild = null;
        for (var i = s + 1; i < this.depth.length; i++) {
          beforeChild = this.depth[i]._elem;
          if (beforeChild)
            break;
        }
        shape._elem.parentNode.insertBefore(shape._elem, beforeChild);
      }
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Drawable.js **************/
var Drawable = _class("DrawableSVG", {
  interfaces : [VisualObject, DrawableImpl],

  props: {
    prefix: "svg",
    wrapper: null,
    _defsManager: null,
    _depthManager: null,
    _svg:         null,
    _vg:          null,
    _viewport:    null,
    _capturingShape: null,
    _handledEvents: {
      mousedown: null,
      mouseup:   null,
      mousemove: null,
      mouseout:  null
    },
    _eventFunc: null,
    _captureEventFunc: null,
    _refresher: null
  },

  class_props: {
    _refresher: new Refresher().setup({
      preHandler: function() {
        if (!this._viewport.parentNode != this.wrapper.target) {
          this.wrapper.target.appendChild(this._viewport);
        }
      },

      handlers: [
        [
          DIRTY_SIZE,
          function() {
            var viewportSize = this.wrapper._viewport_size;
            this._viewport.style.width  = viewportSize.x + 'px';
            this._viewport.style.height = viewportSize.y + 'px';
            this._updateContentSize();
          }
        ],
        [
          DIRTY_TRANSFORM,
          function() {
            this._vg.setAttribute("transform", matrixString(this.wrapper._transform));
            this._updateContentSize();
          }
        ],
        [
          DIRTY_EVENT_HANDLERS,
          function() {
            for (var type in this._handledEvents) {
              var handled = this.wrapper.handler.handles(type);
              var eventFunc = this._handledEvents[type];
              if (!eventFunc && handled) {
                this._svg.addEventListener(type, this._eventFunc, false);
                this._handledEvents[type] = this._eventFunc;
              } else if (eventFunc && !handled) {
                this._svg.removeEventListener(type, eventFunc, false);
                this._handledEvents[type] = null;
              }
            }
          }
        ]
      ]
    })
  },

  methods: {
    init: function(wrapper) {
      this.wrapper = wrapper;
      this._refresher = this.constructor._refresher;

      var self = this;
      this._eventFunc = function(domEvt) {
        if (self._capturingShape)
          return true;
        domEvt.stopPropagation();
        self.wrapper.handler.dispatch(buildMouseEvt(self, domEvt));
        return false;
      };

      this._captureEventFunc = function (domEvt) {
        var func = self._capturingShape._handledEvents[domEvt.type];
        return func ? func(domEvt): true;
      };

      var viewport = this._buildViewportElement();

      var svg = this._buildSvgElement();
      viewport.appendChild(svg);

      var defs = newElement("defs");
      svg.appendChild(defs);

      var root = newElement("g");
      svg.appendChild(root);

      this._defsManager = new DefsManager(defs);
      this._depthManager = new DepthManager(root);

      this._viewport = viewport;
      this._svg      = svg;
      this._vg       = root;
    },

    dispose: function() {
      if (this._viewport && this._viewport.parentNode)
        this._viewport.parentNode.removeChild(this._viewport);
      this._viewport = null;
      this._svg = null;
      this._vg = null;
      this._wrapper = null;
      this._defsManager = null;
      this._depthManager = null;
    },

    refresh: function (dirty) {
      this._refresher.call(this, dirty);
    },

    scrollPosition: function(position) {
      if (position) {
        var _position = this.wrapper._transform.apply(position);
        this._viewport.scrollLeft = _position.x;
        this._viewport.scrollTop  = _position.y;
        return position;
      }
      return this.wrapper._inverse_transform.apply({ x: this._viewport.scrollLeft, y: this._viewport.scrollTop });
    },

    append: function(shape) {
      shape.drawable = this;
    },

    remove: function(shape) {
      if (this._capturingShape == shape)
        this.releaseMouse(shape);
      if (this._vg && shape._elem)
        this._vg.removeChild(shape._elem);
      shape._removed(shape);
    },

    anchor: function() {
    },

    getViewportOffset: function() {
      return UtilImpl.getDomOffsetPosition(this._viewport);
    },

    captureMouse: function(shape) {
      var self = this;

      if (this._capturingShape) {
        throw new AlreadyExists("The shape is already capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.addEventListener(type, this._captureEventFunc, true);

      this._capturingShape = shape;
    },

    releaseMouse: function(shape) {
      var handler = shape.handler;

      if (this._capturingShape != shape) {
        throw new NotFound("The shape is not capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.removeEventListener(type, this._captureEventFunc, false);

      this._capturingShape = null;
    },

    convertToLogicalPoint: function(point) {
      return _addPoint(this.scrollPosition(), this.wrapper._inverse_transform.apply(point));
    },

    convertToPhysicalPoint: function(point) {
      return _addPoint(this.wrapper._transform.apply(this.scrollPosition()), point);
    },

    _updateContentSize: function () {
      var viewportSize = this.wrapper._viewport_size;
      var contentSize = this.wrapper._transform.apply(this.wrapper._content_size);
      this._svg.setAttribute('width', contentSize.x + 'px');
      this._svg.setAttribute('height', contentSize.y + 'px');
      this._svg.style.width = contentSize.x + 'px';
      this._svg.style.height = contentSize.y + 'px';
      this._viewport.style.overflow =
         (contentSize.x <= viewportSize.x &&
          contentSize.y <= viewportSize.y) ? 'hidden': 'scroll';
    },

    _buildSvgElement: function() {
      var svg = newElement("svg");
      svg.setAttribute('version', '1.1');
      // svg.style.background = "#ccc";
      svg.setAttribute('style', [
        'margin: 0',
        'padding: 0',
        '-moz-user-select: none',
        '-khtml-user-select: none',
        '-webkit-user-select: none',
        '-ms-user-select: none',
        'user-select: none'
      ].join(';'));
      return svg;
    },

    _buildViewportElement: function () {
      var viewport = _window.document.createElement("div");
      viewport.setAttribute('style', [
        'margin: 0',
        'padding: 0'
      ].join(';'));
      return viewport;
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */

  return {
    Util     : Util,
    Circle   : Circle,
    Rect     : Rect,
    Path     : Path,
    Text     : Text,
    Drawable : Drawable
  };
})();

/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/vml/vml.js **************/
var VML = (function() {

  // checking browser.
  if ((BROWSER.identifier !== 'ie' || BROWSER.version > 8 )) return null;

  var _ = {};
  var VML_PREFIX = 'v';
  var VML_NAMESPACE_URL = 'urn:schemas-microsoft-com:vml';
  var VML_BEHAVIOR_URL = '#default#VML';

  function setup() {
    var namespaces = _window.document.namespaces;
    if (!namespaces[VML_PREFIX])
      namespaces.add(VML_PREFIX, VML_NAMESPACE_URL);
    _window.document.createStyleSheet().addRule(VML_PREFIX + '\\:*', "behavior:url(#default#VML)");
  }

  function newElement(type) {
    var elem = _window.document.createElement(VML_PREFIX + ':' + type);
    return elem;
  }

  function matrixString(m) {
    return [m.a, m.c, m.b, m.d, m.e, m.f].join(',');
  }

  function pathString(path) {
    var retval = [];
    for (var i = 0; i < path.length; i++) {
      var p = path[i];
      switch (p[0]) {
      case 'M':
        retval.push('m', (p[1] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[2] * VML_FLOAT_PRECISION).toFixed(0));
        break;
      case 'L':
        retval.push('l', (p[1] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[2] * VML_FLOAT_PRECISION).toFixed(0));
        break;
      case 'C':
        retval.push('c', (p[1] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[2] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[3] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[4] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[5] * VML_FLOAT_PRECISION).toFixed(0),
                         (p[6] * VML_FLOAT_PRECISION).toFixed(0));
        break;
      case 'Z':
        retval.push('x');
        break;
      // TODO !!!!
      case 'R':
      case 'T':
      case 'S':
      case 'Q':
      case 'A':
      }
    }
    retval.push('e');
    return retval.join(' ');
  }

  function strokePattern(pattern) {
    return pattern.join(' ');
  }

  function buildMouseEvt(impl, msieEvt) {
    var retval = new MouseEvt();
    retval.type = msieEvt.type;
    retval.target = impl.wrapper;
    var which = msieEvt.which;
    var button = msieEvt.button;
    if (!which && button !== void(0)) {
      which = ( button & 1 ? 1 : ( button & 2 ? 3 : ( button & 4 ? 2 : 0 ) ) );
    }
    switch(which) {
    case 0: retval.left = retval.middle = retval.right = false; break;
    case 1: retval.left = true; break;
    case 2: retval.middle = true; break;
    case 3: retval.right = true; break;
    }

    var physicalPagePosition;

    var doc = _window.document, body = doc.body;
    physicalPagePosition = {
      x: msieEvt.clientX + body.scrollLeft,
      y: msieEvt.clientY + body.scrollTop
    };

    if (impl instanceof Drawable) {
      retval.physicalPosition = _subtractPoint(physicalPagePosition, impl.getViewportOffset());
      retval.logicalPosition = impl.convertToLogicalPoint(retval.physicalPosition);
    } else {
      retval.physicalPosition = _subtractPoint(physicalPagePosition, impl.drawable.getViewportOffset());
      retval.logicalPosition = impl.drawable.convertToLogicalPoint(retval.physicalPosition);
      retval.offsetPosition = _subtractPoint(retval.logicalPosition, impl.wrapper._position);
    }

    return retval;
  }



/************** src/../backends/vml/Base.js **************/
var Base = (function() { 
  function toVMLOMString(value) {
    if (typeof value == 'string') {
      return value;
    } else if (typeof value == 'boolean') {
      return value ? 't': 'f'
    } else {
      return value.toString();
    }
  }

  var VMLOMMarkupBuilder = _class('VMLOMMarkupBuilder', {
    props: {
      innerAttrs: null,
      outerAttrs: null
    },

    methods: {
      init: function (tagName) {
        this.tagName = tagName;
      },

      setInnerAttribute: function (name, value) {
        if (!this.innerAttrs)
          this.innerAttrs = {};
        this.innerAttrs[name] = value;
      },

      setOuterAttribute: function (name, value) {
        if (!this.outerAttrs)
          this.outerAttrs = {};
        this.outerAttrs[name] = value;
      },

      appendHTML: function (bufferPair) {
        if (this.outerAttrs) {
          for (var name in this.outerAttrs)
            bufferPair.outer.push(' ', name, '="', _escapeXMLSpecialChars(toVMLOMString(this.outerAttrs[name])), '"');
        }
        if (this.innerAttrs) {
          bufferPair.inner.push('<', VML_PREFIX, ':', this.tagName);
          for (var name in this.innerAttrs)
            bufferPair.inner.push(' ', name, '="', _escapeXMLSpecialChars(toVMLOMString(this.innerAttrs[name])), '"');
          bufferPair.inner.push(' />');
        }
      },

      assign: function (nodePair) {
        if (this.outerAttrs) {
          for (var name in this.outerAttrs)
            nodePair.outer[name] = this.outerAttrs[name];
        }
        if (this.innerAttrs) {
          for (var name in this.innerAttrs)
            nodePair.inner[name] = this.innerAttrs[name];
        }
      }
    }
  });

  VMLFillAndStroke = _class('VMLFillAndStroke', {
    props: {
      fill: null,
      stroke: null,
      styles: {}
    },

    methods: {
      init: function () {
        this.fill = new VMLOMMarkupBuilder('fill');
        this.stroke = new VMLOMMarkupBuilder('stroke');
      },

      setStyle: function (name, value) {
        if (typeof name == 'object' && value === void(0)) {
          for (var _name in name)
            this.styles[_name] = name[_name];
        } else {
          this.styles[name] = value;
        }
      },

      assignToElement: function (elem) {
        if (this.fill) {
          var fillNode = elem.fill;
          if (this.fill.innerAttrs && !fillNode)
            fillNode = newElement(this.fill.tagName);
          this.fill.assign({ outer: elem.node, inner: fillNode });
          if (fillNode && !elem.fill) {
            elem.node.appendChild(fillNode);
            elem.fill = fillNode;
          }
        }
        if (this.stroke) {
          var strokeNode = elem.stroke;
          if (this.stroke.innerAttrs && !strokeNode)
            strokeNode = newElement(this.stroke.tagName);
          this.stroke.assign({ outer: elem.node, inner: strokeNode });
          if (strokeNode && !elem.stroke) {
            elem.node.appendChild(strokeNode);
            elem.stroke = strokeNode;
          }
        }
        for (var name in this.styles)
          elem.node.style[name] = this.styles[name];
      },

      appendHTML: function (buf) {
        var innerBuf = [];
        this.fill.appendHTML({ outer: buf, inner: innerBuf });
        this.stroke.appendHTML({ outer: buf, inner: innerBuf });
        if (this.styles) {
          var attrChunks = [];
          for (var name in this.styles)
            attrChunks.push(name.replace(/[A-Z]/, function ($0) { return '-' + $0.toLowerCase(); }), ':', this.styles[name], ';');
          buf.push(' style', '="', _escapeXMLSpecialChars(attrChunks.join('')), '"');
        }
        buf.push(">");
        buf.push.apply(buf, innerBuf);
      }
    }
  });

  return _class("BaseVML", {
    props : {
      drawable: null,
      _elem: null,
      wrapper: null,
      _refresher: null,
      _handledEvents: {
        mousedown: false,
        mouseup: false,
        mousemove: false,
        mouseout: false
      }
    },

    class_props: {
      _refresher: new Refresher().setup({
        preHandler: function (dirty) {
          if (!this.drawable)
            return dirty;
          if (!this._elem) {
            this._elem = this.newElement(this.drawable._vg);
            return dirty & DIRTY_EVENT_HANDLERS;
          }
          return dirty;
        },

        handlers: [
          [
            DIRTY_TRANSFORM,
            function () {
              var transform = this.wrapper._transform;
              if (transform) {
                var scale = this.wrapper._transform.isScaling();
                if (scale) {
                  if (this._elem.skew) {
                    this._elem.node.removeChild(this._elem.skew);
                    this._elem.skew = null;
                  }
                  this._elem.node.coordOrigin = (-transform.e * VML_FLOAT_PRECISION).toFixed(0) + ',' + (-transform.f * VML_FLOAT_PRECISION).toFixed(0);
                  this._elem.node.coordSize = (VML_FLOAT_PRECISION / scale.x).toFixed(0) + ',' + (VML_FLOAT_PRECISION / scale.y).toFixed(0);
                } else {
                  if (!this._elem.skew) {
                    this._elem.skew = newElement('skew');
                    this._elem.node.appendChild(this._elem.skew);
                  }
                  this._elem.node.coordOrigin = null;
                  this._elem.node.coordSize = VML_FLOAT_PRECISION + ',' + VML_FLOAT_PRECISION;
                  this._elem.skew.matrix = matrixString(transform);
                  this._elem.skew.on = true;
                }
              } else {
                this._elem.node.removeChild(this._elem.skew);
                this._elem.skew = null;
              }
            }
          ],
          [
            DIRTY_STYLE,
            function () {
              var fillAndStroke = new VMLFillAndStroke();
              this._buildVMLStyle(fillAndStroke);
              fillAndStroke.assignToElement(this._elem);
            }
          ],
          [
            DIRTY_VISIBILITY,
            function () {
              this._elem.node.style.display = st.visibility ? 'block' : 'none';
            }
          ],
          [
            DIRTY_EVENT_HANDLERS,
            function () {
              for (var type in this._handledEvents) {
                var beingHandled = this._handledEvents[type];
                var toHandle = this.wrapper.handler.handles(type);
                if (!beingHandled && toHandle) {
                  this.drawable._handleEvent(type);
                  this._handledEvents[type] = true;
                } else if (beingHandled && !toHandle) {
                  this.drawable._unhandleEvent(type);
                  this._handledEvents[type] = false;
                }
              }
            }
          ]
        ]
      })
    },

    methods: {
      init: function (wrapper) {
        this.wrapper = wrapper;
        this._refresher = this.constructor._refresher;
        var self = this;
      },

      dispose: function() {
        if (this.drawable)
          this.drawable.remove(this);
        else
          this._removed();
      },

      _removed: function () {
        if (this._elem) {
          for (var type in this._handledEvents) {
            if (this._handledEvents[type])
              this.drawable._unhandleEvent(type);
          }
          this._elem.__fashion__id = null;
          this._elem = null;
        }
        this.drawable = null;
      },

      newElement: function (vg) {
        return null;
      },

      refresh: function (dirty) {
        this._refresher.call(this, dirty);
      },

      _buildVMLStyle: function (fillAndStroke) {
        var st = this.wrapper._style;
        function populateWithGradientAttributes(fill) {
          var firstColor = st.fill.colors[0];
          var lastColor = st.fill.colors[st.fill.colors.length - 1];
          // The order is reverse.
          fill.setInnerAttribute('color2', firstColor[1]._toString(true));
          fill.setInnerAttribute('color', lastColor[1]._toString(true));
          if (firstColor[0] == 0 && lastColor[0] == 1) {
            fill.setInnerAttribute('opacity2', firstColor[1].a / 255.);
            fill.setInnerAttribute('opacity', lastColor[1].a / 255.);
          }
          var colors = [];
          for (var i = st.fill.colors.length; --i >= 0; ) {
            var color = st.fill.colors[i];
            colors.push((color[0] * 100).toFixed(0) + "% " + color[1]._toString(true));
          }
          fill.setInnerAttribute('colors', colors.join(","));
        }

        var fill = fillAndStroke.fill, stroke = fillAndStroke.stroke;
        if (st.fill) {
          if (st.fill instanceof FloodFill) {
            if (st.fill.color.a == 255) {
              fill.setOuterAttribute('fillColor', st.fill.color._toString(true));
            } else {
              fill.setInnerAttribute('type', "solid");
              fill.setInnerAttribute('color', st.fill.color._toString(true));
              fill.setInnerAttribute('opacity', st.fill.color.a / 255.);
            }
          } else if (st.fill instanceof LinearGradientFill) {
            populateWithGradientAttributes(fill);
            fill.setInnerAttribute('type', "gradient");
            fill.setInnerAttribute('method', "sigma");
            fill.setInnerAttribute('angle', (st.fill.angle * 360).toFixed(0));
          } else if (st.fill instanceof RadialGradientFill) {
            populateWithGradientAttributes(fill);
            fill.setInnerAttribute('type', "gradientRadial");
            fill.setInnerAttribute('focusPosition', st.fill.focus.x + " " + st.fill.focus.y);
          } else if (st.fill instanceof ImageTileFill) {
            fill.setInnerAttribute('type', "tile");
            fill.setInnerAttribute('src', st.fill.imageData.url);
          }
          fill.setOuterAttribute('filled', true);
        } else {
          fill.setOuterAttribute('filled', false);
        }

        if (st.stroke) {
          if (st.stroke.color.a == 255 && !st.stroke.pattern) {
            stroke.setOuterAttribute('strokeColor', st.stroke.color._toString(true));
            stroke.setOuterAttribute('strokeWeight', st.stroke.width);
          } else {
            stroke.setInnerAttribute('color', st.stroke.color._toString(true));
            stroke.setInnerAttribute('opacity', st.stroke.color.a / 255.);
            stroke.setInnerAttribute('weight', st.stroke.width);
            if (st.stroke.pattern)
              stroke.setInnerAttribute('dashStyle', st.stroke.pattern.join(' '));
          }
          stroke.setOuterAttribute('stroked', true);
        } else {
          stroke.setOuterAttribute('stroked', false);
        }
        fillAndStroke.setStyle('cursor', st.cursor ? st.cursor: 'normal');
      }
    }
  });
})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/vml/Circle.js **************/
var Circle = _class("CircleVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION,
          function() {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ],
        [
          DIRTY_SIZE,
          function() {
            var size = this.wrapper._size;
            this._elem.node.style.width = size.x + 'px';
            this._elem.node.style.height = size.y + 'px';
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function(vg) {
      var position = this.wrapper._position;
      var size = this.wrapper._size;
      var vml = [
        '<', VML_PREFIX, ':oval',
        ' __fashion__id="', this.wrapper.id, '"'
      ];
      var fillAndStroke = new VMLFillAndStroke();
      this._buildVMLStyle(fillAndStroke);
      fillAndStroke.setStyle({
        position: 'absolute',
        display: 'block',
        margin: 0,
        padding: 0,
        width: size.x + 'px',
        height: size.y + 'px',
        left: position.x + 'px',
        top: position.y + 'px'
      });
      fillAndStroke.appendHTML(vml);
      vml.push('</', VML_PREFIX, ':oval', '>');
      vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
      return {
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null
      };
    }
  }
});


/************** src/../backends/vml/Rect.js **************/
var Rect = _class("RectVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION,
          function() {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ],
        [
          DIRTY_SIZE,
          function() {
            var size = this.wrapper._size;
            this._elem.node.style.width = size.x + 'px';
            this._elem.node.style.height = size.y + 'px';
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function(vg) {
      var position = this.wrapper._position;
      var size = this.wrapper._size;
      var vml = [
        '<', VML_PREFIX, ':rect',
        ' __fashion__id="', this.wrapper.id, '"'
      ];
      var fillAndStroke = new VMLFillAndStroke();
      this._buildVMLStyle(fillAndStroke);
      fillAndStroke.setStyle({
        position: 'absolute',
        display: 'block',
        margin: 0,
        padding: 0,
        width: size.x + 'px',
        height: size.y + 'px',
        left: position.x + 'px',
        top: position.y + 'px'
      });
      fillAndStroke.appendHTML(vml);
      vml.push('</', VML_PREFIX, ':rect', '>');
      vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
      return {
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null
      };
    }
  }
});


/************** src/../backends/vml/Path.js **************/
var Path = _class("PathVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_SHAPE,
          function () {
            this._elem.node.setAttribute('path', pathString(this.wrapper._points));
          }
        ],
        [
          DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function(vg) {
      var position = this.wrapper._position;
      var vml = [
        '<', VML_PREFIX, ':shape',
        ' __fashion__id="', this.wrapper.id, '"',
        ' coordsize="',
            VML_FLOAT_PRECISION, ',',
            VML_FLOAT_PRECISION, '" ',
        ' path="', pathString(this.wrapper._points), '"'
      ];
      var fillAndStroke = new VMLFillAndStroke();
      this._buildVMLStyle(fillAndStroke);
      fillAndStroke.setStyle({
        position: 'absolute',
        display: 'block',
        width: '1px',
        height: '1px',
        margin: 0,
        padding: 0,
        left: position.x + 'px',
        top: position.y + 'px'
      });
      fillAndStroke.appendHTML(vml);
      vml.push('</', VML_PREFIX, ':shape', '>');
      vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
      return {
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null
      };
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/vml/Text.js **************/
var Text = _class("TextVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ],
        [
          DIRTY_SIZE,
          function () {
            var size = this.wrapper._size;
            this._elem.node.style.width = size.x + 'px';
            this._elem.node.style.height = size.y + 'px';
          }
        ],
        [
          DIRTY_SHAPE,
          function () {
            this._elem.textpath.fontSize = this.wrapper._fontSize + 'px'; 
            this._elem.textpath.fontFamily = this.wrapper._fontFamily;
            this._elem.textpath.string = this.wrapper._text;
          }
        ]
      ]
    })
  },

  methods: {
    newElement: function(vg) {
      var vml = [
        '<', VML_PREFIX, ':line',
        ' __fashion__id="', this.wrapper.id, '"',
        ' from="0,0" to="1,0"'
      ];
      var fillAndStroke = new VMLFillAndStroke();
      fillAndStroke.setStyle({
        position: 'absolute',
        width: '1px',
        height: '1px',
        left: this.wrapper._position.x + 'px',
        top: this.wrapper._position.y + 'px'
      });
      this._buildVMLStyle(fillAndStroke);
      fillAndStroke.appendHTML(vml);
      vml.push(
        '<', VML_PREFIX, ':path textpathok="t" />',
        '<', VML_PREFIX, ':textpath string="', _escapeXMLSpecialChars(this.wrapper._text), '" on="t"',
        ' style="', 'font-size:', this.wrapper._fontSize, 'px;',
                    'font-family:', _escapeXMLSpecialChars(this.wrapper._fontFamily), ';',
                    'v-text-align:left" />',
        '</', VML_PREFIX, ':line', '>');
      vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
      return {
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null,
        textpath: vg.node.lastChild.lastChild
      };
    }
  }
});


/************** src/../backends/vml/Drawable.js **************/
var Drawable = _class("DrawableVML", {
  props: {
    _vg: null,
    _content: null,
    _viewport: null,
    _capturingShape: null,
    _handledEvents: {
      mousedown: [ false, 0, null ],
      mouseup: [ false, 0, null ],
      mousemove: [ false, 0, null ],
      mouseout: [ false, 0, null ]
    },
    _scrollPosition: { x: 0, y: 0 },
    _currentEvent: null,
    _eventFunc: null,
    _captureEventFunc: null,
    _scrollEventFunc: null,
    _refresher: null
  },

  class_props: {
    _refresher: new Refresher().setup({
      preHandler: function () {
        if (!this._viewport.parentNode != this.wrapper.target) {
          this.wrapper.target.appendChild(this._viewport);
        }
      },
      handlers: [
        [
          DIRTY_SIZE,
          function() {
            var viewportSize = this.wrapper._viewport_size;
            this._viewport.style.width  = viewportSize.x + 'px';
            this._viewport.style.height = viewportSize.y + 'px';
            this._updateContentSize();
          }
        ],
        [
          DIRTY_TRANSFORM,
          function () {
            var transform = this.wrapper._transform;
            if (transform) {
              var scale = this.wrapper._transform.isScaling();
              if (scale) {
                if (this._vg.skew) {
                  this._vg.node.removeChild(this._vg.skew);
                  this._vg.skew = null;
                }
                var contentSize = this.wrapper._transform.apply(this.wrapper._content_size);
                this._vg.node.coordOrigin = (-transform.e * VML_FLOAT_PRECISION) + ',' + (-transform.f * VML_FLOAT_PRECISION);
                this._vg.node.coordSize = (VML_FLOAT_PRECISION / scale.x) + ',' + (VML_FLOAT_PRECISION / scale.y);
              } else {
                if (!this._vg.skew) {
                  this._vg.skew = newElement('skew');
                  this._vg.node.appendChild(this._vg.skew);
                }
                this._vg.node.coordOrigin = null;
                this._vg.node.coordSize = VML_FLOAT_PRECISION + ',' + VML_FLOAT_PRECISION;
                this._vg.skew.matrix = matrixString(transform);
                this._vg.skew.on = true;
              }
            } else {
              this._vg.node.removeChild(this._vg.skew);
              this._vg.skew = null;
            }
            this._updateContentSize();
          }
        ],
        [
          DIRTY_EVENT_HANDLERS,
          function () {
            for (var type in this._handledEvents) {
              var beingHandled = this._handledEvents[type][0];
              var toHandle = this.wrapper.handler.handles(type);
              if (!beingHandled && toHandle) {
                this._handleEvent(type);
                this._handledEvents[type][0] = true;
              } else if (beingHandled && !toHandle) {
                this._unhandleEvent(type);
                this._handledEvents[type][0] = false;
              }
            }
          }
        ]
      ]
    })
  },

  methods: {
    init: function(wrapper) {
      this.wrapper = wrapper;
      this._refresher = this.constructor._refresher;

      var self = this;
      this._eventFunc = function(msieEvt) {
        if (self._capturingShape)
          return false;
        var target = msieEvt.srcElement;
        var fashionId = target.__fashion__id;
        var retval = void(0);
        self._currentEvent = msieEvt;
        if (fashionId) {
          var targetShape = self.wrapper._elements[fashionId];
          if (targetShape.handler)
            retval = targetShape.handler.dispatch(buildMouseEvt(targetShape.impl, msieEvt));
        }
        if (retval !== false) {
          if (self._handledEvents[msieEvt.type][0]) {
            if (self.wrapper.handler)
              retval = self.wrapper.handler.dispatch(buildMouseEvt(self, msieEvt));
          }
        }
        self._currentEvent = null;
        return retval;
      };

      this._captureEventFunc = function (msieEvt) {
        return self._capturingShape.wrapper.handler.dispatch(buildMouseEvt(self._capturingShape, msieEvt));
      };

      this._scrollEventFunc = function (msieEvt) {
        self._scrollPosition = self.wrapper._inverse_transform.apply({ x: parseInt(self._viewport.scrollLeft), y: parseInt(self._viewport.scrollTop) });
      };

      this._viewport = this._buildViewportElement();
      _bindEvent(this._viewport, 'scroll', this._scrollEventFunc);
      this._content = this._buildContentElement();
      this._viewport.appendChild(this._content);
      this._vg = this._buildRoot();
      this._content.appendChild(this._vg.node);
    },

    dispose: function() {
      if (this._viewport && this._viewport.parentNode)
        this._viewport.parentNode.removeChild(this._viewport);
      this._viewport = null;
      this._content = null;
      this._vg = null;
      this._wrapper = null;
    },

    refresh: function (dirty) {
      this._refresher.call(this, dirty);
    },

    scrollPosition: function(position) {
      if (position) {
        this._scrollPosition = position;
        if (_window.readyState == 'complete') {
          var _position = this.wrapper._transform.apply(position);
          this._viewport.scrollLeft = _position.x;
          this._viewport.scrollTop  = _position.y;
        } else {
          var self = this;
          _bindEvent(_window, 'load', function () {
            _unbindEvent(_window, 'load', arguments.callee);
            var _position = self.wrapper._transform.apply(self._scrollPosition);
            self._viewport.scrollLeft = _position.x;
            self._viewport.scrollTop  = _position.y;
          });
        }
        return position;
      }
      return this._scrollPosition;
    },

    append: function(shape) {
      shape.drawable = this;
    },

    remove: function(shape) {
      if (this._capturingShape == shape)
        this.releaseMouse(shape);
      if (this._vg && shape._elem)
        this._vg.node.removeChild(shape._elem.node);
      shape._removed(shape);
    },

    anchor: function () {
    },

    getViewportOffset: function() {
      return UtilImpl.getDomOffsetPosition(this._viewport);
    },

    captureMouse: function(shape) {
      var self = this;

      if (this._capturingShape) {
        throw new AlreadyExists("The shape is already capturing.");
      }

      var self = this;

      self._currentEvent.cancelBubble = true;
      for (var type in shape._handledEvents)
        this._viewport.offsetParent.attachEvent('on' + type, this._captureEventFunc);

      this._capturingShape = shape;
    },

    releaseMouse: function(shape) {
      var handler = shape.handler;

      if (this._capturingShape != shape) {
        throw new NotFound("The shape is not capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.detachEvent('on' + type, this._captureEventFunc);

      this._capturingShape = null;
    },

    convertToLogicalPoint: function(point) {
      return _addPoint(this.scrollPosition(), this.wrapper._inverse_transform.apply(point));
    },

    _updateContentSize: function () {
      var viewportSize = this.wrapper._viewport_size;
      var _scrollPosition = this.wrapper._transform.apply(this._scrollPosition);
      var contentSize = this.wrapper._transform.apply(this.wrapper._content_size);
      this._content.style.width = contentSize.x + 'px';
      this._content.style.height = contentSize.y + 'px';
      this._viewport.scrollLeft = _scrollPosition.x;
      this._viewport.scrollTop  = _scrollPosition.y;
      this._viewport.style.overflow =
         (contentSize.x <= viewportSize.x &&
          contentSize.y <= viewportSize.y) ? 'hidden': 'scroll';
    },

    _buildRoot: function () {
      var vg = newElement('group');
      vg.style.cssText = 'position:absolute;display:block;margin:0;padding:0;width:' + VML_FLOAT_PRECISION + 'px;height:' + VML_FLOAT_PRECISION + 'px';
      vg.coordSize = VML_FLOAT_PRECISION + ',' + VML_FLOAT_PRECISION;
      return { node: vg, skew: null };
    },

    _buildContentElement: function () {
      var content = _window.document.createElement("div");
      content.style.cssText = 'position:absolute;left:0px;top:0px;display:block;margin:0;padding:0;overflow:hidden;';
      return content;
    },

    _buildViewportElement: function () {
      var viewport = _window.document.createElement("div");
      viewport.style.cssText = 'position:absolute;display:block;margin:0;padding:0;overflow:hidden;';
      return viewport;
    },

    _handleEvent: function (type) {
      var triple = this._handledEvents[type];
      __assert__(triple);
      if (triple[1]++ == 0)
        this._content.attachEvent('on' + type, triple[2] = this._eventFunc);
    },

    _unhandleEvent: function (type) {
      var triple = this._handledEvents[type];
      __assert__(triple);
      if (triple[1] == 0)
        return;
      if (--triple[1] == 0) {
        this._content.detachEvent('on' + type, triple[2]);
        triple[2] = null;
      }
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */

  _.Util       = Util;
  _.Circle     = Circle;
  _.Rect       = Rect;
  _.Path       = Path;
  _.Text       = Text;
  _.Drawable   = Drawable;

  setup();

  return _;

})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/canvas/canvas.js **************/
var Canvas = null;

/** /
var JS_CANVAS = {
  version: "0.0.0",
  namespace: "http://www.w3.org/2000/svg",
  name: "JS_CANVAS"
};

(function(prefix) {
  var Set = function(that) {
    this.items = {};
    if (that !== void(0))
      this.update(that);
  };

  Set.prototype.add = function(item) {
    var oldItem = this.items[item.id];
    this.items[item.id] = item;
    return oldItem;
  };

  Set.prototype.update = function(set) {
    for (var id in set.items) {
      if (set.items.hasOwnProperty(id))
        this.items[id] = set.items[id];
    }
  };

  Set.prototype.remove = function(item) {
    delete this.items[item.id];
  };

  Set.prototype.contains = function(item) {
    return this.items[item.id] !== void(0);
  };

  Set.prototype.each = function(f) {
    for (var id in this.items) {
      if (this.items.hasOwnProperty(id))
        f(this.items[id]);
    }
  };

  var Tile = function(canvas, id, x, y) {
    this.id = id;
    this.x = x;
    this.y = y;
    this.objects = [];
    this.canvas = canvas;
    this.needsUpdate = true;
    this.n = null;
  };

  Tile.prototype.refresh = function() {
    if (!this.needsUpdate)
      return;
    var n = this.n;
    if (n === null)
      this.n = n = document.createElement('canvas');
    n.style.position = 'absolute';
    n.style.left = this.x + 'px';
    n.style.top = this.y + 'px';
    n.style.width = (n.width = this.canvas.tileWidth) + 'px';
    n.style.height = (n.height = this.canvas.tileHeight) + 'px';
    for (var i = this.objects.length; --i >= 0;) {
      var object = this.objects[i];
      var ctx = n.getContext('2d');
      ctx.strokeStyle = "rgb(0, 0, 0)";
      switch (object.type) {
      case 'oval':
        ctx.beginPath();
        ctx.arc(object.x - this.x, object.y - this.y, object.width / 2, 0, Math.PI * 2, 0);
        ctx.stroke();
        break;
      }
    }
    if (!this.n.parentNode)
      this.canvas.vg.appendChild(n);
    this.needsUpdate = false;
  };

  Tile.prototype.discard = function() {
    this.n.parentNode.removeChild(this.n);
    this.n = null;
    this.needsUpdate = true;
  };

  Tile.prototype.addObject= function(object) {
    this.objects.push(object);
    this.needsUpdate = true;
  };

  var Canvas = function(n) {
    this.n = n;
    var vg = document.createElement("div");
    vg.style.width = '4000px';
    vg.style.height = '4000px';
    vg.style.backgroundColor = '#fff';
    vg.style.position = 'relative';
    vg.style.overflow = 'hidden';
    this.n.appendChild(vg);
    this.vg = vg;
    this.objects = [];
    this.tileWidth = 400;
    this.tileHeight = 400;
    this.tiles = {};
    this.nextId = 1;
    this.visibleTiles = new Set();
    var self = this;
    this.n.addEventListener('scroll', function(e) {
      self.refresh();
    }, false);
  };

  Canvas.prototype.buildTileKey = function Canvas_buildTileKey(x, y) {
    return x + ":" + y;
  };

  Canvas.prototype.getTile = function Canvas_getTile(x, y) {
    var tileX = (x / this.tileWidth | 0) * this.tileWidth,
        tileY = (y / this.tileHeight | 0) * this.tileHeight;
    var key = this.buildTileKey(tileX, tileY);
    var tile = this.tiles[key];
    if (tile === void(0))
      tile = this.tiles[key] = new Tile(this, key, tileX, tileY);
    return tile;
  };

  Canvas.prototype.getViewportLeftTop = function() {
    var vp = this.n;
    return { x: parseInt(vp.scrollLeft), y: parseInt(vp.scrollTop) };
  };

  Canvas.prototype.getViewportSize = function() {
    var vp = this.n;
    return { x: parseInt(vp.style.width), y: parseInt(vp.style.height) };
  };

  Canvas.prototype.refresh = function() {
    var vpSize = this.getViewportSize(); 
    var vpLT = this.getViewportLeftTop();
    var visibleTiles = new Set(), hiddenTiles = new Set(this.visibleTiles);
    var ly = ((vpLT.y + vpSize.y + this.tileHeight) / this.tileHeight| 0) * this.tileHeight;
    var lx = ((vpLT.x + vpSize.x + this.tileWidth) / this.tileWidth | 0) * this.tileWidth;
    for (var y = vpLT.y; y < ly; y += this.tileHeight) {
      for (var x = vpLT.x; x < lx; x += this.tileWidth) {
        var tile = this.getTile(x, y);
        tile.refresh();
        visibleTiles.add(tile);
        hiddenTiles.remove(tile);
      }
    }
    hiddenTiles.each(function(tile) { tile.discard(); });
    this.visibleTiles = visibleTiles;
  };

  Canvas.prototype.drawOval = function Canvas_drawOval(x, y, width, height) {
    var object = { id: this.nextId++, type: 'oval', x: x, y: y, width: width, height: height };
    this.objects.push(object);
    var tiles = new Set();
    tiles.add(this.getTile(x - width / 2, y - height / 2));
    tiles.add(this.getTile(x + width / 2, y - height / 2));
    tiles.add(this.getTile(x - width / 2, y + height / 2));
    tiles.add(this.getTile(x + width / 2, y + height / 2));
    tiles.each(function(tile) { tile.addObject(object); });
  };

  this.JS_CANVAS.Canvas = Canvas;
})('v');

/**/

  var unsupported = function () {
    throw new NotSupported('Browser is not supported');
  }

  var Dummy = {
    Shape    : unsupported,
    Circle   : unsupported,
    Rect     : unsupported,
    Path     : unsupported,
    Text     : unsupported,
    Drawable : unsupported
  };

  var determineImplementation = function determineImplementation(priority) {
    for (var i=0, l=priority.length; i<l; i++) {
      var target = priority[i].toLowerCase();
      if (target === 'svg' && (SVG !== null))            return SVG;
      else if (target === 'vml' && (VML !== null))       return VML;
      else if (target === 'canvas' && (Canvas !== null)) return Canvas;
    }
    return Dummy;
  };

  return {
    UtilImpl       : UtilImpl,
    VisualObject   : VisualObject,
    Refresher      : Refresher,
    TransformStack : TransformStack,
    DrawableImpl   : DrawableImpl,
    SVG            : SVG,
    VML            : VML,
    Canvas         : Canvas,
    Dummy          : Dummy,
    determineImplementation : determineImplementation
  };

})();
  Fashion.Backend = Backend;



/************** src/Color.js **************/
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
  Fashion.Color = Color;



/************** src/Stroke.js **************/
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
  Fashion.Stroke = Stroke;



/************** src/Fill.js **************/
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
  Fashion.Fill = Fill;
  Fashion.FloodFill = FloodFill;
  Fashion.GradientFill = GradientFill;
  Fashion.LinearGradientFill = LinearGradientFill;
  Fashion.RadialGradientFill = RadialGradientFill;
  Fashion.ImageTileFill = ImageTileFill;



/************** src/ImageData.js **************/
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
      _bindEvent(this.node, 'load', function () {
        self._size = { width: self.node.width, height: self.node.height };
        _unbindEvent(self.node, 'load', arguments.callee);
        for (var i = 0; i < self.callbacks.length; i++)
          self.callbacks[i](self._size);
        self.callbacks = null;
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
  Fashion.ImageData = ImageData;



/************** src/PathData.js **************/
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
      var x = this.parseNumber(arr[i]), y = this.parseNumber(arr[i + 1]);
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
  Fashion.PathData = PathData;



/************** src/MouseEvt.js **************/
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
  Fashion.MouseEvt = MouseEvt;



/************** src/MouseEventsHandler.js **************/
var MouseEventsHandler = _class("MouseEventsHandler", {
  props : {
    _handlersMap: {
      mousedown: [],
      mouseup:   [],
      mousemove: [],
      mouseover: [],
      mouseout:  []
    },
    _target: null
  },

  methods: {
    init: function(target, h) {
      this._target = target;

      if (h) {
        this.add(h);
      }
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
  Fashion.MouseEventsHandler = MouseEventsHandler;



/************** src/BatchUpdater.js **************/
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
  Fashion.BatchUpdater = BatchUpdater;
  Fashion.BasicBatchUpdater = BasicBatchUpdater;



/************** src/Bindable.js **************/
var Bindable = _class("Bindable", {
  methods: {
    addEvent:         function(e) {},
    removeEvent:      function(e) {}
  }
});


/************** src/VisualObject.js **************/
var VisualObject = _class("VisualObject", {
  methods: {
    _refresh:         function() {}
  }
});


/************** src/Shape.js **************/
/*
 * Shape interface class.
 */
var Shape = _class("Shape", {
  parent: VisualObject,
  methods: {
    position:         function(d) {},
    size:             function(d) {},
    displayPosition:  function()  {},
    displaySize:      function()  {},
    hitTest:          function(d) {},
    transform:        function(d) {},
    style:            function(d) {},
    _refresh:         function() {}
  }
});


/************** src/Base.js **************/
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
    _dirty: DIRTY_POSITION | DIRTY_SIZE | DIRTY_ZINDEX ,
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
        this._dirty |= DIRTY_POSITION;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._position;
    },

    size: function(value) {
      if (value) {
        this._size = value;
        this._dirty |= DIRTY_SIZE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._size;
    },

    zIndex: function(value) {
      if (value !== void(0)) {
        this._zIndex = value;
        this._dirty |= DIRTY_ZINDEX;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._zIndex;
    },

    transform: function(value) {
      if (value !== void(0)) {
        this._transform = value;
        this._dirty |= DIRTY_TRANSFORM;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._transform;
    },

    style: function(value) {
      if (value !== void(0)) {
        this._style = value;
        this._dirty |= DIRTY_STYLE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._style;
    },

    _attachTo: function(drawable) {
      this.drawable = drawable;
    },

    captureMouse: function() {
      if (!this.drawable)
        throw new NotAttached("This Shape is not attached any Drawable yet.");
      this.drawable.captureMouse(this);
    },

    releaseMouse: function() {
      if (!this.drawable)
        throw new NotAttached("This Shape is not attached any Drawable yet.");
      this.drawable.releaseMouse(this);
    },

    addEvent: function(type, h) {
      if (this.handler === null)
        this.handler = new MouseEventsHandler(this);
      this.handler.add.apply(this.handler, arguments);
      this._dirty |= DIRTY_EVENT_HANDLERS;
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
      this._dirty |= DIRTY_EVENT_HANDLERS;
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



/************** src/Circle.js **************/
var Circle = _class("Circle", {
  mixins: [Base],
  interfaces: [Bindable, Shape],
  props: {},
  methods: {
    init: function (values) {
      Base.prototype.init.apply(this, arguments);
      this.impl = new Fashion.IMPL.Circle(this);
    },

    displayPosition: function() {
    },

    displaySize: function() {
    },

    gravityPosition: function() {
    },

    hitTest: function(d) {
    }
  }
});


/************** src/Rect.js **************/
var Rect = _class("Rect", {
  mixins: [Base],
  interfaces: [Bindable, Shape],
  props: {},
  methods: {
    init: function (values) {
      Base.prototype.init.apply(this, arguments);
      this.impl = new Fashion.IMPL.Rect(this);
    },

    displayPosition: function() {
    },

    displaySize: function() {
    },

    gravityPosition: function() {
    },

    hitTest: function(d) {
    }
  }
});


/************** src/Path.js **************/
var Path = _class("Path", {
  mixins: [Base],
  interfaces: [Bindable, Shape],
  props: {
    _points: [],
    _position_matrix: new Util.Matrix()
  },
  methods: {
    init: function (values) {
      Base.prototype.init.apply(this, arguments);
      this.impl = new Fashion.IMPL.Path(this);
    },

    points: function(points) {
      if (points !== void(0)) {
        this._points = points;
        this._dirty |= DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._points;
    },

    displayPosition: function() {
    },

    displaySize: function() {
    },

    gravityPosition: function() {
    },

    hitTest: function(d) {
    }
  }
});


/************** src/Drawable.js **************/
var Drawable = _class("Drawable", {
  interfaces: [Bindable, VisualObject],
  props: {
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
      this.target = target;
      this.impl = new Fashion.IMPL.Drawable(this);
      this.transform(Util.Matrix.scale(1.));
      if (options && options.viewportSize) {
        this.viewportSize(options.viewportSize);
      } else {
        var self = this;
        _bindEvent(_window, 'load', function () {
          _unbindEvent(_window, 'load', arguments.callee);
          var size = { x: target.clientWidth, y: target.clientHeight };
          self.viewportSize(size);
          if (!options || !options.contentSize)
            self.contentSize(size);
        });
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
        this._dirty |= DIRTY_SIZE;
        this._enqueueForUpdate(this);
      }
      return this._viewport_size;
    },

    contentSize: function(size) {
      if (size) {
        this._content_size = size;
        this._dirty |= DIRTY_TRANSFORM;
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
        this._dirty |= DIRTY_TRANSFORM;
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
      this.impl.append(shape.impl);
      shape._attachTo(this);
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

    captureMouse: function(shape) {
      this.impl.captureMouse(shape.impl);
    },

    releaseMouse: function(shape) {
      this.impl.releaseMouse(shape.impl);
    },

    addEvent: function(type, h) {
      if (this.handler === null)
        this.handler = new MouseEventsHandler(this);
      this.handler.add.apply(this.handler, arguments);
      this._dirty |= DIRTY_EVENT_HANDLERS;
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
      this._dirty |= DIRTY_EVENT_HANDLERS;
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


/************** src/Text.js **************/
var Text = _class("Text", {
  mixins: [Base],
  interfaces: [Bindable, Shape],
  props: {
    _text: '',
    _fontFamily: 'Sans',
    _fontSize: 10
  },
  methods: {
    init: function (values) {
      Base.prototype.init.apply(this, arguments);
      this.impl = new Fashion.IMPL.Text(this);
    },

    fontFamily: function(value) {
      if (value) {
        this._fontFamily = value
        this._dirty |= DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._fontFamily;
    },

    fontSize: function(value) {
      if (value) {
        this._fontSize = value;
        this._dirty |= DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      };
      return this._fontSize;
    },

    text: function (value) {
      if (value) {
        this._text = value;
        this._dirty |= DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      };
      return this._text;
    },

    displayPosition: function() {
    },

    displaySize: function() {
    },

    gravityPosition: function() {
    },

    hitTest: function(d) {
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/Image.js **************/
var Image = _class('Image', {
  mixins: [Base],

  interfaces: [Shape],

  props: {
    _imageData: null
  },

  methods: {
    init: function Image_init() {
      Base.prototype.init.apply(this, arguments);
      this.impl = new Fashion.IMPL.Image(this);
    },

    imageData: function (value) {
      if (value !== void(0)) {
        this._imageData = value;
        this._dirty |= DIRTY_SHAPE;
        if (this.drawable)
          this.drawable._enqueueForUpdate(this);
      }
      return this._imageData;
    },

    displayPosition: function() {
    },

    displaySize: function() {
    },

    gravityPosition: function() {
    },

    hitTest: function(d) {
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */

  Fashion.Bindable = Bindable;
  Fashion.VisualObject = VisualObject;
  Fashion.Shape    = Shape;
  Fashion.Base     = Base;
  Fashion.Circle   = Circle;
  Fashion.Rect     = Rect;
  Fashion.Path     = Path;
  Fashion.Text     = Text;
  Fashion.Image    = Image;
  Fashion.Drawable = Drawable;



/************** src/conf.js **************/
var DEBUG_MODE = true;

var DEFAULT_PRIORITY = ['svg', 'vml', 'canvas'];

var VML_FLOAT_PRECISION = 1e4;
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

  Fashion.IMPL = Backend.determineImplementation(DEFAULT_PRIORITY);

  return this;
}).call(typeof exports !== 'undefined' ? exports: {});
