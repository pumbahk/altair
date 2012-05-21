var VenueEditor = _class("VenueEditor", {

  props: {
    dragging: false,
    startPos: {x:0,y:0},
    mask: null,
    drawable: null,
    originalStyles: (function() {
      var stor = {};
      return {
        save: function(id, data) {
          if (!stor[id]) stor[id] = data;
        },
        restore: function(id) {
          var rt = stor[id];
          delete stor[id];
          return rt;
        }
      };
    })(),
    shift: false,
    xml: null,
    metadata: null,
    keyEvents: null,
    adjacencies: null,
    zoomRatio: 1.0,
    toolType: 'select1',
    shapes: {},
    seats: {}
  },

  methods: {

    init : function(canvas, xml, metadata) {
      canvas.empty();
      this.xml = xml;
      this.canvas = canvas[0];
      this.metadata = metadata;
      this.zoomRatio = CONF.DEFAULT.ZOOM_RATIO;

      this.initDrawable();
      this.adjacencies = new SeatAdjacencies(this.metadata.seat_adjacencies);
      this.initSeats();
      this.addKeyEvent();

      this.mask = new Fashion.Rect({
        position: {x: 0, y: 0},
        size: {x: 0, y: 0}
      });

      this.mask.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.MASK));
    },

    dispose: function() {
      this.removeKeyEvent();
    },

    initDrawable: function() {

      if (this.drawable !== null) return;
      var xml = this.xml;
      var attrs = Util.allAttributes(xml.documentElement);
      var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
      var vb = attrs.viewBox ? attrs.viewBox.split(/\s+/).map(parseFloat) : null;

      vb = [0, 0, 1000, 1000];

      var size = ((vb || w || h) ? {
        x:  ((vb && vb[2]) || w || h),
        y: ((vb && vb[3]) || h || w)
      } : null);

      this.drawable = new Fashion.Drawable(this.canvas, { contentSize: {x: size.x, y: size.y} });

      (function iter(nodeList) {

        outer:
        for (var i = 0; i < nodeList.length; i++) {
          var n = nodeList[i];
          if (n.nodeType != 1) continue;

          var shape = null;
          var attrs = Util.allAttributes(n);

          switch (n.nodeName) {
          case 'g':
            iter.call(this, n.childNodes);
            continue outer;

          case 'path':
            if (!attrs.d) throw "Pathdata is not provided for the path element";
            shape = this.drawable.draw(new Fashion.Path({points: new Fashion.PathData(attrs.d)}));
            shape.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SHAPE));
            break;

          case 'text':
            shape = this.drawable.draw(
              new Fashion.Text({
                position: {
                  x: parseFloat(attrs.x),
                  y: parseFloat(attrs.y)
                },
                fontSize: parseFloat(n.style.fontSize),
                text: n.firstChild.nodeValue
              }));
            shape.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.TEXT));
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
            shape.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SHAPE));
            break;

          default:
            continue outer;

          }
          this.shapes[attrs.id] = shape;
        }

      }).call(this, xml.documentElement.childNodes);

      var cs = this.drawable.contentSize();
      var vs = this.drawable.viewportSize();
      var center = {
        x: (cs.x - vs.x) / 2,
        y: (cs.y - vs.y) / 2
      };

      this.drawable.transform(Fashion.Util.Matrix.scale(this.zoomRatio));
    },

    initSeats: function() {
      var self = this;
      for (var id in this.shapes) {
        var shape = this.shapes[id];
        var meta  = this.metadata.seats[id];

        if (!meta) continue;

        this.seats[id] = new Seat(id, shape, meta, this, {
          mouseover: function(evt) { this.mouseover(); },
          mouseout: function(evt)  { this.free(); }
        });

      }
    },

    addKeyEvent: function() {
      if (this.keyEvents) return;

      var self = this;

      this.keyEvents = {
        down: function(e) { if (Util.eventKey(e).shift) self.shift = true;  return true; },
        up:   function(e) { if (Util.eventKey(e).shift) self.shift = false; return true; }
      };

      document.addEventListener('keydown', this.keyEvents.down, false);
      document.addEventListener('keyup',   this.keyEvents.up,   false);

    },

    removeKeyEvent: function() {
      if (!this.keyEvents) return;

      document.removeEventListener('keydown', this.keyEvents.down, false);
      document.removeEventListener('keyup',   this.keyEvents.up,   false);
    },

    changeTool: function(type) {
      var self = this;

      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);
      this.toolType = type;

      switch(type) {
      case 'select1':
        this.adjacencies.enable();
        this.drawable.addEvent({
          mousedown: function(evt) {
            var pos = evt.logicalPosition;
            for (var i in self.seats) {
              var seat = self.seats[i];
              var p = seat.shape.position(), s = seat.shape.size();
              if (p.x < pos.x && pos.x < (p.x + s.x) &&
                  p.y < pos.y && pos.y < (p.y + s.y)) {
                if (seat.status() === 'selected' && !self.shift) {
                  seat.neutral();
                } else {
                  seat.selected();
                }
              }
            }
          }
        });
        break;

      case 'select':
        this.adjacencies.disable();
        this.drawable.addEvent({
          mousedown: function(evt) {
            self.startPos = evt.logicalPosition;
            self.mask.position({x: self.startPos.x, y: self.startPos.y});
            self.mask.size({x: 0, y: 0});
            self.drawable.draw(self.mask);
            self.dragging = true;
          },

          mouseup: function(evt) {
            self.dragging = false;
            var hitTest = Util.makeHitTester(self.mask);
            for (var i in self.seats) {
              var seat = self.seats[i];
              if (hitTest(seat.shape)) {
                if (seat.status() === 'selected' && !self.shift) {
                  seat.status('neutral');
                } else {
                  seat.status('selected');
                }
              }
            }
            self.drawable.erase(self.mask);
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
                self.mask.position(origin);

              self.mask.size({x: w, y: h});
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

      }
    }
  }
});