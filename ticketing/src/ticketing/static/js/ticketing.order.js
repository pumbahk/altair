var order = {};

order.init = function(order_id) {
  this.app = new order.ApplicationController();
  this.app.init(order_id);
};

order.ApplicationController = function() {
};

order.ApplicationController.prototype.init = function(order_id) {
  this.orderFormPresenter = new order.OrderFormPresenter({viewType: order.OrderProductFormView});
  this.orderFormPresenter.initialize(order_id);
  this.orderFormPresenter.showForm();
};


/* presenter */

order.OrderFormPresenter = function(params) {
  for (var k in params) this[k] = params[k];
};

order.OrderFormPresenter.prototype = {
  defaults: {
  },
  initialize: function(order_id) {
    var self = this;
    this.view = new this.viewType({
      el: $('#orderProductForm'),
      presenter: this
    });
    this.order = new order.Order({id: order_id});
    $('.btn-save-order').on('click', function() {
      self.save(self);
    });
    $('.btn-cancel').on('click', function() {
      self.view.hide();
      $('.btn-edit-order').show();
      $('.btn-save-order, .btn-cancel').hide();
    });
  },
  events: {
    'click .btn-save-order': 'save'
  },
  showForm: function() {
    var self = this;
    this.order.fetch({
      success: function() {
        self.view.show(self.order);
      }
    });
  },
  addSeat: function(ordered_product) {
    var self = this;
    var selection = venueEditorRoot.venueeditor('selection');
    ordered_product.get('ordered_product_items').each(function(opi) {
      if (opi.get('product_item').get('is_seat')) {
        var seats = opi.get('seats');
        selection.each(function(seat) {
          if (!seats.get(seat)) {
            seats.push(new order.Seat({
              'id':seat.get('id'),
              'name':seat.get('name')
            }));
          }
        });
        opi.trigger('change:seats');
        self.view.show(self.order);
      }
    });
  },
  deleteSeat: function(seat) {
    var self = this;
    var selection = venueEditorRoot.venueeditor('selection');
    selection.each(function(s) {
      if (s.get('id') == seat.get('id')) s.set('selected', false);
    });
    seat.collection.remove(seat);
    self.view.show(self.order);
  },
  save: function(self) {
    self.order.save();
  }
};
_.extend(order.OrderFormPresenter.prototype, Backbone.Event);


/* model */

order.Order = Backbone.Model.extend({
  urlRoot: '/orders/api/edit',
  defaults: {
    id: null,
    order_no: null,
    transaction_fee: 0,
    delivery_fee: 0,
    system_fee: 0,
    total_amount: 0,
    ordered_products: null
  },
  parse: function (response) {
    var op = new order.OrderedProductCollection();
    for (var i = 0; i < response.ordered_products.length; i++) {
      op.push(new order.OrderedProduct(response.ordered_products[i]));
    }
    response.ordered_products = op;
    return response;
  }
});

order.OrderedProduct = Backbone.Model.extend({
  defaults: {
    id: null,
    price: 0,
    quantity: 0,
    product_name: 0,
    sales_segment_name: 0,
    ordered_product_items: null
  },
  initialize: function() {
    var self = this;
    var opi = new order.OrderedProductItemCollection();
    var items = this.get('ordered_product_items');
    for (var i = 0; i < items.length; i++) {
      opi.push(new order.OrderedProductItem(items[i]));
      opi.on('change', function() {
        var opi = this;
        opi.each(function(item) {
          if (item.get('seats')) {
            var quantity = item.get('quantity') / item.get('product_item').get('quantity');
            self.set('quantity', quantity);
          }
        })
      });
    }
    this.set('ordered_product_items', opi);
  }
});

order.OrderedProductItem = Backbone.Model.extend({
  defaults: {
    id: null,
    price: 0,
    quantity: 0,
    product_item: null,
    seats: null
  },
  initialize: function() {
    var pi = new order.ProductItem(this.get('product_item'));
    this.set('product_item', pi);

    var s = new order.SeatCollection();
    var seats = this.get('seats');
    for (var i = 0; i < seats.length; i++) {
      s.push(new order.Seat(seats[i]));
    }
    this.set('seats', s);
    this.on('change:seats', function() {
      this.set('quantity', this.get('seats').length);
    });
  }
});

order.ProductItem = Backbone.Model.extend({
  defaults: {
    quantity: 0,
    stock_holder_name: 0,
    is_seat: false
  }
});

order.Seat = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null
  }
});


/* collection */

order.OrderedProductCollection = Backbone.Collection.extend({
  model: order.OrderedProduct
});

order.OrderedProductItemCollection = Backbone.Collection.extend({
  model: order.OrderedProductItem
});

order.SeatCollection = Backbone.Collection.extend({
  model: order.Seat
});


/* view */

order.OrderProductFormView = Backbone.View.extend({
  defaults: {
    el: $('#orderProductForm')
  },
  initialize: function() {
    this.$el.off();
    this.presenter = this.options.presenter;
    this.template = new orderProductTemplate();
    this.template.get();
  },
  events: {
    'click .btn-add-seat': 'addSeat',
    'click .chk-select-seat': 'deleteSeat'
  },
  addSeat: function(e) {
    e.preventDefault();
    this.presenter.addSeat($(e.target).data('ordered_product'));
  },
  deleteSeat: function(e) {
    this.presenter.deleteSeat($(e.target).data('seat'));
  },
  show: function(order) {
    this.render(order);
    this.$el.show();
  },
  hide: function() {
    this.$el.hide();
  },
  render: function(order) {
    var self = this;
    self.$el.html(_.template(self.template.template, order.attributes));

    var tr = self.$el.find('.add-product');
    order.get('ordered_products').each(function(op) {
      var product = $('<tr/>');
      var product_name = $('<td colspan="2" />').text(op.get('product_name'));
      var sales_segment_name = $('<span class="label label-info" /> ').text(op.get('sales_segment_name'));
      var product_price = $('<td style="text-align: right;" />').text(op.get('price'));
      var product_quantity = $('<td/>').text(op.get('quantity'));
      var sum_amount = $('<td style="text-align: right;" />').text(op.get('price') * op.get('quantity'));

      product_name.prepend(sales_segment_name);
      product.append(product_name);
      product.append(product_price);
      product.append(product_quantity);
      product.append(sum_amount);
      tr.before(product);

      op.get('ordered_product_items').each(function(opi) {
        var pi = opi.get('product_item');
        var item = $('<tr/>');
        var stock_holder_name = $('<td style="text-align: right;" />');
        var span = $('<span class="label label-info" />').text(pi.get('stock_holder_name'));
        var seat_name = $('<td class="span4" />');
        var seats = $('<ul/>');
        opi.get('seats').each(function(seat) {
          var chk_select = $('<input type="checkbox" checked="checked" class="chk-select-seat">');
          chk_select.data('seat', seat);
          seats.append($('<li/>').text(seat.get('name')).append(chk_select));
        });
        seat_name.append(seats);
        var product_item_price = $('<td style="text-align: right;" />').text(pi.get('price'));
        var product_item_quantity = $('<td/>').text(opi.get('quantity'));
        var btn_add_td = $('<td/>');
        var div_right = $('<div class="pull-right" />');
        var btn_add = $('<a href="#" class="btn btn-primary btn-mini btn-add-seat" />').text('選択座席を追加');
        btn_add.data('ordered_product', op);

        stock_holder_name.prepend(span);
        item.append(stock_holder_name);
        item.append(seat_name);
        item.append(product_item_price);
        item.append(product_item_quantity);
        div_right.append(btn_add);
        btn_add_td.append(div_right);
        item.append(btn_add_td);
        tr.before(item);
      })
    })
  }
});

var orderProductTemplate = function() {
  return {
    template: '',
    get: function() {
      var self = this;
      $.ajax({
        url: '/static/tiny_order.html',
        async: false,
        dataType: 'html',
        success: function (data) {
          self.template = data;
        },
        error: function (xhr, text) {
        }
      });
    }
  }
};
