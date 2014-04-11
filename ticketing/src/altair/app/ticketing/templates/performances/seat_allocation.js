<%page args="performance" />

function deepClone(o) {
  if (o !== null && typeof o == 'object' && o.constructor == Object) {
    var retval = {};
    for (var k in o)
      retval[k] = deepClone(o[k]);
    return retval;
  } else {
    return _.clone(o);
  }
}

function gradientStyle(name, colors) {
  var buf = [], n = colors.length;
  buf.push(name, ':linear-gradient(top');
  for (var i = 0; i < n; i++) {
    var color = colors[i];
    buf.push(',', color[1], (color[0] * 100).toFixed(0) + '%');
  }
  buf.push(');');
  buf.push(name, ':-moz-linear-gradient(top');
  for (var i = 0; i < n; i++) {
    var color = colors[i];
    buf.push(',', color[1], (color[0] * 100).toFixed(0) + '%');
  }
  buf.push(');');
  buf.push(name, ':-o-linear-gradient(top');
  for (var i = 0; i < n; i++) {
    var color = colors[i];
    buf.push(',', color[1], (color[0] * 100).toFixed(0) + '%');
  }
  buf.push(');');
  buf.push(name, ':-webkit-gradient(linear,left top,left bottom');
  for (var i = 0; i < n; i++) {
    var color = colors[i];
    buf.push(',color-stop(',color[0], ',', color[1], ')');
  }
  buf.push(');');
  return buf.join(' ');
}

function buildColorButton(model, attr) {
  var button = $('<button></button>');
  function refresh() {
    var style = model.get(attr);
    if (style && style.fill)
      button.attr('style', gradientStyle('background', [[0, '#fff'], [.4, style.fill.color]]));
  }
  model.on('change:style', refresh);
  if (model.id != "") {
    button.click(function () {
      if (!$(this).data('colorpicker')) {
        $(this).data('colorpicker', true);
        $(this).decentcolorpicker({
          value: function () {
            var style = model.get(attr);
            return style && style.fill && style.fill.color;
          },
          select: function (value) {
            var style = deepClone(model.get(attr));
            if (!style.fill)
              style.fill = {};
            style.fill.color = value.hash;
            model.set(attr, style);
          }
        });
        $(this).click();
      }
    });
  }
  refresh();
  return button;
}

function bind(bindable, model, attr) {
  function onchange() {
    bindable.set(this.get(attr));
  }
  model.on('change:' + attr, onchange);
  bindable.bindStock('change:assignable', onchange);
  bindable.bindSave(function (value) {
    return model.set(attr, value, {
      error: function (msg) {
        bindable.element.popover(msg);
      }
    });
  });
  onchange.call(model);
}

function makeLockHandler(n, stock) {
  var lockable = $('<i class="icon-lock"></i>').appendTo(n);
  var venue = venueEditorRoot.venueeditor('model');
  function onClick() {
    var status = stock.get('assignable') ? false : true;
    stock.set('assignable', status);
    if (venue.perStockSeatSet[stock.id]) {
      venue.perStockSeatSet[stock.id].each(function(seat){
        if (!seat.get('sold')) seat.set('selectable', status);
      })
    }
    return false;
  }
  lockable.bind('click', onClick);
  function refresh() {
    if (stock.get('assignable')) {
      lockable.addClass('icon-white');
    } else {
      lockable.removeClass('icon-white');
    }
  }
  stock.on('change:assignable', refresh);
  refresh();
}

function makeAssignable(n, stock) {
  var assignable = $('<span></span>').appendTo(n);
  function onClick() {
    var selection = venueEditorRoot.venueeditor('selection');
    selection.each(function (seat) {
      seat.set('stock', stock);
    });
    venueEditorRoot.venueeditor('clearSelection');
    return false;
  }
  function refresh() {
    assignable.text(stock.get('assigned'));
    if (stock.get('assignable')) {
      assignable.bind('click', onClick).addClass('assignable');
    } else {
      assignable.unbind().removeClass('assignable');
    }
  }
  stock.on('change:assigned', refresh);
  stock.on('change:assignable', refresh);
  refresh();
}

var makeEditable = (function () {
  var editing = null;
  var prevDisplayStyleValue = null;

  return function makeEditable(n, stock) {
    var editable = $('<span></span>').appendTo(n);
    var editableIcon = $('<i class="icon-pencil" style="margin-left: 4px;"></i>').appendTo(n);
    var save = function (value) { set(value); };
    var value = '';

    function beginEdit() {
      if (editing)
        return;
      editing = $('<input type="text" class="editable" style="height:1em;margin:0 0; position: absolute;" />');
      var pos = editable.position();
      editing.val(value);
      prevDisplayStyleValue = editable.css('display');
      editable.css('display', 'none');
      editableIcon.css('display', 'none');
      editing.insertAfter(editable);
      editing.css({
       width: (n.innerWidth() - 10) + "px",
       left: '0px',
       top: (editable.parent().innerHeight() - editing.outerHeight()) / 2 + 'px'
      });
      editing.focus();
      editing.blur(function (e) {
        var _value = endEdit();
        save && save(_value);
        return false;
      });
      editing.keydown(function (e) {
        if (e.which == 13) {
          var _value = endEdit();
          save && save(_value);
          return false;
        }
        return true;
      });
    }

    function endEdit() {
      var value = editing.val();
      editable.css('display', prevDisplayStyleValue);
      editableIcon.css('display', 'inline-block');
      editing.remove();
      editing = null;
      return value;
    }

    function cancel() {
      endEdit();
    }

    function save() {
      save();
    }

    function onClick() {
      if (editing)
        cancel();
      beginEdit();
    }

    function set(_value) {
      if (editing)
        editing.val(_value)
      editable.text(_value);
      value = _value;

      if (stock.get('assignable')) {
        editable.bind('click', onClick).addClass('editable');
        editableIcon.css('display', 'inline-block');
      } else {
        editable.unbind().removeClass('editable');
        editableIcon.css('display', 'none');
      }
    }

    return {
      element: editable,
      set: set,
      get: function () {
        return value;
      },
      bindSave: function (_save) {
        save = _save;
      },
      bindStock: function (event, listener) {
        stock.on(event, listener);
      }
    }
  }
})();

function buildStockRow(stock) {
  var tr = $('<tr></tr>');
  var legend = $('<td class="stock-legend"></td>');
  var name = $('<td class="stock-name"></td>');
  var stockType = stock.get('stockType');
  if (stockType.id != "") {
    buildColorButton(stockType, 'style').appendTo(legend);
    bind(makeEditable(name, stock), stockType, 'name');
  } else {
    name.text(stockType.get('name'));
  }
  var quantity = $('<td class="stock-quantity"></td>');
  if (stockType.get('isSeat') && !stockType.get('quantityOnly')) {
    makeAssignable(quantity, stock);
  } else {
    bind(makeEditable(quantity, stock), stock, 'assigned');
  }
  var lock = $('<td class="stock-lock"></td>');
  makeLockHandler(lock, stock);
  tr.append(legend);
  tr.append(name);
  tr.append(quantity);
  tr.append(lock);
  return tr;
}

function buildStockRowForStockType(stock) {
  var tr = $('<tr></tr>');
  var legend = $('<td class="stock-legend"></td>');
  var name = $('<td class="stock-name"></td>');
  var stockType = stock.get('stockType');
  var stockHolder = stock.get('stockHolder');
  var style = stockHolder.get('style');
  if (stockType.id != "") {
    legend.text(style['text']);
    bind(makeEditable(name, stock), stockHolder, 'name');
  } else {
    name.text(stockHolder.get('name'));
  }
  var quantity = $('<td class="stock-quantity"></td>');
  if (stockType.get('isSeat') && !stockType.get('quantityOnly')) {
    makeAssignable(quantity, stock);
  } else {
    bind(makeEditable(quantity, stock), stock, 'assigned');
  }
  var lock = $('<td class="stock-lock"></td>');
  makeLockHandler(lock, stock);
  tr.append(legend);
  tr.append(name);
  tr.append(quantity);
  tr.append(lock);
  return tr;
}

function buildStockTypeHolderTables(venue) {
  var retval = $('<div></div>');
  venue.stockTypes.each(function (stockType) {
    var keyedStocks = stockType.keyedStocks();
    var swatch = buildColorButton(stockType, 'style').addClass('swatch');
    var head = $('<h5 class="ui-header" style="float: left;"></h5>').text(' ' + stockType.get('name'));
    var rest = $('<span class="rest label"></span>');
    function refresh() {
      rest.text('残席: ' + stockType.get('available') + '席');
    }
    stockType.on('change:available', refresh);
    refresh();
    stockType.recalculateQuantity();
    var div = $('<div></div>').css('display', 'none');
    var table = $('<table class="table table-bordered"></table>');
    var tbody = $('<tbody></tbody>').appendTo(table);

    venue.stockHolders.each(function (stockHolder) {
      var stock = keyedStocks && keyedStocks[stockHolder.id];
      if (!stock)
        return;
      var row = buildStockRowForStockType(stock);
      tbody.append(row);
    });

    head.click(function () {
      if (div.css('display') == 'block')
        div.css('display', 'none');
      else
        div.css('display', 'block');
    });
    head.prepend(swatch);
    table.appendTo(div);

    retval.append(head);
    retval.append(rest);
    retval.append('<div style="clear: both;"></div>');
    retval.append(div);
  });
  return retval;
}

function buildStockHolderTypeTables(venue) {
  var retval = $('<div></div>');
  venue.stockHolders.each(function (stockHolder) {
    var keyedStocks = stockHolder.keyedStocks();
    var style = stockHolder.get('style');
    var swatch = $('<span class="swatch"></span>').css('text-color', style.text_color).text(style.text||'　');
    var head = $('<h5 class="ui-header" style="float: left;"></h5>').text(' ' + stockHolder.get('name'));
    var transfer = $('<a class="transfer btn btn-mini btn-inverse" href="javascript:buildTransferModal(' + stockHolder.id + ');">枠移動</a>');
    var rest = $('<span class="rest label"></span>');
    function refresh() {
      rest.text('残席: ' + stockHolder.get('available') + '席');
    }
    stockHolder.on('change:available', refresh);
    refresh();
    stockHolder.recalculateQuantity();
    var div = $('<div></div>').css('display', 'none');
    var table = $('<table class="table table-bordered"></table>');
    var tbody = $('<tbody></tbody>').appendTo(table);
    venue.stockTypes.each(function (stockType) {
      var stock = keyedStocks && keyedStocks[stockType.id];
      if (!stock)
        return;
      var row = buildStockRow(stock);
      tbody.append(row);
    });
    head.click(function () {
      if (div.css('display') == 'block')
        div.css('display', 'none');
      else
        div.css('display', 'block');
    });
    head.prepend(swatch);
    table.appendTo(div);

    retval.append(head);
    retval.append(transfer);
    retval.append(rest);
    retval.append('<div style="clear: both;"></div>');
    retval.append(div);
  });
  return retval;
}

function buildSeatDetailRow(seat) {
  var tr = $('<tr></tr>');
  var count = $('span.selection-count');
  var checkbox = $('<input type="checkbox" checked="checked" />').attr('name', seat.get('id')).click(function () {
    if (this.checked)
      seat.set('selected', true);
    else
      seat.set('selected', false);
    count.text(parseInt(count.text())+(this.checked ? 1 : -1));
  });
  var checkbox_td = $('<td></td>').append(checkbox);
  var seat_id = $('<td></td>').text(seat.get('id'));
  var name = $('<td></td>').text(seat.get('name'));
  var stock_type = $('<td></td>').text(seat.get('stock').get('stockType').get('name'));
  var stock_holder = $('<td></td>').text(seat.get('stock').get('stockHolder').get('name'));
  tr.append(checkbox_td);
  tr.append(seat_id);
  tr.append(name);
  tr.append(stock_type);
  tr.append(stock_holder);
  return tr;
}

function buildSeatDetailTable(selection) {
  var table = $('<table class="table table-condensed"></table>');
  var tbody = $('<tbody></tbody>').appendTo(table);
  var header = $('<th width="8%"></th width="15%"><th>ID</th><th width="30%">座席</th><th width="27%">席種</th><th width="20%">配券先</th>');
  tbody.append(header);
  if (selection.length) {
    selection.each(function (seat) {
      tbody.append(buildSeatDetailRow(seat));
    });
  }
  return table;
}

function buildTransferModal(id) {
  var id = id || "";
  var modal = $('#modal-transfer');
  var body = modal.find('.modal-body');
  var venue = venueEditorRoot.venueeditor('model');
  var current = $('<p>選択した枠：' +  + '</p>');
  var select = $('<p>移動先の枠：</p><select name="to"></select>');
  venue.stockHolders.each(function (stockHolder) {
    if (stockHolder.get('id') == id) {
      current = $('<p>選択した枠：' + stockHolder.get('name') + '</p><input name="from" type="hidden" value="' + stockHolder.get('id') + '" />');
    } else {
      select.append($("<option>").text(stockHolder.get('name')).attr("value", stockHolder.get('id')));
    }
  });
  body.empty().append(current).append(select);
  modal.show();
}

function transferStocks() {
  var errors = [];
  var modal = $('#modal-transfer');
  var body = modal.find('.modal-body');
  var venue = venueEditorRoot.venueeditor('model');
  var from_stock_holder = body.find('input[name="from"]').val();
  var to_stock_holder = body.find('select[name="to"] option:selected').val();

  for (var i in venue.perStockHolderStockMap[from_stock_holder]) {
    var from_stock = venue.perStockHolderStockMap[from_stock_holder][i];
    var to_stock = null;

    var assignable = from_stock.get('assignable');
    if(!assignable){
        errors.push(from_stock);
        continue;
    }

    var stock_type = from_stock.get('stockType');
    for (var j in venue.perStockTypeStockMap[stock_type.get('id')]) {
      to_stock = venue.perStockTypeStockMap[stock_type.get('id')][j];
      if (to_stock_holder == to_stock.get('stockHolder').get('id')) {
        break;
      }
    }

    if (!to_stock || to_stock.id == from_stock.id){
        errors.push(from_stock);
        continue;
    }
    if (stock_type.get('isSeat') && !stock_type.get('quantityOnly')) {
      if (venue.perStockSeatSet[from_stock.id]) {
        venue.perStockSeatSet[from_stock.id].each(function(seat){
          if (seat.get('selectable')) seat.set('stock', to_stock);
        })
      }
    } else {
      var unavailable = parseInt(from_stock.get('assigned')) - parseInt(from_stock.get('available'));
      to_stock.set('assigned', parseInt(to_stock.get('assigned')) + parseInt(from_stock.get('available')));
      from_stock.set('assigned', unavailable);
    }
  }
  modal.hide();
  buildCannotStockActionModal(errors, '枠移動ができなかった在庫がありました');
  setTimeout(update_tables, 1000);
}

function buildTransferStocksSelectedModal() {
  var id = id || "";
  var modal = $('#modal-transfer-selected');
  var body = modal.find('.modal-body');
  var venue = venueEditorRoot.venueeditor('model');
  var current = $('<p>選択した枠：' +  + '</p>');
  var select = $('<p>移動先の枠：</p><select name="to"></select>');
  venue.stockHolders.each(function (stockHolder) {
      select.append($("<option>").text(stockHolder.get('name')).attr("value", stockHolder.get('id')));
  });
  body.empty().append(select);
  modal.show();
}

function buildCannotSeatActionModal(seats, message){
    if (seats.length == 0){
        return; // no error
    }
    var modal = $('#modal-cannot-seat-action');
    var msg = modal.find('#cannot-seat-action-message');
    var body = modal.find('.modal-body');

    var table = $('<table><tr>'+
                  '<th>l0_id</th>'+
                  '<th>座席名</th>'+
                  '</tr></table>');

    $.each(seats, function(index, seat){
        var row = $('<tr>'+
                    '<td>'+seat.get('id')+'</td>' +
                    '<td>'+seat.get('name')+'</td>' +
                    '</tr>');
        table.append(row);
    });

    msg.text(message);
    body.empty();
    body.append(table);
    modal.show();
}

function buildCannotStockActionModal(stocks, message){
    if (stocks.length == 0){
        return; // no error
    }
    var modal = $('#modal-cannot-stock-action');
    var msg = modal.find('#cannot-stock-action-message');
    var body = modal.find('.modal-body');

    var table = $('<table><tr>'+
                  '<th>枠</th>'+
                  '<th>席種</th>'+
                  '</tr></table>');

    $.each(stocks, function(index, stock){
        var row = $('<tr>'+
                    '<td>'+stock.get('stockHolder').get('name')+'</td>' +
                    '<td>'+stock.get('stockType').get('name')+'</td>' +
                    '</tr>');
        table.append(row);
    });

    msg.text(message);
    body.empty();
    body.append(table);
    modal.show();
}

function buildCannotSeatConvertModal(errors, cannot_converts){
    var msg = '';
    var modal = $('#modal-cannot-seat-convert');
    var message = modal.find('#cannot-seat-action-message');
    var body = modal.find('.modal-body');
    body.empty();
    if (errors.length > 0){
        msg += '選択できなかった座席 ';
        var header = $('<h4>選択できなかった座席</h4>')
        var error_table = $('<table><tr>'+
                            '<th>l0_id</th>'+
                            '<th>座席名</th>'+
                            '</tr></table>');
        $.each(errors, function(index, seat){
            var row = $('<tr>'+
                        '<td>'+seat.get('id')+'</td>' +
                        '<td>'+seat.get('name')+'</td>' +
                        '</tr>');
            error_table.append(row);
        });
        body.append(header);
        body.append(error_table);
    }
    if (cannot_converts.length > 0){
        msg += '座席情報を変換できなかった座席 ';
        var header = $('<h4>座席情報を変換できなかった座席</h4>')
        var cannot_convert_table = $('<table><tr>'+
                                     '<th>外部座席ID</th>'+
                                     '</th></table>');
        $.each(cannot_converts, function(index, ex_l0_id){
            var row = $('<tr>'+
                        '<td>'+ex_l0_id+'</td>' +
                        '</tr>');
            cannot_convert_table.append(row);
        });
        body.append(header);
        body.append(cannot_convert_table);
    }
    if (errors.length > 0 ||  cannot_converts.length > 0){
        msg += 'があります。';
        message.text(msg);
        modal.show();
    }
}

function transferStocksSelected() {
  var modal = $('#modal-transfer-selected');
  var body = modal.find('.modal-body');
  var venue = venueEditorRoot.venueeditor('model');
  var to_stock_holder_id = body.find('select[name="to"]').val();
  var stocks = venue.perStockHolderStockMap[to_stock_holder_id];
  var errors = [];
  venue.seats.each(function(seat){
      if (seat.get('selected')){
          var stock = seat.get('stock');
          var stock_type = stock.get('stockType');
          var stock_type_id = stock_type.get('id');

          if (stock_type_id){
              var stock = stocks[stock_type_id];
              if (stock){
                  seat.set('stock', stock);
                  if (seat.get('stock') == stock){
                      seat.set('selected', false);
                  }
              }else{
                  errors.push(seat);
              }
          }else{
              errors.push(seat);
          }
      }
  });
  modal.hide();
  buildCannotSeatActionModal(errors, '枠移動ができなかった座席がありました');
  setTimeout(update_tables, 1000);
}

function saveStocks() {
  var modal = $('#modal-result');
  modal.find('.modal-body .alert').remove();
  var label = $('a[name="save"]');
  label.text('保存中').attr('disabled', 'disabled');
  var venue = venueEditorRoot.venueeditor('model');
  $.ajax({
    type: 'post',
    url: "${request.route_path('stocks.allocate', performance_id=performance.id)}",
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    data: JSON.stringify(venue.toJSON()),
    success: function(result) {
      $('.content').html('<div class="alert alert-success"><a class="close" data-dismiss="alert">&times;</a><h4 class="alert-heading">' + result.message + '</h4></div>');
      modal.modal('hide');
      label.text('保存する').removeAttr('disabled');
      venueEditorRoot.venueeditor('clearAll');
    },
    error: function(xhr, text) {
      var responseText = JSON.parse(xhr.responseText);
      var messages = responseText['message'] || xhr.statusText;
      var errors = '';
      if (typeof messages == 'string') {
        errors += '<li>' + messages + '</li>';
      } else {
        for (i in messages)
          errors += '<li>' + messages[i] + '</li>';
      }
      modal.find('#message').text("保存できませんでした").after('<div class="alert alert-error"><ul>' + errors + '</ul></div>');
      modal.modal('toggle');
      label.text('保存する').removeAttr('disabled');
    }
  });
}

function csv_seat_allocation() {
    var modal = $('#modal-csv-seat-allocation');
    modal.modal('show');
}

function update_tables(){
    var selection = venueEditorRoot.venueeditor('selection');
    update_selection_table(selection);
    /*$('span.selection-count').text(selection.length);*/
}

function select_seats_by_csv(){
    var fd;
    var modal = $("#modal-csv-seat-allocation");
    var $form = $("#csv-seat-allocation-form");
    var url = "${request.route_path('cooperation.get_seat_l0_ids', performance_id=performance.id)}"
    var venue = venueEditorRoot.venueeditor('model');
    var errors = [];
    var cannot_converts = [];
    var msg = '';
    fd = new FormData($form[0]);
    modal.modal('hide');
    $.ajax(url, {
        type: "POST",
        processData: false,
        contentType: false,
        data: fd,
        dataType: "json",
        success: function(data){
            $.each(data.fail, function (ex_l0_id, value){
                cannot_converts.push(ex_l0_id);
            });

            for (var name in data.success){
                var l0_id = data.success[name];
                venue.seats.each(function(seat){
                    if (seat.get('id') == l0_id){
                        seat.set('selected', true);
                        if (seat.get('selected') != true){
                            errors.push(seat);
                        }
                        return false;
                    }
                });
            }
            buildCannotSeatConvertModal(errors, cannot_converts);
        },
        error: function(xhr, text) {
            var responseText = JSON.parse(xhr.responseText);
            var messages = responseText['message'] || xhr.statusText;
            var errors = '';
            if (typeof messages == 'string') {
                errors += '<li>' + messages + '</li>';
            } else {
                for (i in messages)
                    errors += '<li>' + messages[i] + '</li>';
            }
            msg = modal.find('#message');
            msg.empty();
            msg.text("選択できませんでした").append('<div class="alert alert-error"><ul>' + errors + '</ul></div>');
            modal.modal('toggle');
        }
    });
    setTimeout(update_tables, 1000);
}

function update_selection_table(selection) {
  if (selection.length)
    $(".assignable").addClass("enabled");
  else
    $(".assignable").removeClass("enabled");

  var selection_set = venueEditorRoot.venueeditor('selection');
  if (selection.length == 1) {
    var tbody = $('#venue-editor-main-side-tab2').find('table tbody');
    // 単一選択なら選択状態を反映
    var tr = tbody.find('tr input[name="' + selection[0].get('id') + '"]');
    if (tr.length > 0) {
      if (selection[0].get('selected'))
        tr.attr('checked', 'checked');
      else
        tr.removeAttr('checked');
    } else {
      tbody.append(buildSeatDetailRow(selection[0]));
    }
  } else {
    // 複数選択ならテーブル再生成
    tab2.empty();
    tab2.append(buildSeatDetailTable(selection_set));
  }
  $('span.selection-count').text(selection_set.length);
};
