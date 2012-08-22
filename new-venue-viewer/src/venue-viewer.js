(function ($) {

  include("classify.js");
  include("helpers.js");

  var CONF = require('CONF.js');
  var seat = require('seat.js');
  var util = require('util.js');

  var createDrawingLoader = function(url) {
    return function (next, error) {
      $.ajax({
        type: 'get',
        url: url,
        dataType: 'xml',
        success: function(xml) {
          next(xml);
        },
        error: function(xhr, text) { throw new Error("Failed to load drawing data (reason: " + text + ")"); }
      });
    }
  }

  var StoreObject = _class("StoreObject", {
    props: {
      store: {}
    },
    methods: {
      save: function(id, data) {
        if (!this.store[id]) this.store[id] = data;
      },
      restore: function(id) {
        var rt = this.store[id];
        delete this.store[id];
        return rt;
      },
      clear: function() {
        for (var id in this.store) {
          delete this.store[id];
        }
      }
    }
  });

  var VenueViewer = _class("VenueViewer", {

    props: {
      canvas: null,
      callbacks: {
        uimodeselect: null,
        load: null,
        loadstart: null,
        click: null,
        selectable: null,
        select: null,
        changeCurrentClassName: null,
        messageBoard: null,
        slider: null
      },
      dataSource: null,
      zoomRatio: CONF.DEFAULT.ZOOM_RATIO,
      contentOriginPosition: {x: 0, y: 0},
      dragging: false,
      startPos: { x: 0, y: 0 },
      rubberBand: new Fashion.Rect({
        position: {x: 0, y: 0},
        size: {x: 0, y: 0}
      }),
      drawable: null,
      availableAdjacencies: [ 1 ],
      originalStyles: new StoreObject(),
      overlayShapes: new StoreObject(),
      shift: false,
      keyEvents: null,
      uiMode: 'select1',
      shapes: null,
      seats: {},
      selection: {},
      selectionCount: 0,
      highlighted: {},
      animating: false,
      blocks: null,
      _adjacencyLength: 1,
      currentClass: 'root',
      currentFocusedIds: null,
      parentLinks: [],
      seatTitles: {},
      optionalViewportSize: null
    },

    methods: {
      init: function VenueViewer_init(canvas, options) {
        this.canvas = canvas;
        this.stockTypes = null;
        if (options.callbacks) {
          for (var k in this.callbacks)
            this.callbacks[k] = options.callbacks[k] || function () {};
        }
        this.dataSource = options.dataSource;
        if (options.zoomRatio) this.zoomRatio = options.zoomRatio;
        this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
        canvas.empty();
        this.optionalViewportSize = options.viewportSize;
      },

      load: function VenueViewer_load() {
        if (this.drawable !== null)
          this.drawable.dispose();

        if (this.blocks !== null) {
          for (id in this.blocks) {
            this.blocks[id].removeEvent();
          }
        }

        this.originalStyles.clear();
        this.overlayShapes.clear();

        this.seatAdjacencies = null;
        var self = this;
        self.callbacks.loadstart('drawing');
        self.initDrawable(self.dataSource.drawing, function () {
          self.callbacks.loadstart('drawingClasses');
          self.initBlocks(self.dataSource.drawingClasses, function() {
            self.callbacks.loadstart('stockTypes');
            self.dataSource.stockTypes(function (data) {
              self.stockTypes = data;
              self.callbacks.loadstart('info');
              self.dataSource.info(function (data) {
                if (!'available_adjacencies' in data) {
                  self.callbacks.message("Invalid data"); return;
                }
                self.availableAdjacencies = data.available_adjacencies;
                self.seatAdjacencies = new seat.SeatAdjacencies(self);
                self.callbacks.loadstart('seats');
                self.initSeats(self.dataSource.seats, function () {
                  self.callbacks.load(self);
                });
              }, self.callbacks.message);
            }, self.callbacks.message);
          });
        });
      },

      dispose: function VenueViewer_dispose() {
        this.removeKeyEvent();
        if (this.drawable) {
          this.drawable.dispose();
          this.drawable = null;
        }
        this.seats = null;
        this.selection = null;
        this.highlighted = null;
      },

      initDrawable: function VenueViewer_initDrawable(dataSource, next) {
        var self = this;
        var isFocused = function isFocused(id){
          return self.currentFocusedIds == null || self.currentFocusedIds.indexOf(id) > -1;
        };
        dataSource(function (drawing) {
          var attrs = util.allAttributes(drawing.documentElement);
          var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
          var focused = isFocused(attrs.id);
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

          var drawable = new Fashion.Drawable( self.canvas[0], {
            contentSize: {x: size.x, y: size.y},
            viewportSize: self.optionalViewportSize
          });

          var shapes = {};
          var styleClasses = CONF.DEFAULT.STYLES;

          var xmax = -Infinity, ymax = -Infinity,
              xmin = Infinity,  ymin = Infinity;

          (function iter(svgStyle, defs, nodeList, focused) {
            outer:
            for (var i = 0; i < nodeList.length; i++) {
              var n = nodeList[i];
              if (n.nodeType != 1) continue;
              var attrs = util.allAttributes(n);
              var shape = null;

              { // stylize
                var currentSvgStyle = svgStyle;
                if (attrs.style)
                  currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, defs));
                if (attrs['class']) {
                  var style = styleClasses[attrs['class']];
                  if (style) currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
                }
              }

              switch (n.nodeName) {
              case 'defs':
                parseDefs(n, defs);
                break;

              case 'g': {
                arguments.callee.call(self, currentSvgStyle, defs, n.childNodes,
                                      (focused || isFocused(attrs.id)));
                continue outer;
              }

              case 'path':
                if (!attrs.d) throw new Error("Pathdata is not provided for the path element");
                shape = new Fashion.Path({
                  points: new Fashion.PathData(attrs.d)
                });
                break;

              case 'text':
                if (n.firstChild) {
                  shape = new Fashion.Text({
                    text: collectText(n),
                    zIndex: 99
                  });
                }
                break;

              case 'symbol':
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
                for (var j=0,ll=n.childNodes.length; j<ll; j++) {
                  if (n.childNodes[j].nodeName == "title") {
                    self.seatTitles[attrs.id] = n.childNodes[j].childNodes[0].nodeValue;
                    break;
                  }
                }
                break;

              default:
                continue outer;
              }

              if (shape !== null) {
                var x = parseFloat(attrs.x),
                    y = parseFloat(attrs.y);

                if (!isNaN(x) && !isNaN(y)) {

                  if (focused) {
                    if (xmax < x) xmax = x;
                    else if (x < xmin) xmin = x;
                    if (ymax < y) ymax = y;
                    else if (y < ymin) ymin = y;
                  }

                  shape.position({ x: x, y: y });
                }
                //if (focused) {
                shape.style(buildStyleFromSvgStyle(currentSvgStyle));
                if (shape instanceof Fashion.Text) {
                  shape.fontSize(currentSvgStyle.fontSize);
                }
                // } else {
                // shape.style(styleClasses['glayout']);
                //}
                drawable.draw(shape);
              }
              shapes[attrs.id] = shape;
            }
          }).call(
            self,
            {
              fill: false, fillOpacity: false,
              stroke: false, strokeOpacity: false,
              fontSize: 10
            },
            {},
            drawing.documentElement.childNodes,
            focused);

          self.drawable = drawable;
          self.shapes = shapes;

          var center = {
            x: (xmax + xmin) / 2,
            y: (ymax + ymin) / 2
          };

          var width  = (xmax - xmin) / 0.8;
          var height = (ymax - ymin) / 0.8;

          var origin_of_shapes = {
            x: center.x - (width/2),
            y: center.y - (height/2)
          };

          var vs = drawable.viewportSize();
          var wr = vs.x / width;
          var hr = vs.y / height;
          var r = (wr < hr) ? wr : hr;
          var origin = {
            x: (wr < hr) ? origin_of_shapes.x : center.x - ((vs.x/2)/hr),
            y: (wr < hr) ? center.y - ((vs.y/2)/wr) : origin_of_shapes.y
          };
          self.zoomRatio = r;
          self.callbacks.slider.setOriginZoomRatio(r);
          self.contentOriginPosition = origin;

          drawable.transform(
            Fashion.Matrix.scale(self.zoomRatio)
              .translate({x: -origin.x, y: -origin.y}));

          drawable.contentSize({x: (vs.x/r) + origin.x, y: (vs.y/r) + origin.y});

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      initBlocks: function VenueViewer_initBlocks(dataSource, next) {
        var self = this;

        self.blocks = {};

        dataSource(function (classes) {
          var current_class_meta = classes[self.currentClass];
          var ids = current_class_meta.group_l0_ids;

          var getSibling = function(meta) {
            var rt = [];
            for (var id in ids) {
              if (ids[id] == meta) rt.push(self.shapes[id]);
            }
            return rt;
          };

          var getParentLinks = function(current) {
            var found = false;
            outer:
            for (var c in classes) {
              var ids = classes[c]["group_l0_ids"];
              for (var id in ids) {
                if (ids[id] == current) {
                  found = c;
                  break outer;
                }
              }
            }
            var parents = (found) ? getParentLinks(found) : [];

            parents.push([function(){
              self.currentClass = current;
              self.currentFocusedIds = classes[current]['focused_ids'];
              self.dataSource.drawing = createDrawingLoader('data/xebio-arena/drawings/'+current+'.xml');
              self.load();
            }, classes[current].name]);

            return parents;
          };

          self.parentLinks = getParentLinks(self.currentClass);
          self.callbacks.changeCurrentClassName(self.parentLinks);

          for (var id in ids) (function(id) {
            var shape = self.shapes[id];
            var meta = ids[id];
            self.blocks[id] = shape;
            shape.addEvent({
              mouseover: function(evt) {
                if (self.uiMode == 'select1') {
                  var shapes = getSibling(meta);
                  for (var i=0, l=shapes.length; i<l; i++) {
                    var shape = copyShape(shapes[i]);
                    shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                    self.drawable.draw(shape);
                    self.overlayShapes.save(shapes[i].id, shape);
                  }
                  self.callbacks.messageBoard.up(classes[meta].name);
                }
              },
              mouseout: function(evt) {
                if (self.uiMode == 'select1') {
                  var shapes = getSibling(meta);
                  for (var i=0, l=shapes.length; i<l; i++) {
                    var shape = self.overlayShapes.restore(shapes[i].id);
                    if (shape) self.drawable.erase(shape);
                  }
                  self.callbacks.messageBoard.down();
                }
              },
              mousedown: function(evt) {
                if (self.uiMode == 'select1') {
                  self.callbacks.messageBoard.down();
                  self.currentClass = ids[id];
                  self.currentFocusedIds = classes[self.currentClass]['focused_ids'];
                  self.dataSource.drawing =
                    createDrawingLoader('data/xebio-arena/drawings/'+self.currentClass+'.xml');
                  self.load();
                }
              }
            });
          })(id);

          next.call(self);
        }, self.callbacks.message);
      },

      initSeats: function VenueViewer_initSeats(dataSource, next) {
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
                self.callbacks.messageBoard.up(self.seatTitles[this.id]);
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
                self.callbacks.messageBoard.down();
                var highlighted = self.highlighted;
                self.highlighted = {};
                for (var i in highlighted)
                  highlighted[i].removeOverlay('highlighted');
              },
              mousedown: function(evt) {
                self.callbacks.click(self, self, self.highlighted);
              }
            });
          }
          next.call(self);
        }, self.callbacks.message);
      },

      refresh: function VenueViewer_refresh() {
        for (var id in this.seats) this.seats[id].refresh();
      },

      addKeyEvent: function VenueViewer_addKeyEvent() {
        if (this.keyEvents) return;
        var self = this;
        this.keyEvents = {
          down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
          up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
        };

        $(document).bind('keydown', this.keyEvents.down);
        $(document).bind('keyup',   this.keyEvents.up);
      },

      removeKeyEvent: function VenueViewer_removeKeyEvent() {
        if (!this.keyEvents) return;

        $(document).unbind('keydown', this.keyEvents.down);
        $(document).unbind('keyup',   this.keyEvents.up);
      },

      changeUIMode: function VenueViewer_changeUIMode(type) {
        if (this.drawable) {
          var self = this;
          this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

          switch(type) {
          case 'move':
            var mousedown = false, scrollPos = null;
            this.drawable.addEvent({
              mousedown: function (evt) {
                if (self.animating) return;
                mousedown = true;
                scrollPos = self.drawable.scrollPosition();
                self.startPos = evt.logicalPosition;
              },

              mouseup: function (evt) {
                if (self.animating) return;
                mousedown = false;
                if (self.dragging) {
                  self.drawable.releaseMouse();
                  self.dragging = false;
                }
              },

              mousemove: function (evt) {
                if (self.animating) return;
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
            /* this.drawable.addEvent({
              mousedown: {
              }
            });
            */
            break;

          case 'select':
            this.drawable.addEvent({
              mousedown: function(evt) {
                if (self.animating) return;
                self.startPos = evt.logicalPosition;
                self.rubberBand.position({x: self.startPos.x,
                                          y: self.startPos.y});
                self.rubberBand.size({x: 0, y: 0});
                self.drawable.draw(self.rubberBand);
                self.dragging = true;
                self.drawable.captureMouse();
              },

              mouseup: function(evt) {
                if (self.animating) return;
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
                self.callbacks.select(self, selection);
              },

              mousemove: function(evt) {
                if (self.animating) return;
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
                self.zoom(self.zoomRatio * 1.2, evt.logicalPosition);
              }
            });
            break;

          case 'zoomout':
            this.drawable.addEvent({
              mouseup: function(evt) {
                self.zoom(self.zoomRatio / 1.2, evt.logicalPosition);
              }
            });
            break;

          default:
            throw new Error("Invalid ui mode: " + type);
          }
        }
        this.uiMode = type;
        this.callbacks.uimodeselect(this, type);
      },

      zoom: function(ratio, center) {

        if (!center) {
          var vs = this.drawable.viewportSize();
          var logicalSize = {
            x: vs.x / this.zoomRatio,
            y: vs.y / this.zoomRatio
          };
          var scroll = this.drawable.scrollPosition();
          center = {
            x: scroll.x + (logicalSize.x / 2),
            y: scroll.y + (logicalSize.y / 2)
          }
        }

        this.zoomRatio = ratio;
        this.drawable.transform(Fashion.Matrix.scale(ratio)
                                .translate({x: -this.contentOriginPosition.x,
                                            y: -this.contentOriginPosition.y}));

        var vs = this.drawable.viewportSize();

        var logicalSize = {
          x: vs.x / ratio,
          y: vs.y / ratio
        };

        var logicalOrigin = {
          x: center.x - (logicalSize.x / 2),
          y: center.y - (logicalSize.y / 2)
        };

        this.drawable.scrollPosition(logicalOrigin);

      },

      unselectAll: function VenueViewer_unselectAll() {
        var prevSelection = this.selection;
        this.selection = {};
        for (var id in prevSelection) {
          this.seats[id].__unselected();
        }
      },

      _select: function VenueViewer__select(seat, value) {
        if (value) {
          if (!(seat.id in this.selection)) {
            this.selection[seat.id] = seat;
            this.selectionCount++;
            seat.__selected();
          }
        } else {
          if (seat.id in this.selection) {
            delete this.selection[seat.id];
            this.selectionCount--;
            seat.__unselected();
          }
        }
      },

      adjacencyLength: function VenueViewer_adjacencyLength(value) {
        if (value !== void(0)) {
          this._adjacencyLength = value;
        }
        return this._adjacencyLength;
      },

      scrollTo: function VenueViewer_scrollTo(leftTopCorner) {
        if (this.animating) return;
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
      },

      back: function VenueViewer_back() {
        if (this.parentLinks.length >= 2) {
          var link = this.parentLinks[this.parentLinks.length - 2];
          link[0].call(this);
        }
      }
    }
  });

  /* main */

  $.fn.venueviewer = function (options) {
    var aux = this.data('venueviewer');

    if (!options)
      throw new Error("Options must be given");
    if (typeof options == 'object') {
      if (!options.dataSource || typeof options.dataSource != 'object')
        throw new Error("Required option missing: dataSource");
      if (aux)
        aux.dispose();

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
          createDrawingLoader(options.dataSource.drawing)
      };

      $.each(
        [
          [ 'stockTypes', 'stock_types' ],
          [ 'seats', 'seats' ],
          [ 'areas', 'areas' ],
          [ 'info', 'info' ],
          [ 'seatAdjacencies', 'seat_adjacencies' ],
          [ 'drawingClasses', 'drawing_classes' ]
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

      if (options.uimode) aux.changeUIMode(options.uimode);

    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        aux.dispose();
        this.data('venueviewer', null);
      } else {
        if (!aux)
          throw new Error("Command issued against an uninitialized element");
        switch (options) {
        case 'load':
          aux.load();
          break;

        case 'uimode':
          if (arguments.length >= 2)
            aux.changeUIMode(arguments[1]);
          else
            return aux.uiMode;
          break;

        case 'selection':
          return aux.selection;

        case 'refresh':
          return aux.refresh();

        case 'adjacency':
          aux.adjacencyLength(arguments[1]|0);
          break;

        case 'back':
          aux.back();
          break;

        case 'zoom':
          aux.zoom(arguments[1]);
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
