function applyUIStyles(root) {
  root = $(root);
  root.find(".ui-button").each(function(i, n) {
    n = $(n);
    options = {};
    $.each(n.attr("class").split(/\s+/), function(i, klass) {
      if (klass.indexOf('ui-icon-') == 0) {
        if (!options.icons) {
          options.icons = {}
          if (klass != 'ui-icon-')
            options.icons.primary = klass;
        } else {
          options.icons.secondary = klass;
        }
      }
    });
    n.button(options);
  });
  root.find(".ui-buttonset").buttonset();
  root.find(".ui-tabs").tabs();
  root.find(".datetime_field").datepicker();
  root.find(".flexigrid").flexigrid();
}
function showDialog(url, options) {
  if (typeof options == 'undefined')
    options = {};
  $.ajax({
    url: url,
    failure: function() {
      alert('Oops, something went wrong!');
    },
    success: function(data) {
      $("<div></div>").append(data).appendTo(document.body).dialog(
        $.extend(
          {
            open: function() {
              applyUIStyles(this);
              if (dialog_onload)
                dialog_onload.apply(this);
            },
            close: function() {
              $(this).dialog('destroy');
            },
          },
          options
        )
      );
    }
  });
}
$(function() {
  $('.checkboxed_table .__action__-select_all_in_group').click(function() {
    var self = $(this);
    var parent = self.closest('tr')
    var matches = /__group__-(\d+)/.exec(parent.attr('class'));
    parent.nextAll('.' + matches[0]).andSelf().find(':checkbox').each(function(_, n) { n.checked = self[0].checked; });
  });
  $('.checkboxed_table .__action__-select_all').click(function() {
    var self = $(this);
    self.closest('table').find('tbody :checkbox').each(function(_, n) { n.checked = self[0].checked; });
  });
  $('.checkboxed_table :checkbox[class=""]').click(function() {
    var self = $(this);
    var parent = self.closest('tr');
    var matches = /__group__-\d+/.exec(parent.attr('class'));
    if (!matches)
      return;
    var grandma = parent.parent();
    var all_checkboxes_in_group = grandma.find('.' + matches[0] + ' :checkbox[class=""]');
    grandma.find('.' + matches[0] + ' .__action__-select_all_in_group')[0].checked = 
      all_checkboxes_in_group.length ==
        all_checkboxes_in_group.filter(':checked').length;
  });
  $('.__action__-open_in_dialog').click(function() {
    var m = /#(.+)/.exec(this.href), options = {};
    if (m[1]) {
      try {
        options = $.parseJSON(decodeURIComponent(m[1]));
      } catch (e) {
        alert("Oops!");
        return false;
      }
    }
    showDialog(this.href, options);
    return false;
  });
});
