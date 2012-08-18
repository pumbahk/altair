var util = require('util.js');
var CONF = require('CONF.js');
var models = require('models.js');

var Seat = exports.Seat = Backbone.Model.extend({
  defaults: {
    shape: null,
    model: null,
    events: null
  },

  label: null,
  styleTypes: null,

  initialize: function Seat_initialize(attrs, options) {
    var self = this;

    this.styleTypes = [];

    function selectableChanged() {
      if (self.get('model').selectable())
        self.addStyleType('unselectable');
      else
        self.removeStyleType('unselectable');
    };
    
    function selectedChanged() {
      if (this.get('selected'))
        self.addStyleType('selected');
      else
        self.removeStyleType('selected');
    }

    function onStockChanged() {
      var prevModel = self.get('model').previous('stock');
      if (prevModel)
        prevModel.off('change:style', onStockChanged);
      var model = self.get('model').get('stock');
      if (model)
        model.on('change:style', onStockChanged);
      self._refreshStyle();
    };

    function onModelChange() {
      var prevModel = self.previous('model');
      var model = self.get('model');
      if (prevModel) {
        model.off('change:venue', selectableChanged);
        model.off('change:selectable', selectableChanged);
        model.off('change:selected', selectedChanged);
        model.off('change:stock', onStockChanged);
      }
      if (model) {
        model.on('change:venue', selectableChanged);
        model.on('change:selectable', selectableChanged);
        model.on('change:selected', selectedChanged);
        model.on('change:stock', onStockChanged);
      }
    }

    function onShapeChange(init) {
      var prev = self.previous('shape');
      var events = self.get('events');
      if (events) {
        if (prev) {
          for (var eventKind in events) {
            if (events[eventKind])
              prev.removeEvent(eventKind, events[eventKind]);
          }
          if (self.label) {
            for (var eventKind in events) {
              if (events[eventKind])
                self.label.removeEvent(eventKind, events[eventKind]);
            }
          }
        }
        var new_ = self.get('shape');
        new_.addEvent(events);
      }
      if (!init)
        self._refreshStyle();
    }

    function onEventsChange() {
      var shape = self.get('shape')
      if (shape) {
        var prev = self.previous('events');
        var new_ = self.get('events');
        if (prev) {
          for (var eventKind in prev) {
            if (prev[eventKind])
              shape.removeEvent(eventKind, prev[eventKind]);
          }
          if (self.label) {
            for (var eventKind in prev) {
              if (prev[eventKind])
                self.label.removeEvent(eventKind, prev[eventKind]);
            }
          }
        }
        if (new_) {
          shape.addEvent(new_);
          if (self.label)
            self.label.addEvent(new_);
        }
      }
    }

    this.on('change:model', onModelChange);
    this.on('change:shape', onShapeChange);
    this.on('change:events', onEventsChange);

    // The following line is kind of hack; there's no way to
    // ensure change events to get invoked correctly on the
    // initialization.
    this._previousAttributes = {};
    onModelChange();
    onShapeChange(true);
    onEventsChange();
    onStockChanged();
  },

  _refreshStyle: function Seat__refreshStyle() {
    var model = this.get('model');
    var style = model && model.get('stock').get('style') || {};
    style = util.mergeStyle(style, CONF.DEFAULT.SEAT_STATUS_STYLE[model.get('status')]);
    var shape = this.get('shape');
    if (!shape)
      return;
    for (var i = 0; i < this.styleTypes.length; i++) {
      var styleType = this.styleTypes[i];
      style = util.mergeStyle(style, CONF.DEFAULT.AUGMENTED_STYLE[styleType]);
    }
    shape.style(util.convertToFashionStyle(style));
    var styleText = style.text || model.get('seat_no');
    if (style.text && $.inArray('highlighted', this.styleTypes) != -1) {
      styleText = model.get('seat_no');
    }
    if (!this.label) {
      var p = shape.position(),
          s = shape.size();
      this.label = shape.drawable.draw(
        new Fashion.Text({
          position: {
            x: p.x + (s.x * 0.10),
            y: p.y + (s.y * 0.75)
          },
          fontSize: (s.y * 0.75),
          text: styleText,
          style: { fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) }
        })
      );
      this.label.addEvent(this.get('events'));
    } else {
      this.label.text(styleText);
      this.label.style({ fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) });
    }
  },

  addStyleType: function Seat_addStyleType(value) {
    this.styleTypes.push(value);
    this._refreshStyle();
  },

  removeStyleType: function Seat_removeStyleType(value) {
    for (var i = 0; i < this.styleTypes.length;) {
      if (this.styleTypes[i] == value)
        this.styleTypes.splice(i, 1);
      else
        i++;
    }
    this._refreshStyle();
  }
});

/*
 * vim: sts=2 sw=2 ts=2 et
 */
