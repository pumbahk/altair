var Seat = _class("Seat", {
  class_props: {
    styles: {
      neutral : {
        shape: Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SEAT),
        label: Util.convertToFashionStyle(CONF.DEFAULT.STYLE.LABEL)
      },
      selected: {
        shape: Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_SEAT),
        label: Util.convertToFashionStyle(CONF.DEFAULT.STYLE.SELECTED_LABEL)
      },
      additional: {
        free: {},
        mouseover: {
          shape: Util.convertToFashionStyle({
            stroke: { color: "#F63", width: 3, pattern: 'solid' }
          }),
        }
      }
    }
  },

  props: {
    id:     null,
    editor: null,
    type:   null,
    floor:  null,
    gate:   null,
    block:  null,
    events: {},
    _status: 'neutral',
    _condition: 'free',
    mata:   null,
    shape:   null,
    original_style: null,
    _mouseoveredSeats: []
  },

  methods: {
    init: function(id, shape, meta, parent, events) {
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

        this.original_style = Util.convertToFashionStyle(this.type.style, true);
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
    },

    stylize: function() {
      var shape_style = _clone(this.constructor.styles[this._status].shape);
      var label_style = _clone(this.constructor.styles[this._status].label);
      var add_shape = this.constructor.styles.additional[this._condition].shape;
      var add_label = this.constructor.styles.additional[this._condition].label;

      if (this._status == 'neutral' && this.original_style)
        shape_style = _clone(this.original_style);

      if (add_shape) {
        if (add_shape.fill) shape_style.fill = add_shape.fill;
        if (add_shape.stroke) shape_style.stroke = add_shape.stroke;
      }
      if (add_label) {
        if (add_label.fill)   label_style.fill = add_label.fill;
        if (add_label.stroke) label_style.stroke = add_label.stroke;
      }

      this.shape.style(shape_style);
      if (this.label) this.label.style(label_style);
    },

    condition: function(cond) {
      switch (cond) {
      case 'mouseover':
      case 'free':
        this._condition = cond;
        this.stylize();
      default:
      }
      return this._condition;
    },

    status: function(st) {
      switch (st) {
      case 'neutral':
      case 'selected':
        this._status = st;
        this.stylize();
        break;
      default:
      }

      return this._status;
    },

    getAdjacency: function() {
      var candidates = this.parent.adjacencies.getCandidates(this.id);
      var adjacency_len = this.parent.adjacencies.length();
      var seats = this.parent.seats;

      outer:
      for (var i=0,l=candidates.length; i<l; i++) {
        var candidate = candidates[i];
        var prev_status = null;
        for (var j=0; j<adjacency_len; j++) {
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
    },

    forEachAdjacency: function(fn) {
      var pair = this.getAdjacency();
      for (var i=0,l=pair.length; i<l; i++) {
        var id = pair[i];
        fn.call(this, this.parent.seats[id], id);
      }
    },

    selected: function() {
      this.forEachAdjacency(function(seat) {
        seat.status('selected');
      });
    },
    neutral: function() {
      this.forEachAdjacency(function(seat) {
        seat.status('neutral');
      });
    },
    mouseover: function() {
      var self = this;
      this.forEachAdjacency(function(seat) {
        seat.condition('mouseover');
        self._mouseoveredSeats.push(seat);
      });
    },
    free: function() {
      for (var i=0,l=this._mouseoveredSeats.length; i<l; i++) {
        this._mouseoveredSeats.shift().condition('free');
      }
    }
  }
});