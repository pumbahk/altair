var utils = require('utils.js');

function newHandler(objects, styleClasses, drawable, offset) {
  var pathData = [];
  var unit = 'mm';
  var fontSize = 10;
  var styleDefs = [];
  var currentPoint = { x: 0., y: 0. };
  var scale = 1.;
  var lineHeight = null;
  var currentMatrix = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };
  var style = {
    fillColor: null,
    strokeColor: null,
    strokeWidth: null
  };
  var viewport = drawable.impl._viewport;
  viewport.style.position = 'relative';
  var texts = [];
  drawable.addEvent('visualchange', function () {
    for (var i = 0; i < texts.length; i++) {
      var text = texts[i];
      var canvasTransform = drawable.transform();
      var canvasScale = Math.sqrt(Math.abs(determinant(canvasTransform)));
      var _p = canvasTransform.apply(text.position);
      var _s = canvasTransform.apply(text.size);
      text.n.style.left = _p.x + 'px';
      text.n.style.top = _p.y + 'px';
      text.n.style.width = _s.x + 'px';
      text.n.style.height = _s.y + 'px';
      text.n.style.fontSize = text.fontSize * canvasScale + 'px';
      text.n.style.lineHeight = text.lineHeight ? (text.lineHeight * canvasScale) + 'px': '1em';
    }
  });
  function initPathData() {
    if (pathData == null) {
      var p = applyMatrix(currentMatrix, currentPoint);
      pathData = [['M', p.x, p.y]];
    }
  }
  function applyMatrix(matrix, point) {
    return { x: point.x * matrix.a + point.y * matrix.c + matrix.e,
             y: point.x * matrix.b + point.y * matrix.d + matrix.f };
  }
  function determinant(matrix) {
    return matrix.a * matrix.d - matrix.b * matrix.c;
  }
  return {
    xn: function xmlNode(path) {
      this.$stack.push(0); /* dummy */
    },
    sxn: function _stringizeXmlNodes() {
      this.$stack.pop(); /* dummy */
    },
    lo: function _loadObject(name) {
      var obj = objects[name];
      if (obj === void(0))
        throw new Error("Object does not exist");
      var i = 0;
      parse(
        {
          do_: function () {
            return i < obj.length ? obj[i++]: null;
          }
        },
        this,
        this.$stack);
    },
    S: function _scale(value) {
      scale = value;
    },
    fs: function _fontSize(value) {
      fontSize = value;
    },
    lh: function _lineHeight(value) {
      lineHeight = value;
    },
    hc: function pushClass(klass) {
      styleDefs.push(utils.serializeStyleDef(styleClasses[klass]));
    },
    pc: function popClass() {
      styleDefs.pop();
    },
    sc: function setClass(klass) {
      styleDefs = [klass];
    },
    rg: function setFillColor(value) {
      style.fillColor = value;
    },
    RG: function setStrokeColor(value) {
      style.strokeColor = value;
    },
    Sw: function setStrokeWidth(value) {
      style.strokeWidth = value;
    },
    U: function setUnit(_unit) {
      unit = _unit;
    },
    X: function showText(width, height, text) {
      var canvasTransform = drawable.transform();
      var p = applyMatrix(currentMatrix, currentPoint);
      p = {
        x: offset.x + utils.convertToUserUnit(p.x, unit),
        y: offset.y + utils.convertToUserUnit(p.y, unit)
      };
      var _p = canvasTransform.apply(p);
      var s = {
        x: utils.convertToUserUnit(width * scale, unit),
        y: utils.convertToUserUnit(height * scale, unit)
      };
      var _s = canvasTransform.apply(s);
      // Font sizes are always in px. (this is the spec)
      var canvasScale = Math.sqrt(Math.abs(determinant(canvasTransform)));
      var n = document.createElement('div');
      n.setAttribute('style', [
          'position:absolute;',
          'font-size:', fontSize * canvasScale, 'px', ';',
          'line-height:', lineHeight ? (lineHeight * canvasScale) + 'px': '1em', ';',
          'left:', _p.x, 'px', ';',
          'top:', _p.y, 'px', ';',
          'width:', _s.x, 'px', ';',
          'height:', _s.y, 'px', ';'
        ].concat(styleDefs).join(''));
      n.innerHTML = text;
      viewport.appendChild(n);
      texts.push({ n: n, position: p, size: s, fontSize: fontSize, lineHeight: lineHeight });
    },
    cm: function _currentTransformationMatrix(a, b, c, d, e, f) {
      currentMatrix = { a: a, b: b, c: c, d: d, e: e, f: f };
    },
    N: function newPath() {
    },
    m: function moveTo(x, y) {
      x *= scale;
      y *= scale;
      var p = { x: x, y: y };
      var p1 = applyMatrix(currentMatrix, p);
      if (pathData != null)
        pathData.push(['M', p1.x, p1.y]);
      currentPoint = p;
    },
    l: function lineTo(x, y) {
      x *= scale;
      y *= scale;
      var p = { x: x, y: y };
      var p1 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['L', p1.x, p1.y]);
      currentPoint = p;
    },
    c: function curveTo(x1, y1, x2, y2, x3, y3) {
      x1 *= scale;
      y1 *= scale;
      x2 *= scale;
      y2 *= scale;
      x3 *= scale;
      y3 *= scale;
      var p = { x: x3, y: y3 };
      var p1 = applyMatrix(currentMatrix, { x: x1, y: y1 }),
          p2 = applyMatrix(currentMatrix, { x: x2, y: y2 }),
          p3 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['C', p1.x, p1.y, p2.x, p2.y, p3.x, p3.y]);  
      currentPoint = p;
    },
    v: function curveToS1(x2, y2, x3, y3) {
      x2 *= scale;
      y2 *= scale;
      x3 *= scale;
      y3 *= scale;
      var p = { x: x3, y: y3 };
      var p1 = applyMatrix(currentMatrix, currentPoint);
          p2 = applyMatrix(currentMatrix, { x: x2, y: y2 }),
          p3 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['C', p1.x, p1.y, p2.x, p2.y, p3.x, p3.y]);  
      currentPoint = p;
    },
    y: function curveToS2(x1, y1, x3, y3) {
      x1 *= scale;
      y1 *= scale;
      x3 *= scale;
      y3 *= scale;
      var p = { x: x3, y: y3 };
      var p1 = applyMatrix(currentMatrix, { x: x1, y: y1 });
          p3 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['C', p1.x, p1.y, p3.x, p3.y, p3.x, p3.y]);  
      currentPoint = p;
    },
    q: function quadraticCurveTo(x1, y1, x2, y2) {
      x1 *= scale;
      y1 *= scale;
      x2 *= scale;
      y2 *= scale;
      var p = { x: x2, y: y2 };
      var p1 = applyMatrix(currentMatrix, { x: x1, y: y1 }),
          p2 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['Q', p1.x, p1.y, p2.x, p2.y]);
      currentPoint = p;
    },
    a: function arc(rx, ry, phi, largeArc, sweep, x, y) {
      rx *= scale;
      ry *= scale;
      x *= scale;
      y *= scale;
      var p = { x: x, y: y };
      var r = applyMatrix(currentMatrix, { x: rx - currentMatrix.e, y: ry - currentMatrix.f }),
          p1 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push(['A', r.x, r.y, phi, largeArc, sweep, p1.x, p1.y]);
      currentPoint = p;
    },
    h: function closePath() {
      initPathData();
      pathData.push(['Z']);
    },
    f: function fill() {
      if (pathData == null)
        return;
      drawable.draw(new Fashion.Path({
        position: { x: offset.x, y: offset.y },
        points: pathData,
        style: {
          fill: style.fillColor ? new Fashion.FloodFill(new Fashion.Color(style.fillColor)): null,
          stroke: null
        }
      }));
      pathData = null;
    },
    s: function stroke() {
      if (pathData == null)
        return;
      var strokeWidth = style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale;
      drawable.draw(new Fashion.Path({
        points: pathData,
        style: {
          fill: null,
          stroke: style.strokeColor ? new Fashion.Stroke(new Fashion.Color(style.strokeColor), strokeWidth): null
        }
      }));
      pathData = null;
    },
    B: function strokeAndFill() {
      if (pathData == null)
        return;
      var strokeWidth = style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale;
      drawable.draw(new Fashion.Path({
        position: { x: offset.x, y: offset.y },
        points: pathData,
        style: {
          fill: style.fillColor ? new Fashion.FloodFill(new Fashion.Color(style.fillColor)): null,
          stroke: style.strokeColor ? new Fashion.Stroke(new Fashion.Color(style.strokeColor), strokeWidth): null
        }
      }));
      pathData = null;
    }
  };
}

exports.newHandler = newHandler;
