/* extern */ var jQuery, I18n;
(function ($) {
  var CONF = require('CONF.js');
  var models = require('models.js');
  var util = require('util.js');
  var viewobjects = require('viewobjects.js');
  var IdentifiableSet = require('identifiableset.js').IdentifiableSet;
  if (I18n)
    I18n.translations = require('translations.js');

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


  var VenueEditor = function VenueEditor(canvas, options) {
    this.canvas = canvas;
    this.callbacks = {
      uimodeselect: null,
      message: null,
      load: null,
      loadstart: null,
      click: null,
      selectable: null,
      select: null,
      tooltip: null
    };
    if (options.callbacks) {
      for (var k in this.callbacks)
        this.callbacks[k] = options.callbacks[k] || (k == 'message' ? function(){} : null);
    }
    this.dataSource = options.dataSource;
    this.zoomRatio = options.zoomRatio || CONF.DEFAULT.ZOOM_RATIO;
    this.dragging = false;
    this.startPos = { x: 0, y: 0 };
    this.rubberBand = null;
    this.drawable = null;
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
    this.drawing = null;
    this.metadata = null;
    this.keyEvents = null;
    this.uiMode = 'select1';
    this.shapes = null;
    this.seats = null;
    this.seatAdjacencies = null;
    this.selection = new IdentifiableSet();
    this.highlighted = {};
    this._adjacencyLength = 1;
    this.addKeyEvent();
    this.rubberBand = new Fashion.Rect({
      position: {x: 0, y: 0},
      size: {x: 0, y: 0}
    });
    this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
    canvas.empty();
  };

  VenueEditor.prototype.load = function VenueEditor_load(data) {
    if (this.drawable !== null)
      this.drawable.dispose();
    this.drawing = data.drawing;
    this.metadata = data.metadata;
    if (data.metadata.seat_adjacencies)
      this.seatAdjacencies = new models.SeatAdjacencies(data.metadata.seat_adjacencies);
    this.initDrawable();
    this.initModel();
    this.initSeats();
    this.callbacks.load && this.callbacks.load(this);
  };

  VenueEditor.prototype.refresh = function VenueEditor_refresh(data) {
    for (var key in data.metadata) {
      for (var id in data.metadata[key]) {
        this.metadata[key][id] = data.metadata[key][id];
      }
    }
    this.initModel();
    this.initSeats();
    this.callbacks.load && this.callbacks.load(this);
  };

  VenueEditor.prototype.dispose = function VenueEditor_dispose() {
    this.removeKeyEvent();
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
    this.seats = null;
    this.selection = null;
    this.highlighted = null;
  };

  VenueEditor.prototype.initDrawable = function VenueEditor_initDrawable() {
    var self = this;
    var drawing = this.drawing;
    var attrs = util.allAttributes(drawing.documentElement);
    var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
    var vb = null;
    if (attrs.viewBox) {
      var comps = attrs.viewBox.split(/\s+/);
      vb = new Array(comps.length);
      for (var i = 0; i < comps.length; i++)
        vb[i] = parseFloat(comps[i]);
    }

    var size = ((vb || w || h) ? {
      x: ((vb && vb[2]) || w || h),
      y: ((vb && vb[3]) || h || w)
    } : null);

    var drawable = new Fashion.Drawable(self.canvas[0], { contentSize: {x: size.x, y: size.y}, viewportSize: { x: this.canvas.innerWidth(), y: this.canvas.innerHeight() } });
    var shapes = {};
    var styleClasses = CONF.DEFAULT.STYLES;

    (function iter(svgStyle, defs, nodeList) {
      outer:
        for (var i = 0; i < nodeList.length; i++) {
          var n = nodeList[i];
          if (n.nodeType != 1) continue;

          var shape = null;
          var attrs = util.allAttributes(n);

          var currentSvgStyle = svgStyle;
          if (attrs.style)
            currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, defs));
          if (attrs['class']) {
            var style = styleClasses[attrs['class']];
            if (style)
              currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
          }

          switch (n.nodeName) {
            case 'defs':
              parseDefs(n, defs);
              break;

            case 'g':
              arguments.callee.call(self, currentSvgStyle, defs, n.childNodes);
              continue outer;

            case 'path':
              if (!attrs.d) throw new Error("Pathdata is not provided for the path element");
              shape = new Fashion.Path({points: new Fashion.PathData(attrs.d)});
              shape.style(CONF.DEFAULT.SHAPE_STYLE);
              break;

            case 'text':
              if (n.firstChild) {
                shape = new Fashion.Text({
                  fontSize: 10,
                  text: n.firstChild.nodeValue,
                  zIndex: 99
                });
                shape.style(CONF.DEFAULT.TEXT_STYLE);
              }
              break;

            case 'rect':
              shape = new Fashion.Rect({
                //position: {
                //  x: parseFloat(attrs.x),
                //  y: parseFloat(attrs.y)
                //},
                //corner: {
                //  x: parseFloat(attrs.rx || 0),
                //  y: parseFloat(attrs.ry || 0)
                //}
                size: {
                  x: parseFloat(attrs.width),
                  y: parseFloat(attrs.height)
                },
              });
              shape.style(CONF.DEFAULT.SHAPE_STYLE);
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
          shapes[attrs.id] = shape;
        }
    }).call(self,
      { fill: false, fillOpacity: false,
        stroke: false, strokeOpacity: false },
      {},
      drawing.documentElement.childNodes);

    self.drawable = drawable;
    self.shapes = shapes;

    var cs = drawable.contentSize();
    var vs = drawable.viewportSize();
    var center = {
      x: (cs.x - vs.x) / 2,
      y: (cs.y - vs.y) / 2
    };
    self.drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
    self.changeUIMode(self.uiMode);
  };

  VenueEditor.prototype.initModel = function VenueEditor_initModel() {
    this.venue = new models.Venue(this.metadata, {
      callbacks: this.callbacks
    });
  };

  VenueEditor.prototype.initSeats = function VenueEditor_initSeats() {
    var self = this;
    var seats = {};
    for (var id in this.shapes) {
      var shape = this.shapes[id];
      var seat = this.venue.seats.get(id);
      if (!seat)
        continue;
      seats[id] = (function (id) {
        seat.on('change:selected', function () {
          var value = this.get('selected');
          if (value)
            self.selection.add(this);
          else
            self.selection.remove(this);
        });
        return new viewobjects.Seat({
          model: seat,
          shape: shape,
          events: {
            mouseover: function(evt) {
              var candidate = null;
              if (self.seatAdjacencies) {
                var candidates = self.seatAdjacencies.getCandidates(id, self.adjacencyLength());
                if (candidates.length == 0)
                  return;
                for (var i = 0; i < candidates.length; i++) {
                  candidate = candidates[i];
                  for (var j = 0; j < candidate.length; j++) {
                    if (!seats[candidate[j]].get('model').selectable()) {
                      candidate = null;
                      break;
                    }
                  }
                  if (candidate) {
                    break;
                  }
                }
              } else {
                candidate = [id];
              }
              if (!candidate)
                return;
              for (var i = 0; i < candidate.length; i++) {
                var _id = candidate[i];
                var seat = seats[_id];
                if (seat.get('model').selectable()) {
                  seat.addStyleType('highlighted');
                } else {
                  seat.addStyleType('tooltip');
                  //seats[id].get('model').set('timer', setTimeout(function() {
                  //  self.callbacks.tooltip && self.callbacks.tooltip(id);
                  //}, 3000));
                }
                self.highlighted[_id] = seat;
              }
            },
            mouseout: function(evt) {
              var highlighted = self.highlighted;
              self.highlighted = {};
              for (var i in highlighted) {
                var seat = highlighted[i];
                if (seat.get('model').selectable()) {
                  seat.removeStyleType('highlighted');
                } else {
                  seat.removeStyleType('tooltip');
                  //if (seats[id].get('model').get('timer')) {
                  //  clearTimeout(seats[id].get('model').get('timer'));
                  //}
                }
              }
            },
            mousedown: function(evt) {
              self.callbacks.click && self.callbacks.click(self, self, self.highlighted);
            }
          }
        });
      })(id);
    }
    this.seats = seats;
  };

  VenueEditor.prototype.addKeyEvent = function VenueEditor_addKeyEvent() {
    if (this.keyEvents) return;

    var self = this;

    this.keyEvents = {
      down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
      up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
    };

    $(document).bind('keydown', this.keyEvents.down);
    $(document).bind('keyup',   this.keyEvents.up);

  };

  VenueEditor.prototype.removeKeyEvent = function VenueEditor_removeKeyEvent() {
    if (!this.keyEvents) return;

    $(document).unbind('keydown', this.keyEvents.down);
    $(document).unbind('keyup',   this.keyEvents.up);
  };

  VenueEditor.prototype.changeUIMode = function VenueEditor_changeUIMode(type) {
    if (this.drawable) {
      var self = this;
      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

      switch(type) {
      case 'select1':
        break;

      case 'select':
        this.drawable.addEvent({
          mousedown: function(evt) {
            self.startPos = evt.logicalPosition;
            self.rubberBand.position({x: self.startPos.x, y: self.startPos.y});
            self.rubberBand.size({x: 0, y: 0});
            self.drawable.draw(self.rubberBand);
            self.dragging = true;
          },

          mouseup: function(evt) {
            self.dragging = false;
            var selection = []; 
            var hitTest = util.makeHitTester(self.rubberBand);
            for (var id in self.seats) {
              var seatVO = self.seats[id];
              var seat = seatVO.get('model');
              if (seat.get('selectable') && (hitTest(seatVO.get('shape') || (self.shift && seat.get('selected'))))) {
                selection.push(seat);
              }
            }
            self.drawable.erase(self.rubberBand);
            for (var i = 0; i < selection.length; i++) {
              if (selection[i].get('selected')) {
                selection[i].set('selected', false);
              } else {
                selection[i].set('selected', true);
              }
            }
            self.callbacks.select && self.callbacks.select(self, selection);
          },

          mousemove: function(evt) {
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

  VenueEditor.prototype._unselectAll = function VenueEditor__unselectAll() {
    var prevSelection = this.selection;
    this.selection = new IdentifiableSet();
    prevSelection.each(function (seat) {
      seat.set('selected', false);
    });
  };

  VenueEditor.prototype.unselectAll = function VenueEditor_unselectAll() {
    if (this.selection.length > 0) {
      this._unselectAll();
      this.callbacks.select && this.callbacks.select(this, []);
    }
  };

  VenueEditor.prototype.clearAll = function VenueEditor_clearAll() {
    this.venue.clearEdited();
    this.unselectAll();
  };

  VenueEditor.prototype.adjacencyLength = function VenueEditor_adjacencyLength(value) {
    if (value !== void(0)) {
      this._adjacencyLength = value;
    }
    return this._adjacencyLength;
  };

  $.fn.venueeditor = function (options) {
    var aux = this.data('venueeditor');

    if (!aux) { // if there are no store data. init and store the data.
      if (!options)
        throw new Error("Options must be given");
      if (typeof options == 'string' || options instanceof String)
        throw new Error("Command issued against an uninitialized element");
      if (!options.dataSource || !options.dataSource instanceof Object)
        throw new Error("Required option missing: dataSource");
      aux = {
        manager: new VenueEditor(this, options),
        dataSource: options.dataSource,
        callbacks: { message: options.callbacks && options.callbacks.message || null, loading: options.callbacks && options.callbacks.loading || null }
      };
      this.data('venueeditor', aux);
      if (options.uimode)
        aux.manager.changeUIMode(options.uimode);
    } else {
      if (typeof options == 'string' || options instanceof String) {
        switch (options) {
          case 'load':
            // Ajax Waiter
            var waiter = new util.AsyncDataWaiter({
              identifiers: ['drawing', 'metadata'],
              after: function main(data) {
                aux.loaded_at = Math.ceil((new Date).getTime() / 1000);
                aux.manager.load(data);
              }
            });
            // Load drawing
            $.ajax({
              type: 'get',
              url: aux.dataSource.drawing,
              dataType: 'xml',
              success: function(xml) { waiter.charge('drawing', xml); },
              error: function(xhr, text) { aux.callbacks.message && aux.callbacks.message("Failed to load drawing data (reason: " + text + ")"); }
            });

            // Load metadata
            $.ajax({
              url: aux.dataSource.metadata,
              dataType: 'json',
              success: function(data) { waiter.charge('metadata', data); },
              error: function(xhr, text) { aux.callbacks.message && aux.callbacks.message("Failed to load seat data (reason: " + text + ")"); }
            });
            aux.callbacks.loading && aux.callbacks.loading(aux.manager);
            break;

          case 'remove':
            aux.manager.dispose();
            this.data('venueeditor', null);
            break;

          case 'uimode':
            aux.manager.changeUIMode(arguments[1]);
            break;

          case 'selection':
            return aux.manager.selection;

          case 'clearSelection':
            aux.manager.unselectAll();
            return;

          case 'clearAll':
            aux.manager.clearAll();
            return;

          case 'refresh':
            // Load metadata
            $.ajax({
              url: aux.dataSource.metadata + '&loaded_at=' + (aux.loaded_at || ''),
              dataType: 'json',
              success: function(data) {
                aux.loaded_at = Math.ceil((new Date).getTime() / 1000);
                aux.manager.refresh({'metadata':data});
              },
              error: function(xhr, text) { aux.callbacks.message && aux.callbacks.message("Failed to load seat data (reason: " + text + ")"); }
            });
            aux.callbacks.loading && aux.callbacks.loading(aux.manager);
            aux.manager.clearAll();
            break;

          case 'adjacency':
            aux.manager.adjacencyLength(arguments[1]|0);
            break;

          case 'model':
            return aux.manager.venue;

          case 'viewportSize':
            if (aux.manager.drawable) {
              aux.manager.drawable.viewportSize(
                { x: arguments[1].width, y: arguments[1].height }
              );
            }
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
