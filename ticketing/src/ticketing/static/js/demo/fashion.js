

/************** src/main.js **************/
var Fashion = (function() {
  var Fashion = this;



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
    return str.replace(specials, function(x) { return map[special.source.indexOf(x)] });
  };
})();

function _clip(target, min, max, max_is_origin) {
  if (min > max) return (max_is_origin) ? max : min;
  return Math.min(Math.max(target, min), max);
}_lib._atomic_p             = _atomic_p;
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

  var CLASS_RELATIONSHIP = [[Object, null]];

  function get_parent(_class) {
    for (var i = 0, l = CLASS_RELATIONSHIP.length; i < l; i++) {
      var rel = CLASS_RELATIONSHIP[i];
      if (rel[0] === _class) return rel[1];
    }
    return null;
  };

  function __super__() {
    var pro = this.__proto__;
    return ((pro !== void(0)) ?
            ((this.constructor.prototype === this) ? pro : pro.__proto__ ) :
            get_parent(this.constructor).prototype);
  };

  function inherits(_class, parent) {

    CLASS_RELATIONSHIP.push([_class, parent]);

    var f = function(){}
    f.prototype = parent.prototype;
    _class.prototype = new f();
    _class.prototype.constructor = _class;
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

    l = 0;
    for (p in props) {
      if (props.hasOwnProperty(p)) l++;
    }

    __class__['%%INIT_INSTANCE_ORIGN_PROPS'] = (
      ( l > 0 ) ? function(inst) {
        for (var p in props) {
          if (props.hasOwnProperty(p)) {
            inst[p] = _clone(props[p]);
          }
        }
      } : function(){});

    inherits(__class__, parent);

    for (j = 0, l = mixins.length; j < l; j++) {
      mixin(__class__, mixins[j]);
    }

    for (i in methods) {
      if (methods.hasOwnProperty(i)) {
        method(__class__, i, methods[i]);
      }
    }

    __class__['%%CLASSNAME%%'] = name || genclassid();
    for(i in class_methods) {
      if (class_methods.hasOwnProperty(i)) {
        __class__[i] = class_methods[i];
      }
    }

    for(i in class_props) {
      if (class_props.hasOwnProperty(i)) {
        __class__[i] = class_props[i];
      }
    }

    for (j=0, l=interfaces.length; j<l; j++) {
      check_interface(__class__, interfaces[j]);
    }

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

  var rad = function (deg) {
    return deg % 360 * PI / 180;
  };

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

    methods: {

      init: function (a, b, c, d, e, f) {
        if (a) {
          this.a = +a; this.c = +c; this.e = +e;
          this.b = +b; this.d = +d; this.f = +f;
        }
      },

      set: function(tr) {
        for (i in tr) {
          if (tr.hasOwnProperty(i)) {
            if (i === 'scale') {
              var s = tr.scale;
              // console.log("scale:"+s.x+","+s.y+","+s.cx+","+s.cy);
              this.scale(s.x, s.y, s.cx, s.cy);

            } else if (i === 'rotate') {
              var r = tr.rotate;
              // console.log("rotate:"+r.angle+","+r.x+","+r.y);
              this.rotate(r.angle, r.x, r.y);

            } else if (i === 'translate') {
              var t = tr.translate;
              // console.log("translate:"+t.x+","+t.y);
              this.translate(t.x, t.y);

            } else {
              throw new ArgumentError("transform() expects 'tranlate', 'scale', 'rotate'.");

            }
          }
        }
        return this;
      },

      add: function (a, b, c, d, e, f) {
        var a1=this.a, b1=this.b, c1=this.c, d1=this.d, e1=this.e, f1=this.f;

        this.a = a1*a+c1*b;
        this.b = b1*a+d1*b;
        this.c = a1*c+c1*d;
        this.d = b1*c+d1*d;
        this.e = a1*e+c1*f+e1;
        this.f = b1*e+d1*f+f1;

      },

      combine: function(o) {
        this.add(o.a, o.b, o.c, o.d, o.e, o.f);
      },

      invert: function () {
        var me = this,
        x = me.a * me.d - me.b * me.c;
        return new this.constructor(
          me.d / x, -me.b / x, -me.c / x,
          me.a / x, (me.c * me.f - me.d * me.e) / x, (me.b * me.e - me.a * me.f) / x);
      },

      clone: function () {
        return new this.constructor(this.a, this.b, this.c, this.d, this.e, this.f);
      },

      translate: function (x, y) {
        this.add(1, 0, 0, 1, x, y);
        return this;
      },

      scale: function (x, y, cx, cy) {
        this.add(x, 0, 0, y, cx, cy);
        this.add(1, 0, 0, 1, -cx, -cy);
        return this;
      },

      rotate:  function (a, x, y) {
        a = rad(a);
        var cos = +Math.cos(a).toFixed(FLOAT_ACCURACY_ACCURATE);
        var sin = +Math.sin(a).toFixed(FLOAT_ACCURACY_ACCURATE);
        this.add(cos, sin, -sin, cos, x, y);
        this.add(1, 0, 0, 1, -x, -y);
        return this;
      },

      x: function (x, y) {
        return (x * this.a) + (y * this.c) + this.e;
      },

      y: function (x, y) {
        return (x * this.b) + (y * this.d) + this.f;
      },

      apply: function(p) {
        return { x: (p.x * this.a) + (p.y * this.c) + this.e,
                 y: (p.x * this.b) + (p.y * this.d) + this.f };
      },

      get: function (i) {
        return +this[String.fromCharCode(97 + i)].toFixed(FLOAT_ACCURACY);
      },

      getAll: function() {
        var rt = [];
        for(var i=0; i<6; i++) {
          rt.push(this.get(i));
        }
        return rt;
      },

      toString: function () {
        return [this.get(0), this.get(2), this.get(1), this.get(3), 0, 0].join();
      },

      offset: function () {
        return [this.e.toFixed(FLOAT_ACCURACY), this.f.toFixed(FLOAT_ACCURACY)];
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
        var which = dom_evt.which;
        var button = dom_evt.button;
        if (!which && button !== undefined ) {
          which = ( button & 1 ? 1 : ( button & 2 ? 3 : ( button & 4 ? 2 : 0 ) ) );
        }
        switch(which) {
        case 0: this.left = this.middle = this.right = false; break;
        case 1: this.left = true; break;
        case 2: this.middle = true; break;
        case 3: this.right = true; break;
        }

        var pageX = dom_evt.pageX;
        var pageY = dom_evt.pageY;
        if ( dom_evt.pageX == null && dom_evt.clientX != null ) {
          var eventDoc = dom_evt.target.ownerDocument || _window.document;
          var doc = eventDoc.documentElement;
          var body = eventDoc.body;

          pageX = dom_evt.clientX + ( doc && doc.scrollLeft || body && body.scrollLeft || 0 ) - ( doc && doc.clientLeft || body && body.clientLeft || 0 );
          pageY = dom_evt.clientY + ( doc && doc.scrollTop  || body && body.scrollTop  || 0 ) - ( doc && doc.clientTop  || body && body.clientTop  || 0 );
        }

        this.pagePosition.x = pageX;
        this.pagePosition.y = pageY;

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



/************** src/../backends/MouseEvtImpl.js **************/
var MouseEvtImpl = _class("MouseEvtImpl", {
  props: {
    pagePosition: {x:0,y:0},
    left:         false,
    middle:       false,
    right:        false
  }
});

/************** src/../backends/BaseImpl.js **************/
/*
 * interface class.
 */
var BaseImpl = _class("BaseImpl", {
  methods: {
    transform:         function(matrix) {},
    style:             function(style)  {},
    resetStyle:        function()       {},
    holdEventsHandler: function(handl)  {}
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

/************** src/../backends/ShapeImpl.js **************/
/*
 * interface class.
 */
var ShapeImpl = _class("ShapeImpl", {

  mixins: [BaseImpl],

  methods: {
    position: function(x, y, width, height) {},
    size:     function(width, height)       {}
  }
});


/************** src/../backends/PathImpl.js **************/
/*
 * interface class.
 */
var PathImpl = _class("PathImpl", {

  mixins: [BaseImpl],

  methods: {
    points: function(points) {}
  }
});

/************** src/../backends/TextImpl.js **************/
/*
 * interface class.
 */
var TextImpl = _class("TextImpl", {

  mixins: [ShapeImpl],

  methods: {
    fontFamily: function(fam) {}
  }
});


/************** src/../backends/svg/svg.js **************/
var SVG = (function() {
  // checking browser.
  if ((BROWSER.identifier === 'ie' && BROWSER.version < 9)) return null;

  var SVG_NAMESPACE = "http://www.w3.org/2000/svg";
  var XLINK_NAMESPACE = "http://www.w3.org/1999/xlink";

  function newNode(element_name) {
    return _window.document.createElementNS(SVG_NAMESPACE, element_name);
  }



/************** src/../backends/svg/Util.js **************/
var Util = _class("UtilSVG", {
  class_methods: {
    createSvgElement: function(type) {
      return document.createElementNS("http://www.w3.org/2000/svg", type);
    },
    createTextElement: function(str) {
      return document.createTextNode(str);
    },
    matrixString: function(m) {
      return "matrix(" + [m.get(0), m.get(1), m.get(2), m.get(3), m.get(4), m.get(5)].join() + ")";
    }
  }
});


/************** src/../backends/svg/MouseEvt.js **************/
var MouseEvt = _class("MouseEvtSVG", {

  interfaces: [MouseEvtImpl],

  mixins: [UtilImpl.DomEvt],

  props: {
    pagePosition: {x:0,y:0},
    left:         false,
    middle:       false,
    right:        false
  },

  methods: {
    init: function(dom_evt, shape) {
      this.convertToMouseEvt(dom_evt);
    }
  }

});


/************** src/../backends/svg/Base.js **************/
var Base = _class("BaseSVG", {

  interfaces: [BaseImpl],

  props : {
    handler: null,
    drawable: null,
    _elem: null,
    def: null
  },

  methods: {
    dispose: function() {
      if (this.drawable) {
        this.drawable.remove(this);
      }
      if (this.def) {
        this.def.delRef();
        this.def = null;
      }
    },

    transform: function(matrixes)
    {
      if (matrixes.length() > 0) {
        var mat = new Fashion.Util.Matrix();
        matrixes.forEach(function(k, v) { mat.combine(k); }, this);
        this._elem.setAttribute('transform', Util.matrixString(mat));
      } else {
        this._elem.removeAttribute('transform');
      }
    },

    style: function(st)
    {
      if (st.fill) {
        if (st.fill instanceof FloodFill) {
          this._elem.setAttribute('fill', st.fill.color.toString(true));
          this._elem.setAttribute('fill-opacity', st.fill.color.a / 255.0);
        } else if (st.fill instanceof LinearGradientFill
            || st.fill instanceof RadialGradientFill
            || st.fill instanceof ImageTileFill) {
          var def = this.drawable._defsManager.get(st.fill);
          this._elem.setAttribute('fill', "url(#" + def.id + ")");
          if (this.def)
            this.def.delRef();
          this.def = def;
          def.addRef();
        }
      } else {
        this._elem.setAttribute('fill', 'none');
      }

      if (st.stroke) {
        this._elem.setAttribute('stroke', st.stroke.color.toString(true));
        this._elem.setAttribute('stroke-opacity', st.stroke.color.a / 255.0);
        this._elem.setAttribute('stroke-width', st.stroke.width);
        if (st.stroke.pattern && st.stroke.pattern.length > 1)
          this._elem.setAttribute('stroke-dasharray', st.stroke.pattern.join(' '));
      } else {
        this._elem.setAttribute('stroke', 'none');
      }
      var visibility = st.visibility;
      var cursor = st.cursor;

      if (st.zIndex) {
        this._elem.setAttribute('z-index', st.zIndex);
      } else {
        this._elem.setAttribute('z-index', 0);
      }

      this._elem.style.display = visibility ? 'block' : 'none';
      this._elem.style.cursor  = cursor;

    },

    resetStyle: function()
    {
      this.style(DEFAULT_STYLE);
    },

    holdEventsHandler: function(handler)
    {
      var self = this;
      if (this.handler === null) {
        var funcs = new MultipleKeyHash();
        this.handler = handler;
        this.handler.holdTrigger('shape-impl', {
          add:    function(type, raw) {
            var wrapped = function(dom_evt){
              var evt = new MouseEvt(dom_evt, self);
              return raw.call(self, evt);
            };
            funcs.put(raw, wrapped);
            _bindEvent(self._elem, type, wrapped);
          },
          remove: function(type, raw) {
            _unbindEvent(self._elem, type, funcs.pop(raw));
          }
        });
      } else {
        throw new AlreadyExists("impl already has a events handler.");
      }
    },

    releaseEventsHandler: function () {
      if (this.handler !== null) {
        this.handler.releaseTriger('shape-impl');
      } else {
        throw new NotFound("events handler is not exist yet.");
      }
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */


/************** src/../backends/svg/Circle.js **************/
var Circle = _class("CircleSVG", {

  interfaces: [ShapeImpl],

  mixins: [Base],

  methods: {
    init: function()
    {
      this._elem = Util.createSvgElement('ellipse');
    },

    position: function(x, y, width, height)
    {
      this._elem.setAttribute('cx', (x+(width/2))+'px');
      this._elem.setAttribute('cy', (y+(height/2))+'px');
    },

    size: function(width, height)
    {
      this._elem.setAttribute('rx', (width/2)+'px');
      this._elem.setAttribute('ry', (height/2)+'px');
    }
  }
});


/************** src/../backends/svg/Rect.js **************/
var Rect = _class("RectSVG", {

  interfaces: [ShapeImpl],

  mixins: [Base],

  methods: {
    init: function()
    {
      this._elem = Util.createSvgElement('rect');
    },

    position: function(x, y, width, height)
    {
      this._elem.setAttribute('x', x+'px');
      this._elem.setAttribute('y', y+'px');
    },

    size: function(width, height)
    {
      this._elem.setAttribute('width', width+'px');
      this._elem.setAttribute('height', height+'px');
    }
  }
});


/************** src/../backends/svg/Path.js **************/
var Path = _class("PathSVG", {

  interfaces: [PathImpl],

  mixins: [Base],

  methods: {
    init: function()
    {
      this._elem = Util.createSvgElement('path');
    },

    points: function(points)
    {
      if (points !== void(0)) {
        this._points = points;
        this._elem.setAttribute('d', points.join().replace(/,/g, ' '));
      }

      return this._points;
    }
  }
});


/************** src/../backends/svg/Text.js **************/
var Text = _class("TextSVG", {

  interfaces: [TextImpl],

  mixins: [Base],

  methods: {
    init: function(str)
    {
      this._elem = Util.createSvgElement('text');
      this._elem.appendChild(Util.createTextElement(str));
    },

    position: function(x, y)
    {
      this._elem.setAttribute('x', x+'px');
      this._elem.setAttribute('y', y+'px');
    },

    size: function(font_size)
    {
      this._elem.setAttribute('font-size', font_size+'px');
    },

    fontFamily: function(font_family)
    {
      this._elem.setAttribute('font-family', font_family);
    }
  }
});


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


/************** src/../backends/svg/Drawable.js **************/
var Drawable = _class("DrawableSVG", {

  interfaces : [DrawableImpl],

  props: {
    prefix: "svg",
    handler: null,
    _defsManager: null,

    _svg:         null,
    _vg:          null,
    _viewport:    null,

    _onscroll:    null,

    _capturing_shapes: new MultipleKeyHash(),
    _capturing_functions: new MultipleKeyHash()
  },

  methods: {
    init: function(node, content_size, viewport_size, onscroll)
    {
      var svg = newNode("svg");
      svg.setAttribute("version", "1.1");
      svg.setAttribute("width", content_size.width + "px");
      svg.setAttribute("height", content_size.height + "px");
      svg.style.margin = "0";
      svg.style.padding = "0";
      svg.style.background = "#CCC";
      svg.style["-moz-user-select"] = svg.style["-khtml-user-select"] =
        svg.style["-webkit-user-select"] = svg.style["-ms-user-select"] =
        svg.style["user-select"] = 'none';

      var defs = newNode("defs");
      this._defsManager = new DefsManager(defs);
      svg.appendChild(defs);

      var root = newNode("g");
      svg.appendChild(root);

      var viewport = _window.document.createElement("div");
      viewport.style.padding = '0';
      viewport.style.width  = viewport_size.width + "px";
      viewport.style.height = viewport_size.height + "px";

      if (content_size.width <= viewport_size.width &&
          content_size.height <= viewport_size.height)
        viewport.style.overflow = "hidden";
      else
        viewport.style.overflow = "scroll";

      viewport.appendChild(svg);

      node.appendChild(viewport);

      this._viewport = viewport;
      this._svg      = svg;
      this._vg       = root;

      this._onscroll = onscroll || function() {};
      var self = this;
      this._viewport.addEventListener('scroll', function(evt) {
        self._onscroll({x: this.scrollLeft, y:this.scrollTop});
      }, false);

    },

    zoom: function(ratio)
    {
      if (ratio) {
        this._vg.setAttribute("transform", "scale(" + ratio + ")");
      }
    },

    viewportSize: function(size)
    {
      if (size) {
        this._viewport.style.width  = size.width + "px";
        this._viewport.style.height = size.height + "px";
      }
    },

    contentSize: function(size, scrolling)
    {
      if (size) {
        this._svg.setAttribute("width", size.width + "px");
        this._svg.setAttribute("height", size.height + "px");
        this._svg.style.width  = size.width + "px";
        this._svg.style.height = size.height + "px";

        if (scrolling) {
          this._viewport.style.overflow = 'scroll';
        } else {
          this._viewport.style.overflow = 'hidden';
        }

      }
    },

    scrollPosition: function(position)
    {
      if (position) {
        this._viewport.scrollLeft = position.x+'';
        this._viewport.scrollTop  = position.y+'';
        this._onscroll({x: position.x, y: position.y});
      }
    },

    append: function(shape)
    {
      shape.drawable = this;
      this._vg.appendChild(shape._elem);
    },

    remove: function(shape)
    {
      var child = shape._elem;
      this._vg.removeChild(child);
      shape.drawable = null;
    },

    anchor: function()
    {
    },

    getOffsetPosition: function()
    {
      return UtilImpl.getDomOffsetPosition(this._viewport);
    },

    captureMouse: function(shape)
    {
      var self = this;
      var handler = shape.handler;

      if (this._capturing_shapes.exist_p(shape)) {
        throw new AlreadyExists("The shape is already capturing.");
      }

      this._capturing_shapes.put(shape, null);

      var handler_functions = handler.getHandlerFunctionsAll();

      for (var j in handler_functions) {
        for (var i=0, l=handler_functions[j].length; i<l; i++) {
          (function(j, i) {
            var raw = handler_functions[j][i];
            var wrapped = function(dom_evt) {
              if (dom_evt.target !== shape._elem) {
                var evt = new MouseEvt(dom_evt, shape);
                return raw.call(shape, evt);
              }
            }
            self._capturing_functions.put(raw, wrapped);
            self._vg.addEventListener(j, wrapped, false);
          })(j, i);
        }
      }

      var self = this;
      handler.holdTrigger('drawable-impl', {
        append: function(type, raw) {
          var wrapped = function(dom_evt) {
            if (dom_evt.target !== shape._elem) {
              var evt = new MouseEvt(dom_evt, shape);
              return raw.call(shape, evt);
            }
          };
          self._capturing_functions.put(raw, wrapped);
          self._vg.addEventListener(type, wrapped, false);
        },
        remove: function(type, raw) {
          var wrapped = self._capturing_functions.pop(raw);
          self._vg.removeEventListener(type, wrapped, false);
        }
      });

    },

    releaseMouse: function(shape)
    {
      var handler = shape.handler;

      if (!this._capturing_shapes.exist_p(shape)) {
        throw new NotFound("The shape is not capturing.");
      }

      this._capturing_shapes.erace(shape);

      var handler_functions = handler.getHandlerFunctionsAll();

      for (var j in handler_functions) {
        for (var i=0, l=handler_functions[j].length; i<l; i++) {
          var raw = handler_functions[j][i];
          var wrapped = this._capturing_functions.pop(raw);
          this._vg.removeEventListener(j, wrapped, false);
        }
      }

      handler.releaseTrigger('drawable-impl');
    },

    holdEventsHandler: function(handler)
    {
      var self = this;
      if (this.handler === null) {
        var funcs = new MultipleKeyHash();
        this.handler = handler;
        this.handler.holdTrigger('drawable-impl', {
          add:    function(type, raw) {
            var wrapped = function(dom_evt){
              var evt = new MouseEvt(dom_evt, self);
              return raw.call(self, evt);
            };
            funcs.put(raw, wrapped);
            UtilImpl.DomEvt.addEvt(self._svg, type, wrapped);
          },
          remove: function(type, raw) {
            UtilImpl.DomEvt.remEvt(self._svg, type, funcs.pop(raw));
          }
        });
      } else {
        throw new AlreadyExists("impl already has a events handler.");
      }
    },

    releaseEventsHandler: function ()
    {
      if (this.handler !== null) {
        this.handler.releaseTriger('drawable-impl');
      } else {
        throw new NotFound("events handler is not exist yet.");
      }
    }

  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */

  return {
    MouseEvt : MouseEvt,
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
  var prefix = 'v';

  if (!window.console && DEBUG_MODE) {
    window.console = {
      log: function(txt) {
        /*
        var n = document.getElementById('console');
        n.value += txt + "\n";
        var r = n.createTextRange();
        r.move('character', n.value.length);
        r.select();
        */
      }
    }
  }



/************** src/../backends/vml/Util.js **************/
var Util = _class("UtilVML", {
  class_methods: {
    createVmlElement: function(type, attrp) {
      var elem = document.createElement(prefix + ':' + type);
      if (!attrp) elem.style.position = 'absolute';
      return elem;
    },

    matrixString: function(m) {
      return "progid:DXImageTransform.Microsoft.Matrix(" +
        "M11=" + m.get(0) + ", M12=" + m.get(2) + ", M21=" + m.get(1) + ", M22=" + m.get(3) +
        ", Dx=" + m.get(4) + ", Dy=" + m.get(5) + ", sizingmethod='auto expand')";
    },

    convertStrokePattern: function(pattern) {
      return pattern.join(' ');
    },

    convertColorArray: function(color) {
      var r = color.r.toString(16);
      if (r.length < 2) r = '0' + r;
      var g = color.g.toString(16);
      if (g.length < 2) g = '0' + g;
      var b = color.b.toString(16);
      if (b.length < 2) b = '0' + b;
      return { color: '#' + r + g + b, opacity: (color.a / 255.0) };
    },

    convertPathArray: function(path) {

      var str = '';
      var last_idt = '';
      var x, y;

      for (var i=0,l=path.length; i<l; i++ ) {
        var p = path[i];
        var idt = p[0];
        switch (idt) {
        case 'M':
          idt = 'm';
          x = p[1]; y = p[2];
          str += ' ' + idt + ' ' + x.toFixed() + ',' + y.toFixed();
          break;

        case 'H':
        case 'V':
          if (idt ==='V') y = p[1]; else x = p[1];
          p[1] = x; p[2] = y;
        case 'L':
          idt = 'l';
          x = p[1]; y = p[2];
          str += ((last_idt === idt) ? ', ' : ' ' + idt + ' ' ) + x.toFixed() + ',' + y.toFixed();

          break;

        case 'C':
          idt = 'c';
          x = item[5]; y = item[6];
          str += (((last_idt === idt) ? ', ' : ' ' + idt + ' ' ) +
                  p[1].toFixed() + ',' + p[2].toFixed() + ',' + p[3].toFixed() + ',' +
                  p[4].toFixed() + ',' + x.toFixed() + ',' + y.toFixed());

          break;

        case 'Z':
          idt = 'x';
          str += idt+' ';
          break;

        // TODO !!!!
        case 'R':
        case 'T':
        case 'S':
        case 'Q':
        case 'A':
        }

        last_idt = idt;
      }

      return (str + ' e');
    }
  }
});


/************** src/../backends/vml/MouseEvt.js **************/
var MouseEvt = _class("MouseEvtVML", {

  interfaces: [MouseEvtImpl],

  mixins: [UtilImpl.DomEvt],

  props: {
    pagePosition: {x:0,y:0},
    left:         false,
    middle:       false,
    right:        false
  },

  methods: {
    init: function(dom_evt, shape) {
      this.convertToMouseEvt(dom_evt);
    }
  }
});

/************** src/../backends/vml/Base.js **************/
var Base = _class("BaseVML", {

  props : {
    handler: null
  },

  methods: {

    transform: function(matrixes)
    {
      if (matrixes.length() > 0) {
        var mat = new Fashion.Util.Matrix();
        matrixes.forEach(function(k, v) { mat.combine(k); }, this);
        this._elem.style.filter = Util.matrixString(mat);
      } else {
        this._elem.style.filter = '';
      }
    },

    style: function(st)
    {
      var node = this._elem;
      var fill = (node.getElementsByTagName('fill') && node.getElementsByTagName('fill')[0]);
      var stroke = (node.getElementsByTagName('stroke') && node.getElementsByTagName('stroke')[0]);

      if (st.fill && !st.fill.none) {
        if (!fill) fill = Util.createVmlElement('fill', true);
        var color_op = Util.convertColorArray(st.fill.color);

        fill.on = true;
        fill.color = color_op.color;
        fill.opacity = color_op.opacity;
        fill.type = "solid";
        fill.src = '';
        // TODO
        // this._elem.setAttribute('fill-rule', fill.rule);
        node.appendChild(fill);

      } else {
        if (fill) {
          fill.on = false;
          node.removeChild(fill);
        }
      }

      if (st.stroke && !st.stroke.none) {
        if (!stroke) stroke = Util.createVmlElement('stroke', true);
        var color_op = Util.convertColorArray(st.stroke.color);

        stroke.on    = true;
        stroke.color = color_op.color;
        stroke.weight = st.stroke.width + 'px';
        stroke.opacity = color_op.opacity;
        stroke.dashstyle = Util.convertStrokeDash(st.stroke.dash);

        //params["stroke-linejoin"] && (stroke.joinstyle = params["stroke-linejoin"] || "miter");
        //stroke.miterlimit = params["stroke-miterlimit"] || 8;
        //params["stroke-linecap"] && (stroke.endcap = params["stroke-linecap"] == "butt" ? "flat" : params["stroke-linecap"] == "square" ? "square" : "round");

        node.appendChild(stroke);

      } else {
        var stroke = (node.getElementsByTagName('stroke') && node.getElementsByTagName('stroke')[0]);
        if (stroke) {
          stroke.on = false;
          node.removeChild(stroke);
        }
      }

      //stroke.dasharray  = Util.convertStrokeDash(st.stroke.dash);
      var visibility = st.visibility;
      var cursor = st.cursor;

      //this._elem.setAttribute('stroke-dasharray', stroke.dasharray);
      node.style.display = visibility ? 'block' : 'none';
      node.style.cursor  = cursor;

    },

    resetStyle: function()
    {
      this.style(DEFAULT_STYLE);
    },

    holdEventsHandler: function(handler)
    {
      var self = this;
      if (this.handler === null) {
        var funcs = new MultipleKeyHash();
        this.handler = handler;
        this.handler.holdTrigger('shape-impl', {
          add:    function(type, raw) {
            var wrapped = function(dom_evt){
              var evt = new MouseEvt(dom_evt, self);
              return raw.call(self, evt);
            };
            funcs.put(raw, wrapped);
            _bindEvent(self._elem, type, wrapped);
          },
          remove: function(type, raw) {
            _unbindEvent(self._elem, type, funcs.pop(raw));
          }
        });
      } else {
        throw new AlreadyExists("impl already has a events handler.");
      }
    },

    releaseEventsHandler: function () {
      if (this.handler !== null) {
        this.handler.releaseTriger('shape-impl');
      } else {
        throw new NotFound("events handler is not exist yet.");
      }
    }
  }
});


/************** src/../backends/vml/Circle.js **************/
var Circle = _class("CircleVML", {

  mixins: [Base],

  props: {
    _elem: null
  },

  methods: {
    init: function()
    {
      this._elem = Util.createVmlElement('oval');
    },

    position: function(x, y, width, height)
    {
      this._elem.style.left = x + 'px';
      this._elem.style.top  = y + 'px';
    },

    size: function(width, height)
    {
      this._elem.style.width  = width + 'px';
      this._elem.style.height = height + 'px';
    }
  }
});


/************** src/../backends/vml/Rect.js **************/
var Rect = _class("RectVML", {

  mixins: [Base],

  props: {
    _elem: null
  },

  methods: {
    init: function()
    {
      this._elem = Util.createVmlElement('rect');
    },

    position: function(x, y, width, height)
    {
      this._elem.style.left = x + 'px';
      this._elem.style.top  = y + 'px';
    },

    size: function(width, height)
    {
      this._elem.style.width  = width + 'px';
      this._elem.style.height = height + 'px';
    }
  }
});


/************** src/../backends/vml/Path.js **************/
var Path = _class("PathVML", {

  mixins: [Base],

  props: {
    _elem: null
  },

  methods: {

    init: function()
    {
      this._elem = Util.createVmlElement('shape');
      this.resetStyle();
    },

    points: function(points, parent)
    {
      if (points !== void(0)) {
        var s = parent.size();
        var p = parent.position();

        this._points = points;
        this._elem.setAttribute('path', Util.convertPathArray(points));
        this._elem.style.width  = '1000px';
        this._elem.style.height = '1000px';
        this._elem.style.left = '0';
        this._elem.style.top  = '0';
      }

      return this._points;
    }
  }
});



/************** src/../backends/vml/Text.js **************/
var Text = _class("TextVML", {
  mixins: [Base],

  props : {
    _elem: null,
    _child: null,
    _path: null
  },

  methods: {
    init: function(str)
    {

      this._elem  = Util.createVmlElement('line');
      this._path  = Util.createVmlElement('path');
      this._child = Util.createVmlElement('textpath');
      this._path.setAttribute('textpathok', 'true');
      this._child.setAttribute('string', str);
      this._child.setAttribute('on', 'true');
      this._elem.appendChild(this._path);
      this._elem.appendChild(this._child);

      this._elem.style.width = '100px';
      this._elem.style.height = '100px';

/*
        <v:line from="50 200" to="400 100">
        <v:fill on="True" color="red"/>
        <v:path textpathok="True"/>
        <v:textpath on="True" string="VML Text"
           style="font:normal normal normal 36pt Arial"/>
        </v:line>
*/

    },

    position: function(x, y, width, height)
    {
      //this._elem.style.left = x + 'px';
      //this._elem.style.top  = y + 'px';

      this._elem.setAttribute('from', x + ' ' + y);
      this._elem.setAttribute('to', (x + 1) + ' ' + y);
    },

    size: function(font_size)
    {
      this._child.style.font = "normal normal normal " + font_size + "pt 'Arial'";
      // this._elem.style.fontSize = font_size + 'px';
    },

    family: function(font_family)
    {
      // this._elem.style.fontFamily = font_family;
    }
  }
});


/************** src/../backends/vml/Drawable.js **************/
var Drawable = _class("DrawableVML", {

  props: {
    _vg: null
  },

  class_methods: {
    setup: function() {
      document.write('<xml:namespace ns="urn:schemas-microsoft-com:vml" prefix="' + prefix + '" />\n');
      document.write('<style type="text/css">\n' + prefix + '\\:*{behavior:url(#default#VML)}\n</style>');
    }
  },

  methods: {
    init: function(node, content_size)
    {
      var vg = Util.createVmlElement('group');
      vg.style.left = 0;
      vg.style.top = 0;
      vg.style.width = content_size.width + "px";
      vg.style.height = content_size.height + "px";
      this._vg = vg;
      node.appendChild(vg);
    },

    append: function(shape)
    {
      this._vg.appendChild(shape._elem);
    },

    remove: function(shape)
    {
      var child = shape._elem;
      this._vg.removeChild(child);
    }
  }
});

  _.Util       = Util;
  _.MouseEvt   = MouseEvt;
  _.Circle     = Circle;
  _.Rect       = Rect;
  _.Path       = Path;
  _.Text       = Text;
  _.Drawable   = Drawable;
  _.Drawable.setup();

  return _;

})();

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
    MouseEvtImpl   : MouseEvtImpl,
    BaseImpl       : BaseImpl,
    DrawableImpl   : DrawableImpl,
    ShapeImpl      : ShapeImpl,
    PathImpl       : PathImpl,
    TextImpl       : TextImpl,
    SVG            : SVG,
    VML            : VML,
    Canvas         : Canvas,
    Dummy          : Dummy,
    determineImplementation : determineImplementation
  };

})();  Fashion.Backend = Backend;



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
    'dotted': [1, 1],
    'dashed': [2, 2]
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
    parent: Array,

    methods: {
      init: function PathData_init(points) {
        Array.call(this);
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
      }
    }
  });
})();
  Fashion.PathData = PathData;



/************** src/MouseEvt.js **************/
var MouseEvt = _class("MouseEvt", {

  props: {
    contentPosition: {x:0,y:0},
    screenPosition:  {x:0,y:0},
    offsetPosition:  {x:0,y:0},
    left:            false,
    middle:          false,
    right:           false
  },

  methods: {
    init: function(impl_evt, target) {
      this.left   = impl_evt.left;
      this.middle = impl_evt.middle;
      this.right  = impl_evt.right;

      var px = impl_evt.pagePosition.x;
      var py = impl_evt.pagePosition.y;

      var shape = null, drawable = null;
      // drawable
      if (target instanceof Fashion.Drawable) {
        drawable = target;
      } else {
        shape = target;
        drawable = shape.drawable;
      }

      var offset_position = drawable.getOffsetPosition();
      var scroll_position = drawable.scrollPosition();

      // real size
      this.screenPosition.x  = px - offset_position.x;
      this.screenPosition.y  = py - offset_position.y;

      // logical size
      this.contentPosition.x = scroll_position.x + (this.screenPosition.x / drawable._zoom_ratio);
      this.contentPosition.y = scroll_position.y + (this.screenPosition.y / drawable._zoom_ratio);
      this.offsetPosition.x = this.contentPosition.x;
      this.offsetPosition.y = this.contentPosition.y;

      if (shape) {
        // logical size
        var sp = shape.position();
        this.offsetPosition.x -= sp.x;
        this.offsetPosition.y -= sp.y;
      }
    }
  }
});  Fashion.MouseEvt = MouseEvt;



/************** src/MouseEventsHandler.js **************/
var MouseEventsHandler = _class("MouseEventsHandler", {

  class_props: {
    types:  ['mousedown', 'mouseup', 'mousemove', 'mouseout']
  },

  props : {
    mousedown: new MultipleKeyHash(),
    mouseup:   new MultipleKeyHash(),
    mousemove: new MultipleKeyHash(),
    mouseout:  new MultipleKeyHash(),
    _triggers: {},
    _target: null
  },

  methods: {

    init: function(target, h) {
      this._target = target;
      this._target.impl.holdEventsHandler(this);

      if (h) {
        this.add(h);
      }
    },

    getHandlerFunctionsAll: function() {
      var rt = {}, types = MouseEventsHandler.types;
      for (var i=types.length; 0<i; i--) {
        rt[types[i-1]] = this.getHandlerFunctionsFor(types[i-1]);
      }
      return rt;
    },

    getHandlerFunctionsFor: function(idt) {
      if (this.hasOwnProperty(idt)) {
        var funcs = this[idt];
        return funcs.getAllValues();
      }
      throw new NotSupported("Expected keywords are '" + MouseEventsHandler.types.join("', '") + "'.");
    },

    add: function(h) {
      var target = this._target;
      var self = this;
      for (var type in h) {
        (function (type) {
          if (self.hasOwnProperty(type)) {
            var raw = h[type];
            var wrapped = function(impl_evt) {
              var evt = new MouseEvt(impl_evt, target);
              return raw.call(target, evt);
            };
            self[type].put(raw, wrapped);
            self._triggerAppend(type, wrapped);
          } else {
            throw new NotSupported("'" + type + "' cannot add into a MouseEventsHandler. Supported types are '" +
                                   MouseEventsHandler.types.join("', '") + "'.");
          }
        })(type);
      }
    },

    remove: function(idts) {

      idts = Array.prototype.slice.call(arguments);

      for (var i=0, l=idts.length; i<l; i++) {
        var idt = idts[i];
        if (typeof idt === 'string') {
          if (this.hasOwnProperty(idt)) {
            var funcs = this[idt];
            var keys = funcs.getAllKeys();
            for (var k = keys.length; 0<k; k--) {
              var wrapped = funcs.pop(keys[k-1]);
              this._triggerDelete(idt, wrapped);
            }
          } else {
            throw new NotSupported("Expected keywords are '" + MouseEventsHandler.types.join("', '") + "'.");
          }
        } else if (typeof idt === 'function') {
          var h = MouseEventsHandler.types;
          for (var i=h.length; 0<i; i--) {
            var type = h[i-1];
            var wrapped = this[type].pop(idt);
            if (wrapped !== null) {
              this._triggerDelete(type, wrapped);
              return;
            }
          }
          throw new NotFound("The function is not Found in this Handler.");

        } else {
          throw new NotSupported("remove(idts...) expects string or function.");
        }
      }
    },

    holdTrigger: function(id, trigger) {
      if (this._triggers.hasOwnProperty(id)) {
        throw new AlreadyExists("The trigger id is already exists.");
      }
      this._triggers[id] = trigger;
    },

    releaseTrigger: function(id) {
      delete this._triggers[id];
    },

    _triggerAppend: function(type, func) {
      var triggers = this._triggers;
      for (var i in triggers)
        if (triggers.hasOwnProperty(i))
          triggers[i].add(type, func);
    },

    _triggerDelete: function(type, func) {
      var triggers = this._triggers;
      for (var i in triggers)
        if (triggers.hasOwnProperty(i))
          triggers[i].remove(type, func);
    }
  }
});  Fashion.MouseEventsHandler = MouseEventsHandler;



/************** src/Shape.js **************/
/*
 * Shape interface class.
 */
var Shape = _class("Shape", {
  methods: {
    position:         function(d) {},
    size:             function(d) {},
    displayPosition:  function()  {},
    displaySize:      function()  {},
    hitTest:          function(d) {},
    transform:        function(d) {},
    resetTransform:   function()  {},
    style:            function(d) {},
    resetStyle:       function()  {},
    addEvent:         function(e) {},
    removeEvent:      function(e) {}
  }
});


/************** src/Base.js **************/
var Base = _class("Base", {

  props: {
    impl: null,
    drawable: null,
    _position: {x:0, y:0},
    _size: {width:0, height:0},
    _transform: {},
    _transform_matrix: null,
    _matrixes: new MultipleKeyHash(),
    _style: {},
    handler: null
  },

  methods: {
    position: function(d)
    {
      if (d) {
        var x = d.x, y = d.y;
        this._position.x = x;
        this._position.y = y;
        this.impl.position(x, y, this._size.width, this._size.height);
      }
      return _clone(this._position);
    },

    size: function(d)
    {
      if (d) {
        var width = d.width, height = d.height;
        this._size.width = width;
        this._size.height = height;
        this.impl.size(width, height);
      }
      return _clone(this._size);
    },

    transform: function()
    {
      var l;

      if ((l = arguments.length) > 0) {

        this._matrixes.pop(this._transform_matrix);
        this._transform = {};

        var scale, rotate, translate, tr, j, i;
        var pos = this.position();
        var x = pos.x, y = pos.y;
        var m = new Util.Matrix();

        for (j=0; j<l; j++) {

          tr = arguments[j];

          for (i in tr) {
            if (tr.hasOwnProperty(i)) {
              switch(i) {
              case 'scale':
                scale = tr[i];
                if (scale.x === void(0) || scale.y === void(0))
                  throw new ArgumentError("transform() scale needs x, y parameters at least.");
                if (scale.cx === void(0)) scale.cx = x;
                if (scale.cy === void(0)) scale.cy = y;
                this._transform.scale = scale;
                break;

              case 'rotate':
                rotate = tr[i];
                if (rotate.angle === void(0))
                  throw new ArgumentError("transform() rotate needs angle parameter at least.");
                if (rotate.x === void(0)) rotate.x = x;
                if (rotate.y === void(0)) rotate.y = y;
                this._transform.rotate = rotate;
                break;

              case 'translate':
                translate = tr[i];
                if (translate.x === void(0) || translate.y === void(0))
                  throw new ArgumentError("transform() translate needs x, y parameters at least.");
                this._transform.translate = translate;
                break;

              default:
                throw new ArgumentError("transform() expects 'translate', 'scale', 'rotate', but '" + i + "' given.");

              }
            }
          }
          m.set(this._transform);
        }

        this._transform_matrix = m;
        this._matrixes.put(this._transform_matrix, null);
        this.impl.transform(this._matrixes);
      }

      return ({
        scale:     this._transform.scale,
        rotate:    this._transform.rotate,
        translate: this._transform.translate
      });

    },

    resetTransform: function()
    {

      var m = this._matrixes.pop(this._transform_matrix);

      if (m) {
        this.impl.transform(this._matrixes);
      }

      this._transform = {};
      this._transform_matrix = null;
    },

    style: function(st)
    {
      if (st !== void(0)) {
        var i;
        var stroke = null;
        visibility=true,
        fill = null;
        cursor='default',
        zIndex=0;

        for (i in st) {
          if (st.hasOwnProperty(i)) {
            switch(i) {
            case 'stroke':
              stroke = st[i];
              break;
            case 'visibility':
              visibility = st[i];
              break;
            case 'fill':
              fill = st[i];
              break;
            case 'cursor':
              cursor = st[i];
              break;
            case 'zIndex':
              zIndex = st[i];
              break;
            }
          }
        }

        this._style = {
          stroke: stroke,
          visibility: visibility,
          fill: fill,
          cursor: cursor,
          zIndex: zIndex
        };

        if (this.drawable)
          this.impl.style(this._style);
      }

      return this._style;
    },

    attachTo: function(drawable) {
      this.drawable = drawable;
      this.impl.style(this._style);
    },

    resetStyle: function()
    {
      this._style = {};
      this.impl.resetStyle();
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

    addEvent: function(h)
    {
      if (this.handler === null) this.handler = new MouseEventsHandler(this);
      this.handler.add(h);
    },

    removeEvent: function()
    {
      if (this.handler === null) throw new NotSupported("EventsHandler has not initialized in this shape.");
      this.handler.remove.apply(this.handler, arguments);
    }
  }
});



/************** src/Circle.js **************/
var Circle = _class("Circle", {

  mixins: [Base],

  interfaces: [Shape],

  props: {},

  methods: {
    init: function (x, y, width, height)
    {
      this.impl = new Fashion.IMPL.Circle();
      this.size({width: width, height: height});
      this.position({x: x, y: y});
    },

    displayPosition: function()
    {
    },

    displaySize: function()
    {
    },

    gravityPosition: function()
    {
    },

    hitTest: function(d)
    {
    }
  }
});


/************** src/Rect.js **************/
var Rect = _class("Rect", {

  mixins: [Base],

  interfaces: [Shape],

  props: {},

  methods: {
    init: function (x, y, width, height)
    {
      this.impl = new Fashion.IMPL.Rect();
      this.size({width: width, height: height});
      this.position({x: x, y: y});
    },

    displayPosition: function()
    {
    },

    displaySize: function()
    {
    },

    gravityPosition: function()
    {
    },

    hitTest: function(d)
    {
    }
  }
});


/************** src/Path.js **************/
var Path = _class("Path", {

  mixins: [Base],

  interfaces: [Shape],

  props: {
    _points: [],
    _position_matrix: new Util.Matrix()
  },

  methods: {
    init: function (points)
    {
      this.impl = new Fashion.IMPL.Path();
      this.points(points);
      this._matrixes.put(this._position_matrix, null);
    },

    /**
     *
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
    points: function(points)
    {

      if (points !== void(0)) {
        this._points = points;
        this.impl.points(this._points, this);
        this._updateState();
      }

      return this._points;
    },

    position: function(d)
    {
      if (d) {
        var last = this._position_matrix.apply(this._position);
        var xm = d.x - last.x;
        var ym = d.y - last.y;
        this._position_matrix.translate(xm, ym);
        this.impl.transform(this._matrixes);
      }

      return this._position_matrix.apply(this._position);
    },

    size: function(d)
    {

      if (d) {
        var lw = this._size.width;
        var lh = this._size.height;
        var wm = d.width / lw;
        var hm = d.height / lh;
        var pos = this._position;

        var mat = (new Util.Matrix()).scale(wm, hm, pos.x, pos.y);
        this.applyMatrix(mat);
      }

      return {width: this._size.width, height: this._size.height};
    },

    applyMatrix: function(d)
    {
      if (d === void(0))
        throw new ArgumentError("applyMatrix expects 1 argument at least.");
      this._points.applyMatrix(d);
      this.points(this._points, true);
      return this;
    },

    displayPosition: function()
    {
    },

    displaySize: function()
    {
    },

    gravityPosition: function()
    {
    },

    hitTest: function(d)
    {
    },

    /* private */
    _updateState: function()
    {
      var x, y, pos = {x_min: Infinity, y_min: Infinity,
                       x_max: -Infinity, y_max: -Infinity};

      var points = this._points;

      for (var i=0, l=points.length, ll = l-1; i<l; i++) {
        var item = points[i];
        var idt = item[0];

        switch (idt) {

        case 'M':
          if (i < ll) {
            var next_idt = points[i+1][0];
            if (next_idt !== 'M') {
              x = item[1]; y = item[2];
            }
          }
          break;

        case 'L':
        case 'T': // TODO: consider curving line.
        case 'R': // TODO: consider curving line.
          x = item[1]; y = item[2];
          break;

        case 'C': // TODO: consider curving line.
          x = item[5]; y = item[6];
          break;

        case 'Z':
          break;

        case 'H':
          x = item[0];
          break;

        case 'V':
          y = item[0];
          break;

        case 'S': // TODO: consider curving line.
        case 'Q': // TODO: consider curving line.
          x = item[3]; y = item[4];
          break;

        case 'A': // TODO: consider curving line.
          x = item[6]; y = item[7];
          break;
        }

        if (pos.x_min > x) pos.x_min = x;
        if (pos.x_max < x) pos.x_max = x;

        if (pos.y_min > y) pos.y_min = y;
        if (pos.y_max < y) pos.y_max = y;

      }

      this._position.x = pos.x_min;
      this._position.y = pos.y_min;

      this._size.width  = pos.x_max - pos.x_min;
      this._size.height = pos.y_max - pos.y_min;

    }
  }
});


/************** src/Drawable.js **************/
var Drawable = _class("Drawable", {

  props: {
    impl: null,
    handler: null,
    _id_acc: 0,
    _target: null,
    _elements: {},
    _capturing_elements: {},
    _numElements: 0,
    _anchor: 'left-top',
    _content_size:      {width: 0, height: 0},
    _content_size_real: {width: 0, height: 0},
    _viewport_size:     {width: 0, height: 0},
    _scroll_position:      {x: 0, y: 0},
    _scroll_position_real: {x: 0, y: 0},
    _offset_position:      null,
    _zoom_ratio: 1.0
  },

  methods: {
    init: function(target, size)
    {
      var self = this;
      this.target = target;

      this._viewport_size.width  = (size && size.viewport && size.viewport.width)  || (size && size.width)  || target.clientWidth;
      this._viewport_size.height = (size && size.viewport && size.viewport.height) || (size && size.height) || target.clientHeight;
      this._content_size.width   = (size && size.content  && size.content.width)   || (size && size.width)  || this._viewport_size.width;
      this._content_size.height  = (size && size.content  && size.content.height)  || (size && size.height) || this._viewport_size.height;

      if (this._content_size.width < this._viewport_size.width)
        this._content_size.width = this._viewport_size.width;

      if (this._content_size.height < this._viewport_size.height)
        this._content_size.height = this._viewport_size.height;

      this._content_size_real.width  = this._content_size.width * this._zoom_ratio;
      this._content_size_real.height = this._content_size.height * this._zoom_ratio;

      this.impl = new Fashion.IMPL.Drawable(
        target,
        this._content_size_real,
        this._viewport_size,
        function(position) {
          self._scroll_position.x = position.x / self._zoom_ratio;
          self._scroll_position.y = position.y / self._zoom_ratio;
        }
      );

    },

    zoom: function(ratio, position)
    {
      if (ratio) {
        this._zoom_ratio = ratio;
        this.impl.zoom(ratio);
        this.contentSize(this._content_size);
        if (position) {
          this.scrollPosition({
            x: position.x - ((this._viewport_size.width  / this._zoom_ratio) / 2),
            y: position.y - ((this._viewport_size.height / this._zoom_ratio) / 2)
          });
        } else {
        }
      }
      return this._zoom_ratio;
    },

    viewportSize: function(size)
    {
      if (size) {
        size.width  = Math.max(size.width, 0);
        size.height = Math.max(size.height, 0);
        this._viewport_size.width  = size.width;
        this._viewport_size.height = size.height;
        this.impl.viewportSize(this._viewport_size);
        this.contentSize(this._content_size);
      }
      return _clone(this._viewport_size);
    },

    contentSize: function(size)
    {
      if (size) {
        var vs = this._viewport_size;
        this._content_size.width  = Math.max(size.width,  vs.width);
        this._content_size.height = Math.max(size.height, vs.height);
        this._content_size_real.width  = Math.round(Math.max(this._content_size.width  * this._zoom_ratio, vs.width));
        this._content_size_real.height = Math.round(Math.max(this._content_size.height * this._zoom_ratio, vs.height));

        this.impl.contentSize(this._content_size_real,
                              (this._content_size_real.width > this._viewport_size.width ||
                               this._content_size_real.height > this._viewport_size.height));

        this.scrollPosition(this._scroll_position);
      }
      return _clone(this._content_size);
    },

    scrollPosition: function(position)
    {
      if (position) {
        var cs = this._content_size, vs = this._viewport_size;
        var left_limit = cs.width  - (vs.width  / this._zoom_ratio);
        var top_limit  = cs.height - (vs.height / this._zoom_ratio);
        this._scroll_position.x = _clip(position.x, 0, left_limit, false);
        this._scroll_position.y = _clip(position.y, 0, top_limit, false);
        this._scroll_position_real.x = Math.round(this._scroll_position.x * this._zoom_ratio);
        this._scroll_position_real.y = Math.round(this._scroll_position.y * this._zoom_ratio);
        this.impl.scrollPosition(this._scroll_position_real);
      }

      return _clone(this._scroll_position);
    },

    getOffsetPosition: function(reflesh)
    {
      if (reflesh || this._offset_position === null)
        this._offset_position = this.impl.getOffsetPosition(reflesh);

      return _clone(this._offset_position);
    },

    gensym: function()
    {
      var sym = "G" + (++this._id_acc);
      return sym;
    },

    numElements: function()
    {
      return this._numElements;
    },

    each: function(func)
    {
      var elems = this._elements;
      for (var i in elems) {
        if (elems.hasOwnProperty(i)) {
          func.call(this, elems[i], i);
        }
      }
    },

    find: function(func)
    {
      var rt = null;
      this.each(function(elem, i) {
        if (rt || !func.call(this, elem, i)) return;
        rt = elem;
      });
      return rt;
    },

    collect: function(func)
    {
      var rt = [];
      this.each(function(elem, i) {
        if (func.call(this, elem, i)) rt.push(elem);
      });
      return rt;
    },

    map: function(func)
    {
      var elems = this._elements;
      this.each(function(elem, i) { elems[i] = func.call(this, elem); });
      return this;
    },

    anchor: function(d)
    {
      if (d) {
        this._anchor = d;
        this.impl.anchor(d);
      }
      return this._anchor;
    },

    draw: function(shape) {
      this.impl.append(shape.impl);
      var id = this.gensym();
      this._elements[id] = shape;
      shape.__id = id;
      shape.attachTo(this);
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
      var id = shape.__id;

      if (id && (id in this._elements)) {
        shape.drawable = null;
        delete shape.__id;
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

    addEvent: function(h) {
      if (this.handler === null) this.handler = new MouseEventsHandler(this);
      this.handler.add(h);
    },

    removeEvent: function()
    {
      if (this.handler === null) throw new NotSupported("EventsHandler has not initialized in this drawable.");
      this.handler.remove.apply(this.handler, arguments);
    }
  }
});


/************** src/Text.js **************/
var Text = _class("Text", {

  mixins: [Base],

  props: {},

  methods: {
    init: function (x, y, font_size, str)
    {
      this.impl = new Fashion.IMPL.Text(str);
      this.size({font: font_size});
      this.position({x: x, y: y});
    },

    fontFamily: function(d)
    {
      if (d) {
        this._family = d;
        this.impl.family(this._family);
      }
      return this._family;
    },

    lineWidth: function()
    {
    },

    size: function(d)
    {
      if (d) {
        var font = d.font;
        this._size.font = font;
        this.impl.size(font);
      };

      return {font: this._size.font};
    },

    displayPosition: function()
    {
    },

    displaySize: function()
    {
    },

    gravityPosition: function()
    {
    },

    hitTest: function(d)
    {
    }
  }
});


/************** src/Image.js **************/
var Image = _class('Image', {
  mixins: [Base],

  interfaces: [Shape],

  methods: {
    init: function Image_init(imageData, position, size) {
      this.impl = new Fashion.IMPL.Image(imageData);
      this.position = position;
      if (size) {
        this.size = size;
      } else {
        imageData.addEventListener("load", function() {
          this.size(imageData.size);
        });
      }
    },

    displayPosition: function()
    {
    },

    displaySize: function()
    {
    },

    gravityPosition: function()
    {
    },

    hitTest: function(d)
    {
    }
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */

  Fashion.Shape    = Shape;
  Fashion.Circle   = Circle;
  Fashion.Rect     = Rect;
  Fashion.Path     = Path;
  Fashion.Text     = Text;
  Fashion.Image    = Image;
  Fashion.Drawable = Drawable;



/************** src/conf.js **************/
var DEBUG_MODE = true;

var DEFAULT_PRIORITY = ['svg', 'vml', 'canvas'];

var FLOAT_ACCURACY = 4;
var FLOAT_ACCURACY_ACCURATE = 9;
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
