var util = require('util.js');
var CONF = require('CONF.js');

function clone(obj) {
  return $.extend({}, obj);
}

function mergeStyle(a, b) {
  return {
    text: (b.text ? b.text: a.text) || null,
    text_color: (b.text_color ? b.text_color: a.text_color) || null,
    fill: (b.fill ? b.fill: a.fill) || null,
    stroke: (b.stroke ? b.stroke: a.stroke) || null
  };
}

function copyShape(shape) {
  if (shape instanceof Fashion.Path) {
    return new Fashion.Path({ points: shape.points(), style: shape.style(), transform: shape.transform() });
  } else if (shape instanceof Fashion.Rect) {
    return new Fashion.Rect({ position: shape.position(), size: shape.size(), transform: shape.transform() });
  }
  return null;
}

var Seat = exports.Seat = function Seat () {
  this.id = null;
  this.editor = null;
  this.type = null;
  this.floor = null;
  this.gate = null;
  this.block = null;
  this.events = {};
  this._styleTypes = [];
  this.mata = null;
  this.shape = null;
  this.originalStyle = null;
  this._highlightedSeats = [];
  this._selected = false;
  this.label = null;
  this._overlays = {};

  this.init.apply(this, arguments);
};

Seat.prototype.init = function Seat_init(id, meta, parent, events) {
  var self    = this;
  this.id     = id;
  this.parent = parent;
  this.meta   = meta;

  this.type = this.parent.stockTypes[meta.stock_type_id];

  this.originalStyle = this.defaultStyle();

  if (events) {
    for (var i in events) {
      (function(i) {
        self.events[i] = function(evt) {
          if (self.parent.dragging || self.parent.animating)
            return;
          events[i].apply(self, arguments);
        };
      }).call(this, i);
    }
  }

  this.refresh();
};

Seat.prototype.defaultStyle = function Seat_defaultStype() {
  var style = CONF.DEFAULT.SEAT_STYLE;

  if (this.shape)
    style = mergeStyle(style, util.convertFromFashionStyle(this.shape.style()));

  if (this.type)
    style = mergeStyle(style, this.type.style);

  return style;
}

Seat.prototype.attach = function Seat_attach(shape) {
  if (this.shape === shape)
    return;
  if (this.shape !== shape)
    this.detach();

  this.shape = shape;
  this.originalStyle = this.defaultStyle();
  this.refresh();
  if (shape)
    shape.addEvent(this.events);
};

Seat.prototype.detach = function Seat_detach(shape) {
  if (!this.shape)
    return;

  if (this.label) {
    this.parent.drawable.erase(this.label);
    this.label = null;
  }
  this.shape.removeEvent();
  this.shape = null;
};

Seat.prototype.stylize = function Seat_stylize() {
  if (!this.shape)
    return;
  var style = this.originalStyle;
  for (var i = 0; i < this._styleTypes.length; i++) {
    var styleType = this._styleTypes[i];
    style = mergeStyle(style, CONF.DEFAULT.AUGMENTED_STYLE[styleType]);
  }
  this.shape.style(util.convertToFashionStyle(style));

  if (style.text) {
    if (!this.label) {
      var p = this.shape.position(),
          s = this.shape.size();
      this.label = this.parent.drawable.draw(
        new Fashion.Text({
          position: {
            x: p.x,
            y: p.y + (s.y * 0.75)
          },
          fontSize: (s.y * 0.75),
          text: style.text,
          style: { fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) }
        })
      );
      this.label.addEvent(this.events);
    } else {
      this.label.text(style.text);
      this.label.style({ fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) });
    }
  } else {
    if (this.label) {
      this.parent.drawable.erase(this.label);
      this.label = null;
    }
  }
};

Seat.prototype.addOverlay = function Seat_addOverlay(value) {
  if (!(value in this._overlays)) {
    if (this.shape) {
      var shape = copyShape(this.shape)
      shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS[value]));
      this._overlays[value] = shape;
      this.parent.drawable.draw(shape);
    }
  }
};

Seat.prototype.removeOverlay = function Seat_removeOverlay(value) {
  var shape = this._overlays[value];
  if (shape !== void(0)) {
    this.parent.drawable.erase(shape);
    delete this._overlays[value];
  }
};

Seat.prototype.addStyleType = function Seat_addStyleType(value) {
  this._styleTypes.push(value);
  this.stylize();
};

Seat.prototype.removeStyleType = function Seat_removeStyleType(value) {
  for (var i = 0; i < this._styleTypes.length;) {
    if (this._styleTypes[i] == value)
      this._styleTypes.splice(i, 1);
    else
      i++;
  }
  this.stylize();
};

Seat.prototype.refreshDynamicStyle = function Seat_refreshDynamicStyle() {
  if (!this.selectable())
    this.addStyleType('unselectable');
  else
    this.removeStyleType('unselectable');
};

Seat.prototype.refresh = function Seat_refresh() {
  this.refreshDynamicStyle();
  this.stylize();
};

Seat.prototype.__selected = function Seat___selected() {
  this.addStyleType('selected');
  this._selected = true;
};

Seat.prototype.__unselected = function Seat___unselected() {
  this.removeStyleType('selected');
  this._selected = false;
};

Seat.prototype.selected = function Seat_selected(value) {
  if (value !== void(0))
    this.parent._select(this, value);
  return this._selected;
};

Seat.prototype.selectable = function Seat_selectable() {
  return !this.parent.callbacks.selectable ||
    this.parent.callbacks.selectable(this.parent, this);
};

/*
 * vim: sts=2 sw=2 ts=2 et
 */
