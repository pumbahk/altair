(function ($) {
$.fn.venue_editor = function(options) {
  var svgStyle = {
    'fill': new Fashion.Color(0, 0, 0), 'fill-opacity': 1.,
    'stroke': null, 'stroke-opacity': 1.,
    'stroke-width': 1
  };
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

  var manager = null, canvas = null, toolbar = null;
  var data = this.data('venue_editor_available');
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
    this.data('venue_editor_available', data);
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
            if (i.seat) {
              var id = i.id;
              var meta = metadata[id];
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
            }
          });
        });

      loadXml(
        GET_DRAWING_URL,
        function(xml) {
          canvas.empty();
          data.manager = new DemoManager(parseSvg(xml, canvas[0]));
          var cs = data.manager.d.contentSize();
          data.manager.d.zoom(0.4, { x: cs.width / 2, y: cs.height / 2 });
          document.addEventListener('keydown', data.keydown = function(e) { if (key(e).shift) data.manager.shift = true; });
          document.addEventListener('keyup', data.keyup = function(e) { if (key(e).shift) data.manager.shift = false; });
          waiter('drawable', data.manager.d);

        }, function() {
          canvas.find('.message').text("Loading failed");
        }
      );
      loadText(
        "${request.route_path('api.get_seats', venue_id=performance.venue_id)}" + "?" + Math.random(),
        function(txt) {
          eval("var x = " + txt);
          waiter('metadata', x);
        }, function() {
          canvas.find('.message').text("Loading failed");
        });

      loadText(
        "/static/js/demo/renderingRules.json" + "?" + Math.random(),
        function(txt) {
          eval("var x = " + txt);
          waiter('rules', x);
        }, function() {
          canvas.find('.message').text("Loading failed");
        });
      break;

    case 'remove':
      toolbar.remove();
      canvas.remove();
      document.removeEventListener('keydown', data.keydown);
      document.removeEventListener('keyup', data.keyup);
      this.data('venue_editor_available', null);
      break;
    }
  }
  return this;
}
})(jQuery);
