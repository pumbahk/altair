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
