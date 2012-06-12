/**
 * Created with PyCharm.
 * User: odagiriatsushi
 * Date: 12/05/11
 * Time: 10:55
 * To change this template use File | Settings | File Templates.
 */

var carts = {};
carts.init = function(venues_selection, selected) {
    var model = new carts.Model(venues_selection);
    var presenter = new carts.Presenter(model);
    carts.appView = new carts.AppView();
    carts.appView.init(presenter);
    $('#date-select').val(selected[1]);
    $('#date-select').change();
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
            var venues = venues_selection[$('#date-select').val()];
            $('#venue-select').empty();
            $.each(venues, function(index, value) {
                var o = $('<option/>');
                o.text(value['name']);
                o.attr('value', value['seat_types_url']);
                $('#venue-select').append(o);
            });
            if (venues.length > 0) {
                presenter.show_seat_types(venues[0]['seat_types_url']);
            } else {
                // 多分いろいろクリアしないといけない
            }
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
                    alert('OK');
                    window.location.href = data.pyament_url;
                } else {
                    alert('NG');
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

carts.AppView.prototype.show_payments = function(seat_type_name, products) {
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
        for (var i=0; i < 99; i++) { // TODO 枚数制限
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

carts.Presenter = function(model) {
    this.model = model;
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
}

carts.Presenter.prototype.show_products = function(get_url) {
    var view = this.view;
    this.model.fetch_products(get_url, function(data) {
        var seat_type_name = data.seat_type.name;
        var products = data.products;
        view.show_payments(seat_type_name, products);
    });
};



