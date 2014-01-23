/* application */

Backbone.emulateHTTP = true;

var order = {};

order.init = function(order_id, performance_id, options) {
  this.app = new order.ApplicationController();
  this.app.init(order_id, performance_id, options);
};

order.ApplicationController = function() {
};

order.ApplicationController.prototype.init = function(order_id, performance_id, options) {
  this.orderFormPresenter = new order.OrderFormPresenter({viewType: order.OrderFormView});
  this.orderFormPresenter.initialize(order_id, performance_id, options);
  this.orderFormPresenter.fetchAndShow();
};


/* presenter */

order.OrderFormPresenter = function(params) {
  for (var k in params) this[k] = params[k];
};

order.OrderFormPresenter.prototype = {
  defaults: {
  },
  initialize: function(order_id, performance_id, options) {
    var self = this;
    this.order = new order.Order({id: order_id});
    this.options = options;
    this.performance = new order.Performance({id: performance_id});
    this.view = new this.viewType({
      el: $('#orderProductForm'),
      presenter: this,
      order: this.order,
      data_source: this.options.data_source
    });
    this.ensure_seats = new order.EnsureSeatCollection();
    this.release_seats = new order.ReleaseSeatCollection();
    this.change_performance = false;

    $('.btn-confirm').on('click', function() {
      self.confirm();
    });
    $('.btn-save-order').on('click', function() {
      self.save();
    });
    $('.btn-close').on('click', function() {
      self.close();
    });
  },
  showMessage: function(message, option) {
    this.view.showAlert(message, option);
  },
  showForm: function() {
    $('.btn-edit-order, .btn-save-order, #orderProduct').hide();
    $('.btn-confirm, .btn-close').show();

    this.view.close();
    this.view = new this.viewType({
      el: $('#orderProductForm'),
      presenter: this,
      order: this.order,
      data_source: this.options.data_source
    });
    this.view.show();

    if (this.change_performance) {
      this.showMessage('公演が異なる予約を変更します。変更前の公演の予約情報は自動的にクリアされます。', 'alert-warning');
    }
  },
  fetchAndShow: function() {
    var self = this;
    this.order.fetch({
      success: function() {
        self.performance.fetch({
          success: function() {
            if (self.order.get('performance_id') != self.performance.get('id')) {
              self.order.set('performance_id', self.performance.get('id'));
              self.order.get('ordered_products').reset();
              self.change_performance = true;
            }
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
    var add_flag = false;
    selection.each(function(seat) {
      var stock_type_id = seat.get('stock').get('stockType').get('id');
      if (stock_type_id != opi.get('product_item').get('stock_type_id')) {
        self.showMessage('席種が異なるので追加できません', 'alert-warning');
        return false;
      }
      if (!seats.get(seat) && !self.ensure_seats.get(seat)) {
        seats.push(new order.Seat({
          'id':seat.get('id'),
          'name':seat.get('name'),
          'stock_type_id':stock_type_id
        }));
        self.ensure_seats.push(seat);
        add_flag = true;
      }
    });
    if (add_flag) {
      opi.trigger('change:seats');
      self.showForm();
    }
  },
  deleteSeat: function(seat) {
    var self = this;
    var venue = venueEditorRoot.venueeditor('model');
    var venue_seat = venue.seats.get(seat.id);
    if (self.ensure_seats.get(venue_seat)) self.ensure_seats.remove(venue_seat);
    if (!self.release_seats.get(venue_seat)) self.release_seats.push(venue_seat);
    seat.collection.remove(seat);
    self.showForm();
  },
  addProduct: function() {
    var self = this;
    var op = new order.OrderedProduct({'ordered_product_items': [{id:null}]});
    self.order.get('ordered_products').push(op);
    self.showForm();
  },
  close: function() {
    var self = this;
    self.ensure_seats.each(function(seat) {
      self.ensure_seats.remove(seat);
    });
    self.release_seats.each(function(seat) {
      self.release_seats.remove(seat);
    });
    self.view.close();
    $('.btn-edit-order, #orderProduct').show();
    $('.btn-confirm, .btn-save-order, .btn-close').hide();
    $('.btn-confirm, .btn-save-order, .btn-close').off();
  },
  confirm: function() {
    var self = this;
    $.ajax({
      url: '/orders/api/edit_confirm',
      async: false,
      dataType: 'json',
      data: JSON.stringify(self.order.attributes),
      type: 'POST',
      success: function (data) {
        console.log(data);
        self.order.set(self.order.parse(data));
        self.view.show();
        self.showMessage('変更内容を確認してください (手数料が再計算されています)', 'alert-warning');
        $('.btn-confirm').hide();
        $('.btn-save-order').show();
      },
      error: function (xhr, text) {
        console.log(xhr);
        var response = JSON.parse(xhr.responseText);
        self.showMessage(response.message, 'alert-error');
      }
    });
  },
  save: function() {
    var self = this;
    self.order.save(null, {
      success: function(model, res) {
        venueEditorRoot.venueeditor('refresh');
        self.close();
        showOrder(null, self.order.get('order_no'));
      },
      error: function(model, res) {
        var response = JSON.parse(res.responseText);
        self.showMessage(response.message, 'alert-error');
      }
    });
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
    sales_segment_id: 0,
    transaction_fee: 0,
    delivery_fee: 0,
    system_fee: 0,
    special_fee: 0,
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
      var total_amount = self.get('transaction_fee') + self.get('delivery_fee') + self.get('system_fee') + self.get('special_fee');
      this.each(function(op) {
        total_amount += op.get('price') * op.get('quantity');
      });
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
    stock_type_id: 0,
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
    quantity: 1,
    stock_holder_name: null,
    stock_type_id: null,
    is_seat: false,
    quantity_only: false
  }
});

order.Seat = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null,
    stock_type_id: null
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
  },
  initialize: function() {
    var pc = new order.ProductCollection();
    var products = this.get('products');
    if (products) {
      for (var i = 0; i < products.length; i++) {
        pc.push(new order.Product(products[i]));
      }
    }
    this.set('products', pc);
  }
});

order.Product = Backbone.Model.extend({
  defaults: {
    id: null,
    name: null,
    price: 0,
    stock_type_id: null,
    stock_type_name: null,
    quantity_only: false
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

order.ProductCollection = Backbone.Collection.extend({
  model: order.Product
});

order.EnsureSeatCollection = Backbone.Collection.extend({
  model: order.Seat,
  initialize: function() {
    this.on('add', function(seat) {
      seat.set('selected', false);
      seat.set('selectable', false);
    });
    this.on('remove', function(seat) {
      seat.set('selectable', true);
      seat.trigger('change:selectable');
    });
  }
});

order.ReleaseSeatCollection = Backbone.Collection.extend({
  model: order.Seat,
  initialize: function() {
    this.on('add', function(seat) {
      seat.set('selected', false);
      seat.set('selectable', true);
    });
    this.on('remove', function(seat) {
      seat.set('selectable', true);
      seat.trigger('change:selectable');
    });
  }
});


/* view */

order.OrderFormView = Backbone.View.extend({
  defaults: {
    el: $('#orderProductForm')
  },
  events: {
    'click .btn-add-product': 'addProduct',
    'click .btn-add-seat': 'addSeat',
    'click .chk-select-seat': 'deleteSeat'
  },
  initialize: function() {
    this.presenter = this.options.presenter;
    this.order = this.options.order;
    this.template = new orderProductTemplate(this.options.data_source);
    this.template.get();
  },
  showAlert: function(message, option) {
    var el = $('#orderProductAlert');
    var alert_el = $('<div class="alert"/>').addClass(option);
    alert_el.append($('<a class="close" data-dismiss="alert">&times;</a>'));
    alert_el.append($('<h4 class="alert-heading"/>').text(message));
    el.find('.alert').remove();
    el.append(alert_el);
  },
  hideAlert: function() {
    var el = $('#orderProductAlert');
    el.empty();
  },
  show: function() {
    this.render();
    this.$el.show();
  },
  close: function() {
    this.hideAlert();
    this.$el.off();
    this.$el.hide();
  },
  addProduct: function(e) {
    e.preventDefault();
    this.presenter.addProduct();
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
    self.$el.html(_.template(self.template.template, this.order.attributes));

    this.order.get('ordered_products').each(function(op) {
      var product_el = $('<tr/>');
      var product_view = new order.OrderProductFormView({
        el: product_el,
        order: self.order,
        presenter: self.presenter,
        model: op
      });
      self.$el.find('.add-product').before(product_el);
      product_view.show();
    })
  }
});

order.OrderProductFormView = Backbone.View.extend({
  initialize: function() {
    this.el = this.options.el;
    this.order = this.options.order;
    this.presenter = this.options.presenter;
    this.model = this.options.model;
    this.children = [];
  },
  show: function() {
    _.each(this.children, function(child) {
      child.$el.empty();
    });
    this.$el.empty();
    this.render();
  },
  selectSalesSegment: function(el) {
    var op = this.model;
    op.set('sales_segment_id', el.val());
  },
  selectProduct: function(el) {
    var op = this.model;
    var sales_segment_id = op.get('sales_segment_id') || this.order.get('sales_segment_id');
    var ss = this.presenter.performance.get('sales_segments').get(sales_segment_id);
    var p = ss.get('products').get(el.val());
    op.set('product_id', p.get('id'));
    op.set('price', p.get('price'));
    var opi = op.get('ordered_product_items').at(0);
    var product_item = new order.ProductItem({stock_type_id: p.get('stock_type_id'), quantity_only: p.get('quantity_only')});
    opi.set('product_item', product_item);
  },
  render: function() {
    var self = this;
    var op = self.model;

    var product_name = $('<td colspan="2" />');

    var sales_segment_id = op.get('sales_segment_id') || self.order.get('sales_segment_id');
    var sales_segment = $('<select id="sales_segment_id" name="sales_segment_id"></select>');
    var ssc = self.presenter.performance.get('sales_segments');
    ssc.each(function(ss) {
      var option = $('<option/>').text(ss.get('name')).attr('value', ss.get('id'));
      if (ss.get('id') == sales_segment_id) option.attr('selected', 'selected');
      sales_segment.append(option);
    });
    sales_segment.on('change', function() {
      self.selectSalesSegment($(this));
      self.show();
    });
    product_name.append(sales_segment);

    var product_list = $('<select id="product_id" name="product_id" />');
    var product_id = op.get('product_id');
    var ss = ssc.get(sales_segment_id);
    if (ss) {
      var stock_type_id = op.get('stock_type_id');
      var existing_pid = [];
      self.order.get('ordered_products').each(function(existing_op) {
        if (op != existing_op) existing_pid.push(existing_op.get('product_id'));
      })
      ss.get('products').each(function(p) {
        if ($.inArray(p.get('id'), existing_pid) > -1) return false;
        if (!stock_type_id || stock_type_id == p.get('stock_type_id')) {
          var option = $('<option/>').text(p.get('name')).attr('value', p.get('id'));
          if (p.get('id') == product_id) option.attr('selected', 'selected');
          product_list.append(option);
        }
      });
      product_list.on('change', function() {
        self.selectProduct($(this));
        self.show();
      });
      if (op.get('id') == null && product_list.find('option').length == 1) {
        product_list.val(product_list.find('option:first').val());
        this.selectProduct(product_list);
      }
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

    this.$el.append(product_name);
    this.$el.append(product_price);
    this.$el.append(product_quantity);
    this.$el.append(sum_amount);

    var item_view = null;
    op.get('ordered_product_items').each(function(opi) {
      var product_item_el = $('<tr/>');
      item_view = new order.OrderProductItemFormView({
        el: product_item_el,
        presenter: self.presenter,
        model: opi
      });
      self.$el.after(product_item_el);
      self.children.push(item_view);
      item_view.show();
    });
  }
});

order.OrderProductItemFormView = Backbone.View.extend({
  initialize: function() {
    this.el = this.options.el;
    this.presenter = this.options.presenter;
    this.model = this.options.model;
  },
  events: {
    'focusout .txt-edit-quantity': 'editQuantity'
  },
  editQuantity: function(e) {
    this.model.set('quantity', $(e.target).val());
    this.show();
  },
  show: function() {
    this.$el.empty();
    this.render();
  },
  render: function() {
    var self = this;
    var opi = self.model;

    var pi = opi.get('product_item');
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
    var product_item_quantity = $('<td/>');
    if (pi.get('quantity_only')) {
      var txt_quantity = $('<input type="text" class="txt-edit-quantity" style="width: 20px; margin: 2px;">').val(opi.get('quantity'));
      product_item_quantity.append(txt_quantity);
    } else {
      product_item_quantity.text(opi.get('quantity'));
    }
    var btn_add_td = $('<td/>');
    var div_right = $('<div class="pull-right" />');
    var btn_add = $('<a href="#" class="btn btn-primary btn-mini btn-add-seat" />').text('選択座席を追加');
    btn_add.data('ordered_product_item', opi);

    stock_holder_name.prepend(span);
    this.$el.append(stock_holder_name);
    seat_name.append(seats);
    this.$el.append(seat_name);
    this.$el.append(product_item_price);
    this.$el.append(product_item_quantity);
    div_right.append(btn_add);
    btn_add_td.append(div_right);
    this.$el.append(btn_add_td);
  }
});

var orderProductTemplate = function(data_source) {
  return {
    template: '',
    get: function() {
      var self = this;
      $.ajax({
        url: data_source.order_template_url,
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
