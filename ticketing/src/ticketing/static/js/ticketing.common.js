function get_id(id) {
  return $('input[name=' + id + ']:checked').val() || $('#' + id).val();
}

function get_modal_form(modal, form, url) {
  $.ajax({
    type: 'get',
    url: url,
    dataType: 'html',
    traditional: true,
    success: function(data) {
      $(form).html(data);
      $(modal).modal('show');
    },
    error: function(xhr, text) {
      $(form).html(xhr.responseText);
      $(modal).modal('show');
    }
  });
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
    error: function(xhr, text) {
      $(modal).modal('hide');
      $(form).html(xhr.responseText);
      $(modal).modal('show');
    },
    dataType: 'html'
  });
}

function reset_form(form, exclude, new_form) {
  exclude = exclude || '';
  new_form = new_form || false;
  form.find(':input').each(function() {
    var $this = $(this);
    if (new_form && $this.attr('data-hide-on-new') == 'hide-on-new') {
      $this.parent().parent().hide();
    } else {
      $this.parent().parent().show();
    }
    if (!$this.not(exclude).length)
      return;
    switch(this.type) {
      case 'password':
      case 'select-multiple':
      case 'select-one':
      case 'text':
      case 'textarea':
      case 'hidden':
        $this.val('');
        break;
      case 'checkbox':
        $this.removeAttr('checked');
        break;
      case 'radio':
        $this.removeAttr('selected');
        break;
    }
  });
}

!(function ($){
  $.fn.disableOnSubmit = function(disablelist){
    var list = disablelist || 'input[type=submit], input[type=button], input[type=reset],button';
    $(this).find(list).removeAttr('disabled');
    $(this).submit(function(){
      $(this).find(list).attr('disabled','disabled');
    });
  };
}(jQuery))
