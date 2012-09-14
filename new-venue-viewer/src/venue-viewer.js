(function ($) {

  include("classify.js");
  include("helpers.js");

  var CONF = require('CONF.js');
  var seat = require('seat.js');
  var util = require('util.js');

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
        loadPartStart: null,
        loadPartEnd: null,
        click: null,
        selectable: null,
        select: null,
        pageChanging: null,
        messageBoard: null,
        zoomRatioChanging: null,
        zoomRatioChange: null
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
      link_pairs: null,
      seats: null,
      selection: {},
      selectionCount: 0,
      highlighted: {},
      animating: false,
      _adjacencyLength: 1,
      currentPage: null,
      rootPage: null,
      _history: [],
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
        if (options.zoomRatio) zoom(options.zoomRatio);
        this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
        canvas.empty();
        this.optionalViewportSize = options.viewportSize;
      },

      load: function VenueViewer_load() {
        this.seatAdjacencies = null;
        var self = this;

        self.callbacks.loadPartStart.call(self, 'pages');
        self.initBlocks(self.dataSource.pages, function() {
          self.callbacks.loadPartEnd.call(self, 'pages');
          self.currentPage = self.rootPage;
          self.callbacks.loadPartStart.call(self, 'stockTypes');
          self.dataSource.stockTypes(function (data) {
            self.callbacks.loadPartEnd.call(self, 'stockTypes');
            self.stockTypes = data;
            self.callbacks.loadPartStart.call(self, 'info');
            self.dataSource.info(function (data) {
              self.callbacks.loadPartEnd.call(self, 'info');
              if (!'available_adjacencies' in data) {
                self.callbacks.message.call(self, "Invalid data");
                return;
              }
              self.availableAdjacencies = data.available_adjacencies;
              self.seatAdjacencies = new seat.SeatAdjacencies(self);
              self.callbacks.loadPartStart.call(self, 'seats');
              self.initSeats(self.dataSource.seats, function () {
                self.callbacks.loadPartEnd.call(self, 'seats');
                if (self.currentPage) {
                  self.loadDrawing(self.currentPage, function () {
                    self.callbacks.load.call(self, self);
                  });
                } else {
                  self.callbacks.load.call(self, self);
                }
              });
            }, self.callbacks.message);
          }, self.callbacks.message);
        });
      },

      loadDrawing: function (page, next) {
        var self = this;
        this.callbacks.loadPartStart.call(this, this, 'drawing');
        this.initDrawable(page, function () {
          next();
          self.callbacks.pageChanging.call(self, page);
          self.callbacks.loadPartEnd.call(self, self, 'drawing');
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

      initDrawable: function VenueViewer_initDrawable(page, next) {
        if (this.link_pairs) {
          for (var i = this.link_pairs.length; --i >= 0; )
            this.link_pairs[i][0].removeEvent();
        }

        if (this.drawable)
          this.drawable.dispose();

        this.originalStyles.clear();
        this.overlayShapes.clear();

        this.currentPage = page;

        var self = this;
        var currentFocusedIds = (function () {
          var retval = {};
          var focused_ids = self.pages[page]['focused_ids'];
          if (focused_ids) {
            for (var i = focused_ids.length; --i >= 0; )
              retval[focused_ids[i]] = true;
          }
          return retval;
        })();

        var isFocused = function isFocused(id){
          return currentFocusedIds[id];
        };

        var dataSource = this.dataSource.drawing(page);

        dataSource(function (drawing) {
          var attrs = util.allAttributes(drawing.documentElement);
          var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
          var vb = null;
          if (attrs['viewBox']) {
            var comps = attrs['viewBox'].split(/\s+/);
            vb = new Array(comps.length);
            for (var i = 0; i < comps.length; i++)
              vb[i] = parseFloat(comps[i]);
          }

          var size = ((vb || w || h) ? {
            x: ((vb && vb[2]) || w || h),
            y: ((vb && vb[3]) || h || w)
          } : null);

          var drawable = new Fashion.Drawable( self.canvas[0], {
            contentSize: size ? {x: size.x, y: size.y}: null,
            viewportSize: self.optionalViewportSize
          });

          var shapes = {}, link_pairs = [];
          var styleClasses = CONF.DEFAULT.STYLES;

          var leftTop = null, rightBottom = null;

          (function iter(context, nodeList) {
            outer:
            for (var i = 0; i < nodeList.length; i++) {
              var n = nodeList[i];
              if (n.nodeType != 1) continue;

              var attrs = util.allAttributes(n);
              var xlink = context.xlink;
              var focused = context.focused || (attrs.id && isFocused(attrs.id));
              var transform = attrs["transform"] ?
                context.transform.multiply(parseTransform(attrs["transform"])):
                context.transform;
              var shape = null;

              { // stylize
                var currentSvgStyle = context.svgStyle;
                if (attrs.style)
                  currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, context.defs));
                if (attrs['class']) {
                  var style = styleClasses[attrs['class']];
                  if (style) currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
                }
                currentSvgStyle = mergeSvgStyle(currentSvgStyle, svgStylesFromMap(attrs));
              }

              switch (n.nodeName) {
              case 'defs':
                parseDefs(n, context.defs);
                break;

              case 'a':
                xlink = attrs['{http://www.w3.org/1999/xlink}href'];
                /* fall-through */
              case 'g': {
                arguments.callee.call(
                  self,
                  {
                    svgStyle: currentSvgStyle,
                    transform: transform,
                    defs: context.defs,
                    focused: focused,
                    xlink: xlink
                  },
                  n.childNodes);
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
                    anchor: currentSvgStyle.textAnchor,
                    transform: _transform
                  });
                }
                break;

              case 'symbol':
                break;

              case 'rect':
                var _transform = attrs.transform || null;
                shape = new Fashion.Rect({
                  size: {
                    x: parseFloat(attrs.width),
                    y: parseFloat(attrs.height)
                  },
                  corner: {
                    x: parseFloat(attrs.rx || 0),
                    y: parseFloat(attrs.ry || 0)
                  },
                  transform: _transform,
                  zIndex: -10
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
                    leftTop = leftTop ? {
                      x: Math.min(leftTop.x, x),
                      y: Math.min(leftTop.y, y)
                    }: { x: x, y: y };
                    rightBottom = rightBottom ? {
                      x: Math.max(rightBottom.x, x),
                      y: Math.max(rightBottom.y, y)
                    }: { x: x, y: y };
                  }
                  shape.position({ x: x, y: y });
                }
                shape.style(buildStyleFromSvgStyle(currentSvgStyle));
                shape.transform(transform);
                if (shape instanceof Fashion.Text) {
                  shape.fontSize(currentSvgStyle.fontSize);
                }
                drawable.draw(shape);
              }
              if (attrs.id) {
                shapes[attrs.id] = shape;
                var seat = self.seats[attrs.id];
                if (seat)
                  seat.attach(shape);
              }
              if (xlink)
                link_pairs.push([shape, xlink])
            }
          }).call(
            self,
            {
              svgStyle: {
                fill: false, fillOpacity: false,
                stroke: false, strokeOpacity: false,
                fontSize: 10
              },
              transform: new Fashion.Matrix(),
              defs: {},
              focused: false,
              xlink: null
            },
            drawing.documentElement.childNodes);

          self.drawable = drawable;
          self.shapes = shapes;
          self.link_pairs = link_pairs;

          if (!leftTop)
            leftTop = { x: 0, y: 0 };
          if (!rightBottom)
            rightBottom = size;

          var center = {
            x: (leftTop.x + rightBottom.x) / 2,
            y: (leftTop.x + rightBottom.y) / 2
          };

          var focusedRegionSize = {
            x: (rightBottom.x - leftTop.x) / 0.8,
            y: (rightBottom.y - leftTop.y) / 0.8
          };
          var focusedRegionOffset = {
            x: center.x - (focusedRegionSize.x / 2),
            y: center.y - (focusedRegionSize.y / 2)
          };

          var vs = drawable.viewportSize();
          var wr = vs.x / focusedRegionSize.x;
          var hr = vs.y / focusedRegionSize.y;
          var r = (wr < hr) ? wr : hr;
          var origin = {
            x: (wr < hr) ? focusedRegionOffset.x : center.x - ((vs.x/2)/hr),
            y: (wr < hr) ? center.y - ((vs.y/2)/wr) : focusedRegionOffset.y
          };
          self.zoomRatioMin = r;
          self.contentOriginPosition = origin;

          drawable.transform(
            Fashion.Matrix.scale(self.zoomRatio)
              .translate({x: -origin.x, y: -origin.y}));

          drawable.contentSize({x: (vs.x/r) + origin.x, y: (vs.y/r) + origin.y});

          function getSiblings(link) {
            var rt = [];
            for (var i = self.link_pairs.length; --i >= 0;) {
              var shape_and_link = self.link_pairs[i];
              if (shape_and_link[1] == link)
                rt.push(shape_and_link[0]);
            }
            return rt;
          }

          for (var i = 0; i < self.link_pairs.length; i++) {
            (function (shape, link) {
              var siblings = getSiblings(link);
              shape.addEvent({
                mouseover: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = copyShape(siblings[i]);
                      if (shape) {
                        shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                        self.drawable.draw(shape);
                        self.overlayShapes.save(siblings[i].id, shape);
                      }
                    }
                    self.callbacks.messageBoard.up.call(self, self.pages[link].name);
                  }
                },
                mouseout: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = self.overlayShapes.restore(siblings[i].id);
                      if (shape)
                        self.drawable.erase(shape);
                    }
                    self.callbacks.messageBoard.down.call(self);
                  }
                },
                mousedown: function(evt) {
                  if (self.pages && self.uiMode == 'select1') {
                    self.callbacks.messageBoard.down.call(self);
                    self.navigate(link);
                  }
                }
              });
            }).apply(self, self.link_pairs[i]);
          }

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      navigate: function (page) {
        if (!(page in this.pages))
          return;
        var previousPage = this.currentPage;
        var self = this;
        this.loadDrawing(page, function () {
          if (self._history.length > 0 && self._history[self._history.length - 1] == page)
            self._history.pop();
          else
            self._history.push(previousPage);
        });
      },

      history: function () {
        return this._history;
      },

      initBlocks: function VenueViewer_initBlocks(dataSource, next) {
        var self = this;

        dataSource(function (pages) {
          self.pages = pages;
          for (var page in pages) {
            if (pages[page].root)
              self.rootPage = page;
          }
          next.call(self);
        }, self.callbacks.message);
      },

      initSeats: function VenueViewer_initSeats(dataSource, next) {
        var self = this;
        dataSource(function (seatMeta) {
          var seats = {};
          for (var id in seatMeta) {
            seats[id] = new seat.Seat(id, seatMeta[id], self, {
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
                      if (!seats[candidate[j]].selectable()) {
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
                    var seat = seats[candidate[i]];
                    seat.addOverlay('highlighted');
                    self.highlighted[seat.id] = seat;
                  }
                }, self.callbacks.message);
              },
              mouseout: function(evt) {
                if (self.uiMode == 'select')
                  return;
                self.callbacks.messageBoard.down.call(self);
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

          self.seats = seats;
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
                  if (seat.shape && (hitTest(seat.shape) || (self.shift && seat.selected())) &&
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
        if (isNaN(ratio))
          return;
        var previousRatio = this.zoomRatio;
        if (this.callbacks.zoomRatioChanging) {
          var corrected = this.callbacks.zoomRatioChanging(ratio);
          if (corrected === false)
            return;
          if (corrected)
            ratio = corrected;
        }
        if (!this.drawable) {
          this.zoomRatio = ratio;
          this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange(ratio);
          return;
        }

        if (!center) {
          var vs = this.drawable.viewportSize();
          var logicalSize = {
            x: vs.x / previousRatio,
            y: vs.y / previousRatio
          };
          var scroll = this.drawable.scrollPosition();
          center = {
            x: scroll.x + (logicalSize.x / 2),
            y: scroll.y + (logicalSize.y / 2)
          }
        }

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
        this.zoomRatio = ratio;
        this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange(ratio);
      },

      unselectAll: function VenueViewer_unselectAll() {
        var prevSelection = this.selection;
        this.selection = {};
        for (var id in prevSelection) {
          this.seats[id].__unselected();
        }
        this.selectionCount = 0;
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
        if (this._history.length > 0)
          this.navigate(this._history[this._history.length - 1]);
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
                    _conts[k] && _conts[k].error(message);
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

      $.each(
        [
          [ 'stockTypes', 'stock_types' ],
          [ 'seats', 'seats' ],
          [ 'areas', 'areas' ],
          [ 'info', 'info' ],
          [ 'seatAdjacencies', 'seat_adjacencies' ],
          [ 'pages', 'pages' ]
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

        case 'unselectAll':
          return aux.unselectAll();

        case 'refresh':
          return aux.refresh();

        case 'adjacency':
          aux.adjacencyLength(arguments[1]|0);
          break;

        case 'root':
          return aux.rootPage;

        case 'back':
          aux.back();
          break;

        case 'zoom':
          aux.zoom(arguments[1]);
          break;

        case 'navigate':
          aux.navigate(arguments[1]);
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
