(function ($) {
  var PRELOADED_OBJECTS = require('preloaded.js');
  var tokenizer = require('tokenizer.js');
  var parse = require('parser.js').parse;
  var newHandler = require('renderer.js').newHandler;
  var utils = require('utils.js');

  var TicketViewer = function TicketViewer() {
    this.initialize.apply(this, arguments);
  };

  TicketViewer.prototype.initialize = function (node, options) {
    this.callbacks = {
      load: null,
      loadstart: null,
      message: null
    };
    if (options.callbacks) {
      for (var k in this.callbacks)
        this.callbacks[k] = options.callbacks[k] || null;
    }
    if (!this.callbacks.message)
      this.callbacks.message = function () {};

    this.node = node;
    this.dataSource = options.dataSource;
    this.zoomRatio = options.zoomRatio || 1.;
    this.drawable = null;
    this.objects = options.objects;
    this.styleClasses = options.styleClasses;
    this.zoomRatio = 1.0;
    this._uiMode = 'move';
  };

  TicketViewer.prototype.load = function TicketViewer_load() {
    if (this.drawable !== null)
      this.drawable.dispose();
    var self = this;
    self.dataSource(function (data) {
      setTimeout(function () {
        var paperSize = {
          x: utils.convertToUserUnit(data['size'].width),
          y: utils.convertToUserUnit(data['size'].height)
        };
        var offset = { x: 4, y: 4 };
        var contentSize = { x: paperSize.x + offset.x * 2 + 2, y: paperSize.y + offset.y * 2 + 2 };
        var drawable = new Fashion.Drawable(self.node, { contentSize: contentSize });
        drawable.draw(new Fashion.Rect({
          position: offset,
          size: paperSize,
          style: { stroke: new Fashion.Stroke(new Fashion.Color('#000'), 1) }
        }));
        if (data.perforations) {
          var verticalPerforations = data['perforations']['vertical'];
          for (var i = 0; i < verticalPerforations.length; i++) {
            var x = utils.convertToUserUnit(verticalPerforations[i]);
            drawable.draw(new Fashion.Path({
              points: [['M', offset.x + x, offset.y], ['L', offset.x + x, offset.y + paperSize.y], ['Z']],
              style: { stroke: new Fashion.Stroke(new Fashion.Color('#ccc'), 1, [2, 2]) }
            }));
          }
          var horizontalPerforations = data['perforations']['horizontal'];
          for (var i = 0; i < horizontalPerforations.length; i++) {
            var y = utils.convertToUserUnit(horizontalPerforations[i]);
            drawable.draw(new Fashion.Path({
              points: [['M', offset.x, offset.y + y], ['L', offset.x + paperSize.x, offset.y + y], ['Z']],
              style: { stroke: new Fashion.Stroke(new Fashion.Color('#ccc'), 1, [2, 2]) }
            }));
          }
        }
        var printableAreas = data['printable_areas'];
        for (var i = 0; i < printableAreas.length; i++) {
          var printableArea = printableAreas[i];
          var position = {
            x: offset.x + utils.convertToUserUnit(printableArea.x),
            y: offset.y + utils.convertToUserUnit(printableArea.y)
          };
          var size = {
            x: utils.convertToUserUnit(printableArea.width),
            y: utils.convertToUserUnit(printableArea.height)
          };
          drawable.draw(new Fashion.Rect({
            position: position,
            size: size,
            style: {
              stroke: new Fashion.Stroke(new Fashion.Color('#cc8'), 1),
              fill: new Fashion.FloodFill(new Fashion.Color('#ffc'))
            }
          }));
        }
        if (data['drawing'] !== void(0)) {
          parse(tokenizer.newScanner(data['drawing']),
                newHandler(self.objects, self.styleClasses, drawable, offset),
                []);
        }
        drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
        self.drawable = drawable;
        self._refreshUI(self.uiMode);
      }, 0);
    }, function () {
      self.callbacks.message('Failed to load data');
    });
  };

  TicketViewer.prototype._refreshUI = function TicketViewer__refreshUI() {
    if (this.drawable) {
      var self = this;
      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

      switch (self._uiMode) {
      case 'move':
        var mousedown = false, scrollPos = null;
        this.drawable.addEvent({
          mousedown: function (evt) {
            if (self.animating)
              return;
            mousedown = true;
            scrollPos = self.drawable.scrollPosition();
            self.startPos = evt.logicalPosition;
          },

          mouseup: function (evt) {
            if (self.animating)
              return;
            mousedown = false;
            if (self.dragging) {
              self.drawable.releaseMouse();
              self.dragging = false;
            }
          },

          mousemove: function (evt) {
            if (self.animating)
              return;
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
        throw new Error("Invalid ui mode: " + self._uiMode);
      }
    }
  };

  TicketViewer.prototype.uiMode = function TicketViewer_uiMode(type) {
    if (type === void(0))
      return this._uiMode;
    this._uiMode = type;
    this._refreshUI();
    this.callbacks.uimodeselect && this.callbacks.uimodeselect(this, type);
  };


  TicketViewer.prototype.dispose = function TicketViewer_dispose() {
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
  };

  $.fn.ticketviewer = function (options) {
    var aux = this.data('ticketviewer');

    if (!options)
      throw new Error("Options must be given");
    if (typeof options == 'object') {
      if (typeof options.dataSource != 'function' &&
          typeof options.dataSource != 'string' &&
          typeof options.dataSource != 'object') {
        throw new Error("Required option missing: dataSource");
      }
      if (aux)
        aux.dispose();

      var _options = $.extend({}, options);
     
      _options.dataSource =
          typeof options.dataSource == 'function' ?
            options.dataSource:
            function (next, error) {
              $.ajax({
                type: 'get',
                url: options.dataSource,
                dataType: 'json',
                success: function(json) { next(json); },
                error: function(xhr, text) { error("Failed to load drawing data (reason: " + text + ")"); }
              });
            };
      if (this.length == 0)
        throw new Error("No nodes are selected");
      this.empty();
      _options.objects = _options.objects || require('preloaded.js');
      _options.styleClasses = _options.styleClasses || require('styles.js');
      aux = new TicketViewer(this[0], _options),
      this.data('ticketviewer', aux);
    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        aux.dispose();
        this.data('ticketviewer', null);
      } else {
        if (!aux)
          throw new Error("Command issued against an uninitialized element");
        switch (options) {
        case 'load':
          aux.load();
          break;

        case 'uimode':
          if (arguments.length >= 2)
            aux.uiMode(arguments[1]);
          else
            return aux.uiMode();
          break;

        case 'refresh':
          return aux.refresh();
        }
      }
    }

    return this;
  };

})(jQuery);
/*
 * vim: sts=2 sw=2 ts=2 et
 */
