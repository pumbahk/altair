$(document).ready(function() {
    $('.kolorPicker').change(function() {

    });

    $(window).resize(function(api){
        $("#venue-map").height($(window).height()-230);
    });

    $("#venue-map").height($(window).height()-230);
});