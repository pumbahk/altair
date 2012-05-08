
$(document).ready(function() {

    $('.kolorPicker').change(function() {

    });

    $('#delete').click(function(){
      $('#delete-modal').modal('toggle');
      $('#delete-modal #delete').attr('href', '/seat_types/delete/' + $('input[name=checked_id]:checked').val());
    });

    $('a[href^=#new-seat-type]').click(function() {
        var performance_id = /^#new-seat-type\[(.+)\]$/.exec($(this).attr('href'))[1];
        $('#edit-modal').modal('toggle');
        $('#edit-modal #edit').attr('action', '/seat_types/new/' + performance_id);
    });

    $('a[href^=#edit-seat-type]').click(function() {
        var vars = /^#edit-seat-type\[(.+)\]\[(.+)\]$/.exec($(this).attr('href'));
        var performance_id  = vars[1];
        var seat_type_id    = vars[2];
        var data = JSON.parse($(this).attr('data'));
        var name = $(this).attr('name');

        $('#edit-modal').modal('toggle');
        $('#edit-modal #name').val(name);
        $('#edit-modal #signature').val(data.text);

        $('#edit-modal #fill_color').val(data.fill);
        $('#edit-modal #line_color').val(data.stroke.color);

        $('#edit-modal #line_thickness_' + data.stroke.width).attr('checked', true);
        $('#edit-modal #line_style_' + data.stroke.pattern).attr('checked', true);

        $('#edit-modal #edit').attr('action', '/seat_types/edit/' + seat_type_id);
    });

    $(window).resize(function(api){
        $("#venue-map").height($(window).height()-230);
    });

    $("#venue-map").height($(window).height()-230);

});