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

    var TARGET_SEAT = {
        GENERAL_PUBLIC:
            {
                "manage_no": 0,
                "name_regexp": /^内野自由席/
            }
    };

    var RESPONSE_DATE_REGEXP = /^(\d+)\D(\d+)\D(\d+)/;
    var SALES_REGEXP = /^購入する/;
    var TARGET_PLACE_REGEXP = /^森林どりスタジアム泉/;
    var DOM_DATE_REGEXP_LIST = [
        /(\d+)月(\d+)日/,
        /(\d+)\/(\d+)/
    ];

    var make_label = function(counted_target, target_seat_order_map) {

        var disp_order = target_seat_order_map[TARGET_SEAT.GENERAL_PUBLIC.manage_no];
        var count = counted_target[disp_order];

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
        function call(successBlock, failureBlock) {
            $.ajax({
                url: URL
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

    var get_target_seat_order_map = function(seat_types) {
        var target_seat_order_map = {};
        $.each(seat_types, function(disp_order, seat_type) {
            $.each(TARGET_SEAT , function(key, value) {
                var match = seat_type.match(value.name_regexp);
                if (!match || match.len === 0) {
                    return true;
                }
                target_seat_order_map[value.manage_no] = disp_order;
                return false;
            });
        });
        return target_seat_order_map
    };

    var count_target = function(stocks, target_seat_order_map) {
        var count = {};
        $.each(target_seat_order_map, function(manage_no, disp_order) {
            var seat_count = stocks[disp_order];
            if (!seat_count) seat_count = 0;
            count[disp_order] = seat_count;
        });
        return count;
    };

    var is_sale = function(tr_element) {
        var buy_element = tr_element.find('.btn');
        return ("" + buy_element.text()).match(SALES_REGEXP)
    };

    var is_target_place = function(tr_element) {
        var place_element = tr_element.find('.place');
        return ("" + place_element.text()).match(TARGET_PLACE_REGEXP)
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
            if (tr.length == 0 || tr.find('th.date').length == 0) {
                return
            }
            var md = parse_date_time(tr);
            var render_data_element = null;
            if (md.length === 3) {
                var key = ('0' + md[1]).slice(-2) + ('0' + md[2]).slice(-2);
                render_data_element = render_data[key];
            }

            if(render_data_element && is_sale(tr) && is_target_place(tr)) {
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
            var target_seat_order_map = get_target_seat_order_map(data.seat_types);

            $.each(performances, function(index, performance) {
                var counted_target = count_target(performance.stocks, target_seat_order_map);
                var label = make_label(counted_target, target_seat_order_map);
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
