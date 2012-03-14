<%def name="widget_palets()">
    <div id="widget_palet">
      <div id="image" class="widget red float-left">画像</div>
      <div id="freetext" class="widget blue float-left">フリーテキスト</div>
      <div id="flash"  class="widget green float-left">flash</div>
      <div id="movie"  class="widget gray float-left">動画</div>
      <div id="calendar"  class="widget green float-left">カレンダー</div>
      <div id="detail"  class="widget blue float-left">イベント詳細</div>
      <div id="ticketlist"  class="widget red float-left">チケットリスト</div>
      <div id="performancelist"  class="widget red float-left">講演リスト</div>
      <div id="menu"  class="widget red float-left">メニュー</div>
      <div id="topic"  class="widget red float-left">トピック</div>
      <div id="topic"  class="widget red float-left">パンくずリスト</div>
    </div>
</%def>

<%def name="render_blocks(blocks)">
  <div id="wrapped">
    % for name  in blocks:
      <div id="${name}" class="block noitem">${name}</div>
    % endfor
  </div>
</%def>

<%def name="widget_js_scripts()">
<script type="text/javascript" src="/static/js/my/widgets/base.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/image.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/freetext.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/movie.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/flash.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/calendar.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/detail.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/ticketlist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/performancelist.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/menu.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/topic.js"></script>
## todo: moveit
<script type="text/javascript" src="/plugins/static/js/widget/lib/breadcrumbs.js"></script>
</%def>
