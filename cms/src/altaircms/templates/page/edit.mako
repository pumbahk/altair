##
##
##
<%inherit file='../layout_2col.mako'/>
##<%inherit file='../layout.mako'/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<%block name="breadcrumbs">
  <a href="${h.page.to_list_page(request)}">page</a> &raquo; ${page.title}
</%block>

<%block name='style'>
    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
    <link rel="stylesheet" href="/static/css/page/edit.css" type="text/css" />

	${css.widget_css_scripts()}

	### widget追加する度に変更する必要(internal.css.mako)
    ${css.container_layout()}
</%block>

%if page and event:
<h1>イベント${event}の${page}の編集</h1>
%elif event:
<h1>イベント${event}のページ追加</h1>
%elif page:
<h1>${page}ページの編集</h1>
%endif

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6"ページのタイトル - ${page.title} (ID: ${page.id})</h2>
</div>

<div class="row-fluid">
  <h4>ページ情報</h4>
  <div class="span5">
     ${co.page_description(page)}
  </div>
  <div class="span1">
    <a class="btn btn-success" href="${h.front.to_preview_page(request,page)}"><i class="icon-eye-open"> </i> Preview</a>
  </div>
  <div class="span1">
    <a class="btn btn-danger" href="${h.page.to_delete(request,page)}"><i class="icon-trash icon-white"></i> Delete</a>
  </div>
  <div class="span1">
	<a class="btn btn-primary" href="#"><i class="icon-cog"></i> Settings</a>
  </div>
  <div class="span1">
	<form action="." method="post">
      <button class="btn" href=""><i class="icon-refresh"> </i> Publish</button>
	</form>          
  </div>
</div>

%if event:
<a href="${request.route_path('event', id=event.id)}">back</a>
%endif

<div id="pagecontentform">
  <!-- <div id="pagelayout">レイアウト選択</div>
   !-- <div id="pageversion">ページのバージョンが入る</div> -->
  <div id="pagewidget">ウィジェット
	${co.widget_palets()}
  </div>
  <br class="clear"/>
    <div id="main_page">ページ編集
      <div id="selected_layout" class="clear">

		### widget追加する度に修正が必要。(component.mako)
        ${co.render_blocks(layout_render.blocks_image())}
      </div>

      <div class="dialog_overlay" id="overlay">
        <!-- the external content is loaded inside this tag -->
        <div id="wrap" class="contentWrap"></div>
      </div>
    </div>
</div>

<script type="text/javascript">
  function get_page(){return ${page.id};}
</script>

### widget追加する度に追加が必要(components.mako)
${co.widget_js_scripts()} 

<script type="text/javascript" src="/static/js/page/backbone_patch.js"></script>
<script type="text/javascript" src="/static/js/page/edit.js"></script>

