(function (jQuery, I18n) {
var __LIBS__ = {};
__LIBS__['K_4LN8NH7HG0S611'] = (function (exports) { (function () { 

/************** CONF.js **************/
exports.DEFAULT = {
  ZOOM_RATIO: 0.8,
  SHAPE_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#fff')),
    stroke: new Fashion.Stroke(new Fashion.Color("#000"), 1)
  },

  TEXT_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#000')),
    stroke: null
  },

  VENUE_STYLE: {
    fill: new Fashion.FloodFill(new Fashion.Color('#FFCB3F')),
    stroke: new Fashion.Stroke(new Fashion.Color('#5ABECD'), 1)
  },

  MASK_STYLE: {
    fill:   new Fashion.FloodFill(new Fashion.Color("#0064ff80")),
    stroke: new Fashion.Stroke(new Fashion.Color("#0080FF"), 2)
  },

  SEAT_STYLE: {
    text_color: "#000",
    fill:   { color: "#fff" },
    stroke: { color: "#000", width: 1 }
  },

  AUGMENTED_STYLE: {
    selected: {
      text_color: "#FFF",
      fill:   { color: "#009BE1" }
    },
    highlighted: {
      fill: null,
      stroke: { color: "#F63", width: 3, pattern: 'solid' }
    },
    unselectable: {
      text_color: "#888",
      fill:   { color: "#eee" },
      stroke: { color: "#ccc", width: 1 }
    }
  }
};
 })(); return exports; })({});
__LIBS__['aD2O0CY0MX_9UPWO'] = (function (exports) { (function () { 

/************** translations.js **************/


/************** en.js **************/
exports.en = {
  altair: {
    venue_editor: {
      unassigned: "Unassigned",
      quantity_cannot_be_negative: "Quantity cannot be negative"
    }
  } 
};


/************** ja.js **************/
exports.ja = {
  altair: {
    venue_editor: {
      unassigned: "未割当",
      quantity_cannot_be_negative: "在庫数は0より大きい数にしてください"
    }
  } 
};
 })(); return exports; })({});
__LIBS__['vCU57LCSUMM0OWU0'] = (function (exports) { (function () { 

/************** util.js **************/
exports.eventKey = function Util_eventKey(e) {
  var shift, ctrl;
  // Mozilla
  if (e != null) {
    keycode = e.which;
    ctrl    = typeof e.modifiers == 'undefined' ? e.ctrlKey : e.modifiers & Event.CONTROL_MASK;
    shift   = typeof e.modifiers == 'undefined' ? e.shiftKey : e.modifiers & Event.SHIFT_MASK;

  }
  // ie
  else {
    keycode = event.keyCode;
    ctrl    = event.ctrlKey;
    shift   = event.shiftKey;

  }

  keychar = String.fromCharCode(keycode).toUpperCase();

  return {
    ctrl:    (!!ctrl) || keycode === 17,
    shift:   (!!shift) || keycode === 16,
    keycode: keycode,
    keychar: keychar
  };
};

exports.convertToFashionStyle = function Util_convertToFashionStyle(style, gradient) {
  var filler = function(color) {
    if (gradient) return new Fashion.LinearGradientFill([[0, new Fashion.Color("#fff")], [1, new Fashion.Color(color || "#fff")]], .125);
    return new Fashion.FloodFill(new Fashion.Color(color || "#000"));
  };

  return {
    "fill": style.fill ? filler(style.fill.color): null,
    "stroke": style.stroke ? new Fashion.Stroke((style.stroke.color || "#000") + " " + (style.stroke.width ? style.stroke.width: 1) + " " + (style.stroke.pattern || "")) : null
  };
};

exports.allAttributes = function Util_allAttributes(el) {
  var rt = {}, attrs=el.attributes, attr;
  for (var i=0, l=attrs.length; i<l; i++) {
    attr = attrs[i];
    rt[attr.nodeName] = attr.nodeValue;
  }
  return rt;
};  

exports.makeHitTester = function Util_makeHitTester(a) {
  var pa = a.position(),
  sa = a.size(),
  ax0 = pa.x,
  ax1 = pa.x + sa.x,
  ay0 = pa.y,
  ay1 = pa.y + sa.y;

  return function(b) {
    var pb = b.position(),
    sb = b.size(),
    bx0 = pb.x,
    bx1 = pb.x + sb.x,
    by0 = pb.y,
    by1 = pb.y + sb.y;

    return ((((ax0 < bx0) && (bx0 < ax1)) || (( ax0 < bx1) && (bx1 < ax1)) || ((bx0 < ax0) && (ax1 < bx1))) && // x
            (((ay0 < by0) && (by0 < ay1)) || (( ay0 < by1) && (by1 < ay1)) || ((by0 < ay0) && (ay1 < by1))));  // y
  }
};

var AsyncDataWaiter = exports.AsyncDataWaiter = function AsyncDataWaiter(options) {
  this.store = {};
  for (var i = 0; i < options.identifiers.length; i++) {
    this.store[options.identifiers[i]] = void(0);
  }
  this.after = options.after;
};

AsyncDataWaiter.prototype.charge = function AsyncDataWaiter_charge(id, data) {
  this.store[id] = data;
  for (var i in this.store) {
    if (this.store[i] === void(0))
      return;
  }
  // fire!! if all data has come.
  this.after.call(window, this.store);
};

exports.mergeStyle = function mergeStyle(a, b) {
  return {
    text: (b.text ? b.text: a.text) || null,
    text_color: (b.text_color ? b.text_color: a.text_color) || null,
    fill: (b.fill ? b.fill: a.fill) || null,
    stroke: (b.stroke ? b.stroke: a.stroke) || null
  };
};
 })(); return exports; })({});
__LIBS__['O73W5HM407XSQ9WC'] = (function (exports) { (function () { 

/************** identifiableset.js **************/
var IdentifiableSet = exports.IdentifiableSet = function IdentifiableSet(options) {
  this.idAttribute = options && options.idAttribute || 'id';
  this.items = {};
  this.length = 0;
};

IdentifiableSet.prototype.add = function IdentifiableSet_add(item) {
  var id = item[this.idAttribute];
  if (!(id in this.items)) {
    this.items[id] = item;
    this.length++;
    return true;
  } else {
    return false;
  }
};

IdentifiableSet.prototype.remove = function IdentifiableSet_remove(item) {
  var id = item[this.idAttribute];
  if (id in this.items) {
    delete this.items[id];
    this.length--;
    return true;
  } else {
    return false;
  }
};

IdentifiableSet.prototype.contains = function IdentifiableSet_contains(item) {
  return item[this.idAttribute] in this.items;
};

IdentifiableSet.prototype.clear = function IdentifiableSet_clear() {
  this.items = {};
  this.length = 0;
};

IdentifiableSet.prototype.each = function IdentifiableSet_each(f) {
  for (var id in this.items)
    f(this.items[id]);
};

/*
 * vim: sts=2 sw=2 ts=2 et
 */
 })(); return exports; })({});
__LIBS__['JC7M69EN5_PGPH3L'] = (function (exports) { (function () { 

/************** models.js **************/
var util = __LIBS__['vCU57LCSUMM0OWU0'];
var CONF = __LIBS__['K_4LN8NH7HG0S611'];
var IdentifiableSet = __LIBS__['O73W5HM407XSQ9WC'].IdentifiableSet;

var VenueItemCollectionMixin = {
  venue: null,

  initialize: function VenueItemCollectionMixin_initialize(models, options) {
    Backbone.Collection.prototype.initialize.apply(this, arguments);
    this.venue = options.venue;
  },

  _prepareModel: function VenueItemCollectionMixin__prepareModel(model, options) {
    model = Backbone.Collection.prototype._prepareModel.call(this, model, options);
    if (!model)
      return model;
    model.set('venue', this.venue);
    return model;
  }
};

var Venue = exports.Venue = function Venue() {
  this.initialize.apply(this, arguments);
};

_.extend(Venue.prototype, Backbone.Events);

Venue.prototype.initialize = function Venue_initialize(initialData, options) {
  initialData = initialData || { seats: {}, stock_types: [], stock_holders: [] };
  var stockTypes = new StockTypeCollection(null, { venue: this });
  var stockHolders = new StockHolderCollection(null, { venue: this });
  var stocks = new StockCollection(null, { venue: this });
  var seats = new SeatCollection(null, { venue: this });
  var perAttributeSeatSet = {};
  var perStockSeatSet = {};
  var perStockHolderStockMap = {};
  var perStockTypeStockMap = {};
  stockTypes.add({
    id: "",
    name: I18n ? I18n.t("altair.venue_editor.unassigned"): "Unassigned",
    isSeat: true,
    quantityOnly: false,
    quantity: 0,
    style: {}
  });
  for (var i = 0; i < initialData.stock_types.length; i++) {
    var stockTypeDatum = initialData.stock_types[i];
    stockTypes.add({
      id: stockTypeDatum.id,
      name: stockTypeDatum.name,
      isSeat: stockTypeDatum.is_seat,
      quantityOnly: stockTypeDatum.quantity_only,
      quantity: stockTypeDatum.quantity,
      style: stockTypeDatum.style
    });
  }
  stockHolders.add({
    id: "",
    name: I18n ? I18n.t("altair.venue_editor.unassigned"): "Unassigned",
    style: {}
  });
  for (var i = 0; i < initialData.stock_holders.length; i++) {
    var stockHolderDatum = initialData.stock_holders[i];
    stockHolders.add({
      id: stockHolderDatum.id,
      name: stockHolderDatum.name,
      style: stockHolderDatum.style
    });
  }
  function normalizedId(id) { return id === null ? "": "" + id; }
  for (var i = 0; i < initialData.stocks.length; i++) {
    var stockDatum = initialData.stocks[i];
    var stockHolder = stockHolders.get(normalizedId(stockDatum.stock_holder_id));
    var stockType = stockTypes.get(normalizedId(stockDatum.stock_type_id));
    var stock = new Stock({
      id: stockDatum.id,
      stockHolder: stockHolder,
      stockType: stockType,
      assigned: stockDatum.assigned,
      available: stockDatum.available
    });
    stocks.push(stock);
    {
      var map = perStockHolderStockMap[stockHolder.id];
      if (!map)
        map = perStockHolderStockMap[stockHolder.id] = {};
      map[stockType.id] = stock;
    }
    {
      var map = perStockTypeStockMap[stockType.id];
      if (!map)
        map = perStockTypeStockMap[stockType.id] = {};
      map[stockHolder.id] = stock;
    }
    stock.on('change:assigned', function () {
      this.get('stockHolder').recalculateQuantity();
      this.get('stockType').recalculateQuantity();
    });
    stock.on('change:stockHolder change:stockType', function () {
      var prevStockHolderId = this.previous('stockHolder').id;
      var newStockHolderId = this.get('stockHolder').id;
      var prevStockTypeId = this.previous('stockType').id;
      var newStockTypeId = this.get('stockType').id;
      delete perStockHolderStockMap[prevStockHolderId][prevStockTypeId];
      delete perStockTypeStockMap[prevStockTypeId][prevStockHolderId];
      perStockHolderStockMap[newStockHolderId][newStockTypeId] = this;
      perStockTypeStockMap[newStockTypeId][newStockHolderId] = this;
    });
  }
  _.each(Seat.styleProviderAttributes, function (name) {
    perAttributeSeatSet[name] = {};
  });
  for (var id in initialData.seats) {
    var seatDatum = initialData.seats[id];
    var seat = new Seat({
      id: seatDatum.id,
      stock: stocks.get(seatDatum.stock_id),
      attrs: seatDatum.attrs,
      areas: seatDatum.areas
    });
    seats.push(seat);
    {
      var attrs = seat.get('attrs');
      for (name in attrs) {
        var set = perAttributeSeatSet[name];
        if (!set)
          set = perAttributeSeatSet[name] = new IdentifiableSet();
        set.add(seat);
      }
    }
    {
      var stock = seat.get('stock');
      var set = perStockSeatSet[stock.id];
      if (!set)
        set = perStockSeatSet[stock.id] = new IdentifiableSet();
      set.add(seat);
      seat.on('change:stock', function () {
        this.set('edited', true);
        var prev = this.previous('stock');
        var new_ = this.get('stock');
        if (prev != new_) {
          if (prev) {
            perStockSeatSet[prev.id].remove(this);
            if (prev.has('assigned')) {
              prev.set('edited', true);
              prev.set('assigned', perStockSeatSet[prev.id].length);
            }
          }
          if (new_) {
            perStockSeatSet[new_.id].add(this);
            if (new_.has('assigned')) {
              new_.set('edited', true);
              new_.set('assigned', perStockSeatSet[new_.id].length);
            }
          }
        }
      });
    }
  }
  this.stockHolders = stockHolders;
  this.stockTypes = stockTypes;
  this.stocks = stocks;
  this.seats = seats;
  this.perAttributeSeatSet = perAttributeSeatSet;
  this.perStockSeatSet = perStockSeatSet;
  this.perStockHolderStockMap = perStockHolderStockMap;
  this.perStockTypeStockMap = perStockTypeStockMap;
  this.callbacks = options && options.callbacks ?
                     _.clone(options.callbacks):
                     {};
};

Venue.prototype.setCallback = function Venue_setCallback(name, value) {
  this.callbacks[name] = value;
  this.trigger('change:' + name);
};

Venue.prototype.isSelectable = function Venue_isSelectable(seat) {
  return !this.callbacks || !this.callbacks.selectable ||
         this.callbacks.selectable.call(this, seat);
};

Venue.prototype.toJSON = function Venue_toJSON () {
  var seatData = [];
  this.seats.each(function (seat) {
    if (seat.get('edited')) {
      seatData.push({
        id: seat.id,
        stock_id: seat.get('stock').id
      });
    }
  });

  var stockData = [];
  this.stocks.each(function (stock) {
    if (stock.get('edited')) {
      stockData.push({
        id: stock.get('id'),
        quantity: stock.get('assigned')
      });
    }
  });

  return {
    seats:seatData,
    stocks:stockData
  };
};

var ProvidesStyle = exports.ProvidesStyle = Backbone.Model.extend({
  venue: null,

  defaults: {
    style: {
      text: null,
      text_color: null,
      stroke: {
        color: null,
        width: null,
        pattern: null,
      },
      fill: {
        color: null
      }
    }
  }
});

var StockType = exports.StockType = ProvidesStyle.extend({
  defaults: {
    id: null,
    name: '',
    isSeat: false,
    quantityOnly: false,
    assigned: 0,
    available: 0
  },

  keyedStocks: function StockType_stocks() {
    return this.collection.venue.perStockTypeStockMap[this.id];
  },

  recalculateQuantity: function StockType_recalculateQuantity() {
    var keyedStocks = this.keyedStocks();
    var assigned = 0, available = 0;
    for (var id in keyedStocks) {
      assigned += keyedStocks[id].get('assigned'); 
      available += keyedStocks[id].get('available');
    }
    this.set('assigned', assigned);
    this.set('available', available);
  }
});

var StockHolder = exports.StockHolder = ProvidesStyle.extend({
  defaults: {
    id: null,
    name: '',
    assigned: 0,
    available: 0
  },

  validate: function (attrs) {
    if (attrs.quantity < 0) {
      return I18n ?
        I18n.t('altair.venue_editor.quantity_cannot_be_negative'):
        "Quantity cannot be negative";
    }
  },

  keyedStocks: function StockHolder_stocks() {
    return this.collection.venue.perStockHolderStockMap[this.id];
  },

  recalculateQuantity: function StockHolder_recalculateQuantity() {
    var keyedStocks = this.keyedStocks();
    var assigned = 0, available = 0;
    for (var id in keyedStocks) {
      assigned += keyedStocks[id].get('assigned'); 
      available += keyedStocks[id].get('available');
    }
    this.set('assigned', assigned);
    this.set('available', available);
  }
});

var Stock = exports.Stock = Backbone.Model.extend({
  idAttribute: "id",

  defaults: {
    stockHolder: null,
    stockType: null,
    assigned: 0,
    available: 0,
    style: CONF.DEFAULT.SEAT_STYLE,
    edited: false
  },

  _refreshStyle: function Stock__refreshStyle() {
    var self = this;
    var style = CONF.DEFAULT.SEAT_STYLE;
    _.each(Stock.styleProviderAttributes, function (name) {
      var styleProvider = self.get(name);
      if (styleProvider)
        style = util.mergeStyle(style, styleProvider.get('style'));
    });
    this.set('style', style);
  },

  initialize: function Stock_initialize() {
    var self = this;

    var refreshStyleCallback = function refreshStyleCallback() {
      self._refreshStyle();
    };

    var styleProviderAttrChanged = {};
    _.each(Stock.styleProviderAttributes, function (name) {
      styleProviderAttrChanged[name] = function () {
        var prevAttr = this.previous(name);
        if (prevAttr)
          prevAttr.off('change:style', refreshStyleCallback);
        var newAttr = this.get(name);
        if (newAttr)
          newAttr.on('change:style', refreshStyleCallback);
        this._refreshStyle();
      };
      self.on('change:' + name, styleProviderAttrChanged[name]);
    });

    this._refreshStyle();
  }
}, {
  styleProviderAttributes: [ 'stockHolder', 'stockType' ]
});

var Seat = exports.Seat = Backbone.Model.extend({
  idAttribute: 'id',

  defaults: {
    id: null,
    venue: null,
    stock: null,
    selectable: true,
    selected: false,
    areas: [],
    edited: false
  },

  validate: function (attrs, options) {
    if (attrs['selected'] && !this.selectable())
      return 'Seat ' + this.id + ' is not selectable';
  },

  selectable: function Seat_selectable() {
    var venue = this.get('venue');
    return this.get('selectable') && (!venue || venue.isSelectable(this));
  }
});

var SeatCollection = exports.SeatCollection = Backbone.Collection.extend(_.extend({ model: Seat }, VenueItemCollectionMixin));
var StockTypeCollection = exports.StockTypeCollection = Backbone.Collection.extend(_.extend({ model: StockType }, VenueItemCollectionMixin));
var StockHolderCollection = exports.StockHolderCollection = Backbone.Collection.extend(_.extend({ model: StockHolder }, VenueItemCollectionMixin));
var StockCollection = exports.StockCollection = Backbone.Collection.extend(_.extend({ model: Stock }, VenueItemCollectionMixin));

var SeatAdjacencies = exports.SeatAdjacencies = function SeatAdjacencies(src) {
  this.tbl = {};
  for (var i = 0; i < src.length; i++) {
    var len = src[i].count;
    this.tbl[len] = this.convertToTable(len, src[i].set);
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
 })(); return exports; })({});
__LIBS__['pTMHQJL2QM3RZGVH'] = (function (exports) { (function () { 

/************** viewobjects.js **************/
var util = __LIBS__['vCU57LCSUMM0OWU0'];
var CONF = __LIBS__['K_4LN8NH7HG0S611'];
var models = __LIBS__['JC7M69EN5_PGPH3L'];

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

    function stockChanged() {
      self._refreshStyle();
    };

    function onModelChange() {
      var prevModel = self.previous('model');
      var model = self.get('model');
      if (prevModel) {
        model.off('change:venue', selectableChanged);
        model.off('change:selectable', selectableChanged);
        model.off('change:selected', selectedChanged);
        model.off('change:stock', stockChanged);
      }
      if (model) {
        model.on('change:venue', selectableChanged);
        model.on('change:selectable', selectableChanged);
        model.on('change:selected', selectedChanged);
        model.on('change:stock', stockChanged);
      }
    }

    function onShapeChange() {
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
    onShapeChange();
    onEventsChange();
  },

  _refreshStyle: function Seat__refreshStyle() {
    var model = this.get('model');
    var style = model && model.get('stock').get('style') || {};
    var shape = this.get('shape');
    if (!shape)
      return;
    for (var i = 0; i < this.styleTypes.length; i++) {
      var styleType = this.styleTypes[i];
      style = util.mergeStyle(style, CONF.DEFAULT.AUGMENTED_STYLE[styleType]);
    }
    shape.style(util.convertToFashionStyle(style));
    if (style.text) {
      if (!this.label) {
        var p = shape.position(),
            s = shape.size();
        this.label = shape.drawable.draw(
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
        this.label.addEvent(this.get('events'));
      } else {
        this.label.text(style.text);
        this.label.style({ fill: new Fashion.FloodFill(new Fashion.Color(style.text_color)) });
      }
    } else {
      if (this.label) {
        this.label.drawable.erase(this.label);
        this.label = null;
      }
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
 })(); return exports; })({});


/************** venue-editor.js **************/
/* extern */ var jQuery, I18n;
(function ($) {
  var CONF = __LIBS__['K_4LN8NH7HG0S611'];
  var models = __LIBS__['JC7M69EN5_PGPH3L'];
  var util = __LIBS__['vCU57LCSUMM0OWU0'];
  var viewobjects = __LIBS__['pTMHQJL2QM3RZGVH'];
  var IdentifiableSet = __LIBS__['O73W5HM407XSQ9WC'].IdentifiableSet;
  if (I18n)
    I18n.translations = __LIBS__['aD2O0CY0MX_9UPWO'];

  var parseCSSStyleText = (function () {
    var regexp_for_styles = /\s*(-?(?:[_a-z\u00a0-\u10ffff]|\\[^\n\r\f#])(?:[\-_A-Za-z\u00a0-\u10ffff]|\\[^\n\r\f])*)\s*:\s*((?:(?:(?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+|"(?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*"|'(?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*')(?:\s+|(?=;|$)))+)(?:;|$)/g;

    var regexp_for_values = /(?:((?:[^;\\ \n\r\t\f"']|\\[0-9A-Fa-f]{1,6}(?:\r\n|[ \n\r\t\f])?|\\[^\n\r\f0-9A-Fa-f])+)|"((?:[^\n\r\f\\"]|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)"|'((?:[^\n\r\f\\']|\\(?:\n|\r\n|\r|\f)|\\[^\n\r\f])*)')(?:\s+|$)/g;

    function unescape(escaped) {
      return escaped.replace(/(?:\\(0{0,2}d[89ab][0-9A-Fa-f]{2})(?:\r\n|[ \n\r\t\f])?)?\\([0-9A-Fa-f]{1,6})(?:\r\n|[ \n\r\t\f])?|\\([^\n\r\f0-9A-Fa-f])/g, function(_, a, b, c) {
        if (a !== void(0)) {
          var c2 = parseInt(b, 16) ;
          if (c2 < 0xdc00 || c2 > 0xdfff)
            throw new ValueError("Invalid surrogate pair");
          return String.fromCharCode((((parseInt(a, 16) & 0x3ff) << 10) | (c2 & 0x3ff)) + 0x10000);
        } else if (b !== void(0)) {
          return String.fromCharCode(parseInt(b, 16));
        } else if (c !== void(0)) {
          return c;
        }
      });
    }

    return function parseCSSStyleText(str) {
      var retval = {};
      var r = str.replace(regexp_for_styles, function (_, k, v) {
        var values = [];
        var r = v.replace(regexp_for_values, function (_, a, b, c) {
          if (a !== void(0)) {
            values.push(unescape(a));
          } else if (b !== void(0)) {
            values.push(unescape(b));
          } else if (c !== void(0)) {
            values.push(unescape(c));
          }
          return '';
        });
        if (r != '')
          throw new ValueError("Invalid CSS rule string: " + str);
        retval[k] = values;
        return '';
      });
      if (r != '')
        throw new ValueError("Invalid CSS rule string: " + str);
      return retval;
    };
  })();

  function parseDefs(node, defset) {
    function parseStops(def) {
      var ref = typeof def.getAttributeNS == 'function' ?
        def.getAttributeNS('http://www.w3.org/1999/xlink', 'href'):
        def.getAttribute("xlink:href");
      if (ref) {
        if (typeof def.ownerDocument.getElementById == 'function')
          def = def.ownerDocument.getElementById(ref.substring(1));
        else
          def = def.ownerDocument.selectSingleNode("*//*[@id='" + ref.substring(1) + "']");
      }
      var stops = def.childNodes;
      var colors = [];
      for (var i = 0; i < stops.length; i++) {
        var node = stops[i];
        if (node.nodeType != 1)
          continue;
        if (node.nodeName == 'stop') {
          var styles = parseCSSStyleText(node.getAttribute('style'));
          colors.push([
            parseFloat(node.getAttribute('offset')),
            new Fashion.Color(styles['stop-color'][0])]);
        }
      }
      return colors;
    }

    var defs = node.childNodes;
    for (var i = 0; i < defs.length; i++) {
      var def = defs[i];
      if (def.nodeType != 1)
        continue;
      var id = def.getAttribute('id');
      switch (def.nodeName) {
      case 'linearGradient':
        var x1 = parseFloat(def.getAttribute("x1")), y1 = parseFloat(def.getAttribute("y1")),
            x2 = parseFloat(def.getAttribute("x2")), y2 = parseFloat(def.getAttribute("y2"));
        var r = Math.acos((x2 - x1) / Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))) + (y2 - y1 < 0 ? Math.PI: 0);
        defset[id] = new Fashion.LinearGradientFill(parseStops(def), r / (Math.PI * 2));
        break;
      case 'radialGradient':
        defset[id] = new Fashion.RadialGradientFill(parseStops(def),
          { x: def.getAttribute('fx') || '50%', y: def.getAttribute('fy') || '50%' });
        break;
      }
    }
  }

  function parseCSSAsSvgStyle(str, defs) {
    var styles = parseCSSStyleText(str);
    var fill = null;
    var fillString = styles['fill'];
    var fillOpacity = null;
    var fillOpacityString = styles['fill-opacity'];
    var stroke = null;
    var strokeString = styles['stroke'];
    var strokeWidth = null;
    var strokeWidthString = styles['stroke-width'];
    var strokeOpacity = null;
    var strokeOpacityString = styles['stroke-opacity'];
    if (fillString) {
      if (fillString[0] == 'none') {
        fill = false;
      } else {
        var g = /url\(#([^)]*)\)/.exec(fillString[0]);
        if (g) {
          fill = defs[g[1]];
          if (!fill)
            throw new Error();
        } else {
          fill = new Fashion.Color(fillString[0]);
        }
      }
    }
    if (fillOpacityString) {
      fillOpacity = parseFloat(fillOpacityString[0]);
    }
    if (strokeString) {
      if (strokeString[0] == 'none')
        stroke = false;
      else
        stroke = new Fashion.Color(strokeString[0]);
    }
    if (strokeWidthString) {
      strokeWidth = parseFloat(strokeWidthString[0]);
    }
    if (strokeOpacityString) {
      strokeOpacity = parseFloat(strokeOpacityString[0]);
    }
    return {
      fill: fill,
      fillOpacity: fillOpacity,
      stroke: stroke,
      strokeWidth: strokeWidth,
      strokeOpacity: strokeOpacity
    };
  }

  function mergeSvgStyle(origStyle, newStyle) {
    return {
      fill: newStyle.fill !== null ? newStyle.fill: origStyle.fill,
      fillOpacity: newStyle.fillOpacity !== null ? newStyle.fillOpacity: origStyle.fillOpacity,
      stroke: newStyle.stroke !== null ? newStyle.stroke: origStyle.stroke,
      strokeWidth: newStyle.strokeWidth !== null ? newStyle.strokeWidth: origStyle.strokeWidth,
      strokeOpacity: newStyle.strokeOpacity !== null ? newStyle.strokeOpacity: origStyle.strokeOpacity
    };
  }

  function buildStyleFromSvgStyle(svgStyle) {
    return {
      fill:
        svgStyle.fill ? 
          (svgStyle.fill instanceof Fashion.Color ?
            new Fashion.FloodFill(
              svgStyle.fill.replace(
                null, null, null,
                svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255)):
            svgStyle.fill):
          null,
      stroke: 
        svgStyle.stroke ? new Fashion.Stroke(
          svgStyle.stroke.replace(
            null, null, null,
            svgStyle.fillOpacity ? svgStyle.fillOpacity * 255: 255),
          svgStyle.strokeWidth ? svgStyle.strokeWidth: 1,
          svgStyle.strokePattern ? svgStyle.strokePattern: null):
          null,
      visibility: true
    };
  }


  var VenueEditor = function VenueEditor(canvas, options) {
    this.canvas = canvas;
    this.callbacks = {
      uimodeselect: null,
      message: null,
      load: null,
      loadstart: null,
      click: null,
      selectable: null,
      select: null
    };
    if (options.callbacks) {
      for (var k in this.callbacks)
        this.callbacks[k] = options.callbacks[k] || (k == 'message' ? function(){} : null);
    }
    this.dataSource = options.dataSource;
    this.zoomRatio = options.zoomRatio || CONF.DEFAULT.ZOOM_RATIO;
    this.dragging = false;
    this.startPos = { x: 0, y: 0 };
    this.rubberBand = null;
    this.drawable = null;
    this.originalStyles = (function() {
      var store = {};
      return {
        save: function(id, data) {
          if (!store[id]) store[id] = data;
        },
        restore: function(id) {
          var rt = store[id];
          delete store[id];
          return rt;
        }
      };
    })();
    this.shift = false;
    this.drawing = null;
    this.metadata = null;
    this.keyEvents = null;
    this.zoomRatio = 1.0;
    this.uiMode = 'select1';
    this.shapes = null;
    this.seats = null;
    this.seatAdjacencies = null;
    this.selection = new IdentifiableSet();
    this.highlighted = {};
    this._adjacencyLength = 1;
    this.addKeyEvent();
    this.rubberBand = new Fashion.Rect({
      position: {x: 0, y: 0},
      size: {x: 0, y: 0}
    });
    this.rubberBand.style(CONF.DEFAULT.MASK_STYLE);
    canvas.empty();
  };

  VenueEditor.prototype.load = function VenueEditor_load(data) {
    if (this.drawable !== null)
      this.drawable.dispose();
    this.drawing = data.drawing;
    this.metadata = data.metadata;
    if (data.metadata.seat_adjacencies)
      this.seatAdjacencies = new models.SeatAdjacencies(data.metadata.seat_adjacencies);
    this.initDrawable();
    this.initModel();
    this.initSeats();
    this.callbacks.load && this.callbacks.load(this);
  };

  VenueEditor.prototype.dispose = function VenueEditor_dispose() {
    this.removeKeyEvent();
    if (this.drawable) {
      this.drawable.dispose();
      this.drawable = null;
    }
    this.seats = null;
    this.selection = null;
    this.highlighted = null;
  };

  VenueEditor.prototype.initDrawable = function VenueEditor_initDrawable() {
    var self = this;
    var drawing = this.drawing;
    var attrs = util.allAttributes(drawing.documentElement);
    var w = parseFloat(attrs.width), h = parseFloat(attrs.height);
    var vb = attrs.viewBox ? attrs.viewBox.split(/\s+/).map(parseFloat) : null;

    var size = ((vb || w || h) ? {
      x: ((vb && vb[2]) || w || h),
      y: ((vb && vb[3]) || h || w)
    } : null);

    var drawable = new Fashion.Drawable(self.canvas[0], { contentSize: {x: size.x, y: size.y}, viewportSize: { x: this.canvas.innerWidth(), y: this.canvas.innerHeight() } });
    var shapes = {};

    (function iter(svgStyle, defs, nodeList) {
      outer:
        for (var i = 0; i < nodeList.length; i++) {
          var n = nodeList[i];
          if (n.nodeType != 1) continue;

          var shape = null;
          var attrs = util.allAttributes(n);

          var currentSvgStyle = attrs.style ?
            mergeSvgStyle(svgStyle, parseCSSAsSvgStyle(attrs.style, defs)):
            svgStyle;

          switch (n.nodeName) {
            case 'defs':
              parseDefs(n, defs);
              break;

            case 'g':
              arguments.callee.call(self, currentSvgStyle, defs, n.childNodes);
              continue outer;

            case 'path':
              if (!attrs.d) throw new Error("Pathdata is not provided for the path element");
              shape = new Fashion.Path({points: new Fashion.PathData(attrs.d)});
              shape.style(CONF.DEFAULT.SHAPE_STYLE);
              break;

            case 'text':
              shape = new Fashion.Text({
                //position: {
                //  x: parseFloat(attrs.x),
                //  y: parseFloat(attrs.y)
                //},
                fontSize: 10,
                text: n.firstChild.nodeValue,
                zIndex: 99
              });
              shape.style(CONF.DEFAULT.TEXT_STYLE);
              break;

            case 'rect':
              shape = new Fashion.Rect({
                //position: {
                //  x: parseFloat(attrs.x),
                //  y: parseFloat(attrs.y)
                //},
                //corner: {
                //  x: parseFloat(attrs.rx || 0),
                //  y: parseFloat(attrs.ry || 0)
                //}
                size: {
                  x: parseFloat(attrs.width),
                  y: parseFloat(attrs.height)
                },
              });
              shape.style(CONF.DEFAULT.SHAPE_STYLE);
              break;

            default:
              continue outer;

          }
          if (shape !== null) {
            var x = parseFloat(attrs.x),
                y = parseFloat(attrs.y);
            if (!isNaN(x) && !isNaN(y))
              shape.position({ x: x, y: y });
            shape.style(buildStyleFromSvgStyle(currentSvgStyle));
            drawable.draw(shape);
          }
          shapes[attrs.id] = shape;
        }
    }).call(self,
      { fill: false, fillOpacity: false,
        stroke: false, strokeOpacity: false },
      {},
      drawing.documentElement.childNodes);

    self.drawable = drawable;
    self.shapes = shapes;

    var cs = drawable.contentSize();
    var vs = drawable.viewportSize();
    var center = {
      x: (cs.x - vs.x) / 2,
      y: (cs.y - vs.y) / 2
    };
    self.drawable.transform(Fashion.Matrix.scale(self.zoomRatio));
    self.changeUIMode(self.uiMode);
  };

  VenueEditor.prototype.initModel = function VenueEditor_initModel() {
    this.venue = new models.Venue(this.metadata, {
      callbacks: this.callbacks
    });
  };

  VenueEditor.prototype.initSeats = function VenueEditor_initSeats() {
    var self = this;
    var seats = {};
    for (var id in this.shapes) {
      var shape = this.shapes[id];
      var seat = this.venue.seats.get(id);
      if (!seat)
        continue;
      seats[id] = (function (id) {
        seat.on('change:selected', function () {
          var value = this.get('selected');
          if (value)
            self.selection.add(this);
          else
            self.selection.remove(this);
        });
        return new viewobjects.Seat({
          model: seat,
          shape: shape,
          events: {
            mouseover: function(evt) {
              if (self.uiMode == 'select')
                return;
              var candidate = null;
              if (self.seatAdjacencies) {
                var candidates = self.seatAdjacencies.getCandidates(id, self.adjacencyLength());
                if (candidates.length == 0)
                  return;
                for (var i = 0; i < candidates.length; i++) {
                  candidate = candidates[i];
                  for (var j = 0; j < candidate.length; j++) {
                    if (!seats[candidate[j]].get('model').selectable()) {
                      candidate = null;
                      break;
                    }
                  }
                  if (candidate) {
                    break;
                  }
                }
              } else {
                if (seats[id].get('model').selectable())
                  candidate = [id];
              }
              if (!candidate)
                return;
              for (var i = 0; i < candidate.length; i++) {
                var _id = candidate[i];
                var seat = seats[_id];
                seat.addStyleType('highlighted');
                self.highlighted[_id] = seat;
              }
            },
            mouseout: function(evt) {
              if (self.uiMode == 'select')
                return;
              var highlighted = self.highlighted;
              self.highlighted = {};
              for (var i in highlighted)
                highlighted[i].removeStyleType('highlighted');
            },
            mousedown: function(evt) {
              self.callbacks.click && self.callbacks.click(self, self, self.highlighted);
            }
          }
        });
      })(id);
    }
    this.seats = seats;
  };

  VenueEditor.prototype.addKeyEvent = function VenueEditor_addKeyEvent() {
    if (this.keyEvents) return;

    var self = this;

    this.keyEvents = {
      down: function(e) { if (util.eventKey(e).shift) self.shift = true;  return true; },
      up:   function(e) { if (util.eventKey(e).shift) self.shift = false; return true; }
    };

    $(document).bind('keydown', this.keyEvents.down);
    $(document).bind('keyup',   this.keyEvents.up);

  };

  VenueEditor.prototype.removeKeyEvent = function VenueEditor_removeKeyEvent() {
    if (!this.keyEvents) return;

    $(document).unbind('keydown', this.keyEvents.down);
    $(document).unbind('keyup',   this.keyEvents.up);
  };

  VenueEditor.prototype.changeUIMode = function VenueEditor_changeUIMode(type) {
    if (this.drawable) {
      var self = this;
      this.drawable.removeEvent(["mousedown", "mouseup", "mousemove"]);

      switch(type) {
      case 'select1':
        break;

      case 'select':
        this.drawable.addEvent({
          mousedown: function(evt) {
            self.startPos = evt.logicalPosition;
            self.rubberBand.position({x: self.startPos.x, y: self.startPos.y});
            self.rubberBand.size({x: 0, y: 0});
            self.drawable.draw(self.rubberBand);
            self.dragging = true;
          },

          mouseup: function(evt) {
            self.dragging = false;
            var selection = []; 
            var hitTest = util.makeHitTester(self.rubberBand);
            for (var id in self.seats) {
              var seatVO = self.seats[id];
              var seat = seatVO.get('model');
              if ((hitTest(seatVO.get('shape')) || (self.shift && seat.get('selected')) && seat.get('selectable'))) {
                selection.push(seat);
              }
            }
            self._unselectAll();
            self.drawable.erase(self.rubberBand);
            for (var i = 0; i < selection.length; i++)
              selection[i].set('selected', true);
            self.callbacks.select && self.callbacks.select(self, selection);
          },

          mousemove: function(evt) {
            if (self.dragging) {
              var pos = evt.logicalPosition;
              var w = Math.abs(pos.x - self.startPos.x);
              var h = Math.abs(pos.y - self.startPos.y);

              var origin = {
                x: (pos.x < self.startPos.x) ? pos.x : self.startPos.x,
                y: (pos.y < self.startPos.y) ? pos.y : self.startPos.y
              };

              if (origin.x !== self.startPos.x || origin.y !== self.startPos.y)
                self.rubberBand.position(origin);

              self.rubberBand.size({x: w, y: h});
            }
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
        throw new Error("Invalid ui mode: " + type);
      }
    }
    this.uiMode = type;
    this.callbacks.uimodeselect && this.callbacks.uimodeselect(this, type);
  };

  VenueEditor.prototype._unselectAll = function VenueEditor__unselectAll() {
    var prevSelection = this.selection;
    this.selection = new IdentifiableSet();
    prevSelection.each(function (seat) {
      seat.set('selected', false);
    });
  };

  VenueEditor.prototype.unselectAll = function VenueEditor_unselectAll() {
    if (this.selection.length > 0) {
      this._unselectAll();
      this.callbacks.select && this.callbacks.select(this, []);
    }
  };

  VenueEditor.prototype.adjacencyLength = function VenueEditor_adjacencyLength(value) {
    if (value !== void(0)) {
      this._adjacencyLength = value;
    }
    return this._adjacencyLength;
  };

  $.fn.venueeditor = function (options) {
    var aux = this.data('venueeditor');

    if (!aux) { // if there are no store data. init and store the data.
      if (!options)
        throw new Error("Options must be given");
      if (typeof options == 'string' || options instanceof String)
        throw new Error("Command issued against an uninitialized element");
      if (!options.dataSource || !options.dataSource instanceof Object)
        throw new Error("Required option missing: dataSource");
      aux = {
        manager: new VenueEditor(this, options),
        dataSource: options.dataSource,
        callbacks: { message: options.callbacks && options.callbacks.message || null, loading: options.callbacks && options.callbacks.loading || null }
      };
      this.data('venueeditor', aux);
      if (options.uimode)
        aux.manager.changeUIMode(options.uimode);
    } else {
      if (typeof options == 'string' || options instanceof String) {
        switch (options) {
          case 'load':
            // Ajax Waiter
            var waiter = new util.AsyncDataWaiter({
              identifiers: ['drawing', 'metadata'],
              after: function main(data) {
                aux.manager.load(data);
              }
            });
            // Load drawing
            $.ajax({
              type: 'get',
              url: aux.dataSource.drawing,
              dataType: 'xml',
              success: function(xml) { waiter.charge('drawing', xml); },
              error: function(xhr, text) { aux.callbacks.message && aux.callbacks.message("Failed to load drawing data (reason: " + text + ")"); }
            });

            // Load metadata
            $.ajax({
              url: aux.dataSource.metadata,
              dataType: 'json',
              success: function(data) { waiter.charge('metadata', data); },
              error: function(xhr, text) { aux.callbacks.message && aux.callbacks.message("Failed to load seat data (reason: " + text + ")"); }
            });
            aux.callbacks.loading && aux.callbacks.loading(aux.manager);
            break;

          case 'remove':
            aux.manager.dispose();
            this.data('venueeditor', null);
            break;

          case 'uimode':
            aux.manager.changeUIMode(arguments[1]);
            break;

          case 'selection':
            return aux.manager.selection;

          case 'clearSelection':
            aux.manager.unselectAll();
            return;

          case 'adjacency':
            aux.manager.adjacencyLength(arguments[1]|0);
            break;

          case 'model':
            return aux.manager.venue;

          case 'viewportSize':
            if (aux.manager.drawable) {
              aux.manager.drawable.viewportSize(
                { x: arguments[1].width, y: arguments[1].height }
              );
            }
            break;
        }
      }
    }
    return this;
  };
})(jQuery);
/*
 * vim: sts=2 sw=2 ts=2 et
 */
})(window.jQuery, window.I18n);
