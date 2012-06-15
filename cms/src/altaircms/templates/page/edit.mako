<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<h2>page編集</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
        names=["Top", "Page", page.title], 
        urls=[request.route_path("dashboard"),
              h.page.to_list_page(request)]
    )}
  </div>
</div>

<%block name='style'>
    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
    <link rel="stylesheet" href="/static/css/page/edit.css" type="text/css" />

	${css.widget_css_scripts()}

	### widget追加する度に変更する必要(internal.css.mako)
    ${css.container_layout()}

<link href="/static/css/jquery.cleditor.css" rel="stylesheet" type="text/css"></link>

<style type="text/css">
  .alert{ margin:1%  }
  .size1{ width:100%;  }
  .size2{ width:44%; }
  .size3{ width:28%; }
  .left{ float:left; }
  .clear{ clear:both; }
</style>
</%block>

%if page and event:
  <h4>イベント"${event.title}"の"${page.title}"の編集</h4>
%elif page:
  <h4>${page.title}ページの編集</h4>
%endif

<div class="row" style="margin-bottom: 9px">
  <h2 class="span6"ページのタイトル - ${page.title} (ID: ${page.id})></h2>
</div>

<select onchange="window.location = this.value">
%for p in page.pageset.pages:
<option value="${request.route_url('page_edit_', page_id=p.id)}" ${'selected="selected"' if p.id == page.id else ''}>${p.version} ${p.title}</option>
%endfor
</select>

<div class="row-fluid">
  <h4>ページ情報</h4>
  <div class="span5">
     ${co.page_description(page)}
  </div>
  <div class="span1">
    <a class="btn btn-success" href="${h.front.to_preview_page(request,page)}" target="_blank"><i class="icon-eye-open"> </i> Preview</a>
  </div>
  <div class="span1">
    <a class="btn btn-danger" href="${h.page.to_delete(request,page)}"><i class="icon-trash icon-white"></i> Delete</a>
  </div>
  <div class="span1">
	<a class="btn btn-primary" href="${h.page.to_update(request,page)}"><i class="icon-cog"></i> Settings</a>
  </div>

  <!-- <div class="span1">
   !--     <button class="btn" href=""><i class="icon-refresh"> </i> Publish</button>
   !-- </div> -->

  <div class="span1">
      <a class="btn" href="${h.page.to_duplicate(request,page)}"><i class="icon-repeat"> </i> Duplicate</a>
  </div>

  <div class="span6">
	<br/>	<br/> <!-- ひどい -->
	<h2>layoutの保存</h2>
	## ここにレイアウト保存用のformが入る
	<form action="${h.page.to_widget_disposition(request,page)}" method="POST">
       <h4>現在のwidget layoutを保存</h4>
       <table class="table table-condensed">
       <tr><th>${forms["disposition_save"].title.label}</th><td>${forms["disposition_save"].title}</td></tr>
       <tr><th>${forms["disposition_save"].is_public.label}</th><td>${forms["disposition_save"].is_public}</td></tr>
	   ## submit button
       <tr><th>${forms["disposition_save"].page}${forms["disposition_save"].owner_id}<button type="submit"><i class="icon-cog"></i>save</button></th><td></td></tr>
       </table>
	</form>

	<form action="${h.page.to_widget_disposition(request,page)}" method="GET">
      <h4>widget layoutの読み込み</h4>
       <table class="table table-condensed">
       <tr><th>${forms["disposition_select"].disposition.label}</th><td>${forms["disposition_select"].disposition}</td></tr>
       <tr><th><button type="submit"><i class="icon-cog"></i>load</button></th><td></td></tr>
       </table>
	</form>

     <a href="${h.widget.to_disposition_list(request)}">widget layout一覧へ</a>
  </div>
</div>

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

