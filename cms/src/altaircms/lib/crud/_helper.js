var create_select_helper = function($bound_element){
    var qinput = $('<input type="text" placeholder="検索..." />') .css({ marginLeft: 10, backgroundColor: '#ffffcc' })
    qinput.bind('change keyup', function(e) {
        var qword = $(e.currentTarget).val();
        var cands = $bound_element.find("option");
        for(var i=0, j=cands.length; i<j; i++){
            var $e = $(cands[i]);
            if($e.text().indexOf(qword) >= 0){
                $bound_element.val($e.val());
                var _dummy = $("<option>");
                $bound_element.append(_dummy);
                _dummy.remove();
                break;
            }
        }
    });
    return qinput
};

var select_helper = function($e){
    $e.parent().append(create_select_helper($e));
};
