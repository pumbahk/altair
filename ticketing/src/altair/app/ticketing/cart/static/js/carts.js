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
    },

    format_currency: function (value) {
        return "￥" + value;
    }
};

cart.order_messages = {
    'no products': {
        title: '購入する枚数を選択してください',
        message: '購入する枚数を選択してください'
    },
    'stock': {
        title: '在庫がありません',
        message: 'ご希望の座席を確保できませんでした'
    },
    'invalid seats': {
        title: 'ご希望の座席が確保できませんでした。',
        message: '画面を最新の情報に更新した上で再度席の選択をしてください。'
    },
    'invalid products': {
        title: 'ご希望の座席が確保できませんでした。',
        message: '画面を最新の情報に更新した上で再度席の選択をしてください。'
    },
    'adjacency': {
        title: '連席で座席を確保できません',
        message: '座席を選んで購入してください'
    },
    'ticket_count_over_upper_bound': {
        title: '上限枚数を超えて購入しようとしています', 
        message: function(order_form_presenter, data) {
            return cart.showErrorDialog(null, data.message, 'btn-close');
        }
    },
    'ticket_count_below_lower_bound': {
        title: '購入枚数が少なすぎます', 
        message: function(order_form_presenter, data) {
            return cart.showErrorDialog(null, data.message, 'btn-close');
        }
    },
    'product_count_over_upper_bound': {
        title: '購入数上限を超えて購入しようとしています', 
        message: function(order_form_presenter, data) {
            return cart.showErrorDialog(null, data.message, 'btn-close');
        }
    },
    'product_count_below_lower_bound': {
        title: '購入数が少なすぎます', 
        message: function(order_form_presenter, data) {
            return cart.showErrorDialog(null, data.message, 'btn-close');
        }
    },
    'too many carts': {
        title: '購入エラー',
        message: '誠に申し訳ございませんが、現在ご購入手続を進めることができない状況となっております。しばらく経ってから再度お試しください。'
    },
    'out_of_term': {
        title: '販売期間終了',
        message: function(order_form_presenter, data) {
            var msg = '誠に申し訳ございませんが、現在選択いただいている条件での販売は終了いたしました。';
            return cart.showErrorDialog(null, msg, 'btn-close');
        }
    }
};

cart.Dialog = function () {
    this.initialize.apply(this, arguments);
};

cart.Dialog.prototype = {
    initialize: function (n, callbacks) {
        var self = this;
        this.n = n.clone();
        this.callbacks = callbacks;
        this.ok = false;
        n.parent().append(this.n);
        this.n.overlay({
            mask: !$.browser.msie || parseInt($.browser.version) >= 8 ? {
                color: "#999",
                opacity: 0.5
            }: null,
            closeOnClick: false,
            onClose: function () {
                var ok = self.ok;
                self.ok = false;
                $.mask.getConf().onClose = function () {
                    setTimeout(function () {
                        if (!ok)
                            self.callbacks.cancel && self.callbacks.cancel.call(self);
                        self.callbacks.close && self.callbacks.close.call(self);
                        self.n.remove();
                    }, 100);
                };
            }
        });
        this.n.on('click', '.cancel-button', function() {
            self.n.overlay().close();
        });
        this.n.on('click', '.ok-button', function() {
            self.ok = true;
            callbacks.ok.call(self);
        });
    },

    close: function () {
        this.n.overlay().close();
    },

    load: function () {
        this.n.overlay().load();
    },

    header: function (n) {
        var h = this.n.find('.modal-header');
        if (n === void(0))
            return h;
        if (n == null) {
            h.remove();
        } else {
            h.empty();
            h.append(n);
        }
    },

    footer: function (n) {
        var f = this.n.find('.modal-footer');
        if (f === void(0))
            return f;
        f.empty();
        f.append(n);
    },

    body: function (n) {
        var b = this.n.find('.modal-body');
        if (n === void(0))
            return b;
        b.empty();
        b.append(n);
    }
};

cart.events = {
    ON_SALES_SEGMENT_RESOLVED: "onSalesSegmentResolved",
    ON_STOCK_TYPE_SELECTED: "onStockTypeSelected",
    ON_CART_CANCELED: "onCartCanceled",
    ON_CART_ORDERED: "onCartOredered",
    ON_VENUE_DATASOURCE_UPDATED: "onVenueDataSourceUpdated"
};
cart.init = function(salesSegmentsSelection, selected, cartReleaseUrl, venueEnabled, spinnerPictureUrl) {
    this.app = new cart.ApplicationController();
    venueEnabled = venueEnabled && (!$.browser.msie || parseInt($.browser.version) >= 9);
    this.app.init(salesSegmentsSelection, selected, cartReleaseUrl, venueEnabled, spinnerPictureUrl);
    $('body').bind('selectstart', function() { return false; });
};

cart.createContentOfShoppingElement = function(product) {
	var comma = function(s, f) {
		var to = String(s);
		var tmp = "";
		while(to != (tmp = to.replace(/^([+-]?\d+)(\d\d\d)/,"$1,$2"))) {
			to = tmp;
		}
		return to;
	};
    var item = $('<tr/>');
    var name = $('<td/>').text(product.name);
    var price = $('<td/>').text("￥ "+comma(product.price));
    var quantity = $('<td/>');
    cart.util.render_template_into(quantity, product.unit_template, {num: product.quantity});
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

cart.proceedToCheckout = function proceedToCheckout(performance, reservationData) {
    var dialog = new cart.Dialog($('#order-reserved'), {
        ok: function () {
            window.location.href = reservationData.payment_url;
        },
        cancel: function () {
            $.ajax({
                url: cartReleaseUrl, // global
                dataType: 'json',
                type: 'POST',  
                success: function() {}
            });
            this.close();
        }
    });
    var products = reservationData.cart.products;
    var inCartProductList = dialog.body().find('.contentsOfShopping');
    var totalAmount = dialog.body().find('.cart-total-amount');

    // insert product items in cart
    inCartProductList.empty();
    for (var i = 0; i < products.length; i++) {
        var product = products[i];
        var item = cart.createContentOfShoppingElement(product);
        inCartProductList.append(item);
    }
    inCartProductList.find("tr").last().addClass("last-child");
    totalAmount.text(cart.util.format_currency(reservationData.cart.total_amount));

    dialog.header(
        $('<h2>')
            .append(
                $('<span id="performance-date"></span>')
                .text(performance.get('performance_start')))
            .append(' ')
            .append(
                $('<span id="performance-name"></span>')
                .text(performance.get('performance_name'))));

    if (reservationData.cart.separate_seats) {
        var warning = $('<span>※お並びの座席ではありません</span>');
        warning.attr('style', 'color: #bf191f; font-weight: bold;');
        dialog.n.find('.modal-inner p:last-child').append(warning);
    }
    dialog.load();
};

cart.showErrorDialog = function showErrorDialog(title, message, footer_button_class) {
    var errorDialog = new this.Dialog($('#order-error-template'), {
        ok: function () {
            this.close();
        }
    });
    errorDialog.header(title ? $('<h2></h2>').text(title): null);
    errorDialog.body($('<div style="text-align:center"></div>').text(message));
    errorDialog.footer($('<a class="ok-button">閉じる</a>').addClass(footer_button_class));
    errorDialog.load();
};

cart.showSeparateSeatOrderDialog = function showSeparateSeatOrderDialog(title, presenter) {
    var message = '連席でお席をご用意することができません。<br>'
                + 'それでもお席を確保したい場合は「購入する」を、<br>'
                + '改めて席を選び直す場合は「座席・枚数を選びなおす」をお選びください。';
    var error_modal = $('#order-error-template');
    var retry_modal = error_modal.clone().attr('id', 'order-retry-template');
    error_modal.parent().append(retry_modal);
    var okPressed = false;
    var dialog = new this.Dialog(retry_modal, {
        ok: function () {
            okPressed = true;
            this.close();
        },
        close: function () {
            if (okPressed)
                presenter.onEntrustSeparateSeatPressed();
        }
    });
    dialog.header(title ? $('<h2></h2>').text(title): null);
    dialog.body($('<div style="text-align:center"></div>').html(message));
    dialog.footer(
        $('<div>')
            .append($('<a class="cancel-button btn-redo">座席・枚数を選びなおす</a>'))
            .append($('<a class="ok-button btn-buy">購入する</a>'))
    );
    dialog.load();
};

cart.ApplicationController = function() {
};

cart.ApplicationController.prototype.init = function(salesSegmentsSelection, selected, cartReleaseUrl, venueEnabled, spinnerPictureUrl) {
    this.performanceSearch = new cart.PerformanceSearch({
        salesSegmentsSelection: salesSegmentsSelection,
        key: selected[1],
        defaultSalesSegmentId: null
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
        performance: this.performance,
        firstSelection: selected
    });
    // 対応するビューがないので直接
    this.performance.on("change", function () {
        $('#performanceDate').text(this.get('performance_name'));
        $('#descPerformanceDate').text(this.get('performance_start'));
        $('#performanceVenue').text(this.get('venue_name'));
        $(".performanceNameSpace").text(this.get('performance_name'));
    });
    // 席種
    this.stockTypeListPresenter = new cart.StockTypeListPresenter({
        viewType: cart.StockTypeListView,
        performance: this.performance
    });
    // 会場図
    this.venuePresenter = new cart.VenuePresenter({
        viewType: venueEnabled ? cart.VenueView: cart.DummyVenueView,
        performance: this.performance,
        stockTypeListPresenter: this.stockTypeListPresenter,
        spinnerPictureUrl: spinnerPictureUrl || '/cart/static/img/settlement/loading.gif'
    });
    // フォーム
    this.orderFormPresenter = new cart.OrderFormPresenter({
        viewType: cart.OrderFormView,
        venuePresenter: this.venuePresenter,
        seatSelectionEnabled: venueEnabled
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
            model: this.performanceSearch,
            el: $("#form1")
        });
        this.view.on(cart.events.ON_SALES_SEGMENT_RESOLVED,
            function(salesSegmentId) {self.onSalesSegmentResolved(salesSegmentId);});
        this.view.setInitialValue(this.firstSelection[0], this.firstSelection[1]);
    },
    onSalesSegmentResolved: function(salesSegmentId) {
        var self = this;
        var salesSegment = this.performanceSearch.getSalesSegment(salesSegmentId);
        this.performance.url = salesSegment.seat_types_url;
        this.performance.fetch();
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
        function callback(data) {
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

        var products = stock_type.get('products');
        if (products)
            callback({ 'products': products });
        else
            $.getJSON(products_url, callback);
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
        viewType: null
    },
    initialize: function() {
        var self = this;
        this.callbacks = {
            selectable: function () { return self.selectable.apply(self, arguments); },
            click: function () { self.click.apply(self, arguments); },
            error: function (err) {
                alert(err);
            },
            queryAdjacency: function (id, adjacency, success, failure) {
                var candidates = null;
                if (self.seatGroups) {
                    var seatGroupId = self.seatIdToSeatGroup[id];
                    if (seatGroupId !== void(0)) {
                        var seatGroup = self.seatGroups[seatGroupId];
                        if (seatGroup['seats'].length <= adjacency)
                            candidates = [seatGroup['seats']];
                        else
                            candidates = [];
                    }
                }
                if (candidates === null)
                    candidates = [[id]];
                success(candidates);
            }
        };
        this.view = new this.viewType({
            presenter: this,
            spinnerPictureUrl: this.spinnerPictureUrl
        });
        this.performance.on("change",
            function() {self.onPerformanceChanged();});
        this.selectedStockType = null;
        this.quantityToSelect = null;
        this.stockIdToSelect = null;
        this.seatGroups = {};
        this.seatIdToSeatGroup = {};
    },
    onPerformanceChanged: function() {
        if (!this.view.readOnly) {
            this.setStocks(null, null);
            this.view.reset();
        }
        var dataSource = this.performance.createDataSource(this);
        this.view.updateVenueViewer(dataSource, this.callbacks);
    },
    onCancelPressed: function () {
        this.setStocks(null, null);
        this.view.reset();
    },
    onSelectPressed: function () {
        var selection = this.view.getChoices();
        if (selection.length < this.quantityToSelect) {
            cart.showErrorDialog(null, "あと " + (this.quantityToSelect - selection.length) + " 席選んでください", "btn-close");
            return;
        } else if (selection.length != this.quantityToSelect) {
            cart.showErrorDialog("エラー", "購入枚数と選択した席の数が一致していません。", "btn-close");
            return;
        }
        this.orderFormPresenter.setSeats(selection);
        this.orderFormPresenter.doOrder();
    },
    setStockType: function (stock_type, quantity_to_select) {
        this.selectedStockType = stock_type;
        var self = this;
        if (this.selectedStockType) {
            self.quantityToSelect = quantity_to_select;
            self.stockTypeListPresenter.setActivePane('venue');
            if (self.view.currentDataSource._reset !== void(0))
                self.view.currentDataSource._reset();
            this.view.currentViewer.venueviewer('loadSeats', function() {
                self.view.setAdjacency(self.quantityToSelect);
                self.view.render();
                self.view.currentDataSource.seatGroups(function (data) {
                    self.seatGroups = data;
                    var seatIdToSeatGroup = {};
                    for (var k in data) {
                        var seatGroup = data[k];
                        var seats = seatGroup['seats'];
                        for (var i = seats.length; --i >= 0; )
                            seatIdToSeatGroup[seats[i]] = k;
                    }
                    self.seatIdToSeatGroup = seatIdToSeatGroup;
                });
            });
        } else {
            self.quantityToSelect = null;
            self.stockTypeListPresenter.setActivePane('stockTypeList');
        }
    },
    setStocks: function (stock_type, quantities_per_stock_id) {
        this.selectedStockType = stock_type;
        var self = this;
        if (this.selectedStockType) {
            var quantityToSelect = null;
            var stockIdToSelect = null;
            for (var stockId in quantities_per_stock_id) {
                if (quantities_per_stock_id[stockId] > 0) {
                    if (stockIdToSelect)
                        throw new Exception("more than one stock");
                    quantityToSelect = quantities_per_stock_id[stockId];
                    stockIdToSelect = stockId;
                }
            }
            if (!stockIdToSelect)
                throw new Exception("no stocks");
            self.stockIdToSelect = stockIdToSelect;
            self.quantityToSelect = quantityToSelect;
            self.stockTypeListPresenter.setActivePane('venue');
            if (self.view.currentDataSource._reset !== void(0))
                self.view.currentDataSource._reset();
            this.view.currentViewer.venueviewer('loadSeats', function() {
                self.view.setAdjacency(self.quantityToSelect);
                self.view.render();
                self.view.currentDataSource.seatGroups(function (data) {
                    self.seatGroups = data;
                    var seatIdToSeatGroup = {};
                    for (var k in data) {
                        var seatGroup = data[k];
                        var seats = seatGroup['seats'];
                        for (var i = seats.length; --i >= 0; )
                            seatIdToSeatGroup[seats[i]] = k;
                    }
                    self.seatIdToSeatGroup = seatIdToSeatGroup;
                });
            });
        } else {
            self.stockIdToSelect = null;
            self.quantityToSelect = null;
            self.stockTypeListPresenter.setActivePane('stockTypeList');
        }
    },
    currentSeatsUrl: function () {
        return this.selectedStockType.get('seats_url2').replace(/__stock_id__/, this.stockIdToSelect);
    },
    selectable: function (viewer, seat) {
        if (!this.selectedStockType) {
            return true;
        }
        var isValidStockType = (seat.meta.stock_type_id == this.selectedStockType.id);
        var isVacant = (seat.meta.status == 1);
        return isValidStockType && isVacant && seat.meta.is_hold;
    },

    click: function (viewer, highlighted) {
        // クリック位置から、座席選択をする
        var self = this;
        var seatsToSelect = {};
        $.each(highlighted, function (id, seat) {
            var seatGroupId = self.seatIdToSeatGroup[id];
            var seatsInGroup = [id];
            if (seatGroupId !== void(0))
                seatsInGroup = self.seatGroups[seatGroupId]['seats'];
            for (var i = seatsInGroup.length; --i >= 0; )
                seatsToSelect[seatsInGroup[i]] = true;
        });

        for (var id in seatsToSelect)
            seatsToSelect[id] = viewer.seats[id];

        $.each(seatsToSelect, function (id, seat) {
            if (seat.selected()) {
                seat.selected(false);
            } else {
                if (viewer.selectionCount < self.quantityToSelect)
                    seat.selected(true);
            }
        });
    }
};
_.extend(cart.VenuePresenter.prototype, Backbone.Event);


cart.PerformanceSearchView = Backbone.View.extend({
    initialize: function() {
        var self = this;
        this.selection = this.$el.find("#date-select");
        this.selection.on("change", function() { self.onKeySelectionChanged(this.value); });
        this.salesSegmentSelection = this.$el.find("#venue-select");
        this.salesSegmentSelection.on("change", function() {self.onSalesSegmentSelectionChanged(this.value)});

        this.model.on("change:key", function (model, value) { self.onKeyChanged(value); });
    },
    renderKeySelection: function () {
        // 公演名
        this.selection.empty();
        var self = this;
        var keys = this.model.getKeys();
        $.each(keys, function (_, v) {
            self.selection.append($('<option></option>').attr('value', v).text(v));
        });
        this.selection.val(this.model.get("key"));
    },
    onKeySelectionChanged: function (value) {
        this.model.set("key", value);
    },
    renderSalesSegmentSelection: function() {
        var key = this.model.get('key');
        var salesSegments = this.model.getSalesSegments(key);
        this.salesSegmentSelection.empty();
        // 公演会場選択
        for (var i = 0; i < salesSegments.length; i++) {
            var salesSegment = salesSegments[i];
            var opt = $('<option/>');
            $(opt).attr('value', salesSegment.id);
            $(opt).text(salesSegment.name_pc);
            this.salesSegmentSelection.append(opt);
        }
        var salesSegmentId = this.model.get('defaultSalesSegmentId');
        if (salesSegmentId) {
            this.salesSegmentSelection.val(salesSegmentId);
            this.onSalesSegmentSelectionChanged(salesSegmentId);
        }

    },
    onSalesSegmentSelectionChanged: function(value) {
        this.trigger(cart.events.ON_SALES_SEGMENT_RESOLVED, value);
    },
    onKeyChanged: function(key) {
        this.selection.val(key);
        this.model.set("defaultSalesSegmentId", this.model.getSalesSegments(key)[0].id); 
        this.renderSalesSegmentSelection();
    },
    render: function() {
        this.renderKeySelection();
        this.renderSalesSegmentSelection();
    },
    setInitialValue: function(key, salesSegmentId) {
        this.model.set("defaultSalesSegmentId", salesSegmentId);
        this.model.set("key", key, { silent: true });
        this.render();
    }
});

cart.PerformanceSearch = Backbone.Model.extend({
    defaults: {
        salesSegmentsSelection: null,
        key: null
    },
    getKeys: function() {
        var retval = [];
        var selections = this.get('salesSegmentsSelection');
        for (var i=0; i < selections.length; i++) {
            retval.push(selections[i][0]);
        }
        return retval;
    },
    getSalesSegments: function(key) {
        var selections = this.get('salesSegmentsSelection');
        for (var i=0; i < selections.length; i++) {
            if (selections[i][0] == key) {
                return selections[i][1];
            }
        }
        return [];   
    },
    getSalesSegment: function(id) {
        var salesSegments = this.getSalesSegments(this.get("key"));
        for (var i = 0; i < salesSegments.length; i++) {
            var salesSegment = salesSegments[i];
            if (salesSegment.id == id) {
                return salesSegment;
            }
        }
    }
});

cart.Performance = Backbone.Model.extend({
    createDataSource: function(venuePresenter) {
        var params = this.attributes;
        var factory_i = newMetadataLoaderFactory(params['data_source']['info']);
        var factory_s = newMetadataLoaderFactory(function () { return venuePresenter.currentSeatsUrl(); });
        var drawingCache = {};
        return {
            drawing: function (page) {
                return function (next, error) {
                    var data = drawingCache[page];
                    if (data) {
                        next(data);
                        return;
                    }
                    $.ajax({
                        url: params['data_source']['venue_drawings'][page],
                        dataType: 'xml',
                        headers: {
                            'X-Dummy': true
                        },
                        success: function (data) {
                            drawingCache[page] = data;
                            next(data);
                        },
                        error: function (xhr, text, status) {
                            error("Failed to load drawing data (" + text + " - " + status + ")");
                        }
                    });
                }
            },
            stockTypes: function (next, error) {
                var stock_types = {};
                for (var i = params.seat_types.length; --i >= 0;)
                    stock_types[params.seat_types[i].id] = params.seat_types[i];
                next(stock_types);
            },
            info: factory_i.create(function (data) { return data['info']; }),
            seats: factory_s.create(function (data) { return data['seats']; }),
            areas: factory_i.create(function (data) { return data['areas']; }),
            seatGroups: factory_s.create(function (data) { return data['seat_groups'] }),
            seatAdjacencies: function (next, error, length) {
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
            pages: factory_i.create(function (data) { return data['pages']; }),
            _reset: function () {
                factory_i.reset();
                factory_s.reset();
            }
        };
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
            var style = stockType.get("style");
            $('<li></li>')
                .append($('<div class="seatListItemInner"></div>')
                   .append(
                     $('<input type="radio" name="seat_type" />')
                     .attr('value', stockType.get("products_url"))
                     .data('stockType', stockType))
                   .append(
                     $('<span class="seatColor"></span>')
                     .css('background-color', style && style.fill && style.fill.color ? style.fill.color: 'white'))
                   .append(
                     $('<span class="seatName"></span>')
                     .text(stockType.get("name")))
                   .append(
                     $('<span class="seatState"></span>')
                     .text(stockType.get("availability_text"))))
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
    defaults: {
        seatSelectionEnabled: true
    },

    initialize: function() {
        this.view = new this.viewType({
            el: $('#selectProductTemplate'),
            updateHandler: $('#seatTypeList').data('updateArrowpos'),
            presenter: this,
            seatSelectionEnabled: this.seatSelectionEnabled
        });
        this.stock_type = null;
        this.products = null;
        this.quantity_to_select = null;
        this.product_quantity_to_select = null;
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
        var total_quantity = 0;
        var total_product_quantity = 0;
        var quantities = {};
        var quantities_per_stock_id = {}
        var selection = this.view.getChoices();
        for (var product_id in selection) {
            var product_quantity = selection[product_id];
            var product = this.products.get(product_id);
            var quantity = product.get('quantity_power') * product_quantity;
            quantities[product_id] = {
                quantity: quantity,
                product_quantity: product_quantity
            };
            var elements = product.get('elements');
            for (stock_id in elements) {
                var element = elements[stock_id];
                if (element['is_seat_stock_type'])
                    quantities_per_stock_id[stock_id] = (quantities_per_stock_id[stock_id] || 0) + element['quantity'] * product_quantity;
            }
            total_quantity += quantity;
            total_product_quantity += product_quantity;
        }
        return {
            total_quantity: total_quantity,
            total_product_quantity: total_product_quantity,
            quantities: quantities,
            quantities_per_stock_id: quantities_per_stock_id
        };
    },
    assertQuantityWithinBounds: function () {
        var result = this.calculateQuantityToSelect();
        if (result.total_quantity == 0) {
            this.showNoSelectProductMessage();
            return false;
        }
        var min_quantity = this.stock_type.get('min_quantity');
        var max_quantity = this.stock_type.get('max_quantity');
        var min_product_quantity = this.stock_type.get('min_product_quantity');
        var max_product_quantity = this.stock_type.get('max_product_quantity');
        if (min_quantity != null && min_quantity > result.total_quantity) {
            this.showTicketCountBelowLowerBoundMessage(min_quantity);
            return false;
        }
        if (max_quantity != null && max_quantity < result.total_quantity) {
            this.showTicketCountAboveUpperBoundMessage(max_quantity);
            return false;
        }
        if (min_product_quantity != null && min_product_quantity > result.total_product_quantity) {
            this.showProductCountBelowLowerBoundMessage(min_product_quantity);
            return false;
        }
        if (max_product_quantity != null && max_product_quantity < result.total_product_quantity) {
            this.showProductCountAboveUpperBoundMessage(max_product_quantity);
            return false;
        }
        var stocks = this.stock_type.get('stocks');
        var l = 0;
        for (var stockId in result.quantities_per_stock_id) {
            for (var i = stocks.length; --i >= 0; ) {
                if (stockId == stocks[i])
                    break;
            }
            if (i < 0) {
                this.showInfeasiblePurchaseMessage();
                return false;
            }
            if (result.quantities_per_stock_id[stockId] != 0)
                ++l;
        }
        if (l != 1) {
            // FIXME
            this.showInfeasiblePurchaseMessage();
            return false;
        }
        return result;
    },
    onSelectSeatPressed: function () {
        var result = this.assertQuantityWithinBounds();
        if (!result)
            return;
        this.venuePresenter.setStocks(this.stock_type, result.quantities_per_stock_id);
    },
    onEntrustPressed: function (order_url) {
        if (!this.assertQuantityWithinBounds())
            return;
        this.setSeats([]);
        this.doOrder(order_url);
    },
    onEntrustSeparateSeatPressed: function () {
        this.onEntrustPressed(cart.app.performance.get('order_separate_seats_url'));
    },
    showNoSelectProductMessage: function(){
        cart.showErrorDialog(null, '商品を1つ以上選択してください', 'btn-close');
        return;
    }, 
    showTicketCountAboveUpperBoundMessage: function(min_quantity) {
        cart.showErrorDialog(null, '枚数は合計' + min_quantity + '枚以内で選択してください', 'btn-close');
        return;
    }, 
    showTicketCountBelowLowerBoundMessage: function(max_quantity) {
        cart.showErrorDialog(null, '枚数は合計' + max_quantity + '枚以上で選択してください', 'btn-close');
        return;
    }, 
    showProductCountAboveUpperBoundMessage: function(min_quantity) {
        cart.showErrorDialog(null, '商品個数は合計' + min_quantity + '個以内にしてください', 'btn-close');
        return;
    }, 
    showProductCountBelowLowerBoundMessage: function(max_quantity) {
        cart.showErrorDialog(null, '商品個数は合計' + max_quantity + '個以上にしてください', 'btn-close');
        return;
    }, 
    showInfeasiblePurchaseMessage: function() {
        cart.showErrorDialog(null, '申し訳ございませんが、その商品の組み合わせはお選びいただけません', 'btn-close');
        return;
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
    doOrder: function (order_url) {
        var self = this;
        var performance = cart.app.performance;
        var values = this.orderForm.serialize();
        $.ajax({
            url: order_url || performance.get('order_url'),
            dataType: 'json',
            data: values,
            type: 'POST',
            async: false,
            success: function(data, textStatus, jqXHR) {
                if (data.result == 'OK') {
                    cart.proceedToCheckout(performance, data);
                } else {
                    var japanized_message = cart.order_messages[data.reason];
                    if(!japanized_message){
                        alert(data.reason);
                    } else if (typeof japanized_message.message == "function") {
                        japanized_message.message(self, data);
                    } else if (data.reason == 'adjacency' && performance.get('order_separate_seats_url')) {
                        cart.showSeparateSeatOrderDialog(japanized_message.title, self);
                    } else {
                        cart.showErrorDialog(japanized_message.title, japanized_message.message, 'btn-redo');
                    }
                }
            }
        });
    }
};

_.extend(cart.OrderFormPresenter.prototype, Backbone.Event);

cart.OrderFormView = Backbone.View.extend({
    defaults: {
        el: $('#selectProductTemplate'),
        selected_stock_type_el: null,
        seatSelectionEnabled: true
    },
    initialize: function() {
        this.presenter = this.options.presenter;
        this.updateHandler = this.options.updateHandler;
        this.seatSelectionEnabled = this.options.seatSelectionEnabled;
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
        if (!stock_type.get('actual_availability'))
            return false;
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
            payment_seat_products.append(self.buildProduct(product, products.length == 1));
        });
        var description = orderForm.find('.selectProduct-description');
        var descriptionText = stock_type.get('description');
        if (!descriptionText)
            description.remove();
        else
            description.html(descriptionText);
        var btn_select_seat = orderForm.find('.btn-select-buy');
        var btn_entrust = orderForm.find('.btn-entrust-buy');
        var btn_buy = orderForm.find('.btn-buy');

        if (stock_type.get("quantity_only")) {
            btn_select_seat.parent().css('display', 'none');
            btn_entrust.parent().css('display', 'none');
            btn_buy.parent().css('display', null);
        } else {
            if (self.seatSelectionEnabled && stock_type.get("seat_choice")) {
                btn_select_seat.parent().css('display', null);
                btn_entrust.parent().css('display', null);
            } else {
                btn_select_seat.parent().css('display', 'none');
                btn_entrust.parent().css('display', null);
            }
            btn_buy.parent().css('display', 'none');
        }
        btn_select_seat.click(function () { self.presenter.onSelectSeatPressed(); return false; });
        btn_entrust.one('click', function () {
            self.presenter.onEntrustPressed();
            $(this).one('click', arguments.callee);
            return false;
        });
        btn_buy.one('click', function () {
            self.presenter.onBuyPressed();
            $(this).one('click', arguments.callee);
            return false;
        });

        return orderForm;
    },
    buildProduct: function(product, singleton) {
        var min_product_quantity_per_product = product.get('min_product_quantity_per_product');
        var max_product_quantity_per_product = product.get('max_product_quantity_per_product');
        var min_product_quantity_from_product = product.get('min_product_quantity_from_product');
        var must_be_chosen = product.get('must_be_chosen');
        if (must_be_chosen === undefined)
            must_be_chosen = false;
        var name = $('<span class="productName"></span>');
        name.text(product.get("name"));
        var payment = $('<span class="productPrice"></span>');
        payment.text('￥' + product.get("price"));
        var quantityBox = $('<span class="productQuantity"></span>');
        var pullDown = $('<select />').attr('name', 'product-' + product.id);
        var possible_quantities = [];
        var min = 0, max = max_product_quantity_per_product;
        if (singleton)
            min = min_product_quantity_per_product;
        if (min_product_quantity_from_product !== null)
            min = Math.max(min, min_product_quantity_from_product);
        if (min > 0 && !must_be_chosen)
            possible_quantities.push(0);
        if (min == 0 && must_be_chosen)
            min = 1;
        for (var i = min; i <= max; i++) {
            possible_quantities.push(i);
        }
        for (var i = 0; i < possible_quantities.length; i++) {
            var quantity = possible_quantities[i];
            $('<option></option>').text(quantity).val(quantity).appendTo(pullDown);
        }
        var descriptionText = product.get('description');
        var description = descriptionText ?
            $('<div class="productListItem-description"></div>').html(product.get('description')): //xxx.
            $();
        cart.util.render_template_into(quantityBox, product.get("unit_template"), { num: pullDown });
        return $('<li class="productListItem"></li>')
            .append(quantityBox)
            .append(payment)
            .append(name)
            .append(description);
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
        this.zoomRatioMin = 1;
        this.zoomRatioMax = 2.5;
        this.updateQueue = [];
        this.currentDataSource = null;
        this.spinnerPictureUrl = this.options.spinnerPictureUrl;

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
        var verticalSlider = $('<div></div>').smihica_vertical_slider({
            'height': 100,
            onchange: function (pos) {
                var level = pos * pos;
                var zoomRatio = self.zoomRatioMin + ((self.zoomRatioMax - self.zoomRatioMin) * level);
                try {
                    self.currentViewer.venueviewer("zoom", zoomRatio);
                } catch (e) {}
            }
        }).css({
            'visibility': 'hidden',
            'position': 'absolute',
            'left': '20px',
            'top': '20px'
        });
        verticalSlider.appendTo(this.currentViewer.parent());
        this.verticalSlider = verticalSlider;
        this.tooltip = $('<div class="tooltip"></div>')
            .css({
                'position': 'absolute'
            })
            .appendTo(document.body);
    },
    setAdjacency: function (adjacency) {
        this.currentViewer.venueviewer('adjacency', adjacency);
    },
    getChoices: function () {
        var selection = this.currentViewer.venueviewer('selection');
        var retval = [];
        for (var seat_id in selection) {
            retval.push(selection[seat_id]);
        }
        return retval;
    },
    updateVenueViewer: function (dataSource, callbacks) {
		this.verticalSlider.css({ visibility: 'hidden' });

        this.updateQueue.push({ dataSource: dataSource, callbacks: callbacks });
        if (!this.loading)
            this._handleQueue();
    },
    _handleQueue: function () {
        var self = this;

        if (this.updateQueue.length == 0)
            return;

        var updateReq = this.updateQueue.shift();
        var dataSource = updateReq.dataSource;
        var callbacks = updateReq.callbacks;

        this.currentViewer.venueviewer("remove");

        var loadingLayer = null;
        var loadPartCount = 0;
        var spinnerPictureUrl = this.spinnerPictureUrl;
        var _callbacks = $.extend($.extend({}, callbacks), {
            zoomRatioChanging: function (zoomRatio) {
                return Math.min(Math.max(zoomRatio, self.zoomRatioMin), self.zoomRatioMax);
            },
            zoomRatioChange: function (zoomRatio) {
                var pos = Math.sqrt((zoomRatio - self.zoomRatioMin) / (self.zoomRatioMax - self.zoomRatioMin));
                self.verticalSlider.smihica_vertical_slider('position', pos);

                if (1.2 < zoomRatio) {
                    self.currentViewer.venueviewer('showSmallTexts');
                } else {
                    self.currentViewer.venueviewer('hideSmallTexts');
                }

            },
            load: function (viewer) {
                self.zoomRatioMin = viewer.zoomRatioMin;
                viewer.zoom(viewer.zoomRatioMin);
                self.updateUIState();
                callbacks.load && callbacks.load.apply(this, arguments);
                self._handleQueue();
            },
            loadPartStart: function (viewer, part) {
                var self = this;
                if (loadPartCount == 0) {
                    loadingLayer =
                        $('<div></div>')
                        .append(
                            $('<div></div>')
                            .css({ position: 'absolute', width: '100%', height: '100%', backgroundColor: 'white', opacity: 0.75 })
                            .append(
                                $('<img />')
                                .attr('src', spinnerPictureUrl)
                                .css({ marginTop: self.canvas.height() / 2 - 16 })
                            )
                        )
                        .append(
                            $('<div></div>')
                            .css({ position: 'absolute', width: '100%', height: '100%' })
                            .append(
                                $('<div>読込中です</div>')
                                .css({ marginTop: self.canvas.height() / 2 + 16 })
                            )
                        )
                        .css({
                            position: 'absolute',
                            width: '100%',
                            height: '100%',
                            marginTop: -self.canvas.height(),
                            textAlign: 'center'
                        });
                    self.canvas.after(loadingLayer);
                }
                loadPartCount++;
            },
            loadPartEnd: function (viewer, part) {
                // part = pages, stockTypes, info, seats, drawing
                var page = viewer.currentPage;

                if (!--loadPartCount) {
                    if (loadingLayer) {
                        loadingLayer.remove();
                        loadingLayer = null;
                    }
                }

                if (part == 'info') {
                    var use_seatmap = $.map(viewer.stockTypes, function(st) {
                        return (!st.quantity_only && st.seat_choice) ? st : null;
                    });
                    var showGuidance = viewer.rootPage && 0 < use_seatmap.length;
                    $('.selectSeatLeftPane .guidance').css({ display: showGuidance ? '' : 'none' });
                    $('.selectSeatLeftPane .guidance').each(function() {
                        if($(this).hasClass('without-venue')) {
                            $(this).css({ display: showGuidance ? 'none' : '' });
                        }
                    });
                }

                if (part == 'drawing') {
                    if(page) {
                        self.verticalSlider.css({ visibility: viewer.pages[page].zoomable===false ? 'hidden' : 'visible' });
                    }
                }

                if (part == 'drawing') {
                    $('.pageSwitchPanel').remove();
                    var ul = $('<ul></ul>');
                    ul
                        .addClass('pageSwitchPanel')
                        .css({ position: 'absolute', top: 10, right : 20, left: 40, textAlign: 'right' });
                    var pages = [ ];
                    for(var k in viewer.pages) {
                        if(!viewer.pages[k].hidden) {
                            viewer.pages[k]._filename = k;
                            pages.push(viewer.pages[k]);
                        }
                    }
                    pages = pages.sort(function(a, b) { return a.order == b.order ? 0 : a.order < b.order ? -1 : +1; });
                    for(var idx in pages) {
                        $('<li></li>')
                            .css({ display: 'inline-block', height: 20, verticalAlign: 'middle', border: '1px solid gray', paddingLeft: 4, paddingRight: 4, marginBottom: 4, marginLeft: 4, cursor: 'pointer', backgroundColor: 'ffffff' })
                            .attr('filename', pages[idx]._filename)
                            .click(function() {
                                viewer.navigate($(this).attr('filename'));
                            })
                            .text(pages[idx].short_name || pages[idx].name).appendTo(ul);
                    }
                    if(page && viewer.pages[page] && viewer.pages[page].zoomable===false) {
                        ;
                    } else if($('li', ul).size() == 1 && $('li', ul).eq(0).attr('filename') == page) {
                        ;
                    } else if(1 <= $('li', ul).size()) {
                        $('li', ul).each(function() {
                            var filename = $(this).attr('filename');
                            $(this).css({ backgroundColor: (filename == page) ? '#cccccc' : '#ffffff' });
                        });
                        $('.venueViewerWrapper').append(ul);
                    }
                }
            },
            message: function (msg) {
                console.log(msg);
            },
            messageBoard: (function() {
                if (self.tooltip)
                    self.tooltip.hide();
                var lastPosition = { x: 0, y: 0 };
                $(document.body).mousemove(function(e){
                    lastPosition = { x: e.pageX, y: e.pageY };
                    if (self.tooltip) {
                        self.tooltip.css({
                            left: (lastPosition.x + 10) + 'px', 
                            top:  (lastPosition.y + 10) + 'px'
                        });
                    }
                });
                return {
                    up: function(msg) {
                        if (self.tooltip) {
                            if (msg)
                                self.tooltip.stop(true, true).show().text(msg).fadeIn(200);
                        }
                    },
                    down: function() {
                        if (self.tooltip)
                            self.tooltip.stop(true, true).fadeOut(200);
                    }
                }
            })()
        });

        this.currentViewer.venueviewer({
            dataSource: dataSource,
            callbacks: _callbacks,
            viewportSize: { x: 490, y: 430 },
            deferSeatLoading: true
        });
        this.currentDataSource = dataSource;
        this.currentViewer.venueviewer("load");
    },
    updateUIState: function () {
        if (this.readOnly) {
            this.currentViewer.venueviewer("uimode", "move");
            $('#selectSeat').removeClass('focused');
            $('#selectSeat').addClass('blur');
        } else {
            this.currentViewer.venueviewer("uimode", "select");
            $('#selectSeat').removeClass('blur');
            $('#selectSeat').addClass('focused');
        }
    },
    render: function() {
        this.updateUIState();
        this.currentViewer.venueviewer("refresh");
    },
    reset: function () {
        this.currentViewer.venueviewer("unselectAll");
        this.currentViewer.venueviewer("destroySeats");
        this.currentViewer.venueviewer("navigate", this.currentViewer.venueviewer("root"));
    }
});


cart.DummyVenueView = Backbone.View.extend({
    initialize: function() {},
    updateVenueViewer: function (dataSource, callbacks) {
        dataSource.pages(function(pages) {
            if(0 < $(pages).size()) {
                $('.venueViewer').append(
                    $('<div class="dummy-venue-viewer"></div>')
                    .css({ position: 'relative',
                           width: '100%',
                           height: '100%' })
                    .append(
                        $('<div style="position: absolute; margin: -8em -40% -8em -40%; top: 50%; left: 50%; width: 80%; height: 15em;"><p>本公演 (試合) でお好みの座席を選択してチケットをお買い求めいただくには、<u>サポート対象のブラウザー</u>をご利用ください。</p><p style="font-weight:bold">※選択の席種から自動的に座席を決定する「おまかせで選択」機能は、全ブラウザーでご利用いただけます。</p><p>サポート対象のブラウザーは以下となっております。</p><ul><li><a href="http://www.google.co.jp/chrome/" target="_blank">Google Chrome</a></li><li><a href="http://www.mozilla.jp/firefox/" target="_blank">Mozilla Firefox 13.0以降</a></li><li><a href="http://windows.microsoft.com/ja-jp/internet-explorer/download-ie" target="_blank">Internet Explorer 9.0以降 (Windows Vista以降)</a></li><li><a href="http://www.apple.com/jp/safari/" target="_blank">Safari 5.0以降</a></li></ul></div>')
                    )
                );
                $('.guidanceBackground').hide();
            } else {
                $('.selectSeatLeftPane .guidance').each(function() {
                    if($(this).hasClass('without-venue')) {
                        $(this).css({ display: '' });
                    }
                });
            }
        });
    },
    updateUIState: function () {
        if (this.readOnly) {
            $('#selectSeat').removeClass('focused');
            $('#selectSeat').addClass('blur');
        } else {
            $('#selectSeat').removeClass('blur');
            $('#selectSeat').addClass('focused');
        }
    },
    render: function() {
        this.updateUIState();
    },
    reset: function () {}
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
              error: function (xhr, text, status) {
                error("Failed to load drawing data (" + text + " - " + status + ")");
              }
            });
          },
          stockTypes: function (next, error) {
            var stock_types = {};
            for (var i = params.seat_types.length; --i >= 0;)
              stock_types[params.seat_types[i].id] = params.seat_types[i];
            next(stock_types);
          },
          info: factory.create(function (data) { return data['info']; }),
          seats: factory.create(function (data) { return data['seats']; }),
          areas: factory.create(function (data) { return data['areas']; }),
          seatAdjacencies: function (next, error, length) {
            var _params = $.extend(params, { length_or_range: length });
            $.ajax({
              url: util.build_route_path(params.data_source.seat_adjacencies._params),
              dataType: 'json',
              success: function (data) { next(data); },
              error: function (xhr, text, status) {
                error("Failed to load adjacency data (" + text + " - " + status + ")");
              }
            });
          }
        };
        this.set('dataSource', dataSource);
        this.trigger(cart.events.ON_VENUE_DATASOURCE_UPDATED);
    },
    defaults: {
    },
    initialize: function() {
    }
});


function newMetadataLoaderFactory(url) {
    var ctx = {
        conts: null,
        data: null,
        first: null,
        reset: function reset() {
            this.conts = [];
            this.data = null;
            this.first = true;
        },
        create: function createMetadataLoader(fetch) {
            return function metadataLoader(next, error) {
                ctx.conts.push({ fetch: fetch, next: next, error: error });
                if (ctx.first) {
                    var _url = typeof url == 'function' ? url(): url;
                    $.ajax({
                        url: _url,
                        dataType: 'json',
                        success: function(data) {
                            ctx.data = data;
                            var _conts = ctx.conts;
                            ctx.conts = [];
                            for (var i = 0; i < _conts.length; i++)
                                _conts[i].next(_conts[i].fetch(data));
                        },
                        error: function(xhr, text) {
                            var message = "Failed to load " + _url + " (reason: " + text + ")";
                            var _conts = ctx.conts;
                            ctx.conts = [];
                            for (var i = 0; i < _conts.length; i++)
                                _conts[i].error && _conts[i].error(message);
                        }
                    });
                    ctx.first = false;
                    return;
                } else {
                    if (ctx.data)
                        next(fetch(ctx.data));
                }
            }
        }
    };
    ctx.reset();
    return ctx;
}

