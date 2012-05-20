(function ($) {

  document.write('<script type="text/javascript" src="/static/js/venue-editor/venue-editor.js"></script>');

  function initWindowUI(target) {
    function generateid() {
      do {
        var id = 'D' + ((Math.random() * 100000) | 0);
      } while (document.getElementById(id));
      return id;
    }

    var toolbar = $('<div class="ui-widget-header ui-corner-all ui-toolbar"></div>');
    var canvas = $('<div class="canvas"><div class="message">Loading...</div></div>');

    var data = {
      manager: null,
      toolbar: toolbar,
      canvas: canvas
    };

    var radio_id = generateid();

    function newButton(icon) {
      var id = generateid();
      var retval = $('<input type="radio" value="*" />')
        .attr('name', radio_id)
        .attr('id', id)
        .appendTo(toolbar);
      $('<label></label>').attr("for", id).appendTo(toolbar).text(icon);
      retval.button({ text: false, icons: { primary: icon }});
      return retval;
    }

    newButton('ui-icon-arrowthick-1-ne').click(
      function() {
        if (data.manager)
          data.manager.changeTool('select1');
      });

    newButton('ui-icon-calculator').click(
      function() {
        if (data.manager)
          data.manager.changeTool('select');
      });

    newButton('ui-icon-zoomin').click(
      function() {
        if (data.manager)
          data.manager.changeTool('zoomin');
      });

    newButton('ui-icon-zoomout').click(
      function() {
        console.log(data.manager);
        if (data.manager)
          data.manager.changeTool('zoomout');
      });

    var holder = $('<select id="adjacencies_selector"></select>');
    holder.appendTo(toolbar);
    $('<option value="1">1</option>').appendTo(holder);

    toolbar.buttonset();

    target.append(data.toolbar);
    target.append(data.canvas);

    return data;
  }

  $.fn.venue_editor = function(options) {

    var data = this.data('venue_editor');

    if (!data) { // if there are no store data. init and stor the data.
      data = initWindowUI(this);
      this.data('venue_editor', data);
    }

    var canvas = data.canvas;
    var toolbar = data.toolbar;

    if (typeof options == 'string' || options instanceof String) {
      switch (options) {
      case 'load':

        // Ajax Waiter
        var waiter = new Util.AsyncDataWaiter({
          identifiers: ['drawing_xml', 'metadata'],
          after: function main(all_data) {
            var xml = all_data['drawing_xml'];
            var metadata = all_data['metadata'];
            data.manager = new VenueEditor(canvas, xml, metadata);
          }
        });

        // Load drawing
        $.ajax({
          type: 'get',
          url: data.drawing_url,
          dataType: 'xml',
          success: function(xml) { waiter.charge('drawing_xml', xml); },
          error: function() { canvas.find('.message').text("Failed to load drawing data"); }
        });

        // Load metadata
        $.ajax({
          url: data.seat_data_url,
          dataType: 'json',
          success: function(data) { waiter.charge('metadata', data); },
          error: function() { canvas.find('.message').text("Failed to load seat data"); }
        });

        break;

      case 'remove':
        toolbar.remove();
        canvas.remove();
        data.manager.dispose();
        this.data('venue_editor', null);
        break;

      }
    } else {
      data.drawing_url = options.drawing_url;
      data.seat_data_url = options.seat_data_url;
    }

    return this;
  };

})(jQuery);
