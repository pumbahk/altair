/**
 * Created with PyCharm.
 * User: odagiriatsushi
 * Date: 12/05/11
 * Time: 10:55
 * To change this template use File | Settings | File Templates.
 */

var util = {
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
    }
};

var carts = {};
carts.init = function(venues_selection, selected, upper_limit, cart_release_url, callbacks) {
    var model = new carts.Model(venues_selection);
    var presenter = new carts.Presenter(model, upper_limit, callbacks);
    carts.appView = new carts.AppView();
    carts.appView.init(presenter);
    $('#date-select').val(selected[1]);
    $('#date-select').change();
    carts.cart_release_url = cart_release_url;
    // initial setup
};


carts.Model = function(perDateVenuesSelection) {
    this.perDateVenuesSelection = perDateVenuesSelection;
    this.seatTypesMap = {};
    this.productsCache = {};
    this.perDateProductsCache = {}
};

carts.Model.prototype.fetch_venues = function() {
};

carts.Model.prototype.fetch_seat_types = function(get_url, callback) {
    var self = this;
    var data = this.seatTypesMap[get_url];
    if (data) {
        callback(data);
        return;
    }
    $.ajax({
        url:get_url,
        dataType: 'json',
        success: function (data) {
            self.seatTypesMap[get_url] = data;
            callback(data);
        }
    });
};

carts.Model.prototype.fetch_products = function(get_url, callback) {
    var self = this;
    var data = this.productsCache[get_url];
    if (data) {
        callback(data);
        return;
    }
    $.ajax({
        url: get_url,
        dataType: 'json',
        success: function (data) {
            self.productsCache[get_url] = data;
            callback(data);
        }
    });
};

carts.Model.prototype.fetch_products_from_date = function(get_url, callback){
    var self = this;
    var data = this.perDateProductsCache[get_url];
    if (data) {
        callback(data);
        return;
    }
    $.ajax({
        url: get_url,
        dateType: "json",
        success: function (data) {
            self.perDateProductsCache[get_url] = data;
            callback(data);
        }
    });
};

carts.AppView = function() {
    this.left_box = null;
    this.right_box = null;
    this.innerPane = null;
    this.dateSelector = null;
    this.venueSelector = null;
    this.orderButton = null;
    this.orderForm = null;
    this.hallName = null;
    this.inCartProductList = null;
    this.totalAmount = null;
    this.reservationDialog = null;
    this.errorDialog = null;
    this.seatTypeList = null;
    this.seatTypeName = null;
    this.productChoices = null;
};

carts.AppView.prototype.show_popup_title = function(event_name, performance_name, performance_start, venu_name) {
    $('#performance-name').text(event_name + " " + performance_name);
    $('#performance-name-sub').text(performance_start + " " + venu_name);
};

carts.AppView.prototype.focusLeftBox = function(){
    var self = this;

    if (this.left_box.hasClass('focused'))
        return;

    if (self.animating)
        return false;

    self.animating = true;

    self.right_box.addClass("blur");
    self.right_box.removeClass("focused");

    this.innerPane.animate({
        scrollLeft: 0,
    }, {
        duration: 300,
        easing: 'swing',
        complete: function () {
            self.left_box.addClass("focused");
            self.left_box.removeClass("blur");
            self.animating = false;
        }
    });

    this.right_box.find("dl").animate({
        opacity: 0
    }, {
        duration: 300,
        easing: 'linear',
        complete: function () {
            self.right_box.find("#payment-seat-products").empty();
            self.right_box.find("#payment-seat-type").empty();
        }
    });
};

carts.AppView.prototype.focusRightBox = function() {
    var self = this;

    if (this.right_box.hasClass('focused'))
        return;

    if (self.animating)
        return false;

    self.animating = true;

    self.left_box.removeClass("focused");
    self.left_box.addClass("blur");

    this.innerPane.animate({
        scrollLeft: 360,
    }, {
        duration: 300,
        easing: 'swing',
        complete: function () {
            self.right_box.addClass("focused");
            self.right_box.removeClass("blur");
            self.animating = false;
        }
    });

    this.right_box.find("dl").animate({
        opacity: 1.
    }, {
        duration: 300,
        easing: 'linear'
    });
};

carts.AppView.prototype.init = function(presenter) {
    var self = this;
    this.left_box = $("#selectSeatType");
    this.right_box = $("#selectSeat");
    this.innerPane = $("#settlementOperation .settlementOperationPaneInner");
    this.dateSelector = $('#date-select');
    this.venueSelector = $("#venue-select");
    this.orderButton = $('#btn-order');
    this.orderForm = $("#order-form");
    this.hallName = $("#hallName");
    this.inCartProductList = $('#contentsOfShopping');
    this.totalAmount = $('#cart-total-amount');
    this.reservationDialog = $('#order-reserved');
    this.errorDialog = $('#order-error-template');
    this.seatTypeList = $('#seatTypeList');
    this.seatTypeName = this.right_box.find('#payment-seat-type');
    this.productChoices = this.right_box.find("#payment-seat-products").empty();


    this.left_box.click(function () {
        if (self.left_box.hasClass('focused'))
            return true;
        self.focusLeftBox();
    });

    this.dateSelector.change(
        function() {
            presenter.on_date_selected($(this).val());
            self.focusLeftBox();
        }
    );
    this.venueSelector.change(
        function(){
            presenter.on_venue_select($(this).text());
            self.focusLeftBox();
        }
    );
    var create_content_of_shopping_element = function(product){
        var item = $('<tr/>');
        var name = $('<td/>').text(product.name);;
        var price = $('<td/>').text("￥ "+product.price);
        var quantity = $('<td/>').text(product.quantity + " 枚");
        item.append(name);
        item.append(price);
        item.append(quantity);
        return item;
    };

    (function () {
        var reservationData = null;

        self.reservationDialog.find('.cancel-button').click(function() {
            $.ajax({
                url: carts.cart_release_url,
                dataType: 'json',
                type: 'POST',  
                success: function() {
                    self.reservationDialog.overlay().close();
                }
            });
        });
        self.reservationDialog.find('.confirm-button').click(function() {
            window.location.href = reservationData.payment_url;
        });

        self.errorDialog.find('.close-button').click(function() {
            self.errorDialog.overlay().close();
        });

        function proceedToCheckout(data) {
            reservationData = data;
            var root = self.hallName;
            var performance_venue = root.find("#performanceVenue").text();
            var products = data.cart.products;

            // insert product items in cart
            self.inCartProductList.empty();
            for (var i = 0; i < products.length; i++) {
                var product = products[i];
                var item = create_content_of_shopping_element(product);//
                self.inCartProductList.append(item);
            }
            self.inCartProductList.find("tr").last().addClass(".last-child");

            self.totalAmount.text("￥ " + data.cart.total_amount);

            self.reservationDialog.overlay({
                mask: {
                    color: "#999",
                    opacity: 0.5
                },
                closeOnClick: false
            });
            self.reservationDialog.overlay().load();
        }

        function error() {
            self.errorDialog.overlay({
                mask: {
                    color: "#999",
                    opacity: 0.5
                },
                closeOnClick: false
            });
            self.errorDialog.overlay().load();
        }

        self.orderButton.click(function (event) {
            var values = self.orderForm.serialize();
            $.ajax({
                url: order_url, //this is global variable
                dataType: 'json',
                data: values,
                type: 'POST',
                success: function(data, textStatus, jqXHR) {
                    if (data.result == 'OK') {
                        proceedToCheckout(data);
                    } else {
                        error();
                    }
                }
            });
            event.stopPropagation(); /* XXX: is this really necessary? */
            return false;
        });
    })();
    this.presenter = presenter;
    this.presenter.init(this);
};

carts.AppView.prototype.set_performance_id = function(performance_id) {
    $('#current-performance-id').val(performance_id);
};

carts.AppView.prototype.update_venues_selectfield = function(venues, selected_date){
    $('#venue-select').empty();
    
    // update select field
    $.each(venues, function(index, value) {
        var o = $('<option/>');
        o.text(value['name']);
        o.attr('value', value['seat_types_url']);
        $('#venue-select').append(o);
    });

    // after field upate then update performance header
    var selected_venue = $("#venue-select").text();
    this.update_performance_header_venue(selected_venue);
};

carts.AppView.prototype.update_performance_header_date = function(selected_date){
    $("#hallName #performanceDate").text(util.datestring_japanize(selected_date));
}
carts.AppView.prototype.update_performance_header_venue = function(selected_venue){
    $("#hallName #performanceVenue").text(selected_venue);
}

carts.AppView.prototype.update_settlement_detail = function(venues, selected_date){
    // update settleElementBox
    var new_td_venues = [];
    $.each(venues, function(index, value){
        new_td_venues.push(value["name"]);
    })
    var root = $("#settlementEventDetail");
    root.find("#venue").text(new_td_venues.join(", "));
    root.find("#performance_date").text(util.datestring_japanize(selected_date));
};

carts.AppView.prototype.update_settlement_pricelist = function(products){
    var arr = [], 
        indices = [], 
        grouped = {};

    // refine product order
    for(var i=0, j=products.length; i<j; i++){
        var product = products[i];
        var prefix = product.name.charAt(0);
        if(!grouped[prefix]){
            indices.push(prefix);
            grouped[prefix] = [];
        }
        grouped[prefix].push(product);
    }

    // listing via grouped order.
    for(var i=0, j=indices.length; i<j; i++){
        var prefix = indices[i];
        var grouped_products = grouped[prefix]
        for(var k=0, l=grouped_products.length; k<l; k++){
            var value = grouped_products[k];
            arr.push(value.name + ": " + value.price + "円");
        }
        arr.push("");
    }

    $("#settlementEventDetail #pricelist").html(arr.join("<br/>"));
};

carts.AppView.prototype.show_seat_types = function(seat_types) {
    var self = this;
    self.seatTypeList.empty();
    $.each(seat_types, function(key, value) {
        var item = $('<li></li>')
          .append(
            $('<input type="radio" name="seat_type" />')
            .attr('value', value.id)
            .change(function() {
                if (!self.left_box.hasClass('focused')) {
                    return false;
                }
                self.presenter.on_seat_type_selected(this.value);
                return true;
            }))
          .append(
            $('<span class="seatColor"></span>')
            .css('background-color', value.style.fill.color))
          .append(
            $('<span class="seatName"></span>')
            .text(value.name))
          .append(
            $('<span class="seatStatus"></span>'))
          .appendTo(self.seatTypeList);
    });
    self.seatTypeList.find("li:even").addClass("seatEven");
    self.seatTypeList.find("li:odd").addClass("seatOdd");
};


carts.AppView.prototype.show_payments = function(seat_type_name, products, upper_limit) {
    var self = this;
    this.seatTypeName.text(seat_type_name);
    this.productChoices.empty();
    $.each(products, function(key, value) {
        var name = $('<th scope="row" />');
        name.text(value.name);
        var payment = $('<td />');
        var price = $('<span/>');
        price.text('￥' + value.price);
        payment.append(price);
        var amount = $('<select/>');
        amount.attr('name', "product-" + value.id);
        for (var i = 0; i < upper_limit+1; i++) {
            opt = $('<option/>');
            opt.text(i);
            opt.val(i);
            amount.append(opt);
        }
        payment.append(amount);
        payment.append('<span>枚</span>');
        var row = $('<tr/>');
        row.append(name).append(payment);
        self.productChoices.append(row);
    });
};

carts.AppView.prototype.select_seat_type = function (seat_type_id) {
    this.seatTypeList.find('li :radio').each(function () {
        if (this.value == seat_type_id)
            $(this).parent().click();
    });
};

carts.Presenter = function(model, upper_limit, callbacks) {
    this.model = model;
    this.upper_limit = upper_limit;
    this.currentEventName = null;
    this.currentPerformanceId = null;
    this.currentSeatTypes = null;
    this.currentSeatTypeMap = null;
    this.callbacks = $.extend({
        seat_types_loaded: null,
        products_loaded: null,
        seat_type_selected: null
    }, callbacks || {});
};


carts.Presenter.prototype.init = function(view) {
    this.view = view;
};

carts.Presenter.prototype.show_seat_types = function(get_url) {
    var self = this;
    this.model.fetch_seat_types(get_url, function(data) {
        var perIdSeatTypeMap = {};
        for (var i = data.seat_types.length; --i >= 0; ) {
            perIdSeatTypeMap[data.seat_types[i].id] = data.seat_types[i];
        }
        self.currentEventName = data.eventName;
        self.currentPerformanceId = data.performance_id;
        self.currentSeatTypes = data.seat_types;
        self.currentSeatTypeMap = perIdSeatTypeMap;
        self.view.show_seat_types(data.seat_types);
        self.view.set_performance_id(data.performance_id);
        self.view.show_popup_title(data.event_name, data.performance_name, data.performance_start, data.venue_name);
        self.callbacks.seat_types_loaded && self.callbacks.seat_types_loaded(data);
    });
};

carts.Presenter.prototype.on_seat_type_selected = function(seat_type_id) {
    var seat_type = this.currentSeatTypeMap[seat_type_id];
    this.show_products(seat_type);
    this.view.focusRightBox();
    this.callbacks.seat_type_selected && this.callbacks.seat_type_selected(seat_type);
};

carts.Presenter.prototype.on_date_selected = function(selected_date){
    var view = this.view;
    var venues = this.model.perDateVenuesSelection[selected_date];

    view.update_performance_header_date(selected_date);
    view.update_venues_selectfield(venues, selected_date);
    view.update_settlement_detail(venues, selected_date);

    this.model.fetch_products_from_date(
        products_from_selected_date_url+"?selected_date="+selected_date,  // this is global variable
        function(data){
            view.update_settlement_pricelist(data.products);
        }
    );
    
    if (venues.length > 0) {
        this.show_seat_types(venues[0]['seat_types_url']);
    } else {
        // 多分いろいろクリアしないといけない
    }
};

carts.Presenter.prototype.on_venue_selected = function(selected_venue){
    var view = this.view;
    view.update_performance_header_venue(selected_venue);
};

carts.Presenter.prototype.show_products = function(seat_type) {
    var self = this;
    this.model.fetch_products(seat_type.products_url, function(data) {
        var seat_type_name = data.seat_type.name;
        var products = data.products;
        self.view.show_payments(seat_type_name, products, self.upper_limit);
        self.callbacks.products_loaded && self.callbacks.products_loaded(data);
    });
};

carts.Future = function carts_Future() {
  this.data = null;
  this.next = null
  this.error = null;
};

carts.Future.prototype.continuation = function carts_Future_continuation(next, error) {
  this.next = next;
  this.error = error;
  if (this.data)
    this.next(data);
};

carts.Future.prototype.data = function carts_Future_data(next, error) {
  this.data = data;
  if (this.next)
    this.next(data);
};

