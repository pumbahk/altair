##
##
##
<%inherit file='../layout.mako'/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
    <link rel="stylesheet" type="text/css" href="/static/css/my/sample.css">
    <link rel="stylesheet" href="/static/css/page/edit.css" type="text/css" />
 ##todo: moveit
    <link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/image.css">
    <link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/calendar.css">
    ${css.edit()}
</%block>
<%block name='js_foot'>
    <script type="text/javascript">
      ${co.form()}
    </script>
</%block>

%if page and event:
<h1>イベント${event}の${page}の編集</h1>
%elif event:
<h1>イベント${event}のページ追加</h1>
%elif page:
<h1>${page}ページの編集</h1>
%endif


${page_render.publish_status(request) | n}

%if event:
<a href="${request.route_url('event', id=event.id)}">back</a>
%endif

<div id="pageform">
    ${form|n}
</div>


<div id="pagecontentform">
  <div id="pagelayout">レイアウト選択</div>
  <div id="pageversion">ページのバージョンが入る</div>
  <div id="pagewidget">ウィジェット
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
    </div>
  </div>
  <br class="clear"/>
  <form action="#" method="post">
  </form>          
    <div id="main_page">ページ編集
      <div id="selected_layout" class="clear">
        <div id="wrapped">
          % for name  in layout_render.blocks_image():
            <div id="${name}" class="block noitem">${name}</div>
          % endfor
        </div>
      </div>

      <div class="dialog_overlay" id="overlay">
        <!-- the external content is loaded inside this tag -->
        <div id="wrap" class="contentWrap"></div>
      </div>
    </div>
    <a href="${request.route_url("front_to_preview", page_id=page.id)}">preview</a>
    <button type="submit">publish</button>
</div>

<script type="text/javascript">
  function get_page(){return ${page.id};}
</script>
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
<script type="text/javascript" src="/static/js/page/backbone_patch.js"></script>
<script type="text/javascript" src="/static/js/page/edit.js"></script>

