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
  var rt = {}, attrs=el.attributes, attr;
  for (var i=0, l=attrs.length; i<l; i++) {
    attr = attrs[i];
    rt[attr.nodeName] = attr.nodeValue;
  }
  return rt;
};  

exports.makeHitTester = function Util_makeHitTester(a) {
  var pa = a.position(),
  sa = a.size(),
  ax0 = pa.x,
  ax1 = pa.x + sa.x,
  ay0 = pa.y,
  ay1 = pa.y + sa.y;

  return function(b) {
    var pb = b.position(),
    sb = b.size(),
    bx0 = pb.x,
    bx1 = pb.x + sb.x,
    by0 = pb.y,
    by1 = pb.y + sb.y;

    return ((((ax0 < bx0) && (bx0 < ax1)) || (( ax0 < bx1) && (bx1 < ax1)) || ((bx0 < ax0) && (ax1 < bx1))) && // x
            (((ay0 < by0) && (by0 < ay1)) || (( ay0 < by1) && (by1 < ay1)) || ((by0 < ay0) && (ay1 < by1))));  // y
  }
};
