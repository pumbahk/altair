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

exports.convertFromFashionStyle = function Util_convertFromFashionStyle(style) {
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
  var rt = {}, attrs=el.attributes, attr;
  for (var i=0, l=attrs.length; i<l; i++) {
    attr = attrs[i];
    rt[attr.nodeName] = attr.nodeValue;
  }
  return rt;
};  

exports.makeHitTester = function Util_makeHitTester(rect) {
  var rp = rect.position(),
  rs = rect.size();
  
  if(rs.x < 3 && rs.y < 3) {
    // click mode
    var rc = { x: rp.x+rs.x/2, y: rp.y+rs.y/2 };
    return function(obj) {
      var trc = obj._transform ? obj._transform.invert().apply(rc) : rc;
      var op = obj.position(),
      os = obj.size(),
      ox0 = op.x,
      ox1 = op.x + os.x,
      oy0 = op.y,
      oy1 = op.y + os.y;
      return ox0 < trc.x && trc.x < ox1 && oy0 < trc.y && trc.y < oy1;
    };
  } else {
    // rect mode
    var rx0 = rp.x,
    rx1 = rp.x + rs.x,
    ry0 = rp.y,
    ry1 = rp.y + rs.y;
    return function(obj) {
      var op = obj.position(),
      os = obj.size(),
      oc = { x: op.x+os.x/2, y: op.y+os.y/2 };
      
      var toc = obj._transform ? obj._transform.apply(oc) : oc;
      return rx0 < toc.x && toc.x < rx1 && ry0 < toc.y && toc.y < ry1;
    };
  }
};

var AsyncDataWaiter = exports.AsyncDataWaiter = function AsyncDataWaiter(options) {
  this.store = {};
  for (var i = 0; i < options.identifiers.length; i++) {
    this.store[options.identifiers[i]] = void(0);
  }
  this.after = options.after;
};

AsyncDataWaiter.prototype.charge = function AsyncDataWaiter_charge(id, data) {
  this.store[id] = data;
  for (var i in this.store) {
    if (this.store[i] === void(0))
      return;
  }
  // fire!! if all data has come.
  this.after.call(window, this.store);
};

exports.mergeStyle = function mergeStyle(a, b) {
  return {
    text: (b.text ? b.text: a.text) || null,
    text_color: (b.text_color ? b.text_color: a.text_color) || null,
    fill: (b.fill ? b.fill: a.fill) || null,
    stroke: (b.stroke ? b.stroke: a.stroke) || null
  };
};

var timer = exports.timer = function(msg) {
  this.start = (new Date()).getTime();
  if(msg) {
    console.log(msg);
  }
};
timer.prototype.lap = function(msg) {
  var lap = (new Date()).getTime()-this.start;
  this.start = (new Date()).getTime();
  if(msg) {
    console.log(msg+": "+lap+" msec");
  }
  return lap;
};
