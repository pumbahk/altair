/** @file vml.js { */
Fashion.Backend.VML = (function() {
  var Fashion = this;
  var window = Fashion.window;
  var _class = Fashion._lib._class;
  var _escapeXMLSpecialChars = Fashion._lib.escapeXMLSpecialChars;
  var __assert__ = Fashion._lib.__assert__;
  var _addPoint = Fashion._lib.addPoint;
  var _subtractPoint = Fashion._lib.subtractPoint;
  var _clipPoint = Fashion._lib.clipPoint;
  var Refresher = Fashion.Backend.Refresher;
  // checking browser.
  if (Fashion.browser.identifier !== 'ie') return null;

  var VML_PREFIX = 'v';
  var VML_NAMESPACE_URL = 'urn:schemas-microsoft-com:vml';
  var VML_BEHAVIOR_URL = '#default#VML';
  var VML_FLOAT_PRECISION = 1e4;

  function setup() {
    var namespaces = window.document.namespaces;
    if (!namespaces[VML_PREFIX])
      namespaces.add(VML_PREFIX, VML_NAMESPACE_URL);
    window.document.createStyleSheet().addRule(VML_PREFIX + '\\:*', "behavior:url(#default#VML)");
  }

  function newElement(type) {
    var elem = window.document.createElement(VML_PREFIX + ':' + type);
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

  function appendPrologue(vml, id, tagName) {
    vml.push(
        '<', VML_PREFIX, ':', tagName,
        ' unselectable="on"',
        ' __fashion__id="', id, '"');
    return vml;
  }

  function appendEpilogue(vml, tagName) {
    vml.push('</', VML_PREFIX, ':', tagName, '>');
    return vml;
  }

  function appendStyles(vml, shape) {
    var position = shape.wrapper._position;
    var size = shape.wrapper._size;
    var fillAndStroke = new VMLFillAndStroke();
    shape._buildVMLStyle(fillAndStroke);
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
    return vml;
  }

  function populateWithChildElements(elem) {
    var childNodes = elem.node.childNodes;
    for (var i = childNodes.length; --i >= 0;) {
      var node = childNodes[i];
      switch (node.tagName.toLowerCase()) {
      case 'fill':
        elem.fill = node;
        break;
      case 'stroke':
        elem.stroke = node;
        break;
      }
    }
    return elem;
  }

  function buildMouseEvt(impl, msieEvt) {
    var retval = new Fashion.MouseEvt();
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

    var doc = window.document, body = doc.body;
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

/** @file Base.js { */
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
        mouseover: false,
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
            return dirty & Fashion.DIRTY_EVENT_HANDLERS;
          }
          return dirty;
        },

        handlers: [
          [
            Fashion.DIRTY_TRANSFORM,
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
                  this._elem.node.coordOrigin = "";
                  this._elem.node.coordSize = VML_FLOAT_PRECISION + ',' + VML_FLOAT_PRECISION;
                  this._elem.skew.matrix = matrixString(transform);
                  this._elem.skew.on = true;
                }
              } else {
                if (this._elem.skew) {
                  this._elem.node.removeChild(this._elem.skew);
                  this._elem.skew = null;
                }
              }
            }
          ],
          [
            Fashion.DIRTY_STYLE,
            function () {
              var fillAndStroke = new VMLFillAndStroke();
              this._buildVMLStyle(fillAndStroke);
              fillAndStroke.assignToElement(this._elem);
            }
          ],
          [
            Fashion.DIRTY_VISIBILITY,
            function () {
              this._elem.node.style.display = this.wrapper._visibility ? 'block' : 'none';
            }
          ],
          [
            Fashion.DIRTY_EVENT_HANDLERS,
            function () {
              for (var type in this._handledEvents) {
                var beingHandled = this._handledEvents[type];
                var toHandle = this.wrapper.handler && this.wrapper.handler.handles(type);
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
          if (st.fill instanceof Fashion.FloodFill) {
            if (st.fill.color.a == 255) {
              fill.setOuterAttribute('fillColor', st.fill.color._toString(true));
            } else {
              fill.setInnerAttribute('type', "solid");
              fill.setInnerAttribute('color', st.fill.color._toString(true));
              fill.setInnerAttribute('opacity', st.fill.color.a / 255.);
            }
          } else if (st.fill instanceof Fashion.LinearGradientFill) {
            populateWithGradientAttributes(fill);
            fill.setInnerAttribute('type', "gradient");
            fill.setInnerAttribute('method', "sigma");
            fill.setInnerAttribute('angle', (st.fill.angle * 360).toFixed(0));
          } else if (st.fill instanceof Fashion.RadialGradientFill) {
            populateWithGradientAttributes(fill);
            fill.setInnerAttribute('type', "gradientRadial");
            fill.setInnerAttribute('focusPosition', st.fill.focus.x + " " + st.fill.focus.y);
          } else if (st.fill instanceof Fashion.ImageTileFill) {
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
/** @} */
/** @file Circle.js { */
var Circle = _class("CircleVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_POSITION,
          function() {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ],
        [
          Fashion.DIRTY_SIZE,
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
      var vml = appendPrologue([], this.wrapper.id, 'oval');
      appendStyles(vml, this);
      appendEpilogue(vml, 'oval');
      vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
      return populateWithChildElements({
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null
      });
    }
  }
});
/** @} */
/** @file Rect.js { */
var Rect = (function () {
  function appendPath(vml, size, corner) {
    var prec = VML_FLOAT_PRECISION,
        rx = (corner.x || 0) * prec / size.x;
        ry = (corner.y || 0) * prec / size.y;
    vml.push('at0,0,', rx * 2, ',', ry * 2, ',', rx, ',0,0,', ry);
    vml.push('l0,', prec - ry);
    vml.push('at0,', prec - ry * 2, ',', rx * 2, ',', prec, ',0,', prec - ry, ',', rx, ',', prec);
    vml.push('l', prec - rx, ',', prec);
    vml.push('at', prec - rx * 2, ',', prec - ry * 2, ',', prec, ',', prec, ',', prec - rx, ',', prec, ',', prec, ',', prec - ry);
    vml.push('l', prec, ',', ry);
    vml.push('at', prec - rx * 2, ',0,', prec, ',', ry * 2, ',', prec, ',', ry, ',', prec - rx, ',', 0);
    vml.push('x');
    return vml;
  }

  var handlers = {
    rect: {
      buildElement: function () {
        var vml = appendPrologue([], this.wrapper.id, 'rect');
        appendStyles(vml, this);
        appendEpilogue(vml, 'rect');
        return vml;
      },

      update: function () {
      }
    },

    roundrect: {
      buildElement: function () {
        var vml = appendPrologue([], this.wrapper.id, 'roundrect');
        vml.push(' arcsize="', (this.wrapper._corner.x || 0) / this.wrapper._size.x, '"');
        appendStyles(vml, this);
        appendEpilogue(vml, 'roundrect');
        return vml;
      },

      update: function () {
        this._elem.arcSize = (this.wrapper._corner.x || 0) / this.wrapper._size.x;
      }
    },

    shape: {
      buildElement: function () {
        var position = this.wrapper._position;
        var vml = appendPrologue([], this.wrapper.id, 'shape');
        vml.push(' path="');
        appendPath(vml, this.wrapper._size, this.wrapper._corner);
        vml.push('"');
        appendStyles(vml, this);
        appendEpilogue(vml, 'shape');
        return vml;
      },

      update: function () {
        this._elem.path = appendPath([], this.wrapper._size, this.wrapper._corner).join('');
      }
    }
  };

  return _class("RectVML", {
    parent: Base,

    props: {
      _handler: null
    },

    class_props: {
      _refresher: new Refresher(Base._refresher).setup({
        moreHandlers: [
          [
            Fashion.DIRTY_POSITION,
            function() {
              var position = this.wrapper._position;
              this._elem.node.style.left = position.x + 'px';
              this._elem.node.style.top = position.y + 'px';
            }
          ],
          [
            Fashion.DIRTY_SIZE | Fashion.DIRTY_SHAPE,
            function() {
              var size = this.wrapper._size;
              var handler = this.determineImpl();
              if (handler === this._handler) {
                this._elem.node.style.width = size.x + 'px';
                this._elem.node.style.height = size.y + 'px';
                handler.update.call(this);
              } else {
                var n = document.createElement('div');
                var elem = this._elem;
                n.innerHTML = handler.buildElement.call(this).join('');
                var nn = n.firstChild, parentNode = elem.node.parentNode;
                parentNode.insertBefore(nn, elem.node);
                parentNode.removeChild(elem.node);
                this._handler = handler;
                this._elem = {
                  node: nn,
                  fill: nn.firstChild,
                  stroke: nn.firstChild ? nn.firstChild.nextSibling: null,
                  skew: null
                };
              }
            }
          ]
        ]
      })
    },

    methods: {
      determineImpl: function() {
        var size = this.wrapper._size;
        var corner = this.wrapper._corner;
        if (corner.x == corner.y && size.x == size.y) {
          if (corner.x == 0)
            return handlers.rect;
          else
            return handlers.roundrect;
        } else {
          return handlers.shape;
        }
      },

      newElement: function(vg) {
        var handler = this._handler = this.determineImpl();
        var vml = handler.buildElement.call(this);
        vg.node.insertAdjacentHTML('beforeEnd', vml.join(''));
        return populateWithChildElements({
          node: vg.node.lastChild,
          fill: null,
          stroke: null,
          skew: null
        });
      }
    }
  });
})();
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file Path.js { */
var Path = _class("PathVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_SHAPE,
          function () {
            this._elem.node.setAttribute('path', pathString(this.wrapper._points));
          }
        ],
        [
          Fashion.DIRTY_POSITION,
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
        ' unselectable="on"',
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
      return populateWithChildElements({
        node: vg.node.lastChild,
        fill: null,
        stroke: null,
        skew: null
      });
    }
  }
});
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
/** @file Text.js { */
var Text = _class("TextVML", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.node.style.left = position.x + 'px';
            this._elem.node.style.top = position.y + 'px';
          }
        ],
        [
          Fashion.DIRTY_SIZE,
          function () {
            var size = this.wrapper._size;
            this._elem.node.style.width = size.x + 'px';
            this._elem.node.style.height = size.y + 'px';
          }
        ],
        [
          Fashion.DIRTY_SHAPE,
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
        ' unselectable="on"',
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
      var n = vg.node.lastChild;
      return populateWithChildElements({
        node: n,
        fill: null,
        stroke: null,
        skew: null,
        textpath: n.lastChild
      });
    }
  }
});
/** @} */
/** @file Drawable.js { */
var Drawable = _class("DrawableVML", {
  props: {
    _vg: null,
    _content: null,
    _viewport: null,
    _viewportInnerSize: { x: 0, y: 0 },
    _capturingShape: null,
    _handledEvents: {
      mousedown: [ false, 0, null ],
      mouseup: [ false, 0, null ],
      mousemove: [ false, 0, null ],
      mouseover: [ false, 0, null ],
      mouseout: [ false, 0, null ],
      scroll: [ false, 0, null ],
      visualchange: [ false, 0, null ]
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
      postHandler: function (_, originalDirty) {
        var evt = new Fashion.VisualChangeEvt();
        evt.target = this.wrapper;
        evt.dirty = originalDirty;
        if (this.wrapper.handler)
          this.wrapper.handler.dispatch(evt);
      },
      handlers: [
        [
          Fashion.DIRTY_SIZE,
          function() {
            var viewportSize = this.wrapper._viewport_size;
            this._viewport.style.width  = viewportSize.x + 'px';
            this._viewport.style.height = viewportSize.y + 'px';
            this._updateContentSize();
          }
        ],
        [
          Fashion.DIRTY_TRANSFORM,
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
          Fashion.DIRTY_EVENT_HANDLERS,
          function () {
            for (var type in this._handledEvents) {
              var beingHandled = this._handledEvents[type][0];
              var toHandle = this.wrapper.handler.handles(type);
              if (!beingHandled && toHandle) {
                if (type != 'scroll' && type.indexOf('visualchange') != 0)
                  this._handleEvent(type);
                this._handledEvents[type][0] = true;
              } else if (beingHandled && !toHandle) {
                if (type != 'scroll' && type.indexOf('visualchange') != 0)
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
        if (self._capturingShape && self._capturingShape !== self)
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
        var physicalPosition = { x: parseInt(self._viewport.scrollLeft), y: parseInt(self._viewport.scrollTop) };
        self._scrollPosition = self.wrapper._inverse_transform.apply(physicalPosition);
        if (self._handledEvents.scroll[0]) {
          var evt = new Fashion.ScrollEvt();
          evt.target = self.wrapper;
          evt.physicalPosition = physicalPosition;
          evt.logicalPosition = self._scrollPosition;
          self.wrapper.handler.dispatch(evt);
        }
      };

      this._viewport = this._buildViewportElement();
      Fashion._lib._bindEvent(this._viewport, 'scroll', this._scrollEventFunc);
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
        position = _clipPoint(
            position,
            { x: 0, y: 0 },
            _subtractPoint(
              this.wrapper._content_size,
              this.wrapper._inverse_transform.apply(
                this._viewportInnerSize)));
        this._scrollPosition = position;
        if (window.readyState == 'complete') {
          var _position = this.wrapper._transform.apply(position);
          this._viewport.scrollLeft = _position.x;
          this._viewport.scrollTop  = _position.y;
        } else {
          var self = this;
          Fashion._lib._bindEvent(window, 'load', function () {
            Fashion._lib._unbindEvent(window, 'load', arguments.callee);
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
      return Fashion.Backend.getDomOffsetPosition(this._viewport);
    },

    captureMouse: function(shape) {
      var self = this;

      if (this._capturingShape) {
        throw new Fashion.AlreadyExists("The shape is already capturing.");
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
        throw new Fashion.NotFound("The shape is not capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.detachEvent('on' + type, this._captureEventFunc);

      this._capturingShape = null;
    },

    capturingShape: function () {
      return this._capturingShape;
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
      this._viewportInnerSize = {
        x: this._viewport.clientWidth,
        y: this._viewport.clientHeight
      };
      this._scrollEventFunc();
    },

    _buildRoot: function () {
      var vg = newElement('group');
      vg.style.cssText = 'position:absolute;display:block;margin:0;padding:0;width:' + VML_FLOAT_PRECISION + 'px;height:' + VML_FLOAT_PRECISION + 'px';
      vg.coordSize = VML_FLOAT_PRECISION + ',' + VML_FLOAT_PRECISION;
      return { node: vg, skew: null };
    },

    _buildContentElement: function () {
      var content = window.document.createElement("div");
      content.style.cssText = 'position:absolute;left:0px;top:0px;display:block;margin:0;padding:0;overflow:hidden;';
      return content;
    },

    _buildViewportElement: function () {
      var viewport = window.document.createElement("div");
      viewport.style.cssText = 'position:relative;display:block;margin:0;padding:0;overflow:hidden;';
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
/** @} */

  setup();

  return {
    Circle: Circle,
    Rect: Rect,
    Path: Path,
    Text: Text,
    Drawable: Drawable
  }; 
}).call(Fashion);
/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
