(function() {
    function setSeatPrice(data) {
        var seatPriceTableElm = $('#seatPriceTarget');

        $.each(seatPriceTableElm.find('tr'), function() {
            var seatNumber = $(this).find('.number').text();
            var seatName = $(this).find('.seat-name').text();

            var targetPriceData = $.grep(data, function(arrayElm, index) {
                var match = arrayElm.stock_type_name.match(/^([0-9]+):(.+)/); // stockTypeName is 'number:name' or 'name'
                if (match) {
                  switch (seatName) {
                    case '内野1塁側カウンターペアシートS':
                        return (seatNumber === match[1]) && match[2] == '内野1塁側カウンターペアシートS';
                    default:
                        return (seatNumber === match[1]) &&
                            (match[2].indexOf(seatName) !== -1 || seatName.indexOf(match[2]) !== -1);
                  }
                } else {
                    return arrayElm.stock_type_name.indexOf(seatName) !== -1 || seatName.indexOf(arrayElm.stock_type_name) !== -1;
                }
            });

            if (targetPriceData[0]) {
                console.log(targetPriceData[0].stock_type_name);
            }

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
        });
    }

    function getPrice(products) {
        var price = {};

        $.each(products, function() {
            if (this.name.indexOf('駐車券') !== -1) {
                return true;
            }
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
                }
            });
        }
    });
})();
