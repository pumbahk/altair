function setzero(val) {
    if (val < 10 & val.length < 2) {
        val = "0" + val;
    }
    return val;
}

function checkdate(strDate) {
    if(strDate == ""){
        return false;
    }
    if(!strDate.match(/^\d{4}\/\d{1,2}\/\d{1,2}$/)){
        return false;
    }

    var date = new Date(strDate);

    var monthtem = (parseInt(strDate.split("/")[1], 10) - 1).toString(10);
    if(date.getFullYear() !=  strDate.split("/")[0]
        || date.getMonth() != monthtem
        || date.getDate() != strDate.split("/")[2]
    ){
        return false;
    }
    return true;
}

function checkisTime (strtime) {
    return strtime.match(/^([01]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/) !== null;
};

$(function(){
    $('#settime_form :input').keydown(function() {
        $("#preview").attr('disabled', true);
    });

    $("#settime").click(function(){
        var year = $('#settime_form [name="now.year"]').val();
        var month = $('#settime_form [name="now.month"]').val();
        month = setzero(month)
        var day = $('#settime_form [name="now.day"]').val();
        day = setzero(day)
        var hour = $('#settime_form [name="now.hour"]').val();
        hour = setzero(hour)
        var minute = $('#settime_form [name="now.minute"]').val();
        minute = setzero(minute)
        var second = $('#settime_form [name="now.second"]').val();
        second = setzero(second)
        var datestr = year + "/" +  month + "/" + day;
        var timestr = hour + ":" + minute + ":" + second;
        if(!checkdate(datestr)|| !checkisTime(timestr)) {
            $("#preview").attr('disabled', true);
            $("#messagearea").hide();
            $("#errormsg").show();
            return;
        }else {
            $("#errormsg").hide();
        }

        $("#preview").attr('disabled', false);

        var timestamp = datestr + " " + timestr;
        $("h4.alert-heading").text("現在時刻が「" + timestamp + "」に設定されました");
        $("#messagearea").show();
    });

    $("#invalidate").click(function(){
        var systime = new Date();

        $('#settime_form [name="now.year"]').val(systime.getFullYear());
        $('#settime_form [name="now.month"]').val(systime.getMonth() + 1);
        $('#settime_form [name="now.day"]').val(systime.getDate());

        $('#settime_form [name="now.hour"]').val(systime.getHours());
        $('#settime_form [name="now.minute"]').val(systime.getMinutes());
        $('#settime_form [name="now.second"]').val(systime.getSeconds());

        $("#preview").attr('disabled', true);
        $("#errormsg").hide();
        $("h4.alert-heading").text("現在時刻の設定が取り消されました。");
        $("#messagearea").show();
    });

    $("#preview").click(function(){
        if (!$("input[name='redirect_to']").val().match(/^(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)$/)) {
            $("#errormsg").show();
            return false;
        } else {
            $("#settime_form").submit();
        }
    });
});


