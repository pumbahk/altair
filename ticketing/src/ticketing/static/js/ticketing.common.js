function get_id(id) {
  return $('input[name=' + id + ']:checked').val() || $('#' + id).val();
}

function post_modal_form(modal, form, url) {
  var param = {};
  $(modal + ' :input').each(function(i, v) {
    param[v.name] = v.value;
  });
  $.post(
    url,
    param,
    function(data) {
      $(modal).modal('hide');
      $(form).html(data);
      $(modal).modal('show');
    },
    'html'
  );
}
