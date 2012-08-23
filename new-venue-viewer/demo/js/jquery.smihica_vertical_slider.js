(function ($) {
$.fn.smihica_vertical_slider = function (options_or_key, value) {
  var self = this;

  function initialize(options) {
    options = $.extend({
      height: this.height() || 40,
      step: .1,
      onchange: function (pos) {}
    }, options);

    var sliderHeight = options.height;
    var step = options.step;

    var plus, minus, vbar, har;

    var cont  = $('<div class="smihica-vertical-slider"></div>')
      .append(plus  = $('<div class="smihica-vertical-slider-plus"></div>'))
      .append(minus = $('<div class="smihica-vertical-slider-minus"></div>'))
      .append(vbar  = $('<div class="smihica-vertical-slider-vbar"></div>'))
      .append(hbar  = $('<div class="smihica-vertical-slider-hbar"></div>'));
    this.replaceWith(cont);

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

    function getNormalizedPosition() {
      return 1 - hbarPosition / hbarPositionMax;
    }

    function setPositionHbar(pos, disableCallback) {
      pos = Math.min(Math.max(pos, 0), hbarPositionMax);
      hbar.css('top', pos + hbarPositionOffset + 'px');
      if (hbarPosition != pos) {
        hbarPosition = pos;
        if (!disableCallback)
          options.onchange && options.onchange.call(self, getNormalizedPosition());
      }
      return pos;
    }

    function moveHandler(e) {
      if (hbarMoving) {
        var dist = e.pageY - lastMouseY;
        setPositionHbar(lastHbarPosition + dist);
      }
    }

    function upHandler(e) {
      hbarMoving = false;
      $(document).unbind("mousemove", moveHandler);
      $(document).unbind("mouseup", upHandler);
    }

    hbar.mousedown(function(e) {
      hbarMoving = true;
      lastHbarPosition = hbarPosition;
      lastMouseY = e.pageY;

      $(document).mousemove(moveHandler);
      $(document).mouseup(upHandler);
    });

    vbar.click(function(e) {
      setPositionHbar(e.offsetY);
      lastMouseY = e.pageY;
    });

    plus.click(function(e) {
      setPositionHbar(hbarPosition - step * hbarPositionMax);
    });
    minus.click(function(e) {
      setPositionHbar(hbarPosition + step * hbarPositionMax);
    });

    this.data('smihica_vertical_slider', { position: getNormalizedPosition });

    setPositionHbar(hbarPositionMax);
  }

  function accessor(key, value) {
    var data = this.data('smihica_vertical_slider');
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
