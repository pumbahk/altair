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

function get_selected_options(select_multiple) {
  var options = select_multiple.options;
  var results = [];
  for (var i = 0; i < options.length; i++) {
    var opt = options.item(i);
    if (opt.selected) {
      results.push(opt.value);
    }
  }
  return results;
}

function build_form_params(form) {
  var param = {}, counts = {};
  $(form).find(':input').each(function(i, v) {
    if (v.type == 'checkbox' || v.type == 'radio') {
      value = v.checked ? v.value: null;
    } else if (v.type == 'select-multiple') {
      value = get_selected_options(v);
    } else {
      value = $(v).val();
      console.log(value);
    }
    if (value != null) {
      if (v.name.substr(-2) == '[]') {
        var _v = param[v.name];
        if (_v === void(0))
          param[v.name] = value;
        else if (_v instanceof Array)
          _v.push(value);
        else
          param[v.name] = [_v, value];
      } else {
        var count = counts[v.name];
        if (count === void(0)) {
          param[v.name] = value;
          counts[v.name] = 1;
        } else {
          var pv = param[v.name];
          delete param[v.name];
          param[v.name + '-0'] = pv;
          param[v.name + '-' + (counts[v.name]++)] = value;
        }
      }
    }
  });
  return param;
}

function post_modal_form(modal, form, url) {
  var data = build_form_params(form);
  $.ajax({
    type: 'post',
    url: url,
    data: data,
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

function load_modal_form(modal, url, data, callback) {
  var submitted = false;
  modal.find('> .modal-body').load(
    url,
    data,
    function () {
      var $form = $(this).find('form');
      $form.submit(function () {
        if (!submitted) {
          submitted = true;
          var data = build_form_params($form);
          load_modal_form(modal, $form.attr('action'), data, callback);
        }
        return false;
      });
      if (window['attach_datepicker'])
        window['attach_datepicker']($form.find('.datetimewidget-container'));
      if (callback)
        callback.call(this, $form);
      modal.modal('show');
    }
  );
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

var get_datetime_for, set_datetime_for, attach_datepicker;

(function () {
  var fields = ['year', 'month', 'day', 'hour', 'minute', 'second'];
  var dowStyleClasses = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var dows = ['日', '月', '火', '水', '木', '金', '土'];
  var datetimewidget_prefix = 'datetimewidget-';

  get_datetime_for = function get_datetime_for($container) {
    function nullIfNan(val) {
      return isNaN(val) ? null: val;
    }
    var retval = {};
    $.each(fields, function (_, k) {
      retval[k] = nullIfNan(parseInt($container.find('.' + datetimewidget_prefix + k + '[value]').val()));
    });
    return retval;
  };

  set_datetime_for = function set_datetime_for($container, value) {
    $.each(fields, function (_, k) {
      v = value[k];
      if (v !== void(0))
        $container.find('.' + datetimewidget_prefix + k + '[value]').val(v);
    });
  };

  function bind_event_for($container, type_or_handlers, optional_handler) {
    $.each(fields, function (_, k) { $container.find('.' + datetimewidget_prefix + k + '[value]').bind(type_or_handlers, optional_handler);
    });
  }

  attach_datepicker = function attach_datepicker($containers) {
    $containers.each(function (_, container) {
      container = $(container);
      if (!container.data('datepicker_enabled')) {
        function refresh_dow() {
          var value = get_datetime_for(container);
          if (value.year !== null && value.month !== null && value.day !== null) {
            var date = new Date(value.year, value.month - 1, value.day, 0, 0, 0);
            dow.removeClass(datetimewidget_prefix + dowStyleClasses.join(' ' + datetimewidget_prefix));
            dow.addClass(datetimewidget_prefix + dowStyleClasses[date.getDay()]);
            dowInner.text(dows[date.getDay()]);
          } else {
            dowInner.text('');
          }
        };

        container.data('datepicker_enabled', true);
      
        // dow checker
        var dow = $('<span class="' + datetimewidget_prefix + 'dow"></span>');
        var dowInner = $('<span class="' + datetimewidget_prefix + 'dow-text"></span>').appendTo(dow);
        dowInner.before('(');
        dowInner.after(')');
        container.find('span.' + datetimewidget_prefix + 'day').append(dow);
        bind_event_for(container, 'change', refresh_dow);

        // button
        var button = $('<a href="#"><i class="icon-calendar"></i></a>');
        button.click(function () {
          var o = button.offset();
          var now = new Date();
          var value = get_datetime_for(container);
          var dateStr =
              (value.year || (now.getYear() + 1900)) + '-' + 
              (value.month || (now.getMonth() + 1)) + '-' + 
              (value.day || now.getDate());
          function destroy() {
            button.datepicker("destroy");
          }
          button.datepicker("dialog",
            dateStr,
            function (date) {
              date = date.split('-');
              set_datetime_for(container, { year: date[0], month: date[1], day: date[2] });
              refresh_dow();
              destroy();
            }, {
              dateFormat: 'yy-m-d',
              showMonthAfterYear: true,
              yearSuffix: '年',
              monthNames: [
                '1月',
                '2月',
                '3月',
                '4月',
                '5月',
                '6月',
                '7月',
                '8月',
                '9月',
                '10月',
                '11月',
                '12月'
              ],
              dayNamesMin: dows,
              onClose: function () {
                destroy();
              }
            },
            [o.left, o.top]
          );
          $.datepicker.dpDiv.css('zIndex', 9999); // XXX: hack
          return false;
        });
        container.append(button);
        refresh_dow();
      }
    });
  };
})();

!(function ($){
  $.fn.disableOnSubmit = function(disablelist){
    var list = disablelist || 'input[type=submit], input[type=button], input[type=reset],button';
    $(this).find(list).removeAttr('disabled');
    $(this).submit(function(){
      $(this).find(list).attr('disabled','disabled');
    });
  };
}(jQuery))
