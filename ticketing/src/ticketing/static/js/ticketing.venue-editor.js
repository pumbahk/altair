(function ($) {
function appendShapes(drawable, nodeList) {
  for (var i = 0; i < nodeList.length; i++) {
    var n = nodeList[i];
    if (n.nodeType != 1) continue;
    var styleString = n.getAttribute('style');
    var shape = null;
    var shape2 = null;
    switch (n.nodeName) {
    case 'g':
      appendShapes(drawable, n.childNodes);
      break;

    case 'path':
      var pathDataString = n.getAttribute('d');
      if (!pathDataString)
        throw "Pathdata is not provided for the path element";
      shape = drawable.draw(new Fashion.Path(new Fashion.PathData(pathDataString)));
      shape.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(255, 203, 63)),
        'stroke': new Fashion.Stroke(new Fashion.Color(90, 190, 205, 255), 1)
      });
      break;

    case 'text':
      var xString = n.getAttribute('x');
      var yString = n.getAttribute('y');
      var widthString = n.getAttribute('width');
      var heightString = n.getAttribute('height');
      var fontSize = n.style.fontSize;
      var idString = n.getAttribute('id');
      shape = drawable.draw(
        new Fashion.Text(
          parseFloat(xString),
          parseFloat(yString),
          parseFloat(fontSize),
          n.firstChild.nodeValue));
      shape.id = idString;
      break;

    case 'rect':
      var xString = n.getAttribute('x');
      var yString = n.getAttribute('y');
      var widthString = n.getAttribute('width');
      var heightString = n.getAttribute('height');
      var idString = n.getAttribute('id');
      shape = drawable.draw(
        new Fashion.Rect(
          parseFloat(xString),
          parseFloat(yString),
          parseFloat(widthString),
          parseFloat(heightString)));
      shape.style({
        fill: new Fashion.FloodFill(new Fashion.Color("#fff")),
        stroke: new Fashion.Stroke(new Fashion.Color("#000"), 1)
      });
      shape.id = idString;
      break;
    }
  }
}

function parseSvg(xml, targetNode) {
  var viewBoxString = xml.documentElement.getAttribute('viewBox');
  var widthString = xml.documentElement.getAttribute('width');
  var heightString = xml.documentElement.getAttribute('height');
  var viewBox = viewBoxString ? viewBoxString.split(/\s+/): null;
  var size =
    viewBox ?
    {
      width: parseFloat(viewBox[2]),
      height: parseFloat(viewBox[3])
    }
  :
  widthString ?
    heightString ?
    {
      width: parseFloat(widthString),
      height: parseFloat(heightString)
    }
  :
  {
    width: parseFloat(widthString),
    height: parseFloat(widthString)
  }
  :
  heightString ?
    {
      width: parseFloat(heightString),
      height: parseFloat(heightString)
    }
  :
  null
  ;
  var drawable = new Fashion.Drawable(targetNode, { content: size });
  appendShapes(drawable, xml.documentElement.childNodes);

  return drawable;
}

function makeTester(a) {
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
};

var VenueEditor = Fashion._lib._class("VenueEditor", {
  props: {
    dragging: false,
    start_pos: {x:0,y:0},
    mask: null,
    d: null,
    originalStyles: {},
    shift: false
  },

  methods: {
    init : function(d) {
      this.d = d;
      this.mask = new Fashion.Rect(0,0,0,0);
      this.mask.style({
        'fill': new Fashion.FloodFill(new Fashion.Color(0, 100, 255, 128)),
        'stroke': new Fashion.Stroke(new Fashion.Color(0, 128, 255, 255), 2)
      });
    },

    changeTool: function(type) {
      var self = this;

      var selectedSeatStyle = {
        'fill': new Fashion.FloodFill(new Fashion.Color(0, 155, 225, 255)),
        'stroke': new Fashion.Stroke(new Fashion.Color(255, 255, 255, 255), 3),
        'label': {
          'fill': new Fashion.FloodFill(new Fashion.Color(255, 255, 255))
        }
      };

      if (this.d.handler)
        this.d.removeEvent("mousedown", "mouseup", "mousemove");

      switch(type) {
      case 'select1':
        this.d.addEvent({
          mousedown: function(evt) {
            var pos = evt.contentPosition;
            self.d.each(function(i) {
              if (i.seat) {
                var p = i.position(), s = i.size();
                if (p.x < pos.x && pos.x < (p.x + s.width) &&
                    p.y < pos.y && pos.y < (p.y + s.height)) {
                  if (i.selecting && !self.shift) {
                    var originalStyle = self.originalStyles[i.id];
                    i.style(originalStyle);
                    if (i.label) {
                      i.label.style(originalStyle.label);
                    }
                    i.selecting = false;
                  } else {
                    self.originalStyles[i.id] = {
                      fill: i.style().fill,
                      stroke: i.style().stroke,
                      label: i.label ? i.label.style(): void(0)
                    };
                    i.style(selectedSeatStyle);
                    i.selecting = true;
                  }
                }
              }
            });
          }
        });

        break;
      case 'select':
        this.d.addEvent({
          mousedown: function(evt) {
            self.start_pos = evt.contentPosition;
            self.mask.position({x: self.start_pos.x, y: self.start_pos.y});
            self.mask.size({width: 0, height: 0});
            self.d.draw(self.mask);
            self.dragging = true;
          },
          mouseup: function(evt) {
            self.dragging = false
            var hitTest = makeTester(self.mask);
            self.d.each(function(i) {
              if (i.seat && hitTest(i)) {
                if (i.selecting && !self.shift) {
                  var originalStyle = self.originalStyles[i.id];
                  i.style(originalStyle);
                  if (i.label) {
                    i.label.style(originalStyle.label);
                  }
                  i.selecting = false;
                } else {
                  self.originalStyles[i.id] = {
                    fill: i.style().fill,
                    stroke: i.style().stroke,
                    label: i.label ? i.label.style(): void(0)
                  };
                  i.style(selectedSeatStyle);
                  if (i.label) {
                    i.label.style(selectedSeatStyle.label);
                  }
                  i.selecting = true;
                }
              }
            });
            self.d.erase(self.mask);
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
        this.d.addEvent({
          mouseup: function(evt) {
            this.zoom(this.zoom()*1.2, evt.contentPosition);
          }
        });
        break;
      case 'zoomout':
        this.d.addEvent({
          mouseup: function(evt) {
            this.zoom(this.zoom()/1.2, evt.contentPosition);
          }
        });
        break;
      }
    }
  }
});

function key(e) {
  var shift, ctrl;

  // Mozilla(Firefox, NN) and Opera
  if (e != null) {
    keycode = e.which;
    ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
    shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;
    // イベントの上位伝播を防止
    e.preventDefault();
    e.stopPropagation();
    // Internet Explorer
  } else {
    keycode = event.keyCode;
    ctrl    = event.ctrlKey;
    shift   = event.shiftKey;
    // イベントの上位伝播を防止
    event.returnValue = false;
    event.cancelBubble = true;
  }

  // キーコードの文字を取得
  keychar = String.fromCharCode(keycode).toUpperCase();

  return {
    ctrl:    (!!ctrl) || keycode === 17,
    shift:   (!!shift) || keycode === 16,
    keycode: keycode,
    keychar: keychar
  };

  // 27Esc
  // 8 BackSpace
  // 9 Tab
  // 32Space
  // 45Insert
  // 46Delete
  // 35End
  // 36Home
  // 33PageUp
  // 34PageDown
  // 38↑
  // 40↓
  // 37←
  // 39→

}

function make_async_set_waiter(async_identifiers, after_doing) {
  var stor = {};
  for (var i=0,l=async_identifiers.length; i < l; i++) {
    stor[async_identifiers[i]] = void(0);
  }
  return function(idt, data) {
    stor[idt] = data;
    for (var i in stor) {
      if (stor.hasOwnProperty(i)) {
        if (stor[i] === void(0)) return;
      }
    }
    // if all data has come.
    after_doing.call(null, stor);
  }
};

$.fn.venue_editor = function(options) {
  var svgStyle = {
    'fill': new Fashion.Color(0, 0, 0), 'fill-opacity': 1.,
    'stroke': null, 'stroke-opacity': 1.,
    'stroke-width': 1
  };
  var manager = null, canvas = null, toolbar = null;
  var data = this.data('venue_editor');
  if (!data) {
    function generateid() {
      do {
        var id = 'D' + ((Math.random() * 100000) | 0);
      } while (document.getElementById(id));
      return id;
    }

    toolbar = $('<div class="ui-widget-header ui-corner-all ui-toolbar"></div>');
    canvas = $('<div class="canvas"><div class="message">Loading...</div></div>');
    data = { manager: null };
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
    this.append(toolbar);
    this.append(canvas);
    this.data('venue_editor', data);
  } else {
    canvas = this.find('.canvas');
    toolbar = this.find('.ui-toolbar');
  }
  if (typeof options == 'string' || options instanceof String) {
    switch (options) {
    case 'load':
      function convertToFashionStyle(style) {
        return {
          "fill": style.fill ? new Fashion.LinearGradientFill([[0, new Fashion.Color("#fff")], [1, new Fashion.Color(style.fill)]], .125): null,
          "stroke": style.stroke ? new Fashion.Stroke(new Fashion.Color(style.stroke), style.strokeWidth ? style.strokeWidth: 1, style.strokePattern): null
        };
      }
      var waiter = make_async_set_waiter(
        ['drawable', 'metadata', 'rules'],
        function(data) {
          var rules = data.rules.seats;
          var metadata = data.metadata.seats;
          var drawable = data.drawable;
          var logged = false;
          drawable.each(function(i){
            var id = i.id;
            var meta = metadata[id];
            if (!meta)
              return;

            var styles = {};
            var rules_to_be_applied = ['seat_type_id', 'stock_holder_id'];
            for (var jj in rules_to_be_applied) {
              var j = rules_to_be_applied[jj];
              var rule = rules[j];
              if (rule) {
                var m = meta[j];
                var st = (m in rule) ? rule[m] : rule['default'];
                for (var k in st)
                  styles[k] = st[k];
              }
            }
            i.style(convertToFashionStyle(styles));
            if (styles.text !== null) {
              var pos = i.position();
              var size = i.size();
              i.label = drawable.draw(
                new Fashion.Text(
                  pos.x,
                  pos.y + (size.height * 0.75),
                  (size.height * 0.75),
                  styles.text))
              i.label.style({ fill: new Fashion.FloodFill(
                new Fashion.Color(styles['text-color'] || "#000")) });
            }
            i.seat = true;
          });
        });

      $.ajax({
        type: 'get',
        url: data.drawing_url,
        dataType: 'xml',
        success: function(xml) {
          canvas.empty();
          data.manager = new VenueEditor(parseSvg(xml, canvas[0]));
          var cs = data.manager.d.contentSize();
          data.manager.d.zoom(0.4, { x: cs.width / 2, y: cs.height / 2 });
          document.addEventListener('keydown', data.keydown = function(e) { if (key(e).shift) data.manager.shift = true; return true; });
          document.addEventListener('keyup', data.keyup = function(e) { if (key(e).shift) data.manager.shift = false; return true; });
          waiter('drawable', data.manager.d);
        },
        error: function() {
          canvas.find('.message').text("Failed to load drawing data");
        }
      });

      $.ajax({
        url: data.seat_data_url,
        dataType: 'json',
        success: function(data) {
          waiter('metadata', data);
        },
        error: function() {
          canvas.find('.message').text("Failed to load seat data");
        }
      });

      $.ajax({
        url: data.rendering_rule_url,
        dataType: 'json',
        success: function(data) {
          waiter('rules', data);
        },
        error: function() {
          canvas.find('.message').text("Failed to load rendering rule");
        }
      });
      break;

    case 'remove':
      toolbar.remove();
      canvas.remove();
      document.removeEventListener('keydown', data.keydown);
      document.removeEventListener('keyup', data.keyup);
      this.data('venue_editor', null);
      break;
    }
  } else {
    data.drawing_url = options.drawing_url;
    data.seat_data_url = options.seat_data_url;
    data.rendering_rule_url = options.rendering_rule_url;
  }
  return this;
};

})(jQuery);
