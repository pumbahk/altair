(function ($) {
  var CONF = require('CONF.js');
  var seat = require('seat.js');
  var util = require('util.js');

  var VenueViewer = function VenueViewer(canvas, options) {
    this.canvas = canvas;
    this.callbacks = {
      uimodeselect: options.callbacks && options.callbacks.uimodeselect || null,
      message: options.callbacks && options.callbacks.message || null,
      load: options.callbacks && options.callbacks.load || null,
      click: options.callbacks && options.callbacks.click || null,
      selectable: options.callbacks && options.callbacks.selectable || null,
      click: options.callbacks && options.callbacks.click || null
    };
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
    this.zoomRatio = 1.0;
    this.uiMode = 'select1';
    this.shapes = {};
    this.seats = {};
    this.selection = {};
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

  VenueViewer.prototype.load = function VenueViewer_load(data) {
    if (this.drawable !== null)
      this.drawable.dispose();
    this.drawing = data.drawing;
    this.metadata = data.metadata; 
    this.seatAdjacencies = new seat.SeatAdjacencies(data.metadata.seat_adjacencies);
    this.initDrawable();
    this.initSeats();
    this.callbacks.load && this.callbacks.load(this);
  };

  VenueViewer.prototype.dispose = function VenueViewer_dispose() {
    this.removeKeyEvent();
    this.drawable.dispose();
    this.drawable = null;
  };

  VenueViewer.prototype.initDrawable = function VenueViewer_initDrawable() {
    var drawing = this.drawing;
    var attrs = util.allAttributes(drawing.documentElement);
    var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
    var vb = attrs.viewBox ? attrs.viewBox.split(/\s+/).map(parseFloat) : null;

    vb = [0, 0, 1000, 1000];

    var size = ((vb || w || h) ? {
      x: ((vb && vb[2]) || w || h),
      y: ((vb && vb[3]) || h || w)
    } : null);

    this.drawable = new Fashion.Drawable(this.canvas[0], { contentSize: {x: size.x, y: size.y} });

    (function iter(nodeList) {

      outer:
      for (var i = 0; i < nodeList.length; i++) {
        var n = nodeList[i];
        if (n.nodeType != 1) continue;

        var shape = null;
        var attrs = util.allAttributes(n);

        switch (n.nodeName) {
        case 'g':
          iter.call(this, n.childNodes);
          continue outer;

        case 'path':
          if (!attrs.d) throw "Pathdata is not provided for the path element";
          shape = this.drawable.draw(new Fashion.Path({points: new Fashion.PathData(attrs.d)}));
          shape.style(CONF.DEFAULT.SHAPE_STYLE);
          break;

        case 'text':
          shape = this.drawable.draw(
            new Fashion.Text({
              position: {
                x: parseFloat(attrs.x),
                y: parseFloat(attrs.y)
              },
              fontSize: parseFloat(n.style.fontSize),
              text: n.firstChild.nodeValue,
              zIndex: 99,
            }));
          shape.style(CONF.DEFAULT.TEXT_STYLE);
          break;

        case 'rect':
          shape = this.drawable.draw(
            new Fashion.Rect({
              position: {
                x: parseFloat(attrs.x),
                y: parseFloat(attrs.y)
              },
              size: {
                x: parseFloat(attrs.width),
                y: parseFloat(attrs.height)
              }
            }));
          shape.style(CONF.DEFAULT.SHAPE_STYLE);
          break;

        default:
          continue outer;

        }
        this.shapes[attrs.id] = shape;
      }

    }).call(this, drawing.documentElement.childNodes);

    var cs = this.drawable.contentSize();
    var vs = this.drawable.viewportSize();
    var center = {
      x: (cs.x - vs.x) / 2,
      y: (cs.y - vs.y) / 2
    };

    this.drawable.transform(Fashion.Util.Matrix.scale(this.zoomRatio));
  };

  VenueViewer.prototype.initSeats = function VenueViewer_initSeats() {
    var self = this;
    for (var id in this.shapes) {
      var shape = this.shapes[id];
      var meta  = this.metadata.seats[id];
      if (!meta) continue;
      this.seats[id] = new seat.Seat(id, shape, meta, this, {
        mouseover: function(evt) {
          if (self.uiMode == 'select')
            return;
          var candidates = self.seatAdjacencies.getCandidates(this.id, self.adjacencyLength());
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
            seat.addStyleType('highlighted');
            self.highlighted[seat.id] = seat;
          }
        },
        mouseout: function(evt) {
          if (self.uiMode == 'select')
            return;
          var highlighted = self.highlighted;
          self.highlighted = {};
          for (var i in highlighted)
            highlighted[i].removeStyleType('highlighted');
        },
        mousedown: function(evt) {
          self.callbacks.click && self.callbacks.click(self, this);
        }
      });
    }
  };

  VenueViewer.prototype.addKeyEvent = function VenueViewer_addKeyEvent() {
    if (this.keyEvents) return;

    var self = this;

    this.keyEvents = {
      down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
      up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
    };

    document.addEventListener('keydown', this.keyEvents.down, false);
    document.addEventListener('keyup',   this.keyEvents.up,   false);

  };

  VenueViewer.prototype.removeKeyEvent = function VenueViewer_removeKeyEvent() {
    if (!this.keyEvents) return;

    document.removeEventListener('keydown', this.keyEvents.down, false);
    document.removeEventListener('keyup',   this.keyEvents.up,   false);
  };

  VenueViewer.prototype.changeUIMode = function VenueViewer_changeUIMode(type) {
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
          this.transform(Fashion.Util.Matrix.scale(self.zoomRatio));
        }
      });
      break;

    case 'zoomout':
      this.drawable.addEvent({
        mouseup: function(evt) {
          self.zoomRatio/=1.2;
          this.transform(Fashion.Util.Matrix.scale(self.zoomRatio));
        }
      });
      break;

    default:
      throw new Error("Invalid ui mode: " + type);
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

  $.fn.venueviewer = function (options) {
    var aux = this.data('venueviewer');

    if (!aux) { // if there are no store data. init and store the data.
      if (!options)
        throw new Error("Options must be given");
      if (typeof options == 'string' || options instanceof String)
        throw new Error("Command issued against an uninitialized element");
      if (!options.dataSource || !options.dataSource instanceof Object)
        throw new Error("Required option missing: dataSource");
      aux = {
        manager: new VenueViewer(this, options),
        dataSource: options.dataSource,
        callbacks: { message: options.callbacks && options.callbacks.message || null }
      };
      this.data('venueviewer', aux);
    } else {
      if (typeof options == 'string' || options instanceof String) {
        switch (options) {
        case 'load':
          // Ajax Waiter
          var waiter = new util.AsyncDataWaiter({
            identifiers: ['drawing', 'metadata'],
            after: function main(data) {
              aux.manager.load(data);
            }
          });

          // Load drawing
          $.ajax({
            type: 'get',
            url: aux.dataSource.drawing,
            dataType: 'xml',
            success: function(xml) { waiter.charge('drawing', xml); },
            error: function(xhr, text) { aux.callbacks.message("Failed to load drawing data (reason: " + text + ")"); }
          });

          // Load metadata
          $.ajax({
            url: aux.dataSource.metadata,
            dataType: 'json',
            success: function(data) { waiter.charge('metadata', data); },
            error: function(xhr, text) { aux.callbacks.message("Failed to load seat data (reason: " + text + ")"); }
          });

          break;

        case 'remove':
          aux.manager.dispose();
          this.data('venueviewer', null);
          break;

        case 'uimode':
          aux.manager.changeUIMode(arguments[1]);
          break;

        case 'adjacency':
          aux.manager.adjacencyLength(arguments[1]|0);
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
