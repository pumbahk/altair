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
    return new Fashion.Path({ points: shape.points(), style:shape.style() });
  } else if (shape instanceof Fashion.Rect) {
    return new Fashion.Rect({ position: shape.position(), size: shape.size() });
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

Seat.prototype.init = function Seat_init(id, shape, meta, parent, events) {
  var self    = this;
  this.id     = id;
  this.parent = parent;
  this.shape  = shape;
  this.meta   = meta;

  this.type = this.parent.metadata.stock_types ?
      this.parent.metadata.stock_types[meta.stock_type_id]: null;

  var style = CONF.DEFAULT.SEAT_STYLE;
  if (this.type)
    style = mergeStyle(style, this.type.style);

  this.originalStyle = style;

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
    this.shape.addEvent(this.events);
  }

  this.refresh();
};

Seat.prototype.stylize = function Seat_stylize() {
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
    var shape = copyShape(this.shape)
    shape.style(util.convertToFashionStyle(CONF.DEFAULT.OVERLAYS[value]));
    this._overlays[value] = shape;
    this.parent.drawable.draw(shape);
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

var SeatAdjacencies = exports.SeatAdjacencies = function SeatAdjacencies(src) {
  this.tbl = {};
  for (var len in src) {
    this.tbl[len] = this.convertToTable(len, src[len]);
  }
};

SeatAdjacencies.prototype.getCandidates = function SeatAdjacencies_getCandidates(id, length) {
  if (length == 1) return [[id]];
  return this.tbl[length][id] || [];
};

SeatAdjacencies.prototype.convertToTable = function SeatAdjacencies_convertToTable(len, src) {
  var rt = {};

  for (var i = 0, l = src.length; i < l; i++) {
    // sort by string.
    src[i] = src[i].sort();
    for (var j = 0;j < len;j++) {
      var id  =  src[i][j];
      if (!rt[id]) rt[id] = [];
      rt[id].push(src[i]);
    }
  }

  // sort by string-array.
  for (var i in rt) rt[i].sort().reverse();

  return rt;
};

SeatAdjacencies.prototype.lengths = function SeatAdjacencies_lengths() {
  var rt = [1];
  for (var len in this.tbl)
    rt.push(len|0);
  return rt;
};

SeatAdjacencies.prototype.disable = function SeatAdjacencies_disable() {
  if (this.selector) this.selector.attr('disabled', 'disabled');
  this._enable = false;
};

SeatAdjacencies.prototype.enable = function SeatAdjacencies_enable() {
  if (this.selector) this.selector.removeAttr('disabled');
  this._enable = true;
};

/*
// test code
// ad == ad2

var ad = new SeatAdjacencies({"3": [["A1", "A2", "A3"], ["A2", "A3", "A4"], ["A3", "A4", "A5"], ["A4", "A5", "A6"]]});
var ad2 = new SeatAdjacencies({"3": [["A1", "A3", "A2"], ["A2", "A3", "A4"], ["A4", "A3", "A5"], ["A6", "A5", "A4"]]});
console.log(ad);
console.log(ad2);
*/
/*
 * vim: sts=2 sw=2 ts=2 et
 */
