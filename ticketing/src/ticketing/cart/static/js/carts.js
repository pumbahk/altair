/**
 * Created with PyCharm.
 * User: odagiriatsushi
 * Date: 12/05/11
 * Time: 10:55
 * To change this template use File | Settings | File Templates.
 */

var carts = {};
carts.init = function(venues_selection, selected, upper_limit) {
    var model = new carts.Model(venues_selection);
    var presenter = new carts.Presenter(model, upper_limit);
    carts.appView = new carts.AppView();
    carts.appView.init(presenter);
    $('#date-select').val(selected[1]);
    $('#date-select').change();
    // initial setup
};


carts.Model = function(venues_selection) {
    this.venus_selection = venues_selection;
};

carts.Model.prototype.fetch_venues = function() {
};

carts.Model.prototype.fetch_seat_types = function(get_url, callback) {
    $.ajax({url:get_url, dataType: 'json', success: callback});
};

carts.Model.prototype.fetch_products = function(get_url, callback) {
    $.ajax({url: get_url, dataType: 'json', success: callback});
};

carts.AppView = function() {
};

carts.AppView.prototype.init = function(presenter) {
    $("#selectSeat li:even").addClass("seatEven");
    $("#selectSeat li:odd").addClass("seatOdd");
    $('#date-select').change(
        function() {
            presenter.on_date_selected($('#date-select').val());
        }
    );
    $('#btn-order').click(function(event) {
        event.stopPropagation();
        var values = $("#order-form").serialize();
        $.ajax({
            url: order_url,
            dataType: 'json',
            data: values,
            type: 'POST',
            success: function(data, textStatus, jqXHR) {
                if (data.result == 'OK') {
                    var products = data.cart.products;
                    $('#contentsOfShopping').empty();
                    for (var i=0; i < products.length; i++) {
                        var product = products[i];
                        var item = $('<tr/>');
                        var name = $('<th/>');
                        $(name).text(product.name);
                        var quantity = $('<td/>');
                        $(quantity).text(product.quantity + " 枚");
                        item.append(name);
                        item.append(quantity);
                        $('#contentsOfShopping').append(item);
                    }
                    $('#cart-total-amount').text(data.cart.total_amount);

                    $('#reserved-confirm-button').click(function() {
                        window.location.href = data.pyament_url;
                    });
                    $('#order-reserved').overlay({
                        mask: {
                            color: "#999",
                            opacity: 0.5
                        },
                        load: true});
                } else {
                    $('#order-error-template').overlay({
                        mask: {
                            color: "#999",
                            opacity: 0.5
                        },
                        load: true});
                }
            }
        })
    });
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
    $("#hallName #performanceDate").text(selected_date);
}
carts.AppView.prototype.update_performance_header_venue = function(selected_venue){
    $("#hallName #performanceVenue").text(selected_venue);
}

carts.AppView.prototype.update_settlement_detail = function(venues, selected_date){
    // update settleElementBox
    var root = $("#settlementEventDetail");
    var new_td_venues = [];
    root.find("#performance_date").text(selected_date);
    $.each(venues, function(index, value){
        new_td_venues.push(value["name"]);
    })
    root.find("#venue").text(new_td_venues.join(", "));
};

carts.AppView.prototype.show_seat_types = function(seat_types) {
    $('#seat-types-list').empty();
    var presenter = this.presenter;
    $.each(seat_types, function(key, value) {
        var item = $('<li />');
        var select = $('<input type="radio" name="seat_type" />');
        select.attr('value', value.products_url);
        select.change(function() {presenter.on_seat_type_selected($(this))});
        var name = $('<span />');
        name.text(value.name);
        item.append(select);
        item.append(name);
        $('#seat-types-list').append(item);

    });
    $("#selectSeat li:even").addClass("seatEven");
    $("#selectSeat li:odd").addClass("seatOdd");

};

carts.AppView.prototype.update_settlelement_pricelist = function(){
    // seat typesだけじゃ足りない。
    console.log(products);
    console.log(seat_types);
};

carts.AppView.prototype.show_payments = function(seat_type_name, products, upper_limit) {
    $('#payment-seat-type').text(seat_type_name);
    $('#payment-seat-products').empty();
    $.each(products, function(key, value) {
        var name = $('<th scope="row" />');
        name.text(value.name);
        var payment = $('<td />');
        var price = $('<span/>');
        price.text('￥' + value.price);
        payment.append(price);
        var amount = $('<select/>');
        amount.attr('name', "product-" + value.id);
        for (var i=0; i < upper_limit+1; i++) {
            opt = $('<option/>');
            opt.text(i);
            opt.val(i);
            amount.append(opt);
        }
        payment.append(amount);
        payment.append('<span>枚</span>');
        var row = $('<tr/>');
        row.append(name).append(payment);
        $('#payment-seat-products').append(row);

    });
};

carts.Presenter = function(model, upper_limit) {
    this.model = model;
    this.upper_limit = upper_limit;
};


carts.Presenter.prototype.init = function(view) {
    this.view = view;
};

carts.Presenter.prototype.show_seat_types = function(get_url) {
    var view = this.view;
    this.model.fetch_seat_types(get_url, function(data) {
        view.show_seat_types(data.seat_types);
        view.set_performance_id(data.performance_id);
    });
};

carts.Presenter.prototype.on_seat_type_selected = function(selected) {
    $('#seat-types-list').children('li').each(function(key, value) {
        $(value).removeClass("selected");
    });
    selected.parent().addClass("selected");
    var get_url = selected.val();
    this.show_products(get_url);
};

carts.Presenter.prototype.on_date_selected = function(selected_date){
    var view = this.view;
    var venues = this.model.venus_selection[selected_date];

    view.update_performance_header_date(selected_date);
    view.update_venues_selectfield(venues, selected_date);
    view.update_settlement_detail(venues, selected_date);

    if (venues.length > 0) {
        console.log(this.show_seat_types);
        this.show_seat_types(venues[0]['seat_types_url']);
    } else {
        // 多分いろいろクリアしないといけない
    }
};

carts.Presenter.prototype.show_products = function(get_url) {
    var view = this.view;
    var upper_limit = this.upper_limit;
    this.model.fetch_products(get_url, function(data) {
        var seat_type_name = data.seat_type.name;
        var products = data.products;
        view.show_payments(seat_type_name, products, upper_limit);
    });
};
