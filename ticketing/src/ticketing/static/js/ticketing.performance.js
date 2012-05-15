
$(document).ready(function() {

    $('.kolorPicker').change(function() {

    });

    $('a[href^=#new-seat-type]').click(function() {
        var event_id = /^#new-seat-type\[(.+)\]$/.exec($(this).attr('href'))[1];
        $('#edit-modal').modal('toggle');
        $('#edit-modal #edit').attr('action', '/stock_types/new/' + event_id);
    });

    $('a[href^=#edit-seat-type]').click(function() {
        var vars = /^#edit-seat-type\[(.+)\]\[(.+)\]$/.exec($(this).attr('href'));
        var event_id  = vars[1];
        var stock_type_id    = vars[2];
        var data = JSON.parse($(this).attr('data'));
        var name = $(this).attr('name');

        $('#edit-modal').modal('toggle');
        $('#edit-modal #name').val(name);
        if (data) {
            $('#edit-modal #text').val(data.text);
            $('#edit-modal #text_color').val(data.text_color);
            if (data.fill) {
                $('#edit-modal #fill_color').val(data.fill.color);
                $('#edit-modal #fill_type').val(data.fill.type);
                $('#edit-modal #fill_image').val(data.fill.image);
            }
            if (data.stroke) {
                $('#edit-modal #stroke_color').val(data.stroke.color);
                $('#edit-modal #stroke_width').val(data.stroke.width);
                $('#edit-modal #stroke_patten').val(data.stroke.pattern);
            }
        }
        $('#edit-modal #edit').attr('action', '/stock_types/edit/' + stock_type_id);
    });

    $(window).resize(function(api){
        $("#venue-map").height($(window).height()-230);
    });

    $("#venue-map").height($(window).height()-230);

});