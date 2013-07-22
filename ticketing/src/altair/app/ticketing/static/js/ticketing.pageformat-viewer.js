(function () {
var __LIBS__ = {};
__LIBS__['t7L2X_A491U6Q22R'] = (function (exports) { (function () { 

/************** utils.js **************/
function convertToUserUnit(value, unit) {
  if (value === null || value === void(0))
    return null;
  if (typeof value != 'string' && !(value instanceof String)) {
    var degree = value;
    switch (unit || 'px') {
    case 'pt':
      return degree * 1.25;
    case 'pc':
      return degree * 15;
    case 'mm':
      return degree * 90 / 25.4;
    case 'cm':
      return degree * 90 / 2.54;
    case 'in':
      return degree * 90.;
    case 'px':
      return degree;
    }
    throw new Error("Unsupported unit: " + unit);
  }
  var spec = /(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px)?/.exec(value);
  if (!spec)
    throw new Error('Invalid length / size specifier: ' + value)
  return convertToUserUnit(parseFloat(spec[1]), spec[2]);
}

exports.convertToUserUnit = convertToUserUnit;
 })(); return exports; })({});


/************** pageformat-viewer.js **************/
(function ($) {
  var utils = __LIBS__['t7L2X_A491U6Q22R'];

  var PageFormatViewer = function PageFormatViewer() {
    this.initialize.apply(this, arguments);
  };

  PageFormatViewer.prototype.initialize = function (node, options) {
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

  PageFormatViewer.prototype.load = function PageFormatViewer_load() {
    if (this.drawable !== null)
      this.drawable.dispose();
    var self = this;
    self.dataSource(function (data) {
      setTimeout(function () {
        var orientation = data['orientation'].toLowerCase();
        var paperSize = {
          x: utils.convertToUserUnit(data['size'].width),
          y: utils.convertToUserUnit(data['size'].height)
        };

        if (orientation == 'landscape')
          paperSize = { x: paperSize.y, y: paperSize.x };

        var offset = { x: 0, y: 0 };
        var contentSize = { x: paperSize.x + offset.x * 2 + 1, y: paperSize.y + offset.y * 2 + 1 };
        var drawable = new Fashion.Drawable(self.node, { contentSize: contentSize });
        drawable.draw(new Fashion.Rect({
          position: offset,
          size: paperSize,
          style: { stroke: new Fashion.Stroke(new Fashion.Color('#000'), 1) }
        }));
        var printableArea = {
          x: utils.convertToUserUnit(data['printable_area'].x),
          y: utils.convertToUserUnit(data['printable_area'].y),
          width: utils.convertToUserUnit(data['printable_area'].width),
          height: utils.convertToUserUnit(data['printable_area'].height)
        };
        if (orientation == 'landscape') {
          printableArea = {
            x: printableArea.y,
            y: printableArea.x,
            width: printableArea.height,
            height: printableArea.width
          };
        }
        drawable.draw(new Fashion.Rect({
          position: { x: offset.x + printableArea.x,
                      y: offset.y + printableArea.y },
          size: { x: printableArea.width, y: printableArea.height },
          style: {
            stroke: new Fashion.Stroke(new Fashion.Color('#cc8'), 1),
            fill: new Fashion.FloodFill(new Fashion.Color('#ffffcc30'))
          }
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
        drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
        self.drawable = drawable;
        self._refreshUI(self.uiMode);
      }, 0);
    }, function () {
      self.callbacks.message('Failed to load data');
    });
  };

  PageFormatViewer.prototype._refreshUI = function PageFormatViewer__refreshUI() {
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

  PageFormatViewer.prototype.uiMode = function PageFormatViewer_uiMode(type) {
    if (type === void(0))
      return this._uiMode;
    this._uiMode = type;
    this._refreshUI();
    this.callbacks.uimodeselect && this.callbacks.uimodeselect(this, type);
  };


  PageFormatViewer.prototype.dispose = function PageFormatViewer_dispose() {
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
  };

  $.fn.pageformatviewer = function (options) {
    var aux = this.data('pageformatviewer');

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
      aux = new PageFormatViewer(this[0], _options),
      this.data('pageformatviewer', aux);
    } else if (typeof options == 'string' || options instanceof String) {
      if (options == 'remove') {
        aux.dispose();
        this.data('pageformatviewer', null);
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
})();
