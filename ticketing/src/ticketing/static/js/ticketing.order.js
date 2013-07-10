/* application */

var order = {};

order.init = function(order_id) {
  this.app = new order.ApplicationController();
  this.app.init(order_id);
};

order.ApplicationController = function() {
};

order.ApplicationController.prototype.init = function(order_id) {
  this.orderFormPresenter = new order.OrderFormPresenter({viewType: order.OrderFormView});
  this.orderFormPresenter.initialize(order_id);
  this.orderFormPresenter.fetchAndShow();
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
    this.performance = new order.Performance();

    $('.btn-save-order').on('click', function() {
      self.order.save();
    });
    $('.btn-cancel').on('click', function() {
      self.view.hide();
      $('.btn-edit-order').show();
      $('.btn-save-order, .btn-cancel').hide();
    });
  },
  showForm: function() {
    this.view.show(this.order);
  },
  fetchAndShow: function() {
    var self = this;
    this.order.fetch({
      success: function() {
        self.performance.set('id', self.order.get('performance_id'));
        self.performance.fetch({
          success: function() {
            self.showForm();
          }
        });
      }
    });
  },
  addSeat: function(ordered_product_item) {
    var self = this;
    var selection = venueEditorRoot.venueeditor('selection');
    var opi = ordered_product_item;
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
  addProduct: function() {
    var self = this;
    var op = new order.OrderedProduct({'ordered_product_items': [{id:null}]});
    self.order.get('ordered_products').push(op);
    self.view.show(self.order);
  }
};
_.extend(order.OrderFormPresenter.prototype, Backbone.Event);


/* model */

order.Order = Backbone.Model.extend({
  urlRoot: '/orders/api/edit',
  defaults: {
    id: null,
    order_no: null,
    performance_id: null,
    transaction_fee: 0,
    delivery_fee: 0,
    system_fee: 0,
    total_amount: 0,
    ordered_products: null
  },
  parse: function (response) {
    var self = this;
    var opc = new order.OrderedProductCollection();
    for (var i = 0; i < response.ordered_products.length; i++) {
      opc.push(new order.OrderedProduct(response.ordered_products[i]));
    }
    opc.on('change', function() {
      var total_amount = self.get('transaction_fee') + self.get('delivery_fee') + self.get('system_fee');
      this.each(function(op) {
        total_amount += op.get('price') * op.get('quantity');
      })
      self.set('total_amount', total_amount);
    });
    response.ordered_products = opc;
    return response;
  }
});

order.OrderedProduct = Backbone.Model.extend({
  defaults: {
    id: null,
    price: 0,
    quantity: 0,
    product_id: 0,
    product_name: null,
    sales_segment_id: 0,
    sales_segment_name: null,
    ordered_product_items: null
  },
  initialize: function() {
    var self = this;
    var opic = new order.OrderedProductItemCollection();
    var items = this.get('ordered_product_items');
    if (items) {
      for (var i = 0; i < items.length; i++) {
        opic.push(new order.OrderedProductItem(items[i]));
      }
    }
    opic.on('change', function() {
      this.each(function(item) {
        if (item.get('seats')) {
          var quantity = item.get('quantity') / item.get('product_item').get('quantity');
          self.set('quantity', quantity);
        }
      })
    });
    this.set('ordered_product_items', opic);
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
    var self = this;
    var pi = new order.ProductItem(this.get('product_item'));
    this.set('product_item', pi);

    var s = new order.SeatCollection();
    var seats = this.get('seats');
    if (seats) {
      for (var i = 0; i < seats.length; i++) {
        s.push(new order.Seat(seats[i]));
      }
    }
    this.set('seats', s);

    this.on('change:seats', function() {
      this.set('quantity', this.get('seats').length);
    });
    s.on('remove', function() {
      self.set('quantity', self.get('seats').length);
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

order.Performance = Backbone.Model.extend({
  urlRoot: '/orders/api/performance',
  defaults: {
    id: null,
    sales_segments: null
  },
  parse: function (response) {
    var ssc = new order.SalesSegmentCollection();
    for (var i = 0; i < response.sales_segments.length; i++) {
      ssc.push(new order.SalesSegment(response.sales_segments[i]));
    }
    response.sales_segments = ssc;
    return response;
  }
});

order.SalesSegment = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null,
    products: null,
    stock_types: null
  },
  initialize: function() {
    var pc = new order.ProductCollection();
    var stc = new order.StockTypeCollection();
    var products = this.get('products');
    if (products) {
      for (var i = 0; i < products.length; i++) {
        pc.push(new order.Product(products[i]));
        var stock_type = new order.StockType({
          'id':products[i].stock_type_id,
          'name':products[i].stock_type_name
        });
        if (!pc.get(stock_type)) stc.push(stock_type);
      }
    }
    this.set('products', pc);
    this.set('stock_types', stc);
  }
});

order.StockType = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null
  }
});

order.Product = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null,
    price: 0,
    stock_type_id: null,
    stock_type_name: null
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

order.SalesSegmentCollection = Backbone.Collection.extend({
  model: order.SalesSegment
});

order.StockTypeCollection = Backbone.Collection.extend({
  model: order.StockType
});

order.ProductCollection = Backbone.Collection.extend({
  model: order.Product
});


/* view */

order.OrderFormView = Backbone.View.extend({
  defaults: {
    el: $('#orderProductForm')
  },
  initialize: function() {
    this.presenter = this.options.presenter;
    this.template = new orderProductTemplate();
    this.template.get();
  },
  show: function(order) {
    this.render(order);
    this.$el.show();
  },
  hide: function() {
    this.$el.hide();
  },
  render: function(_order) {
    var self = this;
    this.$el.off();
    self.$el.html(_.template(self.template.template, _order.attributes));

    _order.get('ordered_products').each(function(op) {
      var product_view = new order.OrderProductFormView({
        el: self.el,
        presenter: self.presenter
      });
      product_view.render(op);
    })
  }
});

order.OrderProductFormView = Backbone.View.extend({
  defaults: {
    el: $('#orderProductForm')
  },
  initialize: function() {
    this.presenter = this.options.presenter;
  },
  events: {
    'click .btn-add-product': 'addProduct',
  },
  addProduct: function(e) {
    e.preventDefault();
    this.presenter.addProduct();
  },
  render: function(op) {
    var self = this;

    var product = $('<tr/>');
    var product_name = $('<td colspan="2" />');

    /*
     var sales_segment = $('<span class="label label-info" /> ').text(op.get('sales_segment_name'));
     var product_name = $('<td colspan="2" />').text(op.get('product_name'));
    */
    var sales_segment_id = op.get('sales_segment_id');
    var sales_segment = $('<select id="sales_segment_id" name="sales_segment_id"></select>');
    var ssc = self.presenter.performance.get('sales_segments');
    ssc.each(function(ss) {
      var option = $('<option/>').text(ss.get('name')).attr('value', ss.get('id'));
      if (ss.get('id') == sales_segment_id) option.attr('selected', 'selected');
      sales_segment.append(option);
    });
    sales_segment.on('change', function() {
      op.set('sales_segment_id', $(this).val());
      self.presenter.showForm();
    });
    product_name.append(sales_segment);

    var product_list = $('<select id="product_id" name="product_id" />');
    if (sales_segment_id) {
      var product_id = op.get('product_id');
      var ss = ssc.get(sales_segment_id);
      ss.get('products').each(function(p) {
        var option = $('<option/>').text(p.get('name')).attr('value', p.get('id'));
        if (p.get('id') == product_id) option.attr('selected', 'selected');
        product_list.append(option);
      });
      product_list.on('change', function() {
        var p = ss.get('products').get($(this).val());
        op.set('product_id', p.get('id'));
        op.set('price', p.get('price'));
        //op.set('quantity', $(this).val());
        self.presenter.showForm();
      });
      product_name.append(product_list);
    }

    var product_price = $('<td style="text-align: right;" />');
    var product_quantity = $('<td/>');
    var sum_amount = $('<td style="text-align: right;" />');
    if (product_id) {
      product_price.text(op.get('price'));
      product_quantity.text(op.get('quantity'));
      sum_amount.text(op.get('price') * op.get('quantity'));
    }

    product.append(product_name);
    product.append(product_price);
    product.append(product_quantity);
    product.append(sum_amount);
    this.$el.find('.add-product').before(product);

    var item_view = null;
    op.get('ordered_product_items').each(function(opi) {
      item_view = new order.OrderProductItemFormView({
        el: self.el,
        presenter: self.presenter,
        model: opi
      });
      item_view.render();
    });
  }
});

order.OrderProductItemFormView = Backbone.View.extend({
  initialize: function() {
    this.presenter = this.options.presenter;
  },
  events: {
    'click .btn-add-seat': 'addSeat',
    'click .chk-select-seat': 'deleteSeat'
  },
  addSeat: function(e) {
    e.preventDefault();
    this.presenter.addSeat($(e.target).data('ordered_product_item'));
  },
  deleteSeat: function(e) {
    this.presenter.deleteSeat($(e.target).data('seat'));
  },
  render: function() {
    var self = this;
    var opi = self.model;

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
    var product_item_price = $('<td style="text-align: right;" />').text(pi.get('price') || '');
    var product_item_quantity = $('<td/>').text(opi.get('quantity'));
    var btn_add_td = $('<td/>');
    var div_right = $('<div class="pull-right" />');
    var btn_add = $('<a href="#" class="btn btn-primary btn-mini btn-add-seat" />').text('選択座席を追加');
    btn_add.data('ordered_product_item', opi);

    stock_holder_name.prepend(span);
    item.append(stock_holder_name);
    seat_name.append(seats);
    item.append(seat_name);
    item.append(product_item_price);
    item.append(product_item_quantity);
    div_right.append(btn_add);
    btn_add_td.append(div_right);
    item.append(btn_add_td);
    this.$el.find('.add-product').before(item);
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
