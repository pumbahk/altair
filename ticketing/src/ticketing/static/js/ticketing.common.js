function get_id(id) {
  return $('input[name=' + id + ']:checked').val() || $('#' + id).val();
}

function post_modal_form(modal, form, url) {
  var param = {}, counts = {};
  $(modal).find(':input').each(function(i, v) {
    var count = counts[v.name];
    if (count === void(0)) {
      param[v.name] = v.value;
      counts[v.name] = 1;
    } else {
      var pv = param[v.name];
      delete param[v.name];
      param[v.name + '-0'] = pv;
      param[v.name + '-' + (counts[v.name]++)] = v.value;
    }
  });
  $.ajax({
    type: 'post',
    url: url,
    data: param,
    traditional: true,
    success: function(data) {
      $(modal).modal('hide');
      $(form).html(data);
      $(modal).modal('show');
    },
    dataType: 'html'
  });
}

function reset_form(form) {
  form.find('input:text, input:password, input:file, select').val('');
  form.find('input:radio, input:checkbox').removeAttr('checked').removeAttr('selected');
}
