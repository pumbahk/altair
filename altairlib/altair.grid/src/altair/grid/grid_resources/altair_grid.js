(function($) {
  $.fn.setRetainChanges = function(cells) {
    if (this.data('retainedChanges') == undefined) {
      this.data('retainedChanges', {});
    }
    var retainedChanges = this.data('retainedChanges');
    cells = cells || this.getChangedCells('dirty');
    for (var i=0; i<cells.length; i++) {
      if (!retainedChanges[cells[i].id]) {
        retainedChanges[cells[i].id] = {};
      }
      retainedChanges[cells[i].id] = $.extend(retainedChanges[cells[i].id], cells[i]);
    }
    this.data('retainedChanges', retainedChanges);
  };
  $.fn.getRetainChanges = function(type) {
    type = type || 'row';
    if (type == 'row') {
      var rows = [];
      if (this.data('retainedChanges') != undefined) {
        var retainedChanges = this.data('retainedChanges');
        for (var k in retainedChanges) {
          rows.push($.extend({id:k}, this.getRowData(k)));
        }
      }
      return rows;
    }
    if (type == 'cell') {
      var cells = []
      if (this.data('retainedChanges') != undefined) {
        var retainedChanges = this.data('retainedChanges');
        for (var k in retainedChanges) {
          cells.push(retainedChanges[k]);
        }
      }
      return cells;
    }
  };
  $.fn.clearRetainChanges = function() {
    this.data('retainedChanges', {});
    this.setGridParam({datatype:'json', treedatatype:'json'}).trigger('reloadGrid');
    this.setGridParam({treedatatype:'local'});
  };
  $.fn.getColumnLabel = function(grid, columnName) {
    var cm = grid.jqGrid('getGridParam','colModel');
    for (var i=0; i<cm.length; i++) {
      if (cm[i].name == columnName) return grid.jqGrid('getGridParam','colNames')[i];
    }
  };
  $.fn.linkFormatter = function(cellvalue, options, rowObject) {
    var link = '';
    if (!rowObject.level) {
      link += '<a href="javascript:addRow(' + "'" + options.gid + "'," + options.rowId + ');"><i class="icon-plus"></i></a>';
    }
    if (rowObject.product_item) {
      link += '<a href="javascript:deleteRow(' + "'" + options.gid + "'," + options.rowId + ');"><i class="icon-trash"></i></a>';
    }
    if (rowObject.ticket_bundle && rowObject.ticket_bundle.id) {
      link += '<a href="javascript:preview_ticket(' + rowObject.product_item.id + ')"><i class="icon-eye-open"></i></a>';
    }
    return link;
  };
})(jQuery);

function addRow(gid, rowId) {
  var grid = $('#' + gid);
  var row = grid.getRowData(rowId);
  if (!row.level) {
    grid.setCell(rowId, 'parent', 'null');
    grid.setCell(rowId, 'level', 0);
    grid.setCell(rowId, 'isLeaf', false);
    grid.setCell(rowId, 'expanded', true);
    grid.setCell(rowId, 'loaded', true);
  }

  var data ={
    product_id:row.product_id,
    product_name:'(複数在庫商品)'
  }
  grid.addChildNode(undefined, rowId, data);
}
function deleteRow(gid, rowId) {
  var grid = $('#' + gid);
  grid.setCell(rowId, 'stock_holder_id', '', {background:'#BD362F'});
  grid.setCell(rowId, 'product_item_name', '', {background:'#BD362F'});
  grid.setCell(rowId, 'product_item_price', '', {background:'#BD362F'});
  grid.setCell(rowId, 'product_item_quantity', '', {background:'#BD362F'});
  grid.setCell(rowId, 'stock_quantity', '', {background:'#BD362F'});
  grid.setCell(rowId, 'stock_status_quantity', '', {background:'#BD362F'});
  grid.setCell(rowId, 'ticket_bundle_id', '', {background:'#BD362F'});
  grid.setCell(rowId, 'deleted', true);
  var row = new Object();
  row['id'] = rowId;
  grid.setRetainChanges([row]);
}
