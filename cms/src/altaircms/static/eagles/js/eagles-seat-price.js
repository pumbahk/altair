(function() {
    function setSeatPrice(data) {
        var seatPriceTableElm = $('#seatPriceTarget');

        $.each(seatPriceTableElm.find('tr'), function() {
            var seatNumber = $(this).find('.number').text();
            var seatName = $(this).find('.seat-name').text();

            var targetPriceData = $.grep(data, function(arrayElm, index) {
                var match = arrayElm.stock_type_name.match(/^([0-9]+):(.+)/); // stockTypeName is 'number:name' or 'name'
                if (match) {
                    switch (seatNumber) {
                        case '1':
                            return (seatNumber === match[1]) && match[2] == 'VIPシート';
                        case '20':
                        case '21':
                            return (seatNumber === match[1]);
                        case '25':
                            if (seatName == 'バックネット裏ボックスシート') {
                                return (seatNumber === match[1]) && match[2] == 'バックネット裏ボックスシート6';
                            }
                        default:
                            return (seatNumber === match[1]) &&
                                (match[2].indexOf(seatName) !== -1 || seatName.indexOf(match[2]) !== -1);
                    }
                } else {
                    return arrayElm.stock_type_name.indexOf(seatName) !== -1 || seatName.indexOf(arrayElm.stock_type_name) !== -1;
                }
            });

            if (targetPriceData.length === 0) {
                return true;
            }

            var price = getPrice(targetPriceData[0].products);
            if (price.adult !== undefined) {
                $(this).find('td.price-adult').text('￥ ' + price.adult);
            }
            if (price.child !== undefined) {
                $(this).find('td.price-child').text('￥ ' + price.child);
            }
            if (price.general !== undefined) {
                $(this).find('td.price-adult').text('￥ ' + price.general);
            }
            if (seatNumber == '20' || seatNumber == '21') {
                $(this).find('td.seat-name').text(targetPriceData[0].stock_type_name.replace(/^[0-9]+:/, ''));
            }
        });
    }

    function getPrice(products) {
        var price = {};

        $.each(products, function() {
            if (this.name.indexOf('大人') !== -1) {
                price.adult = this.price;
                return true;
            }
            if (this.name.indexOf('子供') !== -1) {
                price.child = this.price;
                return true;
            }
            price.general = this.price;
        });

        return price;
    }

    $(function() {
        var performanceDate = $('#performance-date').val();

        if (performanceDate) {
            var staticElm = $('<a>').attr('href', $('#staticBase').val())[0];
            $.ajax({
                url: 'https://' + staticElm.hostname + '/price/RE/' + performanceDate + '/price.json'
            }).then(function(data) {
                if (data.length > 0) {
                    setSeatPrice(data);
                    $('#priceListArea').show();
                }
            });
        }
    });
})();
