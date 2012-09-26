var util = require('util.js');
var CONF = require('CONF.js');
var IdentifiableSet = require('identifiableset.js').IdentifiableSet;

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
    var stockType = new StockType({
      id: stockTypeDatum.id,
      name: stockTypeDatum.name,
      isSeat: stockTypeDatum.is_seat,
      quantityOnly: stockTypeDatum.quantity_only,
      style: stockTypeDatum.style
    });
    stockTypes.add(stockType);
    stockType.on('change:name', function () {
      this.set('edited', true);
    });
    stockType.on('change:style', function () {
      this.set('edited', true);
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
      this.set('edited', true);
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
      seat_no: seatDatum.seat_no,
      status: seatDatum.status,
      stock: stocks.get(seatDatum.stock_id),
      attrs: seatDatum.attrs,
      areas: seatDatum.areas,
      selectable: $.inArray(seatDatum.status, [0, 1]) > -1 ? true : false
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
      var set;
      if (stock) {
        set = perStockSeatSet[stock.id];
      } else {
        console.log('Stock not found in Seat.id:' + seat.id);
      }
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
            var set = perStockSeatSet[new_.id]
            if (!set)
              set = perStockSeatSet[new_.id] = new IdentifiableSet();
            set.add(this);
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

  var stockTypeData = [];
  this.stockTypes.each(function (stockType) {
    if (stockType.get('edited')) {
      stockTypeData.push({
        id: stockType.get('id'),
        name: stockType.get('name'),
        style: stockType.get('style')
      });
    }
  });

  return {
    seats:seatData,
    stocks:stockData,
    stock_types:stockTypeData
  };
};

Venue.prototype.clearEdited = function Venue_clearEdited () {
  this.seats.each(function (seat) {
    if (seat.get('edited')) {
      seat.set('edited', false);
    }
  });
  this.stocks.each(function (stock) {
    if (stock.get('edited')) {
      stock.set('edited', false);
    }
  });
  this.stockTypes.each(function (stockType) {
    if (stockType.get('edited')) {
      stockType.set('edited', false);
    }
  });
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
    available: 0,
    edited: false
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

    _.each(Stock.styleProviderAttributes, function (name) {
      var stock = self.get(name);
      if (stock) {
        stock.on('change:style', function () {
          self._refreshStyle();
        });
      } else {
        console.log(name + ' not found in Stock.id:' + self.id);
      }
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
    seat_no: null,
    status: null,
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
