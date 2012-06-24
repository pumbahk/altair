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
    }
};

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

carts.Model.prototype.fetch_products_from_date = function(get_url, callback){
    $.ajax({url: get_url, dateType: "json", success: callback});
};

carts.AppView = function() {
};

carts.AppView.prototype.focusLeftBox = function(){
    var left_box = $("#selectSeat");
    var right_box = $("#selectBuy");

    left_box.addClass("focused");
    left_box.removeClass("blur");
		right_box.addClass("blur");
    right_box.removeClass("focused");

    right_box.find("#payment-seat-products").empty();
    right_box.find("#payment-seat-type").empty();
};

carts.AppView.prototype.focusRightBox = function(){
    var left_box = $("#selectSeat");
    var right_box = $("#selectBuy");

		left_box.removeClass("focused");
		left_box.addClass("blur");
    right_box.addClass("focused");
		right_box.removeClass("blur");
};

carts.AppView.prototype.init = function(presenter) {
    var view = this;
    $('#date-select').change(
        function() {
            presenter.on_date_selected($(this).val());
            view.focusLeftBox();
        }
    );
    $("#venue-select").change(
        function(){
            presenter.on_venue_select($(this).text());
            view.focusLeftBox();
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

    $('#btn-order').click(function(event) {
        event.stopPropagation();
        var values = $("#order-form").serialize();
        $.ajax({
            url: order_url, //this is global variable
            dataType: 'json',
            data: values,
            type: 'POST',
            success: function(data, textStatus, jqXHR) {
                if (data.result == 'OK') {

                    var root = $("#hallName");
                    // var performance_date = root.find("#performanceDate").text();
                    var performance_venue = root.find("#performanceVenue").text();
                    // modal
                    //$(".modal #performance-name").text(performance_date + performance_venue);
                    $(".modal #performance-name").text(performance_venue);


                    var products = data.cart.products;

                    // insert product items in cart
                    var root = $('#contentsOfShopping');
                    root.empty();
                    for (var i=0; i < products.length; i++) {
                        var product = products[i];
                        var item = create_content_of_shopping_element(product);//
                        $('#contentsOfShopping').append(item);
                    }
                    root.find("tr").last().addClass(".last-child");


                    $('#cart-total-amount').text("￥ "+data.cart.total_amount);

                    var reserved_dialog = $('#order-reserved').overlay({
                        mask: {
                            color: "#999",
                            opacity: 0.5
                        },
                        closeOnClick: false});

                    $('#reserved-cancel-button').click(function() {
                        $('#order-reserved').overlay().close();
                    });
                    
                    $('#reserved-confirm-button').click(function() {
                        window.location.href = data.pyament_url;
                    });
                    reserved_dialog.load();
                    var loopback = function(){
                        var target = $("#order-reserved");
                        if(target.css("display") == "none"){
                            target.overlay().load();
                            setTimeout(loopback, 100);
                        }
                    }
                    loopback();
                } else {
                    var order_error_dialog = $('#order-error-template').overlay({
                        mask: {
                            color: "#999",
                            opacity: 0.5
                        },
                        closeOnClick: false})
                    $('#error-close-button').click(function() {
                        $('#order-error-template').overlay().close();
                    });
                    order_error_dialog.load();
                    var loopback = function(){
                        var target = $("#order-error-template");
                        if(target.css("display") == "none"){
                            target.overlay().load();
                            setTimeout(loopback, 100);
                        }
                    }
                    loopback();
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
    $("#hallName #performanceDate").text(util.datestring_japanize(selected_date));
}
carts.AppView.prototype.update_performance_header_venue = function(selected_venue){
    $("#hallName #performanceVenue").text(selected_venue);
}

carts.AppView.prototype.update_settlement_detail = function(venues){
    // update settleElementBox
    var new_td_venues = [];
    $.each(venues, function(index, value){
        new_td_venues.push(value["name"]);
    })
    $("#settlementEventDetail #venue").text(new_td_venues.join(", "));
};

carts.AppView.prototype.update_settlement_pricelist = function(products){
    var arr = [];
    $.each(products, function(index, value){
        arr.push(value.name + ": " + value.price + "円");
    });
    $("#settlementEventDetail #pricelist").html(arr.join("<br/>"));
};

carts.AppView.prototype.show_seat_types = function(seat_types) {
    $('#seatTypeList').empty();
    var presenter = this.presenter;
    $.each(seat_types, function(key, value) {
        var item = $('<li></li>')
          .append(
            $('<input type="radio" name="seat_type" />')
            .attr('value', value.products_url)
            .change(function() {presenter.on_seat_type_selected($(this))}))
          .append(
            $('<span class="seatColor"></span>')
            .css('background-color', value.style.fill.color))
          .append(
            $('<span class="seatName"></span>')
            .text(value.name))
          .append(
            $('<span class="seatStatus"></span>'))
          .appendTo($('#seatTypeList'));
    });
    $("#selectSeat li:even").addClass("seatEven");
    $("#selectSeat li:odd").addClass("seatOdd");
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
    $('#seatTypeList').children('li').each(function(key, value) {
        $(value).removeClass("selected").addClass("unselected");
    });
    selected.parent().addClass("selected").removeClass("unselected");
    var get_url = selected.val();
    this.show_products(get_url);

    //隣をfocus
    this.view.focusRightBox();
};

carts.Presenter.prototype.on_date_selected = function(selected_date){
    var view = this.view;
    var venues = this.model.venus_selection[selected_date];

    view.update_performance_header_date(selected_date);
    view.update_venues_selectfield(venues, selected_date);
    view.update_settlement_detail(venues);

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

carts.Presenter.prototype.show_products = function(get_url) {
    var view = this.view;
    var upper_limit = this.upper_limit;

    this.model.fetch_products(get_url, function(data) {
        var seat_type_name = data.seat_type.name;
        var products = data.products;
        view.show_payments(seat_type_name, products, upper_limit);
    });
};
