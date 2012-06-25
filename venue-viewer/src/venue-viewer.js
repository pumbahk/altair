(function ($) {
  var CONF = require('CONF.js');
  var seat = require('seat.js');
  var util = require('util.js');

  var parseCSSStyleText = (function () {
    var regexp_for_styles = /\s*(-?(?:[_a-z\u00a0-\u10ffff]|\\[^\n\r\f#])(?:[\-_A-Za-z\u00a0-\u10ffff]|\\[^\n\r\f])*)\s*:\s*((?:(?:(?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+|"(?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*"|'(?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*')(?:\s+|(?=;|$)))+)(?:;|$)/g;

    var regexp_for_values = /(?:((?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+)|"((?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)"|'((?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)')(?:\s+|$)/g;

    function unescape(escaped) {
      return escaped.replace(/(?:\\(0{0,2}d[89ab][0-9A-Fa-f]{2})(?:\r\n|[ \n\r\t\f])?)?\\([0-9A-Fa-f]{1,6})(?:\r\n|[ \n\r\t\f])?|\\([^\n\r\f0-9A-Fa-f])/g, function(_, a, b, c) {
        if (a !== void(0)) {
          var c2 = parseInt(b, 16) ;
          if (c2 < 0xdc00 || c2 > 0xdfff)
            throw new ValueError("Invalid surrogate pair");
          return String.fromCharCode((((parseInt(a, 16) & 0x3ff) << 10) | (c2 & 0x3ff)) + 0x10000);
        } else if (b !== void(0)) {
          return String.fromCharCode(parseInt(b, 16));
        } else if (c !== void(0)) {
          return c;
        }
      });
    }

    return function parseCSSStyleText(str) {
      var retval = {};
      var r = str.replace(regexp_for_styles, function (_, k, v) {
        var values = [];
        var r = v.replace(regexp_for_values, function (_, a, b, c) {
          if (a !== void(0)) {
            values.push(unescape(a));
          } else if (b !== void(0)) {
            values.push(unescape(b));
          } else if (c !== void(0)) {
            values.push(unescape(c));
          }
          return '';
        });
        if (r != '')
          throw new ValueError("Invalid CSS rule string: " + str);
        retval[k] = values;
        return '';
      });
      if (r != '')
        throw new ValueError("Invalid CSS rule string: " + str);
      return retval;
    };
  })();

  function parseDefs(node, defset) {
    function parseStops(def) {
      var ref = typeof def.getAttributeNS == 'function' ?
        def.getAttributeNS('http://www.w3.org/1999/xlink', 'href'):
        def.getAttribute("xlink:href");
      if (ref) {
        if (typeof def.ownerDocument.getElementById == 'function')
          def = def.ownerDocument.getElementById(ref.substring(1));
        else
          def = def.ownerDocument.selectSingleNode("*//*[@id='" + ref.substring(1) + "']");
      }
      var stops = def.childNodes;
      var colors = [];
      for (var i = 0; i < stops.length; i++) {
        var node = stops[i];
        if (node.nodeType != 1)
          continue;
        if (node.nodeName == 'stop') {
          var styles = parseCSSStyleText(node.getAttribute('style'));
          colors.push([
            parseFloat(node.getAttribute('offset')),
            new Fashion.Color(styles['stop-color'][0])]);
        }
      }
      return colors;
    }

    var defs = node.childNodes;
    for (var i = 0; i < defs.length; i++) {
      var def = defs[i];
      if (def.nodeType != 1)
        continue;
      var id = def.getAttribute('id');
      switch (def.nodeName) {
      case 'linearGradient':
        var x1 = parseFloat(def.getAttribute("x1")), y1 = parseFloat(def.getAttribute("y1")),
            x2 = parseFloat(def.getAttribute("x2")), y2 = parseFloat(def.getAttribute("y2"));
        var r = Math.acos((x2 - x1) / Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))) + (y2 - y1 < 0 ? Math.PI: 0);
        defset[id] = new Fashion.LinearGradientFill(parseStops(def), r / (Math.PI * 2));
        break;
      case 'radialGradient':
        defset[id] = new Fashion.RadialGradientFill(parseStops(def),
          { x: def.getAttribute('fx') || '50%', y: def.getAttribute('fy') || '50%' });
        break;
      }
    }
  }

  function parseCSSAsSvgStyle(str, defs) {
    var styles = parseCSSStyleText(str);
    var fill = null;
    var fillString = styles['fill'];
    var fillOpacity = null;
    var fillOpacityString = styles['fill-opacity'];
    var stroke = null;
    var strokeString = styles['stroke'];
    var strokeWidth = null;
    var strokeWidthString = styles['stroke-width'];
    var strokeOpacity = null;
    var strokeOpacityString = styles['stroke-opacity'];
    if (fillString) {
      if (fillString[0] == 'none') {
        fill = false;
      } else {
        var g = /url\(#([^)]*)\)/.exec(fillString[0]);
        if (g) {
          fill = defs[g[1]];
          if (!fill)
            throw new Error();
        } else {
          fill = new Fashion.Color(fillString[0]);
        }
      }
    }
    if (fillOpacityString) {
      fillOpacity = parseFloat(fillOpacityString[0]);
    }
    if (strokeString) {
      if (strokeString[0] == 'none')
        stroke = false;
      else
        stroke = new Fashion.Color(strokeString[0]);
    }
    if (strokeWidthString) {
      strokeWidth = parseFloat(strokeWidthString[0]);
    }
    if (strokeOpacityString) {
      strokeOpacity = parseFloat(strokeOpacityString[0]);
    }
    return {
      fill: fill,
      fillOpacity: fillOpacity,
      stroke: stroke,
      strokeWidth: strokeWidth,
      strokeOpacity: strokeOpacity
    };
  }

  function mergeSvgStyle(origStyle, newStyle) {
    return {
      fill: newStyle.fill !== null ? newStyle.fill: origStyle.fill,
      fillOpacity: newStyle.fillOpacity !== null ? newStyle.fillOpacity: origStyle.fillOpacity,
      stroke: newStyle.stroke !== null ? newStyle.stroke: origStyle.stroke,
      strokeWidth: newStyle.strokeWidth !== null ? newStyle.strokeWidth: origStyle.strokeWidth,
      strokeOpacity: newStyle.strokeOpacity !== null ? newStyle.strokeOpacity: origStyle.strokeOpacity
    };
  }

  function buildStyleFromSvgStyle(svgStyle) {
    return {
      fill:
        svgStyle.fill ? 
          (svgStyle.fill instanceof Fashion.Color ?
            new Fashion.FloodFill(
              svgStyle.fill.replace(
                null, null, null,
                svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255)):
            svgStyle.fill):
          null,
      stroke: 
        svgStyle.stroke ? new Fashion.Stroke(
          svgStyle.stroke.replace(
            null, null, null,
            svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255),
          svgStyle.strokeWidth ? svgStyle.strokeWidth: 1,
          svgStyle.strokePattern ? svgStyle.strokePattern: null):
          null,
      visibility: true
    };
  }

  var VenueViewer = function VenueViewer(canvas, options) {
    this.canvas = canvas;
    this.callbacks = {
      uimodeselect: null,
      load: null,
      loadstart: null,
      click: null,
      selectable: null,
      select: null
    };
    this.stockTypes = null;
    if (options.callbacks) {
      for (var k in this.callbacks)
        this.callbacks[k] = options.callbacks[k] || null;
    }
    this.callbacks.message = options.callbacks && options.callbacks.message || function () {};
    this.dataSource = options.dataSource;
    this.zoomRatio = options.zoomRatio || CONF.DEFAULT.ZOOM_RATIO;
    this.dragging = false;
    this.startPos = { x: 0, y: 0 };
    this.rubberBand = null;
    this.drawable = null;
    this.availableAdjacencies = [ 1 ];
    this.originalStyles = (function() {
      var store = {};
      return {
        save: function(id, data) {
          if (!store[id]) store[id] = data;
        },
        restore: function(id) {
          var rt = store[id];
          delete store[id];
          return rt;
        }
      };
    })();
    this.shift = false;
    this.keyEvents = null;
    this.zoomRatio = 1.0;
    this.uiMode = 'select1';
    this.shapes = {};
    this.seats = {};
    this.selection = {};
    this.highlighted = {};
    this._adjacencyLength = 1;
    this.animating = false;
    this.addKeyEvent();
    this.rubberBand = new Fashion.Rect({
      position: {x: 0, y: 0},
      size: {x: 0, y: 0}
    });
    this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
    canvas.empty();
  };

  VenueViewer.prototype.load = function VenueViewer_load() {
    if (this.drawable !== null)
      this.drawable.dispose();
    this.seatAdjacencies = null;
    var self = this;
    this.callbacks.loadstart && this.callbacks.loadstart('stockTypes');
    this.dataSource.stockTypes(function (data) {
      self.stockTypes = data;
      self.callbacks.loadstart && self.callbacks.loadstart('info');
      self.dataSource.info(function (data) {
        if (!'available_adjacencies' in data) {
          self.callbacks.message("Invalid data");
          return;
        }
        self.availableAdjacencies = data.available_adjacencies;
        self.seatAdjacencies = new seat.SeatAdjacencies(self);
        self.callbacks.loadstart && self.callbacks.loadstart('drawing');
        self.initDrawable(self.dataSource.drawing, function () {
          self.callbacks.loadstart && self.callbacks.loadstart('seats');
          self.initSeats(self.dataSource.seats, function () {
            self.callbacks.load && self.callbacks.load(self);
          });
        });
      }, self.callbacks.message);
    }, self.callbacks.message);
  };

  VenueViewer.prototype.dispose = function VenueViewer_dispose() {
    this.removeKeyEvent();
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
    this.seats = null;
    this.selection = null;
    this.highlighted = null;
  };

  VenueViewer.prototype.initDrawable = function VenueViewer_initDrawable(dataSource, next) {
    var self = this;
    dataSource(function (drawing) {
      var attrs = util.allAttributes(drawing.documentElement);
      var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
      var vb = attrs.viewBox ? attrs.viewBox.split(/\s+/).map(parseFloat) : null;

      vb = [0, 0, 1000, 1000];

      var size = ((vb || w || h) ? {
        x: ((vb && vb[2]) || w || h),
        y: ((vb && vb[3]) || h || w)
      } : null);

      var drawable = new Fashion.Drawable(self.canvas[0], { contentSize: {x: size.x, y: size.y} });

      (function iter(svgStyle, defs, nodeList) {
        outer:
        for (var i = 0; i < nodeList.length; i++) {
          var n = nodeList[i];
          if (n.nodeType != 1) continue;
          var attrs = util.allAttributes(n);

          var shape = null;
          var currentSvgStyle = attrs.style ?
            mergeSvgStyle(svgStyle, parseCSSAsSvgStyle(attrs.style, defs)):
            svgStyle;

          switch (n.nodeName) {
          case 'defs':
            parseDefs(n, defs);
            break;

          case 'g':
            arguments.callee.call(self, currentSvgStyle, defs, n.childNodes);
            continue outer;

          case 'path':
            if (!attrs.d) throw new Error("Pathdata is not provided for the path element");
            shape = new Fashion.Path({
              points: new Fashion.PathData(attrs.d)
            });
            break;

          case 'text':
            shape = new Fashion.Text({
              fontSize: 10,
              text: n.firstChild.nodeValue,
              zIndex: 99
            });
            break;

          case 'rect':
            shape = new Fashion.Rect({
              size: {
                x: parseFloat(attrs.width),
                y: parseFloat(attrs.height)
              },
              corner: {
                x: parseFloat(attrs.rx || 0),
                y: parseFloat(attrs.ry || 0)
              }
            });
            break;

          default:
            continue outer;
          }

          if (shape !== null) {
            var x = parseFloat(attrs.x),
                y = parseFloat(attrs.y);
            if (!isNaN(x) && !isNaN(y))
              shape.position({ x: x, y: y });
            shape.style(buildStyleFromSvgStyle(currentSvgStyle));
            drawable.draw(shape);
          }
          self.shapes[attrs.id] = shape;
        }
      }).call(self,
        { fill: false, fillOpacity: false,
          stroke: false, strokeOpacity: false },
        {},
        drawing.documentElement.childNodes);

      self.drawable = drawable;

      var cs = drawable.contentSize();
      var vs = drawable.viewportSize();
      var center = {
        x: (cs.x - vs.x) / 2,
        y: (cs.y - vs.y) / 2
      };

      self.drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
      self.changeUIMode(self.uiMode);
      next.call(this);
    }, self.callbacks.message);
  };

  VenueViewer.prototype.initSeats = function VenueViewer_initSeats(dataSource, next) {
    var self = this;
    dataSource(function (seats) {
      for (var id in self.shapes) {
        var shape = self.shapes[id];
        var meta  = seats[id];
        if (!meta) continue;
        self.seats[id] = new seat.Seat(id, shape, meta, self, {
          mouseover: function(evt) {
            if (self.uiMode == 'select')
              return;
            self.seatAdjacencies.getCandidates(this.id, self.adjacencyLength(), function (candidates) {
              if (candidates.length == 0)
                return;
              var candidate = null;
              for (var i = 0; i < candidates.length; i++) {
                candidate = candidates[i];
                for (var j = 0; j < candidate.length; j++) {
                  if (!self.seats[candidate[j]].selectable()) {
                    candidate = null;
                    break;
                  }
                }
                if (candidate) {
                  break;
                }
              }
              if (!candidate)
                return;
              for (var i = 0; i < candidate.length; i++) {
                var seat = self.seats[candidate[i]];
                seat.addOverlay('highlighted');
                self.highlighted[seat.id] = seat;
              }
            }, self.callbacks.message);
          },
          mouseout: function(evt) {
            if (self.uiMode == 'select')
              return;
            var highlighted = self.highlighted;
            self.highlighted = {};
            for (var i in highlighted)
              highlighted[i].removeOverlay('highlighted');
          },
          mousedown: function(evt) {
            self.callbacks.click && self.callbacks.click(self, self, self.highlighted);
          }
        });
      }
      next.call(self);
    }, self.callbacks.message);
  };

  VenueViewer.prototype.refresh = function VenueViewer_refresh() {
    for (var id in this.seats)
      this.seats[id].refresh();
  };

  VenueViewer.prototype.addKeyEvent = function VenueViewer_addKeyEvent() {
    if (this.keyEvents) return;

    var self = this;

    this.keyEvents = {
      down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
      up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
    };

    $(document).bind('keydown', this.keyEvents.down);
    $(document).bind('keyup',   this.keyEvents.up);

  };

  VenueViewer.prototype.removeKeyEvent = function VenueViewer_removeKeyEvent() {
    if (!this.keyEvents) return;

    $(document).unbind('keydown', this.keyEvents.down);
    $(document).unbind('keyup',   this.keyEvents.up);
  };

  VenueViewer.prototype.changeUIMode = function VenueViewer_changeUIMode(type) {
    if (this.drawable) {
      var self = this;
      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

      switch(type) {
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

      case 'select1':
        break;

      case 'select':
        this.drawable.addEvent({
          mousedown: function(evt) {
            if (self.animating)
              return;
            self.startPos = evt.logicalPosition;
            self.rubberBand.position({x: self.startPos.x, y: self.startPos.y});
            self.rubberBand.size({x: 0, y: 0});
            self.drawable.draw(self.rubberBand);
            self.dragging = true;
            self.drawable.captureMouse();
          },

          mouseup: function(evt) {
            if (self.animating)
              return;
            self.drawable.releaseMouse();
            self.dragging = false;
            var selection = []; 
            var hitTest = util.makeHitTester(self.rubberBand);
            for (var id in self.seats) {
              var seat = self.seats[id];
              if ((hitTest(seat.shape) || (self.shift && seat.selected())) &&
                  (!self.callbacks.selectable
                      || self.callbacks.selectable(this, seat))) {
                selection.push(seat);
              }
            }
            self.unselectAll();
            self.drawable.erase(self.rubberBand);
            for (var i = 0; i < selection.length; i++)
              selection[i].selected(true);
            self.callbacks.select && self.callbacks.select(self, selection);
          },

          mousemove: function(evt) {
            if (self.animating)
              return;
            if (self.dragging) {
              var pos = evt.logicalPosition;
              var w = Math.abs(pos.x - self.startPos.x);
              var h = Math.abs(pos.y - self.startPos.y);

              var origin = {
                x: (pos.x < self.startPos.x) ? pos.x : self.startPos.x,
                y: (pos.y < self.startPos.y) ? pos.y : self.startPos.y
              };

              if (origin.x !== self.startPos.x || origin.y !== self.startPos.y)
                self.rubberBand.position(origin);

              self.rubberBand.size({x: w, y: h});
            }
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
        throw new Error("Invalid ui mode: " + type);
      }
    }
    this.uiMode = type;
    this.callbacks.uimodeselect && this.callbacks.uimodeselect(this, type);
  };

  VenueViewer.prototype.unselectAll = function VenueViewer_unselectAll() {
    var prevSelection = this.selection;
    this.selection = {};
    for (var id in prevSelection) {
      this.seats[id].__unselected();
    }
  };

  VenueViewer.prototype._select = function VenueViewer__select(seat, value) {
    if (value) {
      if (!(seat.id in this.selection)) {
        this.selection[seat.id] = seat;
        seat.__selected();
      }
    } else {
      if (seat.id in this.selection) {
        delete this.selection[seat.id];
        seat.__unselected();
      }
    }
  };

  VenueViewer.prototype.adjacencyLength = function VenueViewer_adjacencyLength(value) {
    if (value !== void(0)) {
      this._adjacencyLength = value;
    }
    return this._adjacencyLength;
  };

  VenueViewer.prototype.scrollTo = function VenueViewer_scrollTo(leftTopCorner) {
    if (this.animating)
      return;
    var scrollPos = this.drawable.scrollPosition();
    leftTopCorner = { x: leftTopCorner.x, y: leftTopCorner.y };
    var contentSize = this.drawable.contentSize();
    var rightBottomCorner = Fashion._lib.addPoint(
      leftTopCorner,
      this.drawable._inverse_transform.apply(
        this.drawable.viewportInnerSize()));
    if (rightBottomCorner.x > contentSize.x)
      leftTopCorner.x += contentSize.x - rightBottomCorner.x;
    if (rightBottomCorner.y > contentSize.y)
      leftTopCorner.y += contentSize.y - rightBottomCorner.y;
    leftTopCorner.x = Math.max(leftTopCorner.x, 0);
    leftTopCorner.y = Math.max(leftTopCorner.y, 0);

    this.animating = true;
    var self = this;
    var t = setInterval(function () {
      var delta = Fashion._lib.subtractPoint(
        leftTopCorner,
        scrollPos);
      if (Math.sqrt(delta.x * delta.x + delta.y * delta.y) < 1) {
        clearInterval(t);
        self.animating = false;
        return;
      }
      delta = { x: delta.x / 2, y: delta.y / 2 };
      scrollPos = Fashion._lib.addPoint(scrollPos, delta);
      self.drawable.scrollPosition(scrollPos);
    }, 50);
  };

  $.fn.venueviewer = function (options) {
    var aux = this.data('venueviewer');

    if (!aux) { // if there are no store data. init and store the data.
      if (!options)
        throw new Error("Options must be given");
      if (typeof options == 'string' || options instanceof String)
        throw new Error("Command issued against an uninitialized element");
      if (!options.dataSource || !options.dataSource instanceof Object)
        throw new Error("Required option missing: dataSource");

      var _options = $.extend({}, options);
     
      var createMetadataLoader = (function () {
        var conts = {}, allData = null, first = true;
        return function createMetadataLoader(key) {
          return function metadataLoader(next, error) {
            conts[key] = { next: next, error: error };
            if (first) {
              $.ajax({
                url: options.dataSource.metadata,
                dataType: 'json',
                success: function(data) {
                  allData = data;
                  var _conts = conts;
                  conts = {};
                  for (var k in _conts)
                    _conts[k].next(data[key]);
                },
                error: function(xhr, text) {
                  var message = "Failed to load " + key + " (reason: " + text + ")";
                  var _conts = conts;
                  conts = {};
                  for (var k in _conts)
                    _conts[k].error(message);
                }
              });
              first = false;
              return;
            } else {
              if (allData) {
                conts[key].next(allData[key]);
                delete conts[key];
              }
            }
          };
        };
      })();

      _options.dataSource = {
        drawing:
          typeof options.dataSource.drawing == 'function' ?
            options.dataSource.drawing:
            function (next, error) {
              $.ajax({
                type: 'get',
                url: options.dataSource.drawing,
                dataType: 'xml',
                success: function(xml) { next(xml); },
                error: function(xhr, text) { error("Failed to load drawing data (reason: " + text + ")"); }
              });
            }
      };
      $.each(
        [
          [ 'stockTypes', 'stock_types' ],
          [ 'seats', 'seats' ],
          [ 'areas', 'areas' ],
          [ 'info', 'info' ],
          [ 'seatAdjacencies', 'seat_adjacencies' ]
        ],
        function(n, k) {
          _options.dataSource[k[0]] =
            typeof options.dataSource[k[0]] == 'function' ?
              options.dataSource[k[0]]:
              createMetadataLoader(k[1]);
        }
      );
      aux = new VenueViewer(this, _options),
      this.data('venueviewer', aux);
      if (options.uimode)
        aux.changeUIMode(options.uimode);
    } else {
      if (typeof options == 'string' || options instanceof String) {
        switch (options) {
        case 'load':
          aux.load();
          break;

        case 'remove':
          aux.dispose();
          this.data('venueviewer', null);
          break;

        case 'uimode':
          aux.changeUIMode(arguments[1]);
          break;

        case 'selection':
          return aux.selection;

        case 'refresh':
          return aux.refresh();

        case 'adjacency':
          aux.adjacencyLength(arguments[1]|0);
          break;
        }
      }
    }

    return this;
  };

})(jQuery);
/*
 * vim: sts=2 sw=2 ts=2 et
 */
