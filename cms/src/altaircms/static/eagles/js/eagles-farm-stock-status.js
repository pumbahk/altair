(function() {
    const URL = 'https://s3-ap-northeast-1.amazonaws.com/tstar-dev/stocks/RE/farm-all.json';
    let LABEL_GROUP = {
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
    let RENDER_DATA_FIELD = {
        LABEL: "label",
        MONTH: "month",
        DATE: "date"
    };

    let GENERAL_PUBLIC = 1;
    let TARGET_SEAT = [GENERAL_PUBLIC];
    let RESPONSE_DATE_REGEXP = /^(\d+)\D(\d+)\D(\d+)/;
    let SALES_REGEXP = /購入する/;
    let DOM_DATE_REGEXP_LIST = [
        /(\d+)月(\d+)日/,
        /(\d+)\/(\d+)/
    ];

    let target_counter = (function() {

        let count = {};

        function counter(stocks) {
            $.each(TARGET_SEAT, function(index, target) {
                let seat_count = stocks[target];
                if (!seat_count) return true;

                let value = count[target];
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

    let make_label = function(counted_target) {

        let count = counted_target[GENERAL_PUBLIC];
        let status;
        if (count > 100) {
            status = LABEL_GROUP.SEAT_FULL;
        }else if (count > 0) {
            status = LABEL_GROUP.SEAT_FEW;
        }else {
            status = LABEL_GROUP.SOLD_OUT;
        }
        return [status.class_attribute, status.label_text];
    };

    let stock_api = (function(){
        let url = URL;
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

    let is_sale = function(tr_element) {
        return ("" + tr_element.text()).match(SALES_REGEXP)
    };

    let parse_date_time = function(tr_element) {
        let date_element = tr_element.find('th.date');
        let md = [];
        $.each(DOM_DATE_REGEXP_LIST, function(index, regexp) {
            let match = date_element.eq(0).text().match(regexp);
            if (match) {
                md = match;
                return false;
            }
        });
        return md;
    };

    let extend_row = function(row, status, is_show_icon) {
        let td = row.find('td:last');
        if(0 < td.find('.stockStatusInfomation').size()) {
            return;
        }
        td.addClass('state');
        td.addClass(status[0]);
        let box = td.find('.state-box');
        if (is_show_icon) {
            box.find('p.state-txt').html(status[1]);
        }else {
            box.remove();
        }
    };

    let extend_table = function(table, render_data) {
        $(table).find('tr').each(function() {
            let tr = $(this);
            let md = parse_date_time(tr);
            let render_data_element = null;
            if (md.length === 3) {
                let key = ('0' + md[1]).slice(-2) + ('0' + md[2]).slice(-2);
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

    let render = function(render_data) {
        $('table').each(function() {
            extend_table(this, render_data);
        });
    };

    $(function() {
        stock_api.get(function(data) {
            let render_data = {};
            let performances = data.performances;
            $.each(performances, function(index, performance) {
                target_counter.put(performance.stocks);
                let counted_target = target_counter.get();
                let label = make_label(counted_target);
                let start_on = performance.start_on.match(RESPONSE_DATE_REGEXP);
                let render_data_element = {};
                render_data_element[RENDER_DATA_FIELD.LABEL] = label;
                render_data_element[RENDER_DATA_FIELD.MONTH] = start_on[2];
                render_data_element[RENDER_DATA_FIELD.DATE] = start_on[3];
                render_data[start_on[2]+start_on[3]] = render_data_element;
            });
            render(render_data);
        });
    });
})();
