<%def name="site_editor(image, callback=None)">
<div class="site_editor ui-widget">
  <div class="site_editor-header ui-widget-header">
    <div class="site_editor-header-content">
      ${caller.body()}
    </div>
  </div>
  <div class="site_editor-main ui-widget-content">
    <div class="site_editor-main-content">
      <div class="site_editor-figure">
        <div>
          <img src="${image}" />
        </div>
      </div>
      <script type="text/javascript">
      (function() {
        var n = $("script:last").prev().scrollview();
% if callback:
        (function() {${callback|n};}).apply(n);
% endif
      })();
      </script>
    </div>
  </div>
</div>
</%def>
