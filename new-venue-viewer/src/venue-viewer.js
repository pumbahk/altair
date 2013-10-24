(function ($) {

  include("classify.js");
  include("helpers.js");

  var CONF = require('CONF.js');
  var seat = require('seat.js');
  var util = require('util.js');

  var VenueViewer = _class("VenueViewer", {

    props: {
      canvas: null,
      callbacks: {
        uimodeselect: function () {},
        load: function () {},
        loadPartStart: function () {},
        loadPartEnd: function () {},
        loadAbort: function () {},
        click: function () {},
        selectable: function () {},
        select: function () {},
        pageChanging: function () {},
        message: function () {},
        messageBoard: function () {},
        zoomRatioChanging: function () {},
        zoomRatioChange: function () {},
        queryAdjacency: null
      },
      dataSource: null,
      zoomRatio: CONF.DEFAULT.ZOOM_RATIO,
      contentOriginPosition: {x: 0, y: 0},
      dragging: false,
      startPos: { x: 0, y: 0 },
      drawable: null,
      overlayShapes: {},
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
      pageBeingLoaded: false,
      pagesCoveredBySeatData: null, 
      loadAborted: false,
      loadAbortionHandler: null,
      _smallTextsShown: true,
      nextSingleClickAction: null,
      doubleClickTimeout: 400,
      mouseUpHandler: null,
      onMouseUp: null,
      onMouseMove: null,
      deferSeatLoading: false
    },

    methods: {
      init: function VenueViewer_init(canvas, options) {
        this.canvas = canvas;
        this.stockTypes = null;
        for (var k in this.callbacks) {
          if (options.callbacks[k])
            this.callbacks[k] = options.callbacks[k];
        }
        this.dataSource = options.dataSource;
        if (options.zoomRatio) zoom(options.zoomRatio);
        canvas.empty();
        this.optionalViewportSize = options.viewportSize;
        this.deferSeatLoading = !!options.deferSeatLoading;
        var self = this;
        this.mouseUpHandler = function() {
          if (self.onMouseUp) {
            self.onMouseUp.call(self);
          }
        };
        $(document.body).bind('mouseup', this.mouseUpHandler);
        this.mouseMoveHandler = function(evt) {
          if (self.onMouseMove) {
            var fasevt = new Fashion.MouseEvt();
            var physicalPagePosition = { x: evt.pageX, y: evt.pageY };
            var screenPosition = Fashion._lib.subtractPoint(physicalPagePosition, self.drawable.impl.getViewportOffset());
            var physicalPosition = Fashion._lib.addPoint(self.drawable.impl.convertToPhysicalPoint(self.drawable.impl.scrollPosition()), screenPosition);
            fasevt.logicalPosition = self.drawable.impl.convertToLogicalPoint(physicalPosition);
            self.onMouseMove.call(self, fasevt);
            evt.stopImmediatePropagation();
            evt.stopPropagation();
            evt.preventDefault();
            return false;
          }
        };
        $(document.body).bind('mousemove', this.mouseMoveHandler);
      },

      load: function VenueViewer_load() {
        this.loading = true;
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
              if (self.currentPage) {
                self.loadDrawing(self.currentPage, function () {
                  self.callbacks.load.call(self, self);
                  self.zoomAndPan(self.zoomRatioMin, { x: 0., y: 0. });
                });
              } else {
                self.callbacks.load.call(self, self);
              }
              if (!self.deferSeatLoading)
                self.loadSeats(function () { onDrawingOrSeatsLoaded('seats'); });
            }, self.callbacks.message);
          }, self.callbacks.message);
        });
      },

      loadDrawing: function (page, next) {
        var self = this;
        this.callbacks.loadPartStart.call(self, self, 'drawing');
        this.initDrawable(page, function () {
          if (self.pagesCoveredBySeatData && (self.pagesCoveredBySeatData === 'all-in-one' || page in self.pagesCoveredBySeatData)) {
            for (var id in self.seats) {
              var shape = self.shapes[id];
              if (shape)
                self.seats[id].attach(shape);
            }
          }
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

        this.overlayShapes = {};

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
        self.pageBeingLoaded = page;
        dataSource(function (drawing) {
          self.loading = false;
          self.pageBeingLoaded = null;
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
            viewportSize: self.optionalViewportSize             // fixed parameter
          });

          /*
          var frame = new Fashion.Rect({
                  size: { x: size.x, y: size.y },
                  position: { x: (vb && vb[0]) || 0, y: (vb && vb[1]) || 0 },
                  corner: { x: 0, y: 0 },
                  transform: null,
                  zIndex: -10
              });
          frame.style({ fill: new Fashion.FloodFill(new Fashion.Color("#ff000080")) });
          drawable.draw(frame);
          */

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
                    fontSize: currentSvgStyle.fontSize,
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
              }
              if (xlink)
                link_pairs.push([shape, xlink])
            }
          }).call(
            self,
            {
              svgStyle: {
                fill: false, fillOpacity: false,
                stroke: false, strokeOpacity: false, strokeDashArray: false,
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
            leftTop = { x: (vb && vb[0]) || 0, y: (vb && vb[1]) || 0 };
          if (!rightBottom)
            rightBottom = { x: leftTop.x + size.x, y: leftTop.y + size.y };

          var center = {
            x: (leftTop.x + rightBottom.x) / 2,
            y: (leftTop.y + rightBottom.y) / 2
          };
          var focusedRegionSize = {
            x: (rightBottom.x - leftTop.x),
            y: (rightBottom.y - leftTop.y)
          };
          var focusedRegionOffset = {
            x: center.x - (focusedRegionSize.x / 2),
            y: center.y - (focusedRegionSize.y / 2)
          };

          var margin = { x: 20, y: 20 };  /* width of zoom slider and height of map selector */
          var vs = drawable.viewportSize();
          vs = { x: vs.x-margin.x, y: vs.y-margin.y };

          var xr = vs.x / focusedRegionSize.x * 0.9;
          var yr = vs.y / focusedRegionSize.y * 0.9;
          var r = (xr < yr) ? xr : yr;

          var origin = {
            x: center.x - (vs.x/2+margin.x)/r, y: center.y - (vs.y/2+margin.y)/r
          };
          self.zoomRatioMin = r;
          self.contentOriginPosition = origin;

          drawable.transform(
            Fashion.Matrix.scale(self.zoomRatioMin)
              .translate({ x: -origin.x, y: -origin.y })
          );
          drawable.contentSize({
            x: origin.x + vs.x/r, y: origin.y + vs.y/r
          });

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
                  if (self.pages) {
                    for (var i = siblings.length; --i >= 0;) {
                      var id = siblings[i].id;
                      if (self.overlayShapes[id] === void(0)) {
                        var overlayShape = copyShape(siblings[i]);
                        if (overlayShape) {
                          overlayShape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS['highlighted_block']));
                          self.drawable.draw(overlayShape);
                          self.overlayShapes[id] = overlayShapes;
                        }
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
                  self.canvas.css({ cursor: 'default' });
                  for (var i = siblings.length; --i >= 0;) {
                    var id = siblings[i].id;
                    var overlayShape = self.overlayShapes[id];
                    if (overlayShape !== void(0)) {
                      self.drawable.erase(overlayShape);
                      delete self.overlayShapes[id];
                    }
                  }
                  self.callbacks.messageBoard.down.call(self);
                },
                mouseup: function(evt) {
                  if (self.pages) {
                    self.navigate(link);
                  }
                }
              });
            }).apply(self, self.link_pairs[i]);
          }

          (function () {
            var scrollPos = null;

            function drawableMouseUp() {
              self.onMouseUp = null;
              self.onMouseMove = null;
              $(self.canvas[0]).find('div').css({ overflow: 'scroll' });
              drawableMouseDown = false;
              if (self.dragging) {
                self.drawable.releaseMouse();
                self.dragging = false;
              }
            }

            function drawableMouseMove(evt) {
                if (clickTimer) {
                  singleClickFulfilled();
                }
                if (self.animating) return;
                if (!self.dragging) {
                  if (drawableMouseDown) {
                    self.dragging = true;
                    self.drawable.captureMouse();
                    $(self.canvas[0]).find('div').css({ overflow: 'hidden' });
                    self.callbacks.messageBoard.down.call(self);
                  } else {
                    return;
                  }
                }
                var newScrollPos = Fashion._lib.subtractPoint(
                  scrollPos,
                  Fashion._lib.subtractPoint(
                    evt.logicalPosition,
                    self.startPos));
                self.drawable.scrollPosition(newScrollPos);
                scrollPos = newScrollPos;
                return false;
            }

            function singleClickFulfilled() {
              clearTimeout(clickTimer);
              clickTimer = 0;
              var nextSingleClickAction = self.nextSingleClickAction;
              self.nextSingleClickAction = null;
              if (nextSingleClickAction)
                nextSingleClickAction.call(self);
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
                  self.onMouseMove = drawableMouseMove;
                  if (!clickTimer) {
                    scrollPos = self.drawable.scrollPosition();
                    self.startPos = evt.logicalPosition;
                    clickTimer = setTimeout(singleClickFulfilled,
                                            self.doubleClickTimeout);
                  } else {
                    if (!self.dragging) {
                      // double click
                      clearTimeout(clickTimer);
                      clickTimer = 0;
                      self.drawableMouseDown = false;
                      var e = self.zoomRatio * 2;
                      self.zoom(e, evt.logicalPosition);
                      /*
                      self.animating = true;
                      var t = setInterval(function () {
                        var newZoomRatio = Math.min(e, self.zoomRatio * 1.2);
                        if (e - self.zoomRatio < self.zoomRatio * 1e-5 || newZoomRatio - self.zoomRatio > self.zoomRatio * 1e-5) {
                          self.animating = false;
                          clearInterval(t);
                        }
                      }, 50);
                      */
                    }
                  }
                  break;
                }
              },

              mouseup: function (evt) {
                drawableMouseUp(evt);
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
/*
                if (clickTimer) {
                  singleClickFulfilled();
                }
*/
                self.canvas.css({ cursor: 'default' });
                self.callbacks.messageBoard.down.call(self);
              },

              mousemove: function (evt) {
                drawableMouseMove(evt);
              }
            });
          })();

          self.changeUIMode(self.uiMode);
          next.call(this);

        }, self.callbacks.message);
      },

      zoomOnShape: function (shape) {
        if (!this.drawable)
          return;
        var position = shape.position();
        var size = shape.size();
        var p0 = shape._transform.apply(position);
        var p1 = shape._transform.apply({ x: position.x, y: position.y+size.y });
        var p2 = shape._transform.apply({ x: position.x+size.x, y: position.y });
        var p3 = shape._transform.apply({ x: position.x+size.x, y: position.y+size.y });
        var rp = { x: Math.min(p0.x, p1.x, p2.x, p3.x), y: Math.min(p0.y, p1.y, p2.y, p3.y) };
        var rs = { x: Math.max(p0.x, p1.x, p2.x, p3.x)-rp.x, y: Math.max(p0.y, p1.y, p2.y, p3.y)-rp.y };
        var vs = this.drawable.viewportSize();
        var margin = 0.10;
        var ratio = Math.min(vs.x*(1-margin) / rs.x, vs.y*(1-margin) / rs.y);
        // FIXME: ratioが上限を超えないようにしないと、対象オブジェクトがセンターにこない
        var scrollPos = {
          x: Math.max(rp.x - (vs.x/ratio-rs.x)/2, 0),
          y: Math.max(rp.y - (vs.y/ratio-rs.y)/2, 0)
        };
        this.zoomAndPan(ratio, scrollPos);
      },

      navigate: function (pageUrlOrPageInfo) {
        var previousPageInfo = {
          page: this.currentPage,
          zoomRatio: this.zoomRatio,
          scrollPosition: this.drawable ? this.drawable.scrollPosition() : null
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
              if (shape !== void(0) && shape instanceof Fashion.Rect) {
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
        if (!pageInfo)
          return;
        if (!(pageInfo.page in this.pages))
          return;
        this.canvas.css({ cursor: 'default' });
        this.callbacks.messageBoard.down.call(this);
        if (this.currentPage != pageInfo.page) {
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

      loadSeats: function(next) {
        var self = this;
        self.callbacks.loadPartStart.call(self, self, 'seats');
        self.loading = true;
        self.initSeats(self.dataSource.seats, function () {
          self.loading = false;
          if (self.loadAborted) {
            self.loadAborted = false;
            self.loadAbortionHandler && self.loadAbortionHandler.call(self, self);
            self.callbacks.loadAbort && self.callbacks.loadAbort.call(self, self);
            return;
          }
          if (!self.pageBeingLoaded && self.currentPage && (self.pagesCoveredBySeatData === 'all-in-one' || self.currentPage in self.pagesCoveredBySeatData)) {
            for (var id in self.seats) {
              var shape = self.shapes[id];
              if (shape)
                self.seats[id].attach(shape);
            }
          }
          self.callbacks.loadPartEnd.call(self, self, 'seats');
          if (next)
            next();
        });
      },

      initSeats: function VenueViewer_initSeats(dataSource, next) {
        var self = this;
        dataSource(function (seatMeta) {
          var seats = {};
          for (var id in seatMeta) {
            var seat_ = seats[id] = new seat.Seat(id, seatMeta[id], self, {
              mouseover: function(evt) {
                self.callbacks.messageBoard.up.call(self, self.seatTitles[this.id]);
                self.queryAdjacency(this.id, self.adjacencyLength(), function (candidates) {
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
                var highlighted = self.highlighted;
                self.highlighted = {};
                for (var i in highlighted)
                  highlighted[i].removeOverlay('highlighted');
              },
              mousedown: function(evt) {
                self.nextSingleClickAction = function () {
                  self.callbacks.click.call(self, self, self.highlighted);
                };
              }
            });
          }

          for (var id in self.seats)
            self.seats[id].detach();
          self.seats = seats;
          self.pagesCoveredBySeatData = 'all-in-one'; // XXX
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
        this.callbacks.uimodeselect.call(this, this, type);
      },

      zoom: function(ratio, anchor) {
        if (!this.drawable)
          return;
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
          var corrected = this.callbacks.zoomRatioChanging.call(this, ratio);
          if (corrected === false)
            return;
          if (corrected)
            ratio = corrected;
        }
        if (!this.drawable) {
          this.zoomRatio = ratio;
          this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange.call(this, ratio);
          return;
        }
        this.drawable.transform(Fashion.Matrix.scale(ratio)
                                .translate({x: -this.contentOriginPosition.x,
                                            y: -this.contentOriginPosition.y}));

        this.drawable.scrollPosition(scrollPos);
        this.zoomRatio = ratio;
        this.callbacks.zoomRatioChange && this.callbacks.zoomRatioChange.call(this, ratio);
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
      },

      queryAdjacency: function VenueViewer_queryAdjacency(id, adjacency, success, failure) {
        if (this.callbacks.queryAdjacency)
          return this.callbacks.queryAdjacency(id, adjacency, success, failure);
        success([[id]]);
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
                  error: function(xhr, text, status) {
                    var message = "Failed to load " + key + " (reason: " + text + " - " + status + ")";
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

        case 'loadSeats':
          aux.loadSeats(arguments[1]);
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
