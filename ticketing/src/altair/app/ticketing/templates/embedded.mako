<%block name="more_styles" />
<%block name="more_scripts" />
<div class="embedded">
  <div class="embedded-header">
    <h2 class="embedded-header-content"><%block name="title" /></h2>
  </div>
  <div class="embedded-main">
    <div class="embedded-main-content">
      ${next.body(**context.kwargs)}
    </div>
  </div>
</div>
