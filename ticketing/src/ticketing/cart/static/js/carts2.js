// new cart flow

var cart = {};

cart.util = {
    datestring_japanize: function(datestring){
        // year, month, day, rest
        var dates = datestring.split(/[ -]/);
        return "%Y年%m月%d日 %time"
            .replace("%Y", dates[0])
            .replace("%m", dates[1])
            .replace("%d", dates[2])
            .replace("%time", dates[3]);
    },

    build_route_path: function (pattern, kwds) {
        return pattern.replace(/\{([^}]+)\}/, function ($0, $1) {
            return kwds[$1] || '';
        });
    },

    render_template: function (template, vars) {
        return template.replace(/\{\{((?:[^}]|\}[^}])*)\}\}/, function (_, n) { return vars[n]; });
    },

    render_template_into: function (jq, template, vars) {
        var regexp = /\{\{((?:[^}]|\}[^}])*)\}\}|((?:[^{]|\{(?:[^{]|$))+)/g, g;
        while ((g = regexp.exec(template))) {
            if (g[1])
                jq.append(vars[g[1]]);
            else if (g[2])
                jq.append(g[2]);
        }
    }
};

cart.events = {
    ON_PERFORMANCE_RESOLVED: "onPerformanceResolved",
    ON_STOCK_TYPE_SELECTED: "onStockTypeSelected",
    ON_CART_CANCELED: "onCartCanceled",
    ON_CART_ORDERED: "onCartOredered",
    ON_VENUE_DATASOURCE_UPDATED: "onVenueDataSourceUpdated"
};
cart.init = function(venues_selection, selected, upper_limit, cart_release_url) {
    venues_selection = $.extend({}, venues_selection); // clone
    $.each(venues_selection, function (k, v) {
        for (var i = 0; i < v.length; i++) {
            v[i].date = k;
        }
    });
    this.app = new cart.ApplicationController();
    this.app.init(venues_selection, selected, upper_limit, cart_release_url);
    this.inCartProductList = $('#contentsOfShopping');
    this.totalAmount = $('#cart-total-amount');
    this.reservationDialog = $('#order-reserved');
    this.errorDialog = $('#order-error-template');
    var self = this;
    this.reservationDialog.find('.cancel-button').click(function() {
        $.ajax({
            url: cart_release_url, // global
            dataType: 'json',
            type: 'POST',  
            success: function() {
                self.reservationDialog.overlay().close();
            }
        });
        $("#selectSeat .venueViewer").venueviewer("refresh");
        self.reservationDialog.overlay().close();
        $("#selectSeatType").click();
    });
    this.reservationDialog.find('.confirm-button').click(function() {
        window.location.href = reservationData.payment_url;
    });
    this.errorDialog.find('.close-button').click(function() {
        self.errorDialog.overlay().close();
    });
};

cart.createContentOfShoppingElement = function(product) {
    var item = $('<tr/>');
    var name = $('<td/>').text(product.name);;
    var price = $('<td/>').text("￥ "+product.price);
    var quantity = $('<td/>').text(product.quantity + " 枚");
    // TODO: 予約席をProductごとに追加
    var seats_container = $('<td/>');
    var seats = $('<ul/>');
    var selected_seats = product.seats;
    for (var i = 0; i < selected_seats.length; i++) {
        var seat_item = $('<li/>');
        seat_item.text(selected_seats[i].name);
        seats.append(seat_item);
    }
    seats_container.append(seats);
    item.append(name);
    item.append(price);
    item.append(quantity);
    item.append(seats_container);
    return item;
};

cart.proceedToCheckout = function proceedToCheckout(data) {
    reservationData = data;
    var root = this.hallName;
    var products = data.cart.products;

    // insert product items in cart
    this.inCartProductList.empty();
    for (var i = 0; i < products.length; i++) {
        var product = products[i];
        var item = this.createContentOfShoppingElement(product);//
        this.inCartProductList.append(item);
    }
    this.inCartProductList.find("tr").last().addClass(".last-child");

    this.totalAmount.text("￥ " + data.cart.total_amount);

    this.reservationDialog.overlay({
        mask: {
            color: "#999",
            opacity: 0.5
        },
        closeOnClick: false
    });
    this.reservationDialog.overlay().load();
}

cart.showErrorDialog = function showErrorDialog() {
    this.errorDialog.overlay({
        mask: {
            color: "#999",
            opacity: 0.5
        },
        closeOnClick: false
    });
    this.errorDialog.overlay().load();
};

cart.ApplicationController = function() {
};

cart.ApplicationController.prototype.init = function(venues_selection, selected, upper_limit, cart_release_url) {
    this.performanceSearch = new cart.PerformanceSearch({
        venuesSelection: venues_selection,
        performance: selected[1],
        venue: null
    });
    this.performance = new cart.Performance({
    });
    this.venue = new cart.Venue({
            data_source: null
    });
    // 絞込み
    this.performanceSearchPresenter = new cart.PerformanceSearchPresenter({
        viewType: cart.PerformanceSearchView,
        performanceSearch: this.performanceSearch,
        performance: this.performance
    });
    // 席種
    this.stockTypeListPresenter = new cart.StockTypeListPresenter({
        viewType: cart.StockTypeListView,
        performance: this.performance
    });
    // 会場図
    this.venuePresenter = new cart.VenuePresenter({
        viewType: cart.VenueView,
        performance: this.performance,
        stockTypeListPresenter: this.stockTypeListPresenter
    });
    // フォーム
    this.orderFormPresenter = new cart.OrderFormPresenter({
        viewType: cart.OrderFormView,
        venuePresenter: this.venuePresenter
    });

    this.performanceSearchPresenter.stockTypeListPresenter = this.stockTypeListPresenter;
    this.stockTypeListPresenter.venuePresenter = this.venuePresenter;
    this.stockTypeListPresenter.orderFormPresenter = this.orderFormPresenter;
    this.venuePresenter.orderFormPresenter = this.orderFormPresenter;

    this.performanceSearchPresenter.initialize();
    this.stockTypeListPresenter.initialize();
    this.venuePresenter.initialize();
    this.orderFormPresenter.initialize();

};

cart.PerformanceSearchPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};


cart.PerformanceSearchPresenter.prototype = {
    initialize: function() {
        var self = this;
        this.view = new this.viewType({
            presenter: this,
            el: $("#form1")
        });
        this.view.on(cart.events.ON_PERFORMANCE_RESOLVED,
            function(performance) {self.onPerformanceResolved(performance);});
        this.view.model = this.performanceSearch;
        this.view.renderDateSelection();
    },
    onPerformanceResolved: function(performance_id) {
        var performance = this.performanceSearch.getPerformance(performance_id);
        this.performance.url = performance.seat_types_url;
        this.performance.fetch({
            success: function () {
                $('#performanceDate').text(cart.util.datestring_japanize(performance.date));
                $('#performanceVenue').text(performance.name);
            }
        });
    }
};
_.extend(cart.PerformanceSearchPresenter.prototype, Backbone.Event);

cart.StockTypeListPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.StockTypeListPresenter.prototype = {
    initialize: function() {
        var self = this;
        this.view = new this.viewType({ });
        this.performance.on("change",
            function() {self.onPerformanceChanged();});
        this.view.on(cart.events.ON_STOCK_TYPE_SELECTED,
            function(products_url, stock_type) {self.onStockTypeSelected(products_url, stock_type);});
        this.setActivePane('stockTypeList');
    },
    setActivePane: function (active) {
        this.active = active;
        switch (this.active) {
        case 'stockTypeList':
            this.view.active = true;
            this.view.updateUIState();
            if (this.venuePresenter.view) {
                this.venuePresenter.view.readOnly = true;
                this.venuePresenter.view.updateUIState();
            }
            break;
        case 'venue':
            this.view.active = false;
            this.view.updateUIState();
            if (this.venuePresenter.view) {
                this.venuePresenter.view.readOnly = false;
                this.venuePresenter.view.updateUIState();
            }
            break;
        }
    },
    onPerformanceChanged: function() {
        $("#current-performance-id").val(this.performance.get('performance_id'));
        var stockTypes = this.performance.get("seat_types");
        // collectionを作ってViewにpush
        var stockTypeCollection = new Backbone.Collection();
        for (var i=0; i < stockTypes.length; i++) {
            var stockType = new cart.StockType(stockTypes[i]);
            stockTypeCollection.push(stockType);
        }
        this.view.collection = stockTypeCollection;
        this.view.render();
    },
    onStockTypeSelected: function(products_url, stock_type) {
        var self = this;
        $.getJSON(
            products_url,
            function(data) {
                var products = data.products;
                var productCollection = new cart.ProductQuantityCollection();
                for (var i=0; i < products.length; i++) {
                    var product = products[i];
                    var p = new cart.ProductQuantity(product);
                    productCollection.push(p);
                }
                var selected = self.view.selected;
                self.orderFormPresenter.showOrderForm(selected, stock_type, productCollection);
            }
        );
    }
};

_.extend(cart.StockTypeListPresenter.prototype, Backbone.Event);


cart.VenuePresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.VenuePresenter.prototype = {
    defaults: {
        viewType: null,
    },
    initialize: function() {
        var self = this;
        this.callbacks = {
            selectable: function () { return self.selectable.apply(self, arguments); },
            click: function () { self.click.apply(self, arguments); }
        };
        this.view = new this.viewType({
            presenter: this
        });
        this.performance.on("change",
            function() {self.onPerformanceChanged();});
        this.selectedStockType = null;
    },
    onPerformanceChanged: function() {
        var dataSource = this.performance.createDataSource();
        this.view.updateVenueViewer(dataSource, this.callbacks);
    },
    onCancelPressed: function () {
        this.setStockType(null);
    },
    onSelectPressed: function () {
        var selection = this.view.getChoices();
        var quantity_to_select = this.orderFormPresenter.quantity_to_select;
        if (selection.length < quantity_to_select) {
            alert("あと " + (quantity_to_select - selection.length) + " 席選んでください");
            return;
        } else if (selection.length != quantity_to_select) {
            alert("購入枚数と選択した席の数が一致していません。");
            return;
        }
        this.orderFormPresenter.setSeats(selection);
        this.orderFormPresenter.doOrder();
    },
    setStockType: function (stock_type) {
        this.selectedStockType = stock_type;
        this.stockTypeListPresenter.setActivePane(this.selectedStockType ? 'venue': 'stockTypeList');
        this.view.render();
    },
    selectable: function (viewer, seat) {
        if (!this.selectedStockType) {
            return true;
        }
        var isValidStockType = (seat.meta.stock_type_id == this.selectedStockType.id);
        var isVacant = (seat.meta.status == 1);
        return isValidStockType && isVacant && seat.meta.is_hold;
    },

    click: function (viewer, seat, highlighted) {
        // クリック位置から、座席選択をする
        var self = this;
        $.each(highlighted, function (id, seat) {
            if (seat.selected()) {
                seat.selected(false);
            } else {
                var selectable = viewer.selectionCount < self.orderFormPresenter.quantity_to_select;
                seat.selected(selectable);
            }
        });
    }
};
_.extend(cart.VenuePresenter.prototype, Backbone.Event);


cart.PerformanceSearchView = Backbone.View.extend({
    initialize: function() {
        var self = this;
        this.selection = this.$el.find("#date-select");
        this.selection.on("change",
            function() {self.onDateSelectionChanged(this.value)});
        this.venueSelection = this.$el.find("#venue-select");
        this.venueSelection.on("change",
            function() {self.onVenueSelectionChanged()});
    },
    renderDateSelection: function () {
        this.selection.empty();
        var self = this;
        var dates = this.model.getDates();
        $.each(dates, function (_, v) {
            self.selection.append($('<option></option>').attr('value', v).text(cart.util.datestring_japanize(v)));
        });
        this.onDateSelectionChanged(dates[0]);
    },
    render: function() {
        // 絞り込み条件を設定する
        var selected = this.model.get("performance");
        var venues = this.model.getVenues(selected);
        var venueSelection = this.$el.find("#venue-select");
        venueSelection.empty();
        for (var i=0; i < venues.length; i++) {
            var venue = venues[i];
            var opt = $('<option/>');
            $(opt).attr('value', venue.id);
            $(opt).text(venue.name);
            $(venueSelection).append(opt);
        }
        $(venueSelection).change();
    },
    onDateSelectionChanged: function(performanceDate) {
        this.model.set("performance", performanceDate);
        this.render();
    },
    onVenueSelectionChanged: function() {
        this.trigger(cart.events.ON_PERFORMANCE_RESOLVED,
            $(this.venueSelection).val());
    }
});

cart.PerformanceSearch = Backbone.Model.extend({
    defaults: {
        venuesSelection: null,
        performance: null
    },
    getDates: function() {
        var retval = [];
        for (var k in this.get('venuesSelection'))
            retval.push(k);
        retval = retval.sort();
        return retval;
    },
    getVenues: function(selected) {
        var venuesSelection = this.get('venuesSelection');
        return venuesSelection[selected];
    },
    getPerformance: function(id) {
        var venues = this.getVenues(this.get("performance"));
        for (var i=0; i < venues.length; i++) {
            var venue = venues[i];
            if (venue.id == id) {
                return venue;
            }
        }
    },
});

cart.Performance = Backbone.Model.extend({
    createDataSource: function() {
        return createDataSource(this.attributes);
    }
});

cart.StockType = Backbone.Model.extend({
});


cart.StockTypeListView = Backbone.View.extend({
    defaults: {
        arrow: null,
        selected: null,
        active: false,
        el: $('#selectSeatType')
    },

    render: function() {
        var self = this;
        var ul = $('#seatTypeList');
        ul.empty();
        var i = 0;
        this.collection.each(function(stockType) {
            $('<li></li>')
                .append($('<div class="seatListItemInner"></div>')
                   .append(
                     $('<input type="radio" name="seat_type" />')
                     .attr('value', stockType.get("products_url"))
                     .data('stockType', stockType))
                   .append(
                     $('<span class="seatColor"></span>')
                     .css('background-color', stockType.get("style").fill.color))
                   .append(
                     $('<span class="seatName"></span>')
                     .text(stockType.get("name")))
                   .append(
                     $('<span class="seatStatus"></span>')))
                .append($('<div class="seatListItemAux"></div>'))
                .addClass(["seatEven", "seatOdd"][i & 1])
                .appendTo(ul)
            i++;
        });
        var self = this;
        $(ul.closest('form')).find(':radio').change(function () {
            var radio = $(this);
            self.selected = radio.closest('li');
            self.trigger(cart.events.ON_STOCK_TYPE_SELECTED, 
                radio.val(), radio.data('stockType'));
        });
        this.updateUIState();
    },

    initialize: function() {
        this.selected = null;
    },

    reset: function() {
    },

    updateUIState: function () {
        if (this.active) {
            $('#selectSeatType').removeClass('blur');
            $('#selectSeatType').addClass('focused');
        } else {
            $('#selectSeatType').removeClass('focused');
            $('#selectSeatType').addClass('blur');
        }
    }
});

cart.OrderFormPresenter = function(params) {
    for (var k in params) {
        this[k] = params[k];
    }
};

cart.OrderFormPresenter.prototype = {
    initialize: function() {
        this.view = new this.viewType({
            el: $('#selectProductTemplate'),
            updateHandler: $('#seatTypeList').data('updateArrowpos'),
            presenter: this
        });
        this.stock_type = null;
        this.products = null;
        this.quantity_to_select = null;
        this.orderForm = $('#selectSeatType form');
    },
    hideOrderForm: function() {
        this.view.hideForm(function () {
            this.view.selected_stock_type_el = null;
            this.view.collection = null;
        });
    },
    showOrderForm: function(selected_stock_type_el, stock_type, products) {
        this.stock_type = stock_type;
        this.products = products;
        this.view.showForm(selected_stock_type_el, stock_type, products);
    },
    calculateQuantityToSelect: function () {
        var quantity_to_select = 0;
        var selection = this.view.getChoices();
        for (var product_id in selection) {
            var multiple = selection[product_id];
            var product = this.products.get(product_id);
            quantity_to_select += product.get('quantity_power') * multiple;
        }
        this.quantity_to_select = quantity_to_select; 
    },
    onSelectSeatPressed: function () {
        this.calculateQuantityToSelect();
        if (this.quantity_to_select == 0) {
            alert('商品を1つ以上選択してください');
            return;
        }
        this.venuePresenter.setStockType(this.stock_type);
    },
    onEntrustPressed: function () {
        this.calculateQuantityToSelect();
        if (this.quantity_to_select == 0) {
            alert('商品を1つ以上選択してください');
            return;
        }
        this.setSeats([]);
        this.doOrder();
    },
    onBuyPressed: function () {
        this.setSeats([]);
        this.doOrder();
    },
    setSeats: function (seats) {
        var orderForm = this.orderForm;
        orderForm.find("input[name='selected_seat']").remove();
        $.each(seats, function (_, v) {
            orderForm.append($('<input type="hidden" name="selected_seat" />').val(v.id));
        });
    },
    doOrder: function () {
        var values = this.orderForm.serialize();
        $.ajax({
            url: order_url, //this is global variable
            dataType: 'json',
            data: values,
            type: 'POST',
            success: function(data, textStatus, jqXHR) {
                if (data.result == 'OK') {
                    cart.proceedToCheckout(data);
                } else {
                    cart.showErrorDialog();
                }
            }
        });
    }
};

_.extend(cart.OrderFormPresenter.prototype, Backbone.Event);

cart.OrderFormView = Backbone.View.extend({
    defaults: {
        el: $('#selectProductTemplate'),
        selected_stock_type_el: null
    },
    initialize: function() {
        this.presenter = this.options.presenter;
        this.updateHandler = this.options.updateHandler;
    },
    getChoices: function () {
        var retval = {};
        this.selected_stock_type_el.find('.seatListItemAux select').each(function (_, n) {
            var g = /^product-(\d+)/.exec(n.name);
            if (g)
                retval[g[1]] = parseInt(n.value);
        });
        return retval;
    },
    hideForm: function(done) {
        if (!this.selected_stock_type_el) {
            done && done();
            return;
        }
        var self = this;
        var aux = this.selected_stock_type_el.find('.seatListItemAux');
        aux.animate(
            { 'height': 0 },
            {
                queue: false,
                duration: 300,
                complete: function () {
                    aux.empty();
                    done && done();
                },
                step: this.updateHandler
            }
        );
    },
    showForm: function(selected_stock_type_el, stock_type, products, done) {
        if (this.selected_stock_type_el && selected_stock_type_el[0] == this.selected_stock_type_el[0]) {
            return false;
        }
        this.hideForm();
        var orderForm = this.render(selected_stock_type_el, stock_type, products);
        var aux = selected_stock_type_el.find('.seatListItemAux');
        orderForm.appendTo(aux);
        this.selected_stock_type_el = selected_stock_type_el;
        this.collection = products;
        var height = orderForm.height();
        aux.animate(
            { 'height': height },
            {
                queue: false,
                duration: 300,
                complete: function () {
                    done && done();
                },
                step: this.updateHandler
            }
        );
        return true;
    },
    render: function(selected_stock_type_el, stock_type, products) {
        var self = this;
        var orderForm = this.$el.clone().css("display", "block");
        var selected_seats = orderForm.find('.selected-seats');
        var payment_seat_products = orderForm.find('.payment-seat-products');
        products.each(function(product) {
            payment_seat_products.append(self.buildProduct(product));
        });
        var btn_select_seat = orderForm.find('.btn-select-buy');
        var btn_entrust = orderForm.find('.btn-entrust-buy');
        var btn_buy = orderForm.find('.btn-buy');

        if (stock_type.get("quantity_only")) {
            btn_select_seat.parent().css('display', 'none');
            btn_entrust.parent().css('display', 'none');
            btn_buy.parent().css('display', null);
        } else {
            btn_select_seat.parent().css('display', null);
            btn_entrust.parent().css('display', null);
            btn_buy.parent().css('display', 'none');
        }
        btn_select_seat.click(function () { self.presenter.onSelectSeatPressed(); return false; });
        btn_entrust.click(function () { self.presenter.onEntrustPressed(); return false; });
        btn_buy.click(function () { self.presenter.onBuyPressed(); return false; });

        return orderForm;
    },
    buildProduct: function(product) {
        var name = $('<span class="productName"></span>');
        name.text(product.get("name"));
        var payment = $('<span class="productPrice"></span>');
        payment.text('￥' + product.get("price"));
        var quantity = $('<span class="productQuantity">');
        var pullDown = $('<select />').attr('name', 'product-' + product.id);
        for (var i = 0; i < upper_limit+1; i++) {
            $('<option></option>').text(i).val(i).appendTo(pullDown);
        }
        cart.util.render_template_into(quantity, product.get("unit_template"), { num: pullDown });
        return $('<li class="productListItem"></li>')
            .append(name)
            .append(payment)
            .append(quantity);
    }
});


cart.Product = Backbone.Model.extend({
    defaults: {
        quantity_power: 1,
        id: null,
        name: null,
        price: '0', // 表示用
        unit_template: null
    },
    initialize: function() {
        
    }
});

cart.ProductQuantity = Backbone.Model.extend({

});

cart.ProductQuantityCollection = Backbone.Collection.extend({
    defaults: {
        stockType: null
    },
    model: cart.ProductQuantity,
    initialize: function() {
    },

    setStockType: function(stockType) {
        this.url = stockType.productsUrl;
        this.fetch({success: function() {this.change();}});
    }
});

cart.VenueView = Backbone.View.extend({
    initialize: function() {
        // VenueViewer作成
        this.currentViewer = $('.venueViewer');
        this.presenter = this.options.presenter;
        this.readOnly = true;
        var self = this;
        $('#selectSeat .btn-select-seat').click(function () {
            if (self.readOnly)
                return false;
            self.presenter.onSelectPressed();
            return false;
        });
        $('#selectSeat .btn-cancel').click(function () {
            if (self.readOnly)
                return false;
            self.presenter.onCancelPressed();
            return false;
        });
    },
    getChoices: function () {
        var selection = this.currentViewer.venueviewer('selection');
        var retval = [];
        for (var seat_id in selection) {
            retval.push(selection[seat_id]);
        }
        return retval;
    },
    updateVenueViewer: function(dataSource, callbacks) {
        this.currentViewer.venueviewer({
            dataSource: dataSource,
            callbacks: callbacks
        })
        this.currentViewer.venueviewer("load");
        this.render();
    },
    updateUIState: function () {
        if (this.readOnly) {
            this.currentViewer.venueviewer("uimode", "move");
            $('#selectSeat').removeClass('focused');
            $('#selectSeat').addClass('blur');
        } else {
            this.currentViewer.venueviewer("uimode", "select1");
            $('#selectSeat').removeClass('blur');
            $('#selectSeat').addClass('focused');
        }
    },
    render: function() {
        this.updateUIState();
        this.currentViewer.venueviewer("refresh");
    }
});


cart.Venue = Backbone.Model.extend({
    updateDataSource: function(params) {
        var factory = newMetadataLoaderFactory(params.data_source.seats);
        var dataSource = {
          drawing: function (next, error) {
            $.ajax({
              url: params.data_source.venue_drawing,
              dataType: 'xml',
              success: function (data) { next(data); },
              error: function (xhr, text) {
                error("Failed to load drawing data (" + text + ")");
              }
            });
          },
          stockTypes: function (next, error) {
            var stock_types = {};
            for (var i = params.seat_types.length; --i >= 0;)
              stock_types[params.seat_types[i].id] = params.seat_types[i];
            next(stock_types);
          },
          info: factory(function (data) { return data['info']; }),
          seats: factory(function (data) { return data['seats']; }),
          areas: factory(function (data) { return data['areas']; }),
          seat_adjacencies: function (next, error, length) {
            var _params = $.extend(params, { length_or_range: length });
            $.ajax({
              url: util.build_route_path(params.data_source.seat_adjacencies._params),
              dataType: 'json',
              success: function (data) { next(data); },
              error: function (xhr, text) {
                error("Failed to load adjacency data (" + text + ")");
              }
            });
          },
          stock_types: function (next, error) {
            continuations.stock_types_loaded.continuation(next, error);
          }
        };
        this.set('dataSource', dataSource);
        this.trigger(cart.events.ON_VENUE_DATASOURCE_UPDATED);
    },
    defaults: {
    },
    initialize: function() {
    },

});


function newMetadataLoaderFactory(url) {
  var conts = [], allData = null, first = true;
  return function createMetadataLoader(fetch) {
    return function metadataLoader(next, error) {
      conts.push({ fetch: fetch, next: next, error: error });
      if (first) {
        $.ajax({
          url: url,
          dataType: 'json',
          success: function(data) {
            allData = data;
            var _conts = conts;
            conts = [];
            for (var i = 0; i < _conts.length; i++)
              _conts[i].next(_conts[i].fetch(data));
          },
          error: function(xhr, text) {
            var message = "Failed to load " + key + " (reason: " + text + ")";
            var _conts = conts;
            conts = [];
            for (var i = 0; i < _conts.length; i++)
              _conts[i].error(message);
          }
        });
        first = false;
        return;
      } else {
        if (allData)
          next(fetch(allData));
      }
    };
  };
}

function createDataSource(params) {
  var factory = newMetadataLoaderFactory(params.data_source.seats);
  return {
    drawing: function (next, error) {
      $.ajax({
        url: params.data_source.venue_drawing,
        dataType: 'xml',
        success: function (data) { next(data); },
        error: function (xhr, text) {
          error("Failed to load drawing data (" + text + ")");
        }
      });
    },
    stockTypes: function (next, error) {
      var stock_types = {};
      for (var i = params.seat_types.length; --i >= 0;)
        stock_types[params.seat_types[i].id] = params.seat_types[i];
      next(stock_types);
    },
    info: factory(function (data) { return data['info']; }),
    seats: factory(function (data) { return data['seats']; }),
    areas: factory(function (data) { return data['areas']; }),
    seat_adjacencies: function (next, error, length) {
      var _params = $.extend(params, { length_or_range: length });
      $.ajax({
        url: util.build_route_path(params.data_source.seat_adjacencies._params),
        dataType: 'json',
        success: function (data) { next(data); },
        error: function (xhr, text) {
          error("Failed to load adjacency data (" + text + ")");
        }
      });
    },
    stock_types: function (next, error) {
      continuations.stock_types_loaded.continuation(next, error);
    }
  };
}

