INSERT INTO SejTicketTemplateFile (
    status,
    template_id,
    template_name,
    ticket_html,
    ticket_css,
    notation_version
) VALUES (
    '4',
    'TTTS000002',
    '旧台紙用テンプレート2',
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
  <title></title>
<!--[if (lt IE 9)]>
  <style type="text/css">
v\\:* { behavior: url(#default#VML); }
</style>
<![endif]-->
  <style type="text/css">
body {
  margin: 0 0;
}

.pre { white-space: pre; }
.b { font-weight: 900; }
.l { text-align: left; }
.c { text-align: center; }
.r { text-align: right; }
.f0 { font-family: "Arial"; }
.f1 { font-family: "Arial Black"; }
.f2 { font-family: "Verdana"; }
.f3 { font-family: "Impact"; }
.f4 { font-family: "Comic Sans MS"; }
.f5 { font-family: "Times New Roman"; }
.f6 { font-family: "Courier New"; }
.f7 { font-family: "Lucida Console"; }
.f8 { font-family: "Lucida Sans Unicode"; }
.f9 { font-family: "Modern"; }
.f10 { font-family: "Microsoft Sans Serif"; }
.f11 { font-family: "Roman"; }
.f12 { font-family: "Script"; }
.f13 { font-family: "Symbol"; }
.f14 { font-family: "Wingdings"; }
.f15 { font-family: "ＭＳ ゴシック"; }
.f16 { font-family: "ＭＳ Ｐゴシック"; }
.f17 { font-family: "ＭＳ 明朝"; }
.f18 { font-family: "ＭＳ Ｐ明朝"; }
.f19 { font-family: "MS UI Gothic"; }

#appearance {
  position: absolute;
  left: 0px;
  top: 0px;
}

#fixtags {
  position: absolute;
  left: 0px;
  top: 0px;
}

#FIXMSG01 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  position: absolute;
  left: 143px;
  top: 159px;
  font-weight: bold
}

#FIXMSG02 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 168px;
}

/* 発券店：セブン-イレブン */
#FIXMSG03 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 216px;
  width: 5em;
}

/* 払込票 */
#FIXMSG04 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 225px;
  width: 5em;
}

#FIXMSG05 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 420px;
  top: 216px;
}

#FIXMSG06 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 420px;
  top: 225px;
}

/* 再発券印字 使用していない */
#FIXTAG01 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 330px;
  top: 216px;
  white-space: nowrap;
}

/* 発券店名 */
#FIXTAG02 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 83px;
  top: 216px;
  width: 16em;
  white-space: nowrap;
}

/* 発券店番 */
#FIXTAG03 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 285px;
  top: 216px;
  width: 8em;
  white-space: nowrap;
}

/* 発券日時 */
#FIXTAG04 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 180px;
  top: 225px;
  width: 10em;
  white-space: nowrap;
}

/* 払込票番号 */
#FIXTAG05 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 83px;
  top: 225px;
  width: 7em;
  white-space: nowrap;
}

/* 発券枚数 */
#FIXTAG06 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 285px;
  top: 225px;
  width: 5em;
  white-space: nowrap;
}
</style>
  <script type="text/javascript">
var FIXTAGS = [
  ''FIXTAG01'', ''FIXTAG02'', ''FIXTAG03'', ''FIXTAG04'', ''FIXTAG05'', ''FIXTAG06''
];
var FIXTAG_PREFIXES = {
  ''FIXTAG02'': ''セブン－イレブン　''
};
var PRELOADED_OBJECTS = {
};

function loadXml(url, success, error) {
  if (typeof window.ActiveXObject == ''undefined'') {
    var xhr = new XMLHttpRequest();
    if (typeof xhr.overrideMimeType != ''undefined'')
      xhr.overrideMimeType(''text/xml'');
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        if (xhr.status != 200 && xhr.status != 0) {
          error(xhr.status);
          return;
        }

        var xml = xhr.responseXML;
        if ((!xml || !xml.documentElement)) {
          if (!xhr.responseText) {
            error(''General failure'');
            return;
          }
          try {
            var parser = new window.DOMParser();
            xml = parser.parseFromString(xhr.responseText, "text/xml");
          } catch (e) {
            error(e.message);
            return;
          }
        }
        success(xml);
      }
    };
    try {
      xhr.open("GET", url, true);
      xhr.send();
    } catch (e) {
      error(e.message);
    }
  } else {
    var xml = new ActiveXObject("Microsoft.XMLDOM");
    var errorReported = false;
    xml.async = true;
    xml.onreadystatechange = function () {
      if (xml.readyState == 4) {
        if (xml.parseError.errorCode != 0) {
          if (!errorReported) {
            errorReported = true;
            error(xml.parseError.reason);
          }
        } else {
          success(xml);
        }
      }
    };
    try {
      xml.load(url);
    } catch (e) {
      if (!errorReported) {
        errorReported = true;
        error(e.message);
      }
    }
  }
}

function newScanner(text) {
  var regexp = /("(?:\\\\.|[^"])*)"|:([^\\s"]*)|(-?(?:[0-9]+(?:\\.[0-9]+)?|\\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([*+/A-Za-z_-]+)|([ \\t]+)|(\\r\\n|\\r|\\n)|(.)/g;
  var line = 0;
  var column = 0;
  return {
    do_: function () {
      var retval = null;
      for (;;) {
        var g = regexp.exec(text);
        if (!g)
          return null;
        if (g[1]) {
          retval = [''string'', g[1].substring(1).replace(/\\\\(.)/g, ''$1'')];
        } else if (g[2]) {
          retval = [''symbol'', g[2]];
        } else if (g[3]) {
          retval = [''number'', parseFloat(g[3])];
        } else if (g[4]) {
          retval = [''command'', g[4]];
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

function tokenize(text) {
  var retval = [];
  var scanner = newScanner(text);
  for (var token = null; token = scanner.do_();) {
    retval.push(token);
  }
  return retval;
}

function parse(scanner, handlers, stack) {
  handlers.$stack = stack;
  for (var token = null; token = scanner.do_();) {
    switch (token[0]) {
    case ''string'': case ''symbol'': case ''number'':
      stack.push(token[1]);
      break;
    case ''command'':
      switch (token[1]) {
      case ''d'':
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

function findXmlNode(xmldoc, n, path) {
  var retval = null;
  if (typeof ActiveXObject == ''undefined'') {
    var xpathResult = xmldoc.evaluate(path, n, null, XPathResult.ANY_TYPE, null);
    switch (xpathResult.resultType) {
    case XPathResult.UNORDERED_NODE_ITERATOR_TYPE:
    case XPathResult.ORDERED_NODE_ITERATOR_TYPE:
      retval = [];
      for (var n = null; (n = xpathResult.iterateNext());)
        retval.push(n);
      break;
    case XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE:
    case XPathResult.ORDERED_NODE_SNAPSHOT_TYPE:
      retval = [];
      for (var i = 0, l = xpathResult.snapshotLength; i < l; i++)
        retval.push(xpathResult.snapshotItem(i));
      break;
    case XPathResult.NUMBER_TYPE:
      retval = xpathResult.numberValue;
      break;
    case XPathResult.STRING_TYPE:
      retval = xpathResult.stringValue;
      break;
    case XPathResult.BOOLEAN_TYPE:
      retval = xpathResult.booleanValue;
      break;
    }
  } else {
    retval = n.selectNodes(path);
  }
  return retval;
}

function stringizeXmlNodes(nodes) {
  var retval = [];
  for (var i = 0, l = nodes.length; i < l; i++) {
    retval.push(stringizeXmlNode(nodes[i]));
  }
  return retval.join('''');
}

function stringizeXmlNode(n) {
  switch (n.nodeType) {
  case 1:
    return stringizeXmlNodes(n.childNodes);
  default:
    return n.nodeValue;
  }
}

function Drawable() {
  this.initialize.apply(this, arguments);
}

if (window.ActiveXObject) {
  function newVmlElement(name) {
    return document.createElement("v:" + name);
  }

  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    this.width = width;
    this.height = height;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newVmlElement(''shape'');
    var buf = [];
    var currentPoint = { x: 0., y: 0. };
    for (var i in pathData) {
      var datum = pathData[i];
      switch (datum[0]) {
      case ''Z'':
        buf.push(''x'');
        break;
      case ''M'':
        buf.push(''m'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case ''L'':
        buf.push(''l'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case ''C'':
        buf.push(''c'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0),
          (datum[5] * 1000).toFixed(0),
          (datum[6] * 1000).toFixed(0));
        currentPoint = { x: datum[5], y: datum[6] };
        break;
      case ''Q'':
        buf.push(''q'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0));
        currentPoint = { x: datum[3], y: datum[4] };
        break;
      case ''A'':
        var rx = Math.abs(datum[1]), ry = Math.abs(datum[2]),
            phi = Math.abs(datum[3]), largeArc = datum[4], sweep = datum[5],
            x  = datum[6], y = datum[7];
        var s = Math.sin(Math.PI * phi / 180),
            c = Math.cos(Math.PI * phi / 180);
        var cx = (currentPoint.x - x) / 2, cy = (currentPoint.y - y) / 2;
        var x1_ = c * cx + s * cy, y1_ = -s * cx + c * cy;
        var lambda = Math.sqrt((x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry));
        if (lambda > 1)
          rx *= lambda, ry *= lambda;
        var c_ = (largeArc == sweep ? -1: 1) * Math.sqrt((rx * rx * ry * ry - rx * rx * y1_ * y1_ - ry * ry * x1_ * x1_) / (rx * rx * y1_ * y1_ + ry * ry * x1_ * x1_));
        var cx_ = c_ * (rx * y1_) / ry,
            cy_ = -c_ * (ry * x1_) / rx;
        var ecx = c * cx_ - s * cy_ + (x + currentPoint.x) / 2,
            ecy = s * cx_ + c * cy_ + (y + currentPoint.y) / 2;
        var vx1 = (x1_ - cx_) / rx, vy1 = (y1_ - cy_) / ry;
        var vx2 = (-x1_ - cx_) / rx, vy2 = (-y1_ - cy_) / ry;
        var theta1 = (vy1 > 0 ? 1: -1) * Math.acos(vx1 / Math.sqrt(vx1 * vx1 + vy1 * vy1));
        var thetad = (vx1 * vy2 - vy1 * vx2 > 0 ? 1: -1) * Math.acos((vx1 * vx2 + vy1 * vy2) / Math.sqrt(vx1 * vx1 + vy1 * vy1) / Math.sqrt(vx2 * vx2 + vy2 * vy2));
        if (sweep && thetad > 0)
          thetad -= Math.PI * 2;
        else if (!sweep && thetad < 0)
          thetad += Math.PI * 2;
        var rsx = ecx + Math.cos(theta1) * rx,
            rsy = ecy + Math.sin(theta1) * ry;
        var rex = ecx + Math.cos(theta1 + thetad) * rx,
            rey = ecy + Math.sin(theta1 + thetad) * ry;
        if (thetad < 0) {
          var tmp;
          tmp = rsx, rsx = rex, rex = tmp;
          tmp = rsy, rsy = rey, rey = tmp;
        }
        if (phi == 0) {
          var rsxs = (rsx * 1000).toFixed(0),
              rsys = (rsy * 1000).toFixed(0);
          var rexs = (rex * 1000).toFixed(0),
              reys = (rey * 1000).toFixed(0);
          buf.push(''m'', rsxs, rsys);
          buf.push(''at'',
            ((ecx - rx) * 1000).toFixed(0),
            ((ecy - ry) * 1000).toFixed(0),
            ((ecx + rx) * 1000).toFixed(0),
            ((ecy + ry) * 1000).toFixed(0),
            rsxs, rsys, rexs, reys);
          buf.push(''m'', rexs, reys);
          if (thetad < 0) {
            buf.push(''m'', rsxs, rsys);
            buf.push(''l'', rsxs, rsys);
          }
        }
        break;
      }
    }
    path.style.display = ''block'';
    path.style.position = ''absolute'';
    path.style.left = ''0'';
    path.style.top = ''0'';
    path.style.width = this.width;
    path.style.height = this.height;
    path.coordSize = parseFloat(this.width) * 1000 + "," + parseFloat(this.height) * 1000;
    path.setAttribute(''path'', buf.join('' ''));
    this.n.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute(''strokeWeight'', value.strokeWidth);
        if (value.strokeColor) {
          path.setAttribute(''strokeColor'', value.strokeColor || ''none'');
          path.setAttribute(''stroked'', ''t'');
        } else {
          path.setAttribute(''stroked'', ''f'');
        }
        if (value.fillColor) {
          path.setAttribute(''fillColor'', value.fillColor);
          path.setAttribute(''filled'', ''t'');
        } else {
          path.setAttribute(''filled'', ''f'');
        }
      }
    };
  };
} else {
  var SVG_NAMESPACE = ''http://www.w3.org/2000/svg'';
  function newSvgElement(name) {
    return document.createElementNS(SVG_NAMESPACE, name);
  }
  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    var svg = newSvgElement(''svg'');
    svg.setAttribute(''style'', ''display:block;position:absolute;left:0;top:0'');
    svg.setAttribute(''version'', ''1.0'');
    svg.setAttribute(''width'', width);
    svg.setAttribute(''height'', height);
    svg.setAttribute(''viewBox'', ''0 0 '' + parseFloat(width) + '' '' + parseFloat(height));
    this.n.appendChild(svg);
    this.svg = svg;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newSvgElement(''path'');
    var buf = [];
    for (var i in pathData) {
      buf.push.apply(buf, pathData[i]);
    }
    path.setAttribute(''d'', buf.join('' ''));
    this.svg.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute(''stroke-width'', value.strokeWidth);
        path.setAttribute(''stroke'', value.strokeColor || ''none'');
        path.setAttribute(''fill'', value.fillColor || ''none'');
      }
    };
  };
}

function newHandler(n, xmldoc) {
  var pathData = [];
  var drawable = null;
  var unit = ''mm'';
  var fontSize = 10;
  var classes = [];
  var objects = PRELOADED_OBJECTS;
  var currentPoint = { x: 0., y: 0. };
  var scale = 1.;
  var lineHeight = null;
  var currentMatrix = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };
  var style = {
    fillColor: null,
    strokeColor: null,
    strokeWidth: null
  };
  var dpiFix = 1.;
  function initPathData() {
    if (pathData == null) {
      var p = applyMatrix(currentMatrix, currentPoint);
      pathData = [[''M'', p.x * dpiFix, p.y * dpiFix]];
    }
  }
  function initDrawable() {
    if (drawable == null)
      drawable = new Drawable(n, ''1000'' + unit, ''1000'' + unit);
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
      var nodes = findXmlNode(xmldoc, xmldoc.documentElement, path);
      for (var i = 0; i < nodes.length; i++)
        this.$stack.push(nodes[i]);
      this.$stack.push(nodes.length);
    },
    sxn: function _stringizeXmlNodes() {
      var l = this.$stack.pop();
      var nodes = this.$stack.splice(this.$stack.length - l, l);
      this.$stack.push(stringizeXmlNodes(nodes));
    },
    lo: function _loadObject(name) {
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
      classes.push(klass);
    },
    pc: function popClass() {
      classes.pop();
    },
    sc: function setClass(klass) {
      classes = [klass];
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
      if (unit == ''px'')
        dpiFix = 96. / 90;
      else
        dpiFix = 1.;
    },
    X: function showText(width, height, text) {
      var p = applyMatrix(currentMatrix, currentPoint);
      n.insertAdjacentHTML(''beforeEnd'', [
        ''<pre><div style="position:absolute;white-space:pre;'',
        ''font-size:'', fontSize, ''px'', '';'',
        ''line-height:'', lineHeight ? (lineHeight + ''px''): ''1em'', '';'',
        ''left:'', p.x * dpiFix, unit, '';'',
        ''top:'', p.y * dpiFix, unit, '';'',
        ''width:'', width * dpiFix * scale, unit, '';'',
        ''height:'', height * dpiFix * scale, unit, ''"'',
        '' class="'', classes.join('' ''), ''"'',
        ''>'', text, ''</div></pre>''].join(''''));
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
        pathData.push([''M'', p1.x * dpiFix, p1.y * dpiFix]);
      currentPoint = p;
    },
    l: function lineTo(x, y) {
      x *= scale;
      y *= scale;
      var p = { x: x, y: y };
      var p1 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push([''L'', p1.x * dpiFix, p1.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''Q'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix]);
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
      pathData.push([''A'', r.x * dpiFix, r.y * dpiFix, phi, largeArc, sweep,
                          p1.x * dpiFix, p1.y * dpiFix]);
      currentPoint = p;
    },
    h: function closePath() {
      initPathData();
      pathData.push([''Z'']);
    },
    f: function fill() {
      if (pathData == null)
        return;
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: null,
        strokeColor: null,
        fillColor: style.fillColor
      });
      pathData = null;
    },
    s: function stroke() {
      if (pathData == null)
        return;
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale,
        strokeColor: style.strokeColor,
        fillColor: null
      });
      pathData = null;
    },
    B: function strokeAndFill() {
      if (pathData == null)
        return;
      if (drawable == null)
        drawable = new Drawable(n, ''1000'' + unit, ''1000'' + unit);
      drawable.path(pathData).style({
        strokeWidth: style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale,
        strokeColor: style.strokeColor,
        fillColor: style.fillColor
      });
      pathData = null;
    }
  };
}


function textValue(node) {
  if (''text'' in node)
    return node.text;
  return (function _(node) {
    switch (node.nodeType) {
    case 3:
      return node.nodeValue;
    case 1:
      var c = node.childNodes, retval = '''';
      for (var i = 0; i < c.length; i++) {
        retval += _(c[i]);
      }
      return retval;
    }
    return '''';
  })(node);
}

function populateFixtags(xmldoc) {
  for (var i = 0; i < FIXTAGS.length; i++) {
    var name = FIXTAGS[i];
    var src = xmldoc.getElementsByTagName(name);
    var tag = document.getElementById(name);
    var prefix = FIXTAG_PREFIXES[name];
    if (src.length > 0 && tag != null) {
      var text = (prefix || "") + textValue(src[0]);
      tag.appendChild(document.createTextNode(text));
    }
  }
}

function reportError(msg) {
  var page = document.getElementById(''page'');
  page.innerHTML = '''';
  throw new Error(msg);
}

function tryWith(args, f, failure) {
  var i = 0;
  function _() {
    if (i >= args.length)
      return failure.apply(null, arguments);
    f(args[i++], _);
  }
  _();
}

window.onload = function() {
  tryWith(
    [''file:///c:/sejpos/posapl/mmdata/mm60/xml/ptct.xml'', ''ptct.xml''],
    function (dataUrl, next) {
      loadXml(dataUrl, function (xmldoc) {
        var appearance = document.getElementById(''appearance'');
        try {
          var handler = newHandler(appearance, xmldoc);
          parse(
            newScanner(
              stringizeXmlNodes(
                findXmlNode(xmldoc, xmldoc.documentElement, ''b''))),
            handler,
            []);
          populateFixtags(xmldoc);
        } catch (e) {
          reportError(e.message);
        }
      }, next);
    },
    function (msg) {
      reportError("TS00003: Load failure (" + msg.replace(/[\\r\\n]/, '''')+ ")");
    }
  );
};
</script>
</head>
<body>
  <div id="page">
    <div id="appearance"></div>
    <div id="fixtags">
      <div id="FIXMSG03">発券店：</div>
      <div id="FIXMSG04">払込票：</div>
      <div id="FIXTAG01"></div>
      <div id="FIXTAG02"></div>
      <div id="FIXTAG03"></div>
      <div id="FIXTAG04"></div>
      <div id="FIXTAG05"></div>
      <div id="FIXTAG06"></div>
    </div>
  </div>
</body>
</html>',
    '',
    3
);

INSERT INTO SejTicketTemplateFile (
    status,
    template_id,
    template_name,
    ticket_html,
    ticket_css,
    notation_version
) VALUES (
    '4',
    'NTTS000003',
    '新台紙用テンプレート2',
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
  <title></title>
<!--[if (lt IE 9)]>
  <style type="text/css">
v\\:* { behavior: url(#default#VML); }
</style>
<![endif]-->
  <style type="text/css">
body {
  margin: 0 0;
}

.pre { white-space: pre; }
.b { font-weight: 900; }
.l { text-align: left; }
.c { text-align: center; }
.r { text-align: right; }
.f0 { font-family: "Arial"; }
.f1 { font-family: "Arial Black"; }
.f2 { font-family: "Verdana"; }
.f3 { font-family: "Impact"; }
.f4 { font-family: "Comic Sans MS"; }
.f5 { font-family: "Times New Roman"; }
.f6 { font-family: "Courier New"; }
.f7 { font-family: "Lucida Console"; }
.f8 { font-family: "Lucida Sans Unicode"; }
.f9 { font-family: "Modern"; }
.f10 { font-family: "Microsoft Sans Serif"; }
.f11 { font-family: "Roman"; }
.f12 { font-family: "Script"; }
.f13 { font-family: "Symbol"; }
.f14 { font-family: "Wingdings"; }
.f15 { font-family: "ＭＳ ゴシック"; }
.f16 { font-family: "ＭＳ Ｐゴシック"; }
.f17 { font-family: "ＭＳ 明朝"; }
.f18 { font-family: "ＭＳ Ｐ明朝"; }
.f19 { font-family: "MS UI Gothic"; }

.ts {
  text-align:left;
  margin-left: 0;
  margin-top: -1em;
  width: 100%;
}

.tm {
  text-align: center;
  margin-left: -50%;
  margin-top: -1em;
  width: 100%;
}

.te {
  text-align: right;
  margin-left: -100%;
  margin-top: -1em;
  width: 100%;
}

#appearance {
  position: absolute;
  left: 0px;
  top: 0px;
  width: 177.8mm;
}

#fixtags {
  position: absolute;
  left: 0px;
  top: 0px;
}

#FIXMSG01 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  position: absolute;
  left: 143px;
  top: 197px;
  font-weight: bold
}

#FIXMSG02 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 206px;
}

/* 発券店：セブン-イレブン */
#FIXMSG03 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 216px;
  width: 5em;
}

#FIXMSG05 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 420px;
  top: 216px;
}

#FIXMSG06 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 420px;
  top: 225px;
}

/* 再発券印字 使用していない */
#FIXTAG01 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 330px;
  top: 216px;
  white-space: nowrap;
}

/* 発券店名 */
#FIXTAG02 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 83px;
  top: 216px;
  width: 16em;
  white-space: nowrap;
}

/* 発券店番 */
#FIXTAG03 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 285px;
  top: 216px;
  width: 8em;
  white-space: nowrap;
}

/* 発券日時 */
#FIXTAG04 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 180px;
  top: 225px;
  width: 10em;
  white-space: nowrap;
}

/* 払込票番号 */
#FIXTAG05 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 83px;
  top: 225px;
  width: 7em;
  white-space: nowrap;
}

/* 発券枚数 */
#FIXTAG06 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 285px;
  top: 225px;
  width: 5em;
  white-space: nowrap;
}

/* 引換票・払込票 */
#FIXTAG07 {
  font-family: "ＭＳ ゴシック";
  font-size: 7pt;
  font-weight: bold;
  position: absolute;
  left: 50px;
  top: 225px;
  width: 5em;
}
</style>
  <script type="text/javascript">
var FIXTAGS = [
  ''FIXTAG01'', ''FIXTAG02'', ''FIXTAG03'', ''FIXTAG04'', ''FIXTAG05'', ''FIXTAG06'', ''FIXTAG07''
];
var FIXTAG_PREFIXES = {
  ''FIXTAG02'': ''セブン-イレブン　''
};
var FIXTAG_SUFFIXES = {
  ''FIXTAG07'': ''：''
};
var PRELOADED_OBJECTS = {
};

function loadXml(url, success, error) {
  if (typeof window.ActiveXObject == ''undefined'') {
    var xhr = new XMLHttpRequest();
    if (typeof xhr.overrideMimeType != ''undefined'')
      xhr.overrideMimeType(''text/xml'');
    xhr.onreadystatechange = function() {
      if (xhr.readyState == 4) {
        if (xhr.status != 200 && xhr.status != 0) {
          error(xhr.status);
          return;
        }

        var xml = xhr.responseXML;
        if ((!xml || !xml.documentElement)) {
          if (!xhr.responseText) {
            error(''General failure'');
            return;
          }
          try {
            var parser = new window.DOMParser();
            xml = parser.parseFromString(xhr.responseText, "text/xml");
          } catch (e) {
            error(e.message);
            return;
          }
        }
        success(xml);
      }
    };
    try {
      xhr.open("GET", url, true);
      xhr.send();
    } catch (e) {
      error(e.message);
    }
  } else {
    var xml = new ActiveXObject("Microsoft.XMLDOM");
    var errorReported = false;
    xml.async = true;
    xml.onreadystatechange = function () {
      if (xml.readyState == 4) {
        if (xml.parseError.errorCode != 0) {
          if (!errorReported) {
            errorReported = true;
            error(xml.parseError.reason);
          }
        } else {
          success(xml);
        }
      }
    };
    try {
      xml.load(url);
    } catch (e) {
      if (!errorReported) {
        errorReported = true;
        error(e.message);
      }
    }
  }
}

function newScanner(text) {
  var regexp = /("(?:\\\\.|[^"])*)"|:([^\\s"]*)|(-?(?:[0-9]+(?:\\.[0-9]+)?|\\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([*+/A-Za-z_-]+)|([ \\t]+)|(\\r\\n|\\r|\\n)|(.)/g;
  var line = 0;
  var column = 0;
  return {
    do_: function () {
      var retval = null;
      for (;;) {
        var g = regexp.exec(text);
        if (!g)
          return null;
        if (g[1]) {
          retval = [''string'', g[1].substring(1).replace(/\\\\(.)/g, ''$1'')];
        } else if (g[2]) {
          retval = [''symbol'', g[2]];
        } else if (g[3]) {
          retval = [''number'', parseFloat(g[3])];
        } else if (g[4]) {
          retval = [''command'', g[4]];
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

function tokenize(text) {
  var retval = [];
  var scanner = newScanner(text);
  for (var token = null; token = scanner.do_();) {
    retval.push(token);
  }
  return retval;
}

function parse(scanner, handlers, stack) {
  handlers.$stack = stack;
  for (var token = null; token = scanner.do_();) {
    switch (token[0]) {
    case ''string'': case ''symbol'': case ''number'':
      stack.push(token[1]);
      break;
    case ''command'':
      switch (token[1]) {
      case ''d'':
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

function findXmlNode(xmldoc, n, path) {
  var retval = null;
  if (typeof ActiveXObject == ''undefined'') {
    var xpathResult = xmldoc.evaluate(path, n, null, XPathResult.ANY_TYPE, null);
    switch (xpathResult.resultType) {
    case XPathResult.UNORDERED_NODE_ITERATOR_TYPE:
    case XPathResult.ORDERED_NODE_ITERATOR_TYPE:
      retval = [];
      for (var n = null; (n = xpathResult.iterateNext());)
        retval.push(n);
      break;
    case XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE:
    case XPathResult.ORDERED_NODE_SNAPSHOT_TYPE:
      retval = [];
      for (var i = 0, l = xpathResult.snapshotLength; i < l; i++)
        retval.push(xpathResult.snapshotItem(i));
      break;
    case XPathResult.NUMBER_TYPE:
      retval = xpathResult.numberValue;
      break;
    case XPathResult.STRING_TYPE:
      retval = xpathResult.stringValue;
      break;
    case XPathResult.BOOLEAN_TYPE:
      retval = xpathResult.booleanValue;
      break;
    }
  } else {
    retval = n.selectNodes(path);
  }
  return retval;
}

function stringizeXmlNodes(nodes) {
  var retval = [];
  for (var i = 0, l = nodes.length; i < l; i++) {
    retval.push(stringizeXmlNode(nodes[i]));
  }
  return retval.join('''');
}

function stringizeXmlNode(n) {
  switch (n.nodeType) {
  case 1:
    return stringizeXmlNodes(n.childNodes);
  default:
    return n.nodeValue;
  }
}

function Drawable() {
  this.initialize.apply(this, arguments);
}

if (window.ActiveXObject) {
  function newVmlElement(name) {
    return document.createElement("v:" + name);
  }

  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    this.width = width;
    this.height = height;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newVmlElement(''shape'');
    var buf = [];
    var currentPoint = { x: 0., y: 0. };
    for (var i in pathData) {
      var datum = pathData[i];
      switch (datum[0]) {
      case ''Z'':
        buf.push(''x'');
        break;
      case ''M'':
        buf.push(''m'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case ''L'':
        buf.push(''l'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0));
        currentPoint = { x: datum[1], y: datum[2] };
        break;
      case ''C'':
        buf.push(''c'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0),
          (datum[5] * 1000).toFixed(0),
          (datum[6] * 1000).toFixed(0));
        currentPoint = { x: datum[5], y: datum[6] };
        break;
      case ''Q'':
        buf.push(''q'',
          (datum[1] * 1000).toFixed(0),
          (datum[2] * 1000).toFixed(0),
          (datum[3] * 1000).toFixed(0),
          (datum[4] * 1000).toFixed(0));
        currentPoint = { x: datum[3], y: datum[4] };
        break;
      case ''A'':
        var rx = Math.abs(datum[1]), ry = Math.abs(datum[2]),
            phi = Math.abs(datum[3]), largeArc = datum[4], sweep = datum[5],
            x  = datum[6], y = datum[7];
        var s = Math.sin(Math.PI * phi / 180),
            c = Math.cos(Math.PI * phi / 180);
        var cx = (currentPoint.x - x) / 2, cy = (currentPoint.y - y) / 2;
        var x1_ = c * cx + s * cy, y1_ = -s * cx + c * cy;
        var lambda = Math.sqrt((x1_ * x1_) / (rx * rx) + (y1_ * y1_) / (ry * ry));
        if (lambda > 1)
          rx *= lambda, ry *= lambda;
        var c_ = (largeArc == sweep ? -1: 1) * Math.sqrt((rx * rx * ry * ry - rx * rx * y1_ * y1_ - ry * ry * x1_ * x1_) / (rx * rx * y1_ * y1_ + ry * ry * x1_ * x1_));
        var cx_ = c_ * (rx * y1_) / ry,
            cy_ = -c_ * (ry * x1_) / rx;
        var ecx = c * cx_ - s * cy_ + (x + currentPoint.x) / 2,
            ecy = s * cx_ + c * cy_ + (y + currentPoint.y) / 2;
        var vx1 = (x1_ - cx_) / rx, vy1 = (y1_ - cy_) / ry;
        var vx2 = (-x1_ - cx_) / rx, vy2 = (-y1_ - cy_) / ry;
        var theta1 = (vy1 > 0 ? 1: -1) * Math.acos(vx1 / Math.sqrt(vx1 * vx1 + vy1 * vy1));
        var thetad = (vx1 * vy2 - vy1 * vx2 > 0 ? 1: -1) * Math.acos((vx1 * vx2 + vy1 * vy2) / Math.sqrt(vx1 * vx1 + vy1 * vy1) / Math.sqrt(vx2 * vx2 + vy2 * vy2));
        if (sweep && thetad > 0)
          thetad -= Math.PI * 2;
        else if (!sweep && thetad < 0)
          thetad += Math.PI * 2;
        var rsx = ecx + Math.cos(theta1) * rx,
            rsy = ecy + Math.sin(theta1) * ry;
        var rex = ecx + Math.cos(theta1 + thetad) * rx,
            rey = ecy + Math.sin(theta1 + thetad) * ry;
        if (thetad < 0) {
          var tmp;
          tmp = rsx, rsx = rex, rex = tmp;
          tmp = rsy, rsy = rey, rey = tmp;
        }
        if (phi == 0) {
          var rsxs = (rsx * 1000).toFixed(0),
              rsys = (rsy * 1000).toFixed(0);
          var rexs = (rex * 1000).toFixed(0),
              reys = (rey * 1000).toFixed(0);
          buf.push(''m'', rsxs, rsys);
          buf.push(''at'',
            ((ecx - rx) * 1000).toFixed(0),
            ((ecy - ry) * 1000).toFixed(0),
            ((ecx + rx) * 1000).toFixed(0),
            ((ecy + ry) * 1000).toFixed(0),
            rsxs, rsys, rexs, reys);
          buf.push(''m'', rexs, reys);
          if (thetad < 0) {
            buf.push(''m'', rsxs, rsys);
            buf.push(''l'', rsxs, rsys);
          }
        }
        break;
      }
    }
    path.style.display = ''block'';
    path.style.position = ''absolute'';
    path.style.left = ''0'';
    path.style.top = ''0'';
    path.style.width = this.width;
    path.style.height = this.height;
    path.coordSize = parseFloat(this.width) * 1000 + "," + parseFloat(this.height) * 1000;
    path.setAttribute(''path'', buf.join('' ''));
    this.n.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute(''strokeWeight'', value.strokeWidth);
        if (value.strokeColor) {
          path.setAttribute(''strokeColor'', value.strokeColor || ''none'');
          path.setAttribute(''stroked'', ''t'');
        } else {
          path.setAttribute(''stroked'', ''f'');
        }
        if (value.fillColor) {
          path.setAttribute(''fillColor'', value.fillColor);
          path.setAttribute(''filled'', ''t'');
        } else {
          path.setAttribute(''filled'', ''f'');
        }
      }
    };
  };
} else {
  var SVG_NAMESPACE = ''http://www.w3.org/2000/svg'';
  function newSvgElement(name) {
    return document.createElementNS(SVG_NAMESPACE, name);
  }
  Drawable.prototype.initialize = function Drawable_initialize(n, width, height) {
    this.n = n;
    var svg = newSvgElement(''svg'');
    svg.setAttribute(''style'', ''display:block;position:absolute;left:0;top:0'');
    svg.setAttribute(''version'', ''1.0'');
    svg.setAttribute(''width'', width);
    svg.setAttribute(''height'', height);
    svg.setAttribute(''viewBox'', ''0 0 '' + parseFloat(width) + '' '' + parseFloat(height));
    this.n.appendChild(svg);
    this.svg = svg;
  };

  Drawable.prototype.path = function Drawable_path(pathData) {
    var path = newSvgElement(''path'');
    var buf = [];
    for (var i in pathData) {
      buf.push.apply(buf, pathData[i]);
    }
    path.setAttribute(''d'', buf.join('' ''));
    this.svg.appendChild(path);
    return {
      n: path,
      style: function (value) {
        if (value.strokeWidth)
          path.setAttribute(''stroke-width'', value.strokeWidth);
        path.setAttribute(''stroke'', value.strokeColor || ''none'');
        path.setAttribute(''fill'', value.fillColor || ''none'');
      }
    };
  };
}

function newHandler(n, xmldoc) {
  var pathData = [];
  var drawable = null;
  var unit = ''mm'';
  var fontSize = 10;
  var classes = [];
  var objects = PRELOADED_OBJECTS;
  var currentPoint = { x: 0., y: 0. };
  var scale = 1.;
  var lineHeight = null;
  var currentMatrix = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };
  var style = {
    fillColor: null,
    strokeColor: null,
    strokeWidth: null
  };
  var dpiFix = 1.;
  function initPathData() {
    if (pathData == null) {
      var p = applyMatrix(currentMatrix, currentPoint);
      pathData = [[''M'', p.x * dpiFix, p.y * dpiFix]];
    }
  }
  function initDrawable() {
    if (drawable == null)
      drawable = new Drawable(n, ''1000'' + unit, ''1000'' + unit);
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
      var nodes = findXmlNode(xmldoc, xmldoc.documentElement, path);
      for (var i = 0; i < nodes.length; i++)
        this.$stack.push(nodes[i]);
      this.$stack.push(nodes.length);
    },
    sxn: function _stringizeXmlNodes() {
      var l = this.$stack.pop();
      var nodes = this.$stack.splice(this.$stack.length - l, l);
      this.$stack.push(stringizeXmlNodes(nodes));
    },
    lo: function _loadObject(name) {
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
      classes.push(klass);
    },
    pc: function popClass() {
      classes.pop();
    },
    sc: function setClass(klass) {
      classes = [klass];
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
      if (unit == ''px'')
        dpiFix = 96. / 90;
      else
        dpiFix = 1.;
    },
    X: function showTextBlock(width, height, text) {
      var p = applyMatrix(currentMatrix, currentPoint);
      n.insertAdjacentHTML(''beforeEnd'', [
        ''<pre><div style="position:absolute;white-space:pre;'',
        ''font-size:'', fontSize, ''px'', '';'',
        ''line-height:'', lineHeight ? (lineHeight + ''px''): ''1em'', '';'',
        ''left:'', p.x * dpiFix, unit, '';'',
        ''top:'', p.y * dpiFix, unit, '';'',
        ''width:'', width * dpiFix * scale, unit, '';'',
        ''height:'', height * dpiFix * scale, unit, ''"'',
        '' class="'', classes.join('' ''), ''"'',
        ''>'', text, ''</div></pre>''].join(''''));
    },
    x: function showText(anchor, text) {
      var p = applyMatrix(currentMatrix, currentPoint);
      var anchorClass = "t" + anchor;
      n.insertAdjacentHTML(''beforeEnd'', [
        ''<pre><div style="position:absolute;white-space:pre;'',
        ''font-size:'', fontSize, ''px'', '';'',
        ''line-height:'', lineHeight ? (lineHeight + ''px''): ''1em'', '';'',
        ''left:'', p.x * dpiFix, unit, '';'',
        ''top:'', p.y * dpiFix, unit, ''"'',
        '' class="'', classes.join('' ''),'' '', anchorClass, ''"'',
        ''>'', text, ''</div></pre>''].join(''''));
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
        pathData.push([''M'', p1.x * dpiFix, p1.y * dpiFix]);
      currentPoint = p;
    },
    l: function lineTo(x, y) {
      x *= scale;
      y *= scale;
      var p = { x: x, y: y };
      var p1 = applyMatrix(currentMatrix, p);
      initPathData();
      pathData.push([''L'', p1.x * dpiFix, p1.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''C'', p1.x * dpiFix, p1.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix,
                          p3.x * dpiFix, p3.y * dpiFix]);
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
      pathData.push([''Q'', p1.x * dpiFix, p1.y * dpiFix,
                          p2.x * dpiFix, p2.y * dpiFix]);
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
      pathData.push([''A'', r.x * dpiFix, r.y * dpiFix, phi, largeArc, sweep,
                          p1.x * dpiFix, p1.y * dpiFix]);
      currentPoint = p;
    },
    h: function closePath() {
      initPathData();
      pathData.push([''Z'']);
    },
    f: function fill() {
      if (pathData == null)
        return;
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: null,
        strokeColor: null,
        fillColor: style.fillColor
      });
      pathData = null;
    },
    s: function stroke() {
      if (pathData == null)
        return;
      initDrawable();
      drawable.path(pathData).style({
        strokeWidth: style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale,
        strokeColor: style.strokeColor,
        fillColor: null
      });
      pathData = null;
    },
    B: function strokeAndFill() {
      if (pathData == null)
        return;
      if (drawable == null)
        drawable = new Drawable(n, ''1000'' + unit, ''1000'' + unit);
      drawable.path(pathData).style({
        strokeWidth: style.strokeWidth * Math.sqrt(Math.abs(determinant(currentMatrix))) * scale,
        strokeColor: style.strokeColor,
        fillColor: style.fillColor
      });
      pathData = null;
    }
  };
}


function textValue(node) {
  if (''text'' in node)
    return node.text;
  return (function _(node) {
    switch (node.nodeType) {
    case 3:
      return node.nodeValue;
    case 1:
      var c = node.childNodes, retval = '''';
      for (var i = 0; i < c.length; i++) {
        retval += _(c[i]);
      }
      return retval;
    }
    return '''';
  })(node);
}

function populateFixtags(xmldoc) {
  for (var i = 0; i < FIXTAGS.length; i++) {
    var name = FIXTAGS[i];
    var src = xmldoc.getElementsByTagName(name);
    var tag = document.getElementById(name);
    var prefix = FIXTAG_PREFIXES[name];
    var suffix = FIXTAG_SUFFIXES[name];
    if (src.length > 0 && tag != null) {
      var text = (prefix || "") + textValue(src[0]) + (suffix || "");
      tag.appendChild(document.createTextNode(text));
    }
  }
}

function reportError(msg) {
  var page = document.getElementById(''page'');
  page.innerHTML = '''';
  throw new Error(msg);
}

function tryWith(args, f, failure) {
  var i = 0;
  function _() {
    if (i >= args.length)
      return failure.apply(null, arguments);
    f(args[i++], _);
  }
  _();
}

window.onload = function() {
  tryWith(
    [''file:///c:/sejpos/posapl/mmdata/mm60/xml/ptct.xml'', ''ptct.xml''],
    function (dataUrl, next) {
      loadXml(dataUrl, function (xmldoc) {
        var appearance = document.getElementById(''appearance'');
        try {
          var handler = newHandler(appearance, xmldoc);
          parse(
            newScanner(
              stringizeXmlNodes(
                findXmlNode(xmldoc, xmldoc.documentElement, ''b''))),
            handler,
            []);
          populateFixtags(xmldoc);
        } catch (e) {
          reportError(e.message);
        }
      }, next);
    },
    function (msg) {
      reportError("TS00003: Load failure (" + msg.replace(/[\\r\\n]/, '''')+ ")");
    }
  );
};
</script>
</head>
<body>
  <div id="page">
    <div id="appearance"></div>
    <div id="fixtags">
      <div id="FIXMSG03">発券店：</div>
      <div id="FIXTAG01"></div>
      <div id="FIXTAG02"></div>
      <div id="FIXTAG03"></div>
      <div id="FIXTAG04"></div>
      <div id="FIXTAG05"></div>
      <div id="FIXTAG06"></div>
      <div id="FIXTAG07"></div>
    </div>
  </div>
</body>
</html>',
    '',
    4
);
