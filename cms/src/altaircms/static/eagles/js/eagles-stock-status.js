(function() {
    //var url = 'https://s3-ap-northeast-1.amazonaws.com/tstar/stocks/RE/all.json';
    var url = 'https://s3-ap-northeast-1.amazonaws.com/tstar-dev/stocks/eagles/all-1.json';
    
    var combine = function(a, b) {
        var r = { };
        for(var i=0 ; i<a.length ; i++) {
            if(b[i] != null) {
                r[a[i]] = b[i];
            }
        }
        return r;
    };
    var make_status = function(d) {
        var ei3 = 0;
        var inf = 0;
        var out = 0;
        var prk = 0;
        var all = 0;
        var count = 0;
        for(var n in d) {
            if(n.match(/^(2|3|6):/)) {
                ei3 += d[n];
            }
            if(n.match(/^(6|7|8|9|10|11|12|13|14|15|16|21|26|27|28|29|30|31):/)) {
                inf += d[n];
            } else if(n.match(/^(17|18|19|20|22|32|33|34|35|36|37):/)) {
                out += d[n];
            } else if(n.match(/^23:/)) {
                prk += d[n];
            }
            all += d[n];
            if(n.match(/^\d+:/)) {
                count++;
            }
        }
        if(count == 0) {
            // 特殊な公演なので対象としない
            return '';
        }
        if(all == 0) {
            return ['state-sold', '全席種完売'];
        } else if(300 <= ei3) {
            return ['state-has-seat-full', '余裕あり'];
        } else if(1000 <= inf) {
            return ['state-has-seat', '良席あと少し'];
        } else if(1000 <= out) {
            return ['state-infield-few', '内野席あと少し'];
        } else if(1500 <= prk) {
            return ['state-few', '残りわずか'];
        } else if(all < 100) {
            return ['state-piece-seat', 'バラ席のみ'];
        } else {
            return ['state-few', '残りわずか'];
        }
    };
    var load = function(url, cb) {
        $.ajax({
            url: url
        }).done(function(d) {
            var result = { };
            for(var i=0 ; i<d.performances.length ; i++) {
                var start = d.performances[i].start_on;
                var status = make_status(combine(d.seat_types, d.performances[i].stocks));
                if(status != '') {
                    result[start] = status;
                }
            }
            cb(result);
        });
    };
    /*
    var handle = function(id) {
    };
    */
    var extend_row = function(row, month, day, status) {
        var td = row.find('td:last');
        if(0 < td.find('.stockStatusInfomation').size()) {
            return; // do nothing if contains .stockStatusInfomation
        }

		td.addClass('state');
		td.addClass(status[0]);
        td.find('p.state-txt').html(status[1]);
    };
    var extend_table = function(table, result) {
        var header = $(table).find('tr').eq(0).find('th').eq(0).text();
        $(table).find('tr').each(function() {
            var tr = $(this);
            var md = tr.find('th.date').eq(0).text().match(/(\d+)月(\d+)日/);
            if(!md) {
                md = tr.find('th.date').eq(0).text().match(/(\d+)\/(\d+)/);
                if(!md) {
                    return true;
                }
            }
            if(!(""+tr.text()).match(/購入する/)) {
                extend_row(tr, md[1], md[2], [ 'state-sold', '全席種<br />完売' ]);
                return;
            }
            for(var start_on in result) {
                var match = start_on.match(/^(\d+)\D(\d+)\D(\d+)/);
                if(match) {
                    if(md[1]*1 == match[2]*1 && md[2]*1 == match[3]*1) {
                        extend_row(tr, md[1], md[2], result[start_on]);
                        return true;
                    }
                }
            }
        });
    };

    $(function() {
        // for dev
        $('.state').each(function() {
            $(this).attr('class', '');
            $(this).find('p.state-txt').text('');
        });

        load(url, function(result) {
            $('table').each(function() {
                extend_table(this, result);
            });
        });
    });
})();
