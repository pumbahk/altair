(function() {
    var URL = 'https://s3-ap-northeast-1.amazonaws.com/tstar/stocks/RE/farm-all.json';
    var LABEL_GROUP = {
        SOLD_OUT: {
            "label_text": "完売",
            "class_attribute": "state-sold"
        },
        SEAT_FEW: {
            "label_text": "残りわずか",
            "class_attribute": "state-few"
        },
        SEAT_FULL: {
            "label_text": "余裕あり",
            "class_attribute": "state-has-seat-full"
        }
    };
    var RENDER_DATA_FIELD = {
        LABEL: "label",
        MONTH: "month",
        DATE: "date"
    };

    var GENERAL_PUBLIC = 1;
    var TARGET_SEAT = [GENERAL_PUBLIC];
    var RESPONSE_DATE_REGEXP = /^(\d+)\D(\d+)\D(\d+)/;
    var SALES_REGEXP = /購入する/;
    var DOM_DATE_REGEXP_LIST = [
        /(\d+)月(\d+)日/,
        /(\d+)\/(\d+)/
    ];

    var target_counter = (function() {

        var count = {};

        function counter(stocks) {
            $.each(TARGET_SEAT, function(index, target) {
                var seat_count = stocks[target];
                if (!seat_count) return true;

                var value = count[target];
                if (!value) value = 0;
                value += seat_count;

                count[target] = value;
            });
        }

        return {
            put: function(stocks) {
                counter(stocks)
            },
            get: function() {
                return count;
            }
        };
    })();

    var make_label = function(counted_target) {

        var count = counted_target[GENERAL_PUBLIC];
        var status;
        if (count > 100) {
            status = LABEL_GROUP.SEAT_FULL;
        }else if (count > 0) {
            status = LABEL_GROUP.SEAT_FEW;
        }else {
            status = LABEL_GROUP.SOLD_OUT;
        }
        return [status.class_attribute, status.label_text];
    };

    var stock_api = (function(){
        var url = URL;
        function call(successBlock, failureBlock) {
            $.ajax({
                url: url
            }).then(
                function (data) {
                    successBlock(data)
                },
                function () {
                    failureBlock()
                });
        }
        return {
            get: function(callback){
                call(callback);
            }
        }
    })();

    var is_sale = function(tr_element) {
        return ("" + tr_element.text()).match(SALES_REGEXP)
    };

    var parse_date_time = function(tr_element) {
        var date_element = tr_element.find('th.date');
        var md = [];
        $.each(DOM_DATE_REGEXP_LIST, function(index, regexp) {
            var match = date_element.eq(0).text().match(regexp);
            if (match) {
                md = match;
                return false;
            }
        });
        return md;
    };

    var extend_row = function(row, status, is_show_icon) {
        var td = row.find('td:last');
        if(0 < td.find('.stockStatusInfomation').size()) {
            return;
        }
        td.addClass('state');
        td.addClass(status[0]);
        var box = td.find('.state-box');
        if (is_show_icon) {
            box.find('p.state-txt').html(status[1]);
        }else {
            box.remove();
        }
    };

    var extend_table = function(table, render_data) {
        $(table).find('tr').each(function() {
            var tr = $(this);
            var md = parse_date_time(tr);
            var render_data_element = null;
            if (md.length === 3) {
                var key = ('0' + md[1]).slice(-2) + ('0' + md[2]).slice(-2);
                render_data_element = render_data[key];
            }

            if(render_data_element && is_sale(tr)) {
                extend_row(
                    tr,
                    render_data_element[RENDER_DATA_FIELD.LABEL],
                    true);
            }else {
                extend_row(
                    tr,
                    [
                        LABEL_GROUP.SOLD_OUT.class_attribute,
                        ""
                    ],
                    false);
            }
        });
    };

    var render = function(render_data) {
        $('table').each(function() {
            extend_table(this, render_data);
        });
    };

    $(function() {
        stock_api.get(function(data) {
            var render_data = {};
            var performances = data.performances;
            $.each(performances, function(index, performance) {
                target_counter.put(performance.stocks);
                var counted_target = target_counter.get();
                var label = make_label(counted_target);
                var start_on = performance.start_on.match(RESPONSE_DATE_REGEXP);
                var render_data_element = {};
                render_data_element[RENDER_DATA_FIELD.LABEL] = label;
                render_data_element[RENDER_DATA_FIELD.MONTH] = start_on[2];
                render_data_element[RENDER_DATA_FIELD.DATE] = start_on[3];
                render_data[start_on[2]+start_on[3]] = render_data_element;
            });
            render(render_data);
        });
    });
})();
