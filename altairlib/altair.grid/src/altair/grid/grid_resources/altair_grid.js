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
