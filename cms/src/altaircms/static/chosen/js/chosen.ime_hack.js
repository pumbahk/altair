var chosen_ime_hack = function(chosen) {
  var pressed;
  
  chosen.keydown_checker = (function(orig) {
    return function(evt) {
      pressed = -1;
      var stroke = (_ref = evt.which) != null ? _ref : evt.keyCode;
      if (stroke != 13) {
        orig.apply(this, arguments);
      }
    };
  })(chosen.keydown_checker);

  chosen.search_field.bind('keypress.chosen', function(evt) {
    var stroke = (_ref = evt.which) != null ? _ref : evt.keyCode;
    pressed = stroke;
    if (stroke == 13) {
      evt.preventDefault();
    }
  });

  chosen.result_select = (function(orig) {
    return function(evt) {
      var stroke = (_ref = evt.which) != null ? _ref : evt.keyCode;
      if (stroke != 13 || pressed == 13) {
        orig.apply(this, arguments);
      }
    };
  })(chosen.result_select);
};
