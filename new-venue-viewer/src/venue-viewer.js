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
        loadAbort: null,
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
      uiMode: 'select',
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
      optionalViewportSize: null,
      loading: false,
      loadAborted: false,
      loadAbortionHandler: null,
      _smallTextsShown: true,
      nextSingleClickAction: null,
      doubleClickTimeout: 400,
      mouseUpHandler: null,
      onMouseUp: null
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
        var self = this;
        this.mouseUpHandler = function() {
          if (self.onMouseUp) {
            self.onMouseUp.call(self);
          }
        };
        $(document.body).bind('mouseup', this.mouseUpHandler);
      },

      load: function VenueViewer_load() {
        this.loading = true;
        this.seatAdjacencies = null;
        var self = this;

        self.callbacks.loadPartStart.call(self, self, 'pages');
        self.initBlocks(self.dataSource.pages, function() {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          self.callbacks.loadPartEnd.call(self, self, 'pages');
          self.currentPage = self.rootPage;
          self.loading = true;
          self.callbacks.loadPartStart.call(self, self, 'stockTypes');
          self.dataSource.stockTypes(function (data) {
            self.loading = false;
            if (self.loadAborted) {
              self.loadAborted = false;
              self.loadAbortionHandler && self.loadAbortionHandler.call(self);
              self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
              return;
            }
            self.loading = true;
            self.callbacks.loadPartEnd.call(self, self, 'stockTypes');
            self.stockTypes = data;
            self.callbacks.loadPartStart.call(self, self, 'info');
            self.dataSource.info(function (data) {
              self.loading = false;
              if (self.loadAborted) {
                self.loadAborted = false;
                self.loadAbortionHandler && self.loadAbortionHandler.call(self);
                self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
                return;
              }
              self.loading = true;
              self.callbacks.loadPartEnd.call(self, self, 'info');
              if (!'available_adjacencies' in data) {
                self.callbacks.message.call(self, "Invalid data");
                return;
              }
              self.availableAdjacencies = data.available_adjacencies;
              self.seatAdjacencies = new seat.SeatAdjacencies(self);
              self.callbacks.loadPartStart.call(self, self, 'seats');
              self.initSeats(self.dataSource.seats, function () {
                self.loading = false;
                if (self.loadAborted) {
                  self.loadAborted = false;
                  self.loadAbortionHandler && self.loadAbortionHandler.call(self, self);
                  self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
                  return;
                }
                self.loading = true;
                self.callbacks.loadPartEnd.call(self, self, 'seats');
                if (self.currentPage) {
                  self.loadDrawing(self.currentPage, function () {
                    self.callbacks.load.call(self, self);
                    self.zoomAndPan(self.zoomRatioMin, { x: 0., y: 0., });
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
        this.callbacks.loadPartStart.call(self, self, 'drawing');
        this.initDrawable(page, function () {
          self.callbacks.pageChanging.call(self, page);
          self.callbacks.loadPartEnd.call(self, self, 'drawing');
          next.call(self);
        });
      },

      cancelLoading: function VenueViewer_cancelLoading(next) {
        if (this.loading) {
          this.loadAborted = true;
          this.loadAbortionHandler = next;
        } else {
          next.call(this);
        }
      },

      dispose: function VenueViewer_dispose(next) {
        var self = this;
        this.cancelLoading(function () {
          $(document.body).unbind('mouseup', self.mouseUpHandler);
          self.removeKeyEvent();
          if (self.drawable) {
            self.drawable.dispose();
            self.drawable = null;
          }
          self.seats = null;
          self.selection = null;
          self.highlighted = null;
          self.availableAdjacencies = [1];
          self.shapes = null;
          self.small_texts = [ ];
          self.link_pairs = null;
          self.selection = {};
          self.selectionCount = 0;
          self.highlighted = {};
          self.animating = false;
          self._adjacencyLength = 1;
          self.currentPage = null;
          self.rootPage = null;
          self._history = [];
          self.seatTitles = {};
          next && next.call(self);
        });
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
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
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
          var small_texts = [];
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
              var px = parseFloat(attrs.x),
                  py = parseFloat(attrs.y);
              var position = (!isNaN(px) && !isNaN(py)) ? { x: px, y: py } : context.position;
              var transform = attrs["transform"] ?
                context.transform.multiply(parseTransform(attrs["transform"])):
                context.transform;
              var shape = null;

              { // stylize
                var currentSvgStyle = context.svgStyle;
                // 1st: find style by class attribute
                if (attrs['class']) {
                  var style = styleClasses[attrs['class']];
                  if (style) currentSvgStyle = mergeSvgStyle(currentSvgStyle, style);
                }
                // 2nd: overwrite by style attribute (css like string)
                if (attrs.style)
                  currentSvgStyle = mergeSvgStyle(currentSvgStyle, parseCSSAsSvgStyle(attrs.style, context.defs));
                // 3rd: overwrite by some kinds of attributes
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
              case 'tspan':
                if (n.childNodes.length==1 && n.firstChild.nodeType == /* Node.TEXT_NODE */ 3) {
                  shape = new Fashion.Text({
                    text: collectText(n),
                    anchor: currentSvgStyle.textAnchor,
                    position: position || null,
                    transform: transform || null
                  });
                } else if (n.nodeName == 'text') {
                  arguments.callee.call(
                    self,
                    {
                      svgStyle: currentSvgStyle,
                      position: position,
                      transform: transform,
                      defs: context.defs,
                      focused: focused,
                      xlink: xlink
                    },
                    n.childNodes);
                  continue outer;
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
                  },
                  transform: transform || null,
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
                  if (currentSvgStyle.fontSize <= 10) {
                    if (!self._smallTextsShown)
                      shape.visibility(false);
                    small_texts.push(shape);
                  }
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
                fontSize: 10, textAnchor: false
              },
              position: null,
              transform: new Fashion.Matrix(),
              defs: {},
              focused: false,
              xlink: null
            },
            drawing.documentElement.childNodes);

          self.drawable = drawable;
          self.shapes = shapes;
          self.small_texts = small_texts;
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

          var drawableMouseDown = false;
          var clickTimer = 0;

          for (var i = 0; i < self.link_pairs.length; i++) {
            (function (shape, link) {
              var siblings = getSiblings(link);
              shape.addEvent({
                mouseover: function(evt) {
                  if (self.pages && self.uiMode == 'select') {
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = copyShape(siblings[i]);
                      if (shape) {
                        shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                        self.drawable.draw(shape);
                        self.overlayShapes.save(siblings[i].id, shape);
                      }
                    }
                    var pageAndAnchor = link.split('#');
                    var page = pageAndAnchor[0];
                    if (page == '')
                      page = self.currentPage;
                    self.callbacks.messageBoard.up.call(self, self.pages[page].name);
                    self.canvas.css({ cursor: 'pointer' });
                  }
                },
                mouseout: function(evt) {
                  if (self.pages && self.uiMode == 'select') {
                    self.canvas.css({ cursor: 'default' });
                    for (var i = siblings.length; --i >= 0;) {
                      var shape = self.overlayShapes.restore(siblings[i].id);
                      if (shape)
                        self.drawable.erase(shape);
                    }
                    self.callbacks.messageBoard.down.call(self);
                  }
                },
                mousedown: function(evt) {
                  if (self.pages && self.uiMode == 'select') {
                    self.nextSingleClickAction = function() {
                      self.callbacks.messageBoard.down.call(self);
                      self.navigate(link);
                    };
                  }
                }
              });
            }).apply(self, self.link_pairs[i]);
          }

          (function () {
            var scrollPos = null;

            function drawableMouseUp() {
              self.onMouseUp = null;
              drawableMouseDown = false;
              if (self.dragging) {
                self.drawable.releaseMouse();
                self.dragging = false;
              }
            }

            self.drawable.addEvent({
              mousedown: function (evt) {
                if (self.animating) return;
                switch (self.uiMode) {
                case 'zoomin': case 'zoomout':
                  break;
                default:
                  drawableMouseDown = true;
                  self.onMouseUp = drawableMouseUp;
                  if (!clickTimer) {
                    scrollPos = self.drawable.scrollPosition();
                    self.startPos = evt.logicalPosition;
                    clickTimer = setTimeout(function() {
                      var nextSingleClickAction = self.nextSingleClickAction;
                      self.nextSingleClickAction = null;
                      clickTimer = 0;
                      if (nextSingleClickAction)
                        nextSingleClickAction.call(self);
                    }, self.doubleClickTimeout);
                  } else {
                    // double click
                    clearTimeout(clickTimer);
                    clickTimer = 0;
                    self.drawableMouseDown = false;
                    self.animating = true;
                    var e = self.zoomRatio * 2;
                    var t = setInterval(function () {
                      var newZoomRatio = Math.min(e, self.zoomRatio * 1.2);
                      self.zoom(newZoomRatio, evt.logicalPosition);
                      if (e - self.zoomRatio < self.zoomRatio * 1e-5 || newZoomRatio - self.zoomRatio > self.zoomRatio * 1e-5) {
                        self.animating = false;
                        clearInterval(t);
                      }
                    }, 50);
                  }
                  break;
                }
              },

              mouseup: function (evt) {
                drawableMouseUp();
                if (self.animating) return;
                switch (self.uiMode) {
                case 'zoomin':
                  self.zoom(self.zoomRatio * 1.2, evt.logicalPosition);
                  break;
                case 'zoomout':
                  self.zoom(self.zoomRatio / 1.2, evt.logicalPosition);
                  break;
                default:
                  break;
                }
              },

              mouseout: function (evt) {
                if (clickTimer) {
                  clearTimeout(clickTimer);
                  clickTimer = 0;
                }
              },

              mousemove: function (evt) {
                if (self.animating) return;
                if (!self.dragging) {
                  if (drawableMouseDown) {
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
                return false;
              }
            });
          })();

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      zoomOnShape: function (shape) {
        var position = shape.position();
        var size = shape.size();
        var vs = drawable.viewportSize();
        var ratio = Math.min(vs.x / size.x, vs.y / size.y);
        var scrollPos = {
          x: Math.max(position.x - (vs.x * ratio - size.x) / 2, 0),
          y: Math.max(position.y - (vx.y * ratio - size.y) / 2, 0)
        };
        this.zoomAndPan(ratio, scrollPos);
      },

      navigate: function (pageUrlOrPageInfo) {
        var previousPageInfo = {
          page: this.currentPage,
          zoomRatio: this.zoomRatio,
          scrollPosition: this.drawable.scrollPosition()
        };
        var self = this;
        if (typeof pageUrlOrPageInfo == 'string' || pageUrlOrPageInfo instanceof String) {
          // page can be
          // - page.svg
          // - page.svg#id
          // - page.svg#__FIXED__
          // - #id
          var comps = pageUrlOrPageInfo.split('#');
          var anchor = null;
          page = comps[0];
          if (comps.length > 1)
            anchor = comps[1];
          if (page == '')
            page = this.currentPage;
          var afterthings = function () {
            self._history.push(previousPageInfo);
            if (anchor == '__FIXED__') {
              self.zoomAndPan(previousPageInfo.zoomRatio,
                              previousPageInfo.scrollPosition);
            } else {
              var shape = self.shapes[anchor];
              if (shape !== void(0)) {
                self.zoomOnShape(shape);
              } else {
                self.zoomAndPan(self.zoomRatioMin, { x: 0., y: 0. });
              }
            }
          }
          this._loadPage({ page: page }, afterthings);
        } else {
          this._loadPage(pageUrlOrPageInfo, function () {
            self._history.push(previousPageInfo);
          });
        }
      },

      _loadPage: function (pageInfo, next) {
        var self = this;
        var afterthings = function () {
          if (pageInfo.zoomRatio && pageInfo.scrollPosition) {
            self.zoomAndPan(pageInfo.zoomRatio,
                            pageInfo.scrollPosition);
          }
          if (next)
            next.call(self, pageInfo);
        };
        if (!(pageInfo.page in this.pages))
          return;
        this.callbacks.messageBoard.down.call(this);
        if (this.curentPage != pageInfo.page) {
          this.loadDrawing(pageInfo.page, function () {
            self.callbacks.load.call(self, self);
            afterthings();
          });
        } else {
          afterthings();
        }
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
                self.callbacks.messageBoard.up.call(self, self.seatTitles[this.id]);
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
                self.callbacks.messageBoard.down.call(self);
                var highlighted = self.highlighted;
                self.highlighted = {};
                for (var i in highlighted)
                  highlighted[i].removeOverlay('highlighted');
              },
              mousedown: function(evt) {
                self.nextSingleClickAction = function () {
                  self.callbacks.click(self, self, self.highlighted);
                };
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

          switch(type) {
          case 'select': case 'move': case 'zoomin': case 'zoomout':
            break;
          default:
            throw new Error("Invalid ui mode: " + type);
          }
        }
        this.uiMode = type;
        this.callbacks.uimodeselect(this, type);
      },

      zoom: function(ratio, anchor) {
        var vs = this.drawable.viewportSize();
        var scrollPos = this.drawable.scrollPosition();
        var previousRatio = this.zoomRatio;

        var previousLogicalSize = {
          x: vs.x / previousRatio,
          y: vs.y / previousRatio
        };

        if (!anchor) {
          anchor = {
            x: scrollPos.x + (previousLogicalSize.x / 2),
            y: scrollPos.y + (previousLogicalSize.y / 2)
          }
        }

        var physicalOffset = {
          x: (anchor.x - scrollPos.x) * previousRatio,
          y: (anchor.y - scrollPos.y) * previousRatio 
        };
        var logicalSize = {
          x: vs.x / ratio,
          y: vs.y / ratio
        };

        var logicalOrigin = {
          x: anchor.x - (physicalOffset.x / ratio),
          y: anchor.y - (physicalOffset.y / ratio)
        };

        this.zoomAndPan(ratio, logicalOrigin);
      },

      zoomAndPan: function(ratio, scrollPos) {
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
        this.drawable.transform(Fashion.Matrix.scale(ratio)
                                .translate({x: -this.contentOriginPosition.x,
                                            y: -this.contentOriginPosition.y}));

        this.drawable.scrollPosition(scrollPos);
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
          this._loadPage(this._history.pop());
      },

      showSmallTexts: function VenueViewer_showSmallTexts() {
        if (!this._smallTextsShown) {
          for(var i = this.small_texts.length; --i >= 0;)
            this.small_texts[i].visibility(true);
          this._smallTextsShown = true
        }
      },

      hideSmallTexts: function VenueViewer_hideSmallTexts() {
        if (this._smallTextsShown) {
          for(var i = this.small_texts.length; --i >= 0;)
            this.small_texts[i].visibility(false);
          this._smallTextsShown = false;
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
      var self = this;
      function init() {
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
        aux = new VenueViewer(self, _options),
        self.data('venueviewer', aux);

        if (options.uimode) aux.changeUIMode(options.uimode);
      }
      if (aux)
        aux.dispose(init);
      else
        init();
    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        if (aux)
          aux.dispose();
        this.empty();
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

        case 'showSmallTexts':
          aux.showSmallTexts();
          break;
        case 'hideSmallTexts':
          aux.hideSmallTexts();
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
