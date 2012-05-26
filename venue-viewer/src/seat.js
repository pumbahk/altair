var util = require('util.js');
var CONF = require('CONF.js');

function clone(obj) {
  return $.extend({}, obj); 
}

var default_styles = {
  styles: {
    neutral : {
      shape: util.convertToFashionStyle(CONF.DEFAULT.STYLE.SEAT),
      label: util.convertToFashionStyle(CONF.DEFAULT.STYLE.LABEL)
    },
    selected: {
      shape: util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_SEAT),
      label: util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_LABEL)
    }
  },
  additional: {
    free: {
      shape: { fill: null, stroke: null },
      label: { fill: null, stroke: null }
    },
    mouseover: {
      shape: util.convertToFashionStyle({
        fill: null,
        stroke: { color: "#F63", width: 3, pattern: 'solid' }
      }),
      label: { fill: null, stroke: null }
    }
  }
};

var Seat = exports.Seat = function Seat () {
  this.id = null;
  this.editor = null;
  this.type = null;
  this.floor = null;
  this.gate = null;
  this.block = null;
  this.events = {};
  this._status = 'neutral';
  this._condition = 'free';
  this.mata = null;
  this.shape = null;
  this.original_style = null;
  this._mouseoveredSeats = [];

  this.init.apply(this, arguments);
};

Seat.prototype.init = function Seat_init(id, shape, meta, parent, events) {
  var self    = this;
  this.id     = id;
  this.parent = parent;
  this.shape  = shape;
  this.meta   = meta;

  this.type = this.parent.metadata.stock_types[meta.stock_type_id];

  if (this.type) {
    if (this.type.style.text) {

      var style = this.type.style,
      p = this.shape.position(),
      s = this.shape.size();

      this.label = this.parent.drawable.draw(
        new Fashion.Text({
          position: {
            x: p.x,
            y: p.y + (s.y * 0.75),
          },
          fontSize: (s.y * 0.75),
          text: style.text
        })
      );
    }

    this.original_style = util.convertToFashionStyle(this.type.style, true);
  }

  if (events) {
    for (var i in events) {
      (function(i) {
        self.events[i] = function(evt) {
          events[i].apply(self, arguments);
        };
      }).call(this, i);
    }
    this.shape.addEvent(this.events);
  }

  this.stylize();
};

Seat.prototype.stylize = function Seat_stylize() {
  var shape_style = clone(default_styles.styles[this._status].shape);
  var label_style = clone(default_styles.styles[this._status].label);
  var add_shape = default_styles.additional[this._condition].shape;
  var add_label = default_styles.additional[this._condition].label;

  if (this._status == 'neutral' && this.original_style)
    shape_style = clone(this.original_style);

  if (add_shape.fill) shape_style.fill = add_shape.fill;
  if (add_shape.stroke) shape_style.stroke = add_shape.stroke;
  if (add_label.fill)   label_style.fill = add_label.fill;
  if (add_label.stroke) label_style.stroke = add_label.stroke;

  this.shape.style(shape_style);
  if (this.label) this.label.style(label_style);
};

Seat.prototype.condition = function Seat_condition(cond) {
  switch (cond) {
  case 'mouseover':
  case 'free':
    this._condition = cond;
    this.stylize();
  default:
  }
  return this._condition;
};

Seat.prototype.status = function Seat_status(st) {
  switch (st) {
  case 'neutral':
  case 'selected':
    this._status = st;
    this.stylize();
    break;
  default:
  }

  return this._status;
};

Seat.prototype.getAdjacency = function Seat_getAdjacency() {
  var candidates = this.parent.seatAdjacencies.getCandidates(this.id, this.parent.adjacencyLength());
  var seats = this.parent.seats;

  outer:
  for (var i = 0,l = candidates.length; i < l; i++) {
    var candidate = candidates[i];
    var prev_status = null;
    for (var j = 0; j < candidate.length; j++) {
      var id = candidate[j];
      var seat = seats[id];
      if (prev_status && prev_status !== seat.status()) {
        // if statuses of all Seats in this candidate are not same, go next candidate.
        continue outer;
      }
      prev_status = seat.status();
    }
    return candidate;
  }

  return [];
};

Seat.prototype.forEachAdjacency = function Seat_forEachAdjacency(fn) {
  var pair = this.getAdjacency();
  for (var i = 0,l = pair.length; i < l; i++) {
    var id = pair[i];
    fn.call(this, this.parent.seats[id], id);
  }
};

Seat.prototype.selected = function Seat_selected() {
  this.forEachAdjacency(function(seat) {
    seat.status('selected');
  });
};

Seat.prototype.neutral = function Seat_neutral() {
  this.forEachAdjacency(function(seat) {
    seat.status('neutral');
  });
};

Seat.prototype.mouseover = function Seat_mouseover() {
  var self = this;
  this.forEachAdjacency(function(seat) {
    seat.condition('mouseover');
    self._mouseoveredSeats.push(seat);
  });
};

Seat.prototype.free = function Seat_free() {
  var mouseoveredSeats = this._mouseoveredSeats;
  this._mouseoveredSeats = [];
  for (var i = 0, l = mouseoveredSeats.length; i < l; i++) {
    mouseoveredSeats[i].condition('free');
  }
}

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
