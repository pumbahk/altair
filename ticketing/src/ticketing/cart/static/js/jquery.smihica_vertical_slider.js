(function ($) {
  $.fn.smihica_vertical_slider = function (options_or_key, value) {
    var self = this;
    var initialize = function initialize(options) {
      options = $.extend({
        height: this.height() || 100,
        step: .1,
        button: true,
        onchange: function (pos) {}
      }, options);

      var sliderHeight = options.height;
      var step = options.step;

      var plus, minus, vbar, hbar;

      var cont  = $('<div></div>').addClass("smihica-vertical-slider")
        .append(plus  = $('<div></div>').addClass(options.button ? "smihica-vertical-slider-plus" : "smihica-vertical-slider-cover-top"))
        .append(minus = $('<div></div>').addClass(options.button ? "smihica-vertical-slider-minus" : "smihica-vertical-slider-cover-bottom"))
        .append(vbar  = $('<div></div>').addClass("smihica-vertical-slider-vbar"))
        .append(hbar  = $('<div></div>').addClass("smihica-vertical-slider-hbar"));

      this.append(cont);

      var zoomRatioMin = 0.5;
      var zoomRatioMax = 2.2;
      var hbarMoving = false;
      var minusHeight = minus.height();
      var plusHeight = plus.height();
      var hbarPositionOffset = plusHeight - 8;
      var hbarPositionMax = sliderHeight - plusHeight - minusHeight - 4;
      var lastMouseY = 0;
      var hbarPosition = 0;
      var lastHbarPosition = 0;

      vbar.css({
        'height': (sliderHeight - plusHeight / 2 - minusHeight / 2) + 'px',
        'top': plusHeight / 2 + 'px'
      });
      minus.css('top', (sliderHeight - minusHeight) + 'px');

      var onChanged = function(fn) {
        if (fn !== void(0)) options.onchange = fn;
        return options.onchange;
      };

      var normalizedPosition = function normalizedPosition(pos, disableCallback) {
        if (pos === void(0))
          return 1 - hbarPosition / hbarPositionMax;
        else
          setPositionHbar((1 - pos) * hbarPositionMax, disableCallback);
      }

      var setPositionHbar = function setPositionHbar(pos, disableCallback) {
        pos = Math.min(Math.max(pos, 0), hbarPositionMax);
        hbar.css('top', pos + hbarPositionOffset + 'px');
        if (hbarPosition != pos) {
          hbarPosition = pos;
          if (!disableCallback)
            options.onchange.call(self, normalizedPosition());
        }
        return pos;
      }

      var getPageY = function getPageY(e) {
        return e.pageY === void(0) ? e.originalEvent.pageY: e.pageY;
      };

      var moveHandler = function moveHandler(e) {
        if (hbarMoving) {
          var dist = getPageY(e) - lastMouseY;
          setPositionHbar(lastHbarPosition + dist);
        }
        return false;
      }

      var upHandler = function upHandler(e) {
        hbarMoving = false;
        $(document).unbind("mousemove touchmove", moveHandler);
        $(document).unbind("mouseup touchend", upHandler);
        return false;
      }

      hbar.bind('mousedown touchstart', function(e) {
        hbarMoving = true;
        lastHbarPosition = hbarPosition;
        lastMouseY =  getPageY(e);
        $(document).bind('mousemove touchmove', moveHandler);
        $(document).bind('mouseup touchend', upHandler);
        return false;
      });
      vbar.bind('click', function(e) {
        setPositionHbar(e.offsetY);
        lastMouseY = e.pageY;
      });
      if (options.button) {
        plus.bind('click touchstart', function(e) {
          setPositionHbar(hbarPosition - step * hbarPositionMax);
          return false;
        });
        minus.bind('click touchstart', function(e) {
          setPositionHbar(hbarPosition + step * hbarPositionMax);
          return false;
        });
      }

      this.data('vertical_slider', { position: normalizedPosition, change: onChanged });

      setPositionHbar(hbarPositionMax);
    }

    var accessor = function accessor(key, value) {
      var data = this.data('vertical_slider');
      return data[key](value);
    }

    if (options_or_key === void(0))
      options_or_key = {};

    if (typeof options_or_key == 'object') {
      initialize.call(this, options_or_key);
      return this;
    } else if (typeof options_or_key == 'string' || options_or_key instanceof String) {
      return accessor.call(this, options_or_key, value);
    }
  };
})(jQuery);

/*
 * vim: sts=2 sw=2 ts=2 et
 */
