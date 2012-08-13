<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<h2>page編集</h2>

${nco.breadcrumbs(
  names=["Top", "Page", u"詳細ページ",page.name], 
  urls=[request.route_path("dashboard"),
        h.page.to_list_page(request,page),
        request.route_path("page_detail",page_id=page.id)]
)}

<%block name='style'>
    <link rel="stylesheet" type="text/css" href="/static/css/overlay-basic.css"/>
    <link rel="stylesheet" href="/static/css/page/edit.css" type="text/css" />

	### widget追加する度に変更する必要(internal.css.mako)
	${css.widget_css_scripts()}

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
  <h4>イベント"${event.title}"の"${page.name}"の編集</h4>
%elif page:
  <h4>${page.name}ページの編集</h4>
%endif

<div style="margin-bottom: 9px">
  <h2 class="span6"ページのタイトル - ${page.name} (ID: ${page.id})></h2>
</div>

<div class="row">
<div class="span6">
<select onchange="window.location = this.value">
%for p in page.pageset.pages:
<option value="${request.route_url('page_edit_', page_id=p.id)}" ${'selected="selected"' if p.id == page.id else ''}>${p.version} ${p.title}</option>
%endfor
</select>
</div>
<div class="span6">
  <a class="btn" href="${h.link.preview_page_from_page(request,page)}" target="_blank"><i class="icon-eye-open"> </i> Preview</a>
</div>
</div>
<hr/>

<a href="${h.widget.to_disposition_list(request)}">widget layout一覧へ</a>
<div class="row">
  <div class="span6">
	<form action="${h.page.to_widget_disposition(request,page)}" method="POST">
	   <h4>現在のwidget layoutを保存</h4>
	   <table class="table">
		 <tr><th>${disposition_save.title.label}</th><td>${disposition_save.title}</td></tr>
		 <tr><th>${disposition_save.is_public.label}</th><td>${disposition_save.is_public}</td></tr>
		 <tr><th>${disposition_save.save_type.label}</th><td>${disposition_save.save_type}</td></tr>
		 ## submit button
		 <tr><th>${disposition_save.page}${disposition_save.owner_id}<button class="btn" type="submit"><i class="icon-cog"></i>save</button></th><td></td></tr>
	   </table>
	</form>
  </div>

  <div class="span6">
	<form action="${h.page.to_widget_disposition(request,page)}" method="GET">
	  <h4>widget layoutの読み込み</h4>
	   <table class="table table-condensed">
		 <tr><th>${disposition_select.disposition.label}</th><td>${disposition_select.disposition}</td></tr>
		 <tr><th><button class="btn" type="submit"><i class="icon-cog"></i>load</button></th><td></td></tr>
	   </table>
	</form>
  </div>
</div>

## widget layout 
<h2>ページ内容の編集 <a class="btn" href="${h.link.preview_page_from_page(request,page)}" target="_blank"><i class="icon-eye-open"> </i> Preview</a></h2>

<div id="pagecontentform" style="margin-top:20px;">
  <!-- <div id="pagelayout">レイアウト選択</div>
   !-- <div id="pageversion">ページのバージョンが入る</div> -->
  <div id="pagewidget" class="well">ウィジェット
	### paletに表示するwidget
	${widget_aggregator.get_widget_paletcode(request)|n}
  </div>
  <br class="clear"/>
    <div id="main_page">ページ編集
      <div id="selected_layout" class="clear">

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

## jsの読み込み
${widget_aggregator.get_widget_jscode(request)|n} 

<script type="text/javascript" src="/static/js/page/backbone_patch.js"></script>
<script type="text/javascript" src="/static/js/page/edit.js"></script>

