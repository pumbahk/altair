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




order.OrderFormPresenter = function(params) {
  for (var k in params) this[k] = params[k];
};

order.OrderFormPresenter.prototype = {
  defaults: {
  },
  initialize: function(order_id) {
    this.view = new this.viewType({
      el: $('#orderProductForm'),
      presenter: this
    });
    this.order = new order.Order({id: order_id});
  },
  showForm: function() {
    var self = this;
    this.order.fetch({
      success: function() {
        self.view.show(self.order);
      }
    });
  },
  addSeat: function(ordered_product_item) {
    var self = this;
    var selection = venueEditorRoot.venueeditor('selection');
    var seats = ordered_product_item.get('seats');
    selection.each(function (seat) {
      if (!seats.get(seat)) {
        seats.push(new order.Seat({
          'id':seat.get('id'),
          'name':seat.get('name')
        }));
      }
    });
    this.order.get('ordered_products').each(function(op) {
      op.get('ordered_product_items').each(function(opi) {
        if (opi.id == ordered_product_item) {
          opi = ordered_product_item;
        }
      })
    })
    self.view.show(self.order);
  }
};
_.extend(order.OrderFormPresenter.prototype, Backbone.Event);




order.Order = Backbone.Model.extend({
  urlRoot: '/orders/api/get2',
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
    var opi = new order.OrderedProductItemCollection();
    var items = this.get('ordered_product_items');
    for (var i = 0; i < items.length; i++) {
      opi.push(new order.OrderedProductItem(items[i]));
    }
    this.set('ordered_product_items', opi);
  }
});

order.OrderedProductItem = Backbone.Model.extend({
  defaults: {
    id: null,
    price: 0,
    quantity: 0,
    stock_holder_name: 0,
    seats: null
  },
  initialize: function() {
    var s = new order.SeatCollection();
    var seats = this.get('seats');
    for (var i = 0; i < seats.length; i++) {
      s.push(new order.Seat(seats[i]));
    }
    this.set('seats', s);
  }
});

order.Seat = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null
  }
});




order.OrderedProductCollection = Backbone.Collection.extend({
  model: order.OrderedProduct
});
order.OrderedProductItemCollection = Backbone.Collection.extend({
  model: order.OrderedProductItem
});
order.SeatCollection = Backbone.Collection.extend({
  model: order.Seat
});




order.OrderProductFormView = Backbone.View.extend({
  defaults: {
    el: $('#orderProductForm')
  },
  initialize: function() {
    this.presenter = this.options.presenter;
    this.template = new orderProductTemplate();
    this.template.get();
  },
  events: {
    'click .btn-add-seat': 'clickAddSeatHandler'
  },
  clickAddSeatHandler: function(e) {
    e.preventDefault();
  },
  show: function(order) {
    this.render(order);
    this.$el.show();
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
        var item = $('<tr/>');
        var stock_holder_name = $('<td style="text-align: right;" />');
        var span = $('<span class="label label-info" />').text(opi.get('stock_holder_name'));
        var seat_name = $('<td class="span4" />');
        var seats = $('<ul/>');
        opi.get('seats').each(function(seat) {
          seats.append($('<li/>').text(seat.get('name')));
        });
        seat_name.append(seats);
        var product_item_price = $('<td style="text-align: right;" />').text(opi.get('price'));
        var product_item_quantity = $('<td/>').text(opi.get('quantity'));
        var add_button = $('<td/>').append($('<div class="pull-right"><a href="#" class="btn btn-primary btn-mini btn-add-seat">選択座席を追加</a></div>'));
        add_button.click(function() {
          self.presenter.addSeat(opi);
          return false;
        });

        stock_holder_name.prepend(span);
        item.append(stock_holder_name);
        item.append(seat_name);
        item.append(product_item_price);
        item.append(product_item_quantity);
        item.append(add_button);
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
