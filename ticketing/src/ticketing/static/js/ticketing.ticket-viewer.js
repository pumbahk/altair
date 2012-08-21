(function () {
var __LIBS__ = {};
__LIBS__['ZY5ROPG40OCO17K0'] = (function (exports) { (function () { 

/************** utils.js **************/
function convertToUserUnit(value, unit) {
  if (value === null || value === void(0))
    return null;
  if (typeof value != 'string' && !(value instanceof String)) {
    var degree = value;
    switch (unit || 'px') {
    case 'pt':
      return degree * 1.25;
    case 'pc':
      return degree * 15;
    case 'mm':
      return degree * 90 / 25.4;
    case 'cm':
      return degree * 90 / 2.54;
    case 'in':
      return degree * 90.;
    case 'px':
      return degree;
    }
    throw new Error("Unsupported unit: " + unit);
  }
  var spec = /(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px)?/.exec(value);
  if (!spec)
    throw new Error('Invalid length / size specifier: ' + value)
  return convertToUserUnit(parseFloat(spec[1]), spec[2]);
}

exports.convertToUserUnit = convertToUserUnit;

function serializeStyleDef(obj) {
  var retval = [];
  for (var k in obj) {
    var v = obj[k];
    retval.push(k);
    retval.push(':');
    if (typeof v == 'number' || v instanceof Number) {
      retval.push(v);
    } else if (k == 'font-family') {
      retval.push("'" + v + "'");
    } else {
      retval.push(v);
    }
    retval.push(';');
  }
  return retval.join('');
}

exports.serializeStyleDef = serializeStyleDef;

function parseHtml(html) {
  var parser = new window.DOMParser();
  return parser.parseFromString(html, "text/xml");
}

exports.parseHtml = parseHtml;
 })(); return exports; })({});
__LIBS__['i117ANF_O9264E6X'] = (function (exports) { (function () { 

/************** renderer.js **************/
var utils = __LIBS__['ZY5ROPG40OCO17K0'];

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
 })(); return exports; })({});
__LIBS__['aBB4UVQE_GU6HJUQ'] = (function (exports) { (function () { 

/************** parser.js **************/
function parse(scanner, handlers, stack) {
  handlers.$stack = stack;
  for (var token = null; token = scanner.do_();) {
    switch (token[0]) {
    case 'string': case 'symbol': case 'number':
      stack.push(token[1]);
      break;
    case 'command':
      switch (token[1]) {
      case 'd':
        stack.push(stack[stack.length - 1]);
        break;
      default:
        var handler = handlers[token[1]];
        if (handler === void(0))
          throw new Error("TSE00002: Unknown command: " + token[1]);
        var arity = handler.length;
        handler.apply(handlers, stack.splice(stack.length - arity, arity));
        break;
      }
    }
  }
}

exports.parse = parse;
 })(); return exports; })({});
__LIBS__['nZKF2CFO36T9V8LK'] = (function (exports) { (function () { 

/************** tokenizer.js **************/
function newScanner(text) {
  var regexp = /"((?:\\.|[^"])*)"|:([^\s"]*)|(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([*+/A-Za-z_-]+)|([ \t]+)|(\r\n|\r|\n)|(.)/g;
  var line = 0;
  var column = 0;
  return {
    do_: function () {
      var retval = null;
      for (;;) {
        var g = regexp.exec(text);
        if (!g)
          return null;
        if (g[1] !== null && g[1] !== void(0)) {
          retval = ['string', g[1].replace(/\\(.)/g, '$1')];
        } else if (g[2]) {
          retval = ['symbol', g[2]];
        } else if (g[3]) {
          retval = ['number', parseFloat(g[3])];
        } else if (g[4]) {
          retval = ['command', g[4]];
        } else if (g[6]) {
          column = 0;
          line++;
          continue;
        } else if (g[7]) {
          throw new Error("TSE00001: Syntax error at column " + (column + 1) + " line " + (line + 1));
        }
        column += g[0].length;
        if (retval)
          break;
      }
      return retval;
    }
  };
}

exports.newScanner = newScanner;

function tokenize(text) {
  var retval = [];
  var scanner = newScanner(text);
  for (var token = null; token = scanner.do_();) {
    retval.push(token);
  }
  return retval;
}

exports.tokenize = tokenize;
 })(); return exports; })({});
__LIBS__['t0HULC5WTECKO6Y8'] = (function (exports) { (function () { 

/************** preloaded.js **************/
var tokenize = __LIBS__['nZKF2CFO36T9V8LK'].tokenize;

exports.rl = tokenize('1e-2 S 15952 1634 m 15790 1483 15570 1305 15307 1196 c 15307 2144 l 15048 2144 l 15048 405 l 15311 451 l 15318 453 15364 460 15364 486 c 15364 499 15307 534 15307 545 c 15307 1123 l 15410 961 l 15522 1009 15594 1037 15783 1160 c 15957 1275 16038 1347 16126 1424 c 15952 1634 l h 13469 1288 m 13431 1156 13381 1044 13313 932 c 13508 857 l 13589 987 13633 1123 13658 1213 c 13469 1288 l h 14206 1002 m 14187 1013 14185 1022 14162 1108 c 13998 1782 13554 2039 13343 2162 c 13168 2005 l 13594 1795 13893 1494 13976 873 c 14191 938 l 14220 947 14235 963 14235 978 c 14235 991 14231 993 14206 1002 c 13064 1395 m 13027 1270 12970 1154 12898 1042 c 13100 965 l 13174 1081 13231 1196 13269 1318 c 13064 1395 l h 11927 1026 m 11922 1165 11920 1382 11791 1659 c 11635 1995 11402 2177 11281 2273 c 11013 2109 l 11125 2041 11369 1891 11527 1577 c 11646 1340 11652 1145 11655 1026 c 11193 1026 l 11035 1272 10947 1369 10847 1474 c 10590 1331 l 10915 1031 11099 732 11235 282 c 11485 372 l 11499 376 11540 392 11540 416 c 11540 431 11534 436 11512 442 c 11490 453 11488 455 11477 484 c 11442 570 11415 631 11341 778 c 12469 778 l 12469 1026 l 11927 1026 l h 9434 1327 m 9346 1762 9166 1968 8795 2210 c 8582 2023 l 8938 1821 9094 1654 9166 1327 c 8385 1327 l 8385 1083 l 9193 1083 l 9195 1062 9197 1020 9197 947 c 9197 870 9195 822 9184 772 c 8982 818 8863 837 8670 855 c 8551 635 l 8714 627 9177 596 9645 357 c 9825 523 l 9832 530 9851 552 9851 568 c 9851 576 9847 581 9840 583 c 9770 583 l 9757 583 9755 585 9737 592 c 9665 624 9610 651 9458 699 c 9461 778 9467 901 9465 978 c 9465 1035 9463 1046 9463 1083 c 10049 1083 l 10049 1327 l 9434 1327 l h 2404 352 m 2404 80 l 1902 353 l 1902 625 l 2404 352 l h 949 849 m 1510 849 l 1510 1083 l 949 1083 l 949 849 l h 949 417 m 1510 417 l 1510 623 l 949 623 l 949 417 l h 2404 1407 m 2404 1141 l 1902 869 l 1902 1141 l 2393 1407 l 1353 1407 l 1353 1314 l 1761 1314 l 1761 189 l 1326 189 l 1384 0 l 1116 0 l 1058 189 l 700 189 l 700 1314 l 1101 1314 l 1101 1407 l 69 1407 l 559 1141 l 559 870 l 58 1141 l 58 1651 l 897 1651 l 720 1821 444 2021 39 2161 c 0 2175 l 0 2431 l 77 2403 l 517 2245 860 2041 1101 1795 c 1101 2467 l 1353 2467 l 1353 1795 l 1597 2045 1943 2248 2382 2399 c 2458 2425 l 2458 2169 l 2419 2156 l 2013 2021 1736 1822 1556 1651 c 2404 1651 l 2404 1407 l 2404 1407 l h 58 80 m 58 352 l 559 624 l 559 352 l 58 80 l h 7458 340 m 7458 91 l 5000 91 l 5000 340 l 6070 340 l 6070 705 l 6070 801 6068 851 6064 920 c 5076 920 l 5076 1171 l 6025 1171 l 5955 1458 5733 1908 5033 2157 c 4994 2170 l 4994 2462 l 5073 2432 l 5813 2148 6090 1828 6222 1422 c 6382 1836 6762 2168 7377 2432 c 7458 2467 l 7458 2166 l 7418 2153 l 6839 1964 6494 1526 6399 1171 c 7374 1171 l 7374 920 l 6343 920 l 6337 870 6331 810 6331 705 c 6331 340 l 7458 340 l 3591 838 m 3759 838 l 3863 838 3947 923 3947 1028 c 3947 1132 3863 1216 3759 1216 c 3591 1216 l 3591 838 l 3973 1400 m 4106 1326 4190 1183 4190 1028 c 4190 789 3997 595 3759 595 c 3348 595 l 3348 1872 l 3591 1872 l 3591 1459 l 3716 1459 l 3727 1474 4014 1872 4014 1872 c 4312 1872 l 4312 1872 3995 1430 3973 1400 c 4930 1234 m 4930 1891 4397 2423 3740 2423 c 3083 2423 2550 1891 2550 1234 c 2550 576 3083 44 3740 44 c 4397 44 4930 576 4930 1234 c');
 })(); return exports; })({});
__LIBS__['BVOX2P4CDBHXSXJS'] = (function (exports) { (function () { 

/************** styles.js **************/
exports.pre = { 'white-space': 'pre' };
exports.b = { 'font-weight': 900 };
exports.l = { 'text-align': 'left' };
exports.c = { 'text-align': 'center' };
exports.r = { 'text-align': 'right' };
exports.f0 = { 'font-family': 'Arial' };
exports.f1 = { 'font-family': 'Arial Black' };
exports.f2 = { 'font-family': 'Verdana' };
exports.f3 = { 'font-family': 'Impact' };
exports.f4 = { 'font-family': 'Comic Sans MS' };
exports.f5 = { 'font-family': 'Times New Roman' };
exports.f6 = { 'font-family': 'Courier New' };
exports.f7 = { 'font-family': 'Lucida Console' };
exports.f8 = { 'font-family': 'Lucida Sans Unicode' };
exports.f9 = { 'font-family': 'Modern' };
exports.f10 = { 'font-family': 'Microsoft Sans Serif' };
exports.f11 = { 'font-family': 'Roman' };
exports.f12 = { 'font-family': 'Script' };
exports.f13 = { 'font-family': 'Symbol' };
exports.f14 = { 'font-family': 'Wingdings' };
exports.f15 = { 'font-family': 'ＭＳ ゴシック' };
exports.f16 = { 'font-family': 'ＭＳ Ｐゴシック' };
exports.f17 = { 'font-family': 'ＭＳ 明朝' };
exports.f18 = { 'font-family': 'ＭＳ Ｐ明朝' };
exports.f19 = { 'font-family': 'MS UI Gothic' };
 })(); return exports; })({});


/************** ticket-viewer.js **************/
(function ($) {
  var PRELOADED_OBJECTS = __LIBS__['t0HULC5WTECKO6Y8'];
  var tokenizer = __LIBS__['nZKF2CFO36T9V8LK'];
  var parse = __LIBS__['aBB4UVQE_GU6HJUQ'].parse;
  var newHandler = __LIBS__['i117ANF_O9264E6X'].newHandler;
  var utils = __LIBS__['ZY5ROPG40OCO17K0'];

  var TicketViewer = function TicketViewer() {
    this.initialize.apply(this, arguments);
  };

  TicketViewer.prototype.initialize = function (node, options) {
    this.callbacks = {
      load: null,
      loadstart: null,
      message: null
    };
    if (options.callbacks) {
      for (var k in this.callbacks)
        this.callbacks[k] = options.callbacks[k] || null;
    }
    if (!this.callbacks.message)
      this.callbacks.message = function () {};

    this.node = node;
    this.dataSource = options.dataSource;
    this.zoomRatio = options.zoomRatio || 1.;
    this.drawable = null;
    this.objects = options.objects;
    this.styleClasses = options.styleClasses;
    this.zoomRatio = 1.0;
    this._uiMode = 'move';
  };

  TicketViewer.prototype.load = function TicketViewer_load() {
    if (this.drawable !== null)
      this.drawable.dispose();
    var self = this;
    self.dataSource(function (data) {
      setTimeout(function () {
        var paperSize = {
          x: utils.convertToUserUnit(data['size'].width),
          y: utils.convertToUserUnit(data['size'].height)
        };
        var contentSize = { x: 1000, y: 1000 };
        var drawable = new Fashion.Drawable(self.node, { contentSize: contentSize });
        var offset = { x: 0, y: 0 };
        drawable.draw(new Fashion.Rect({
          position: offset,
          size: paperSize,
          style: { stroke: new Fashion.Stroke(new Fashion.Color('#000'), 1) }
        }));
        if (data.perforations) {
          var verticalPerforations = data['perforations']['vertical'];
          for (var i = 0; i < verticalPerforations.length; i++) {
            var x = utils.convertToUserUnit(verticalPerforations[i]);
            drawable.draw(new Fashion.Path({
              points: [['M', offset.x + x, offset.y], ['L', offset.x + x, offset.y + paperSize.y], ['Z']],
              style: { stroke: new Fashion.Stroke(new Fashion.Color('#ccc'), 1, [2, 2]) }
            }));
          }
          var horizontalPerforations = data['perforations']['horizontal'];
          for (var i = 0; i < horizontalPerforations.length; i++) {
            var y = utils.convertToUserUnit(horizontalPerforations[i]);
            drawable.draw(new Fashion.Path({
              points: [['M', offset.x, offset.y + y], ['L', offset.x + paperSize.x, offset.y + y], ['Z']],
              style: { stroke: new Fashion.Stroke(new Fashion.Color('#ccc'), 1, [2, 2]) }
            }));
          }
        }
        var printableAreas = data['printable_areas'];
        for (var i = 0; i < printableAreas.length; i++) {
          var printableArea = printableAreas[i];
          var position = {
            x: offset.x + utils.convertToUserUnit(printableArea.x),
            y: offset.y + utils.convertToUserUnit(printableArea.y)
          };
          var size = {
            x: utils.convertToUserUnit(printableArea.width),
            y: utils.convertToUserUnit(printableArea.height)
          };
          drawable.draw(new Fashion.Rect({
            position: position,
            size: size,
            style: {
              stroke: new Fashion.Stroke(new Fashion.Color('#cc8'), 1),
              fill: new Fashion.FloodFill(new Fashion.Color('#ffc'))
            }
          }));
        }
        if (data['drawing'] !== void(0)) {
          parse(tokenizer.newScanner(data['drawing']),
                newHandler(self.objects, self.styleClasses, drawable, offset),
                []);
        }
        drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
        self.drawable = drawable;
        self._refreshUI(self.uiMode);
      }, 0);
    }, function () {
      self.callbacks.message('Failed to load data');
    });
  };

  TicketViewer.prototype._refreshUI = function TicketViewer__refreshUI() {
    if (this.drawable) {
      var self = this;
      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

      switch (self._uiMode) {
      case 'move':
        var mousedown = false, scrollPos = null;
        this.drawable.addEvent({
          mousedown: function (evt) {
            if (self.animating)
              return;
            mousedown = true;
            scrollPos = self.drawable.scrollPosition();
            self.startPos = evt.logicalPosition;
          },

          mouseup: function (evt) {
            if (self.animating)
              return;
            mousedown = false;
            if (self.dragging) {
              self.drawable.releaseMouse();
              self.dragging = false;
            }
          },

          mousemove: function (evt) {
            if (self.animating)
              return;
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

      case 'zoomin':
        this.drawable.addEvent({
          mouseup: function(evt) {
            self.zoomRatio*=1.2;
            this.transform(Fashion.Matrix.scale(self.zoomRatio));
          }
        });
        break;

      case 'zoomout':
        this.drawable.addEvent({
          mouseup: function(evt) {
            self.zoomRatio/=1.2;
            this.transform(Fashion.Matrix.scale(self.zoomRatio));
          }
        });
        break;

      default:
        throw new Error("Invalid ui mode: " + self._uiMode);
      }
    }
  };

  TicketViewer.prototype.uiMode = function TicketViewer_uiMode(type) {
    if (type === void(0))
      return this._uiMode;
    this._uiMode = type;
    this._refreshUI();
    this.callbacks.uimodeselect && this.callbacks.uimodeselect(this, type);
  };


  TicketViewer.prototype.dispose = function TicketViewer_dispose() {
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
  };

  $.fn.ticketviewer = function (options) {
    var aux = this.data('ticketviewer');

    if (!options)
      throw new Error("Options must be given");
    if (typeof options == 'object') {
      if (typeof options.dataSource != 'function' &&
          typeof options.dataSource != 'string' &&
          typeof options.dataSource != 'object') {
        throw new Error("Required option missing: dataSource");
      }
      if (aux)
        aux.dispose();

      var _options = $.extend({}, options);
     
      _options.dataSource =
          typeof options.dataSource == 'function' ?
            options.dataSource:
            function (next, error) {
              $.ajax({
                type: 'get',
                url: options.dataSource,
                dataType: 'json',
                success: function(json) { next(json); },
                error: function(xhr, text) { error("Failed to load drawing data (reason: " + text + ")"); }
              });
            };
      if (this.length == 0)
        throw new Error("No nodes are selected");
      this.empty();
      _options.objects = _options.objects || __LIBS__['t0HULC5WTECKO6Y8'];
      _options.styleClasses = _options.styleClasses || __LIBS__['BVOX2P4CDBHXSXJS'];
      aux = new TicketViewer(this[0], _options),
      this.data('ticketviewer', aux);
    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        aux.dispose();
        this.data('ticketviewer', null);
      } else {
        if (!aux)
          throw new Error("Command issued against an uninitialized element");
        switch (options) {
        case 'load':
          aux.load();
          break;

        case 'uimode':
          if (arguments.length >= 2)
            aux.uiMode(arguments[1]);
          else
            return aux.uiMode();
          break;

        case 'refresh':
          return aux.refresh();
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
