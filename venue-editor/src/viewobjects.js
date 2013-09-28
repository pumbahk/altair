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

    function onSelectableChanged() {
      if (self.get('model').selectable()) {
        self.removeStyleType('unselectable');
      } else if (!self.get('model').get('sold')) {
        self.addStyleType('unselectable');
      }
    }

    function onSelectedChanged() {
      if (self.get('model').get('selected'))
        self.addStyleType('selected');
      else
        self.removeStyleType('selected');
    }

    function onStockChanged() {
      self._refreshStyle();
    }

    function onModelChange() {
      var prevModel = self.previous('model');
      var model = self.get('model');
      if (prevModel) {
        model.off('change:selectable', onSelectableChanged);
        model.off('change:selected', onSelectedChanged);
        model.off('change:stock', onStockChanged);
      }
      if (model) {
        model.on('change:selectable', onSelectableChanged);
        model.on('change:selected', onSelectedChanged);
        model.on('change:stock', onStockChanged);
      }
    }

    function onShapeChange() {
      var prev = self.previous('shape');
      var new_ = self.get('shape');
      if (prev != new_) {
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
          new_.addEvent(events);
        }
      }
      self._refreshStyle();
    }

    function onEventsChange() {
      var shape = self.get('shape');
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
    onSelectableChanged();
    onModelChange();
    onEventsChange();
    onShapeChange();
  },

  _refreshStyle: function Seat__refreshStyle() {
    var model = this.get('model');
    var stock = model && model.get('stock');
    var style = stock && stock.get('style') || CONF.DEFAULT.SEAT_STYLE;
    var defaultStyle = CONF.DEFAULT.SEAT_STATUS_STYLE[model ? model.get('status'): 0];
    if (defaultStyle)
      style = util.mergeStyle(style, defaultStyle);
    var shape = this.get('shape');
    if (!shape)
      return;
    for (var i = 0; i < this.styleTypes.length; i++) {
      var styleType = this.styleTypes[i];
      var augmentedStyle = CONF.DEFAULT.AUGMENTED_STYLE[styleType];
      if (augmentedStyle)
        style = util.mergeStyle(style, augmentedStyle);
    }
    shape.style(util.convertToFashionStyle(style));
    var styleText = style.text || model.get('seat_no');
    if (!this.label) {
      var p = shape.position(),
          t = shape.transform(),
          s = shape.size();
      var text = new Fashion.Text({
          position: {
			      x: p.x + (s.x * (0.05 + (styleText.length==1 ? 0.2 : 0.0))),
            y: p.y + (s.y * 0.75)
          },
          fontSize: style.text ? s.y * 0.5 : (s.x*1.2/Math.max(2, styleText.length)),
          text: styleText,
          style: { fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)), cursor: 'default' }
      });
      if (t) {
        text.transform(t);
      }
      this.label = shape.drawable.draw(text);
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
