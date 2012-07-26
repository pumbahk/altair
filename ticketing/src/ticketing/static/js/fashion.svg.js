/** @file svg.js { */
Fashion.Backend.SVG = (function() {
  var Fashion = this;
  var window = Fashion.window;
  var _class = Fashion._lib._class;
  var _escapeXMLSpecialChars = Fashion._lib._escapeXMLSpecialChars;
  var __assert__ = Fashion._lib.__assert__;
  var _addPoint = Fashion._lib._addPoint;
  var _subtractPoint = Fashion._lib._subtractPoint;
  var Refresher = Fashion.Backend.Refresher;
  var TransformStack = Fashion.Backend.TransformStack;

  var SVG_NAMESPACE = "http://www.w3.org/2000/svg";
  var XLINK_NAMESPACE = "http://www.w3.org/1999/xlink";

  function newElement(element_name) {
    return window.document.createElementNS(SVG_NAMESPACE, element_name);
  }

  function newTextNode(text) {
    return window.document.createTextNode(text);
  }

  function matrixString(m) {
    return "matrix(" + [m.get(0), m.get(1), m.get(2), m.get(3), m.get(4), m.get(5)].join() + ")";
  }

  function pathString(pathData) {
    return pathData.join(' ').replace(/,/g, ' ');
  }

  function buildMouseEvt(impl, domEvt) {
    var retval = new Fashion.MouseEvt();
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
      var eventDoc = domEvt.target.ownerDocument || window.document;
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

/** @file Base.js { */
var Base = _class("BaseSVG", {
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
          Fashion.DIRTY_ZINDEX,
          function () {
            this.drawable._depthManager.add(this);
          }
        ],
        [
          Fashion.DIRTY_TRANSFORM,
          function () {
            if (this.wrapper._transform)
              this._transformStack.add('last', 'wrapper', this.wrapper._transform);
            else
              this._transformStack.remove('wrapper');
            this._transformUpdated = true;
          }
        ],
        [
          Fashion.DIRTY_STYLE,
          function () {
            var elem = this._elem;
            var style = this.wrapper._style;
            if (style.fill) {
              if (style.fill instanceof Fashion.FloodFill) {
                elem.setAttribute('fill', style.fill.color.toString(true));
                elem.setAttribute('fill-opacity', style.fill.color.a / 255.0);
              } else if (style.fill instanceof Fashion.LinearGradientFill
                  || style.fill instanceof Fashion.RadialGradientFill
                  || style.fill instanceof Fashion.ImageTileFill) {
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
          Fashion.DIRTY_VISIBILITY,
          function () {
            this._elem.style.display = this.wrapper._visibility ? 'block' : 'none'
          }
        ],
        [
          Fashion.DIRTY_EVENT_HANDLERS,
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
/** @} */
/** @file Circle.js { */
var Circle = _class("CircleSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_POSITION | Fashion.DIRTY_SIZE,
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
/** @} */
/** @file Rect.js { */
var Rect = _class("RectSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.setAttribute('x', position.x + 'px');
            this._elem.setAttribute('y', position.y + 'px');
          }
        ],
        [
          Fashion.DIRTY_SIZE,
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
/** @} */
/** @file Path.js { */
var Path = _class("PathSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_SHAPE,
          function () {
            this._elem.setAttribute('d', pathString(this.wrapper._points));
          }
        ],
        [
          Fashion.DIRTY_POSITION,
          function () {
            this._transformStack.add('first', 'path-position', Fashion.Matrix.translate(this.wrapper._position));
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
/** @} */
/** @file Text.js { */
var Text = _class("TextSVG", {
  parent: Base,

  class_props: {
    _refresher: new Refresher(Base._refresher).setup({
      moreHandlers: [
        [
          Fashion.DIRTY_POSITION,
          function () {
            var position = this.wrapper._position;
            this._elem.setAttribute('x', position.x + 'px');
            this._elem.setAttribute('y', position.y + 'px');
          }
        ],
        [
          Fashion.DIRTY_SIZE,
          function () {
            var size = this.wrapper._size;
            this._elem.setAttribute('width', size.x + 'px');
            this._elem.setAttribute('height', size.y + 'px');
          }
        ],
        [
          Fashion.DIRTY_SHAPE,
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
/** @} */
/** @file DefsManager.js { */
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
        '<image xlink:href="', Fashion._lib._escapeXMLSpecialChars(obj.imageData.url), '" width="0" height="0" />',
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
          throw new Fashion.NotSupported(className + " is not supported by SVG backend");
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
/** @} */
/** @file DepthManager.js { */
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
/** @} */
/** @file Drawable.js { */
var Drawable = _class("DrawableSVG", {
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
          function() {
            this._vg.setAttribute("transform", matrixString(this.wrapper._transform));
            this._updateContentSize();
          }
        ],
        [
          Fashion.DIRTY_EVENT_HANDLERS,
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
      return Fashion.Backend.getDomOffsetPosition(this._viewport);
    },

    captureMouse: function(shape) {
      var self = this;

      if (this._capturingShape) {
        throw new Fashion.AlreadyExists("The shape is already capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.addEventListener(type, this._captureEventFunc, true);

      this._capturingShape = shape;
    },

    releaseMouse: function(shape) {
      var handler = shape.handler;

      if (this._capturingShape != shape) {
        throw new Fashion.NotFound("The shape is not capturing.");
      }

      for (var type in shape._handledEvents)
        this._viewport.offsetParent.removeEventListener(type, this._captureEventFunc, true);

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
      var viewport = window.document.createElement("div");
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
/** @} */

  return {
    Circle   : Circle,
    Rect     : Rect,
    Path     : Path,
    Text     : Text,
    Drawable : Drawable
  };
}).call(Fashion);

/*
 * vim: sts=2 sw=2 ts=2 et
 */
/** @} */
