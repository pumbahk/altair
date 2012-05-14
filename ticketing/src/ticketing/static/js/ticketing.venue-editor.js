(function ($) {

  var CONF = {
    DEFAULT: {
      ZOOM_RATIO: 0.4,
      STYLE: {

        SHAPE: {
          fill: { color: '#fff' },
          stroke: { color: '#000', width: 1 }
        },

        TEXT: {
          fill: { color: '#000' }
        },

        VENUE: {
          fill:   { color: "#FFCB3F" },
          stroke: { color: "#5ABECD", width: 1 }
        },

        SEAT: {
          fill:   { color: "#fff" },
          stroke: { color: "#000", width: 1 }
        },

        MASK: {
          fill:   { color: "#0064ff80" },
          stroke: { color: "#0080FF", width: 2 }
        },

        SELECTED_SEAT: {
          fill:   { color: "#009BE1" },
          stroke: { color: "#FFF", width: 3 }
        },

        SELECTED_LABEL: {
          fill:   { color: "#FFF" }
        }

      }
    }
  };

  var Util = Fashion._lib._class("Util", {
    class_methods: {
      eventKey: function(e) {
        var shift, ctrl;
        // Mozilla
        if (e != null) {
          keycode = e.which;
          ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
          shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;

        }
        // ie
        else {
          keycode = event.keyCode;
          ctrl    = event.ctrlKey;
          shift   = event.shiftKey;

        }

        keychar = String.fromCharCode(keycode).toUpperCase();

        return {
          ctrl:    (!!ctrl) || keycode === 17,
          shift:   (!!shift) || keycode === 16,
          keycode: keycode,
          keychar: keychar
        };

      },

      AsyncDataWaiter: Fashion._lib._class("AsyncDataWaiter", {
        props: {
          identifiers: [],
          after: function() {},
          stor: {},
          this_object: null
        },

        methods: {
          charge: function(idt, data) {
            this.stor[idt] = data;

            for (var i=0,l=this.identifiers.length; i<l; i++) {
              var id = this.identifiers[i];
              if (!this.stor.hasOwnProperty(id)) return;
            }

            // fire!! if all data has come.
            this.after.call(this.this_object, this.stor);
          }
        }
      }),

      convertToFashionStyle: function(style, gradient) {
        var filler = function(color) {
          if (gradient) return new Fashion.LinearGradientFill([[0, new Fashion.Color("#fff")], [1, new Fashion.Color(color || "#fff")]], .125);
          return new Fashion.FloodFill(new Fashion.Color(color || "#000"));
        };

        return {
          "fill": style.fill ? filler(style.fill.color): null,
          "stroke": style.stroke ? new Fashion.Stroke((style.stroke.color || "#000") + " " + (style.stroke.width ? style.stroke.width: 1) + " " + (style.stroke.pattern || "")) : null
        };
      },

      allAttributes: function(el) {
        var rt = {}, attrs=el.attributes, attr;
        for (var i=0, l=attrs.length; i<l; i++) {
          attr = attrs[i];
          rt[attr.nodeName] = attr.nodeValue;
        }
        return rt;
      },

      makeHitTester: function(a) {
        var pa = a.position(),
        sa = a.size(),
        ax0 = pa.x,
        ax1 = pa.x + sa.width,
        ay0 = pa.y,
        ay1 = pa.y + sa.height;

        return function(b) {
          var pb = b.position(),
          sb = b.size(),
          bx0 = pb.x,
          bx1 = pb.x + sb.width,
          by0 = pb.y,
          by1 = pb.y + sb.height;

          return ((((ax0 < bx0) && (bx0 < ax1)) || (( ax0 < bx1) && (bx1 < ax1)) || ((bx0 < ax0) && (ax1 < bx1))) && // x
                  (((ay0 < by0) && (by0 < ay1)) || (( ay0 < by1) && (by1 < ay1)) || ((by0 < ay0) && (ay1 < by1))));  // y
        }
      }
    }
  });

  var VenueEditor = Fashion._lib._class("VenueEditor", {

    props: {
      dragging: false,
      start_pos: {x:0,y:0},
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
      seat_meta: null,
      seat_types: null,
      keyEvents: null
    },

    methods: {

      init : function(canvas, xml, metadata) {
        canvas.empty();
        this.xml = xml;
        this.canvas = canvas[0];

        this.initDrawable(metadata);

        this.mask = new Fashion.Rect(0,0,0,0);
        this.mask.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.MASK));
      },

      dispose: function() {
        this.removeKeyEvent();
      },

      initDrawable: function(metadata) {

        this.seat_meta = metadata.seats;
        this.seat_types = metadata.seat_types;

        if (this.drawable !== null) return;
        var xml = this.xml;
        var attrs = Util.allAttributes(xml.documentElement);
        var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
        var vb = attrs.viewBox ? attrs.viewBox.split(/\s+/).map(parseFloat) : null;

        var size = ((vb || w || h) ? {
          width:  ((vb && vb[2]) || w || h),
          height: ((vb && vb[3]) || h || w)
        } : null);

        this.drawable = new Fashion.Drawable(this.canvas, { content: size });

        (function iter(nodeList) {
          for (var i = 0; i < nodeList.length; i++) {
            var n = nodeList[i];
            if (n.nodeType != 1) continue;

            var shape = null;
            var shape2 = null;
            var attrs = Util.allAttributes(n);

            switch (n.nodeName) {
            case 'g':
              iter.call(this, n.childNodes);
              break;

            case 'path':
              if (!attrs.d) throw "Pathdata is not provided for the path element";
              shape = this.drawable.draw(new Fashion.Path(new Fashion.PathData(attrs.d)));

              shape.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.VENUE));

              break;

            case 'text':
              shape = this.drawable.draw(
                new Fashion.Text(
                  parseFloat(attrs.x),
                  parseFloat(attrs.y),
                  parseFloat(n.style.fontSize),
                  n.firstChild.nodeValue));
              shape.id = attrs.id;
              break;

            case 'rect':
              shape = this.drawable.draw(
                new Fashion.Rect(
                  parseFloat(attrs.x),
                  parseFloat(attrs.y),
                  parseFloat(attrs.width),
                  parseFloat(attrs.height)));

              shape.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SEAT));

              shape.id = attrs.id;

              break;
            }
          }
        }).call(this, xml.documentElement.childNodes);

        var cs = this.drawable.contentSize();
        var vs = this.drawable.viewportSize();
        var center = {
          x: (cs.width - vs.width) / 2,
          y: (cs.height - vs.height) / 2
        };

        this.drawable.zoom(CONF.DEFAULT.ZOOM_RATIO, {
          x: center.x,
          y: center.y
        });

        var self = this;
        this.drawable.each(function(i){

          var id = i.id;
          var meta = self.seat_meta[id];

          if (!meta) return;

          i.seat = true;

          var styles = Fashion._lib._clone(CONF.DEFAULT.STYLE.SHAPE);
          var type_meta = self.seat_types[meta.seat_type_id];

          if (!type_meta) return;

          var st = type_meta.style;

          for (var k in st) styles[k] = st[k];

          i.style(Util.convertToFashionStyle(styles, true));

          if (styles.text !== null) {

            var pos = i.position();
            var size = i.size();

            i.label = self.drawable.draw(
              new Fashion.Text(
                pos.x,
                pos.y + (size.height * 0.75),
                (size.height * 0.75),
                styles.text
              )
            );

            i.label.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.TEXT));
          }
        });

        this.addKeyEvent();

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

        this.drawable.removeEvent("mousedown", "mouseup", "mousemove");

        switch(type) {
        case 'select1':
          this.drawable.addEvent({
            mousedown: function(evt) {
              var pos = evt.contentPosition;
              self.drawable.each(function(i) {
                if (i.seat) {
                  var p = i.position(), s = i.size();
                  if (p.x < pos.x && pos.x < (p.x + s.width) &&
                      p.y < pos.y && pos.y < (p.y + s.height)) {
                    if (i.selecting && !self.shift) {
                      var originalStyle = self.originalStyles.restore(i.id);
                      i.style(originalStyle);
                      if (i.label) {
                        i.label.style(originalStyle.label);
                      }
                      i.selecting = false;
                    } else {
                      self.originalStyles.save(i.id, {
                        fill:   i.style().fill,
                        stroke: i.style().stroke,
                        label:  i.label ? i.label.style() : void(0)
                      });
                      i.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_SEAT));
                      if (i.label) {
                        i.label.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_LABEL));
                      }
                      i.selecting = true;
                    }
                  }
                }
              });
            }
          });
          break;

        case 'select':
          this.drawable.addEvent({
            mousedown: function(evt) {
              self.start_pos = evt.contentPosition;
              self.mask.position({x: self.start_pos.x, y: self.start_pos.y});
              self.mask.size({width: 0, height: 0});
              self.drawable.draw(self.mask);
              self.dragging = true;
            },
            mouseup: function(evt) {
              self.dragging = false
              var hitTest = Util.makeHitTester(self.mask);
              self.drawable.each(function(i) {
                if (i.seat && hitTest(i)) {
                  if (i.selecting && !self.shift) {
                    var originalStyle = self.originalStyles.restore(i.id);
                    i.style(originalStyle);
                    if (i.label) {
                      i.label.style(originalStyle.label);
                    }
                    i.selecting = false;
                  } else {
                    self.originalStyles.save(i.id, {
                      fill:   i.style().fill,
                      stroke: i.style().stroke,
                      label:  i.label ? i.label.style(): void(0)
                    });
                    i.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_SEAT));
                    if (i.label) {
                      i.label.style(Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_LABEL));
                    }
                    i.selecting = true;
                  }
                }
              });
              self.drawable.erase(self.mask);
            },
            mousemove: function(evt) {
              if (self.dragging) {
                var pos = evt.contentPosition;
                var w = Math.abs(pos.x - self.start_pos.x);
                var h = Math.abs(pos.y - self.start_pos.y);

                var origin = {
                  x: (pos.x < self.start_pos.x) ? pos.x : self.start_pos.x,
                  y: (pos.y < self.start_pos.y) ? pos.y : self.start_pos.y
                };

                if (origin.x !== self.start_pos.x || origin.y !== self.start_pos.y)
                  self.mask.position(origin);

                self.mask.size({width: w, height: h});
              }
            }
          });
          break;

        case 'zoomin':
          this.drawable.addEvent({
            mouseup: function(evt) {
              this.zoom(this.zoom()*1.2, evt.contentPosition);
            }
          });
          break;

        case 'zoomout':
          this.drawable.addEvent({
            mouseup: function(evt) {
              this.zoom(this.zoom()/1.2, evt.contentPosition);
            }
          });
          break;

        }
      }
    }
  });

  function initWindowUI(target) {
    function generateid() {
      do {
        var id = 'D' + ((Math.random() * 100000) | 0);
      } while (document.getElementById(id));
      return id;
    }

    var toolbar = $('<div class="ui-widget-header ui-corner-all ui-toolbar"></div>');
    var canvas = $('<div class="canvas"><div class="message">Loading...</div></div>');

    var data = {
      manager: null,
      toolbar: toolbar,
      canvas: canvas
    };

    var radio_id = generateid();

    function newButton(icon) {
      var id = generateid();
      var retval = $('<input type="radio" value="*" />')
        .attr('name', radio_id)
        .attr('id', id)
        .appendTo(toolbar);
      $('<label></label>').attr("for", id).appendTo(toolbar).text(icon);
      retval.button({ text: false, icons: { primary: icon }});
      return retval;
    }
    newButton('ui-icon-arrowthick-1-ne').click(
      function() {
        if (data.manager)
          data.manager.changeTool('select1');
      });

    newButton('ui-icon-calculator').click(
      function() {
        if (data.manager)
          data.manager.changeTool('select');
      });

    newButton('ui-icon-zoomin').click(
      function() {
        if (data.manager)
          data.manager.changeTool('zoomin');
      });

    newButton('ui-icon-zoomout').click(
      function() {
        console.log(data.manager);
        if (data.manager)
          data.manager.changeTool('zoomout');
      });

    toolbar.buttonset();

    target.append(data.toolbar);
    target.append(data.canvas);

    return data;
  }

  $.fn.venue_editor = function(options) {

    var data = this.data('venue_editor');

    if (!data) { // if there are no store data. init and stor the data.
      data = initWindowUI(this);
      this.data('venue_editor', data);
    }

    var canvas = data.canvas;
    var toolbar = data.toolbar;

    if (typeof options == 'string' || options instanceof String) {
      switch (options) {
      case 'load':

        // Ajax Waiter
        var waiter = new Util.AsyncDataWaiter({
          identifiers: ['drawing_xml', 'metadata'],
          after: function main(all_data) {
            var xml = all_data['drawing_xml'];
            var metadata = all_data['metadata'];
            data.manager = new VenueEditor(canvas, xml, metadata);
          }
        });

        // Load drawing
        $.ajax({
          type: 'get',
          url: data.drawing_url,
          dataType: 'xml',
          success: function(xml) { waiter.charge('drawing_xml', xml); },
          error: function() { canvas.find('.message').text("Failed to load drawing data"); }
        });

        // Load metadata
        $.ajax({
          url: data.seat_data_url,
          dataType: 'json',
          success: function(data) { waiter.charge('metadata', data); },
          error: function() { canvas.find('.message').text("Failed to load seat data"); }
        });

        break;

      case 'remove':
        toolbar.remove();
        canvas.remove();
        data.manager.dispose();
        this.data('venue_editor', null);
        break;

      }
    } else {
      data.drawing_url = options.drawing_url;
      data.seat_data_url = options.seat_data_url;
    }

    return this;
  };

})(jQuery);
