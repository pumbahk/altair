<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>
<%namespace name="co" file="components.mako"/>
<%namespace name="css" file="internal.css.mako"/>

<h2>page編集</h2>

${nco.breadcrumbs(
  names=["Top", "Page", u"Pageset詳細", u"詳細ページ", page.name], 
  urls=[request.route_path("dashboard"),
        h.page.to_list_page(request,page),
        h.link.pageset_detail(request, page.pageset),
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
  input{ width:auto;}

  .flow-last {
    clear:both;
    height:1px;
    overflow:hidden;
  }
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

<div class="navbar navbar-inverse">
  <div class="navbar-inner">
    <div class="container" style="width: auto;">
      <a class="pull-left brand" href="#">編集中のページ</a>
      <form class="pull-left navbar-search" action="">
        <select class="search-query" style="min-width: 100px;" onchange="window.location = this.value">
          %for p in page.pageset.pages:
          <option value="${request.route_url('page_edit_', page_id=p.id)}" ${'selected="selected"' if p.id == page.id else ''}>${p.version} ${p.title}</option>
          %endfor
          </select>
          </form>
          ## layoutの変更
                  <ul class="nav pull-right">
                    <li id="fat-menu" class="dropdown">
                      <a href="#" id="drop3" role="button" class="dropdown-toggle" data-toggle="dropdown">widget layout <b class="caret"></b></a>
                      <ul class="dropdown-menu" role="menu" aria-labelledby="drop3">
                        <li><a tabindex="-1" href="${h.widget.to_disposition_list(request)}">widget layout一覧へ移動</a></li>
                        <li class="divider"></li>
                        <li><a tabindex="-1" href="#load_widget_layout_modal" data-toggle="modal">widget layoutの読込</a></li>
                        <li><a tabindex="-1" href="#save_widget_layout_modal" data-toggle="modal">widget layoutの保存</a></li>
                      </ul>
                    </li>
                  </ul>
          <ul class="nav pull-right" role="navigation">
            <li><a class="pull-right brand" href="#">現在のLayout</a></li>
            <form id="layout_update_form" class="pull-right navbar-form">
              <select id="layout" style="min-width: 100px;" >
                %for layout in layout_candidates:
                  %if layout.id == page.layout_id:
                  <option selected="selected" value="${layout.id}">${layout.title}(${layout.template_filename})</option>
                  %else:
                  <option value="${layout.id}">${layout.title}(${layout.template_filename})</option>
                  %endif
                %endfor
              </select>
              <button type="submit" class="btn">layoutを変更</button>
            </form>
            <script type="text/javascript">
              $(function(){
                $("#layout_update_form > button").on("click", function(e){
                  if(!window.confirm("ページのレイアウトを変更します。よろしいですか？(保存していないデータは失われます)")){
                     return false;
                   }
                  var layout_id = $('#layout_update_form > #layout > :selected').val(),
                      url       = '${request.route_path("page_partial_update", part="layout",id=page.id)}';
                  $.post(url, {layout_id: layout_id}).done(function(data){ if(data.status){location.reload(); }});
                  return false;
                })
              });
            </script>
          </ul>
    </div>
  </div><!-- /navbar-inner -->
</div><!-- /navbar -->

<div class="modal hide" id="save_widget_layout_modal">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
	  <h3>現在のwidget layoutを保存</h3>
  </div>
  <div class="modal-body">
	<form class="form" action="${h.page.to_widget_disposition(request,page)}" method="POST">
		${disposition_save.title.label} ${disposition_save.title}
    ${disposition_save.is_public.label} ${disposition_save.is_public()}
		${disposition_save.save_type.label} ${disposition_save.save_type}
		 ## submit button
		${disposition_save.page}${disposition_save.owner_id}
  </div>
  <div class="modal-footer">
    <button class="btn" type="button" data-dismiss="modal">キャンセル</button>
    <button class="btn btn-primary" type="submit"><i class="icon-cog"></i>保存</button>
  </div>
	</form>
</div>

<div class="modal hide" id="load_widget_layout_modal">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal">×</button>
	  <h3>widget layoutの読み込み</h3>
  </div>
  <div class="modal-body">
	  <form action="${h.page.to_widget_disposition(request,page)}" method="GET">
		  ${disposition_select.disposition.label} ${disposition_select.disposition}
  </div>
  <div class="modal-footer">
    <button class="btn" type="button" data-dismiss="modal">キャンセル</button>
    <button class="btn btn-primary" type="submit"><i class="icon-plus"></i>読み込み</button>
  </div>
	</form>
</div>

## widget layout 
<a class="btn" href="${h.link.preview_page_from_page(request,page)}" target="_blank"><i class="icon-eye-open"> </i> Preview</a>

<div class="well" id="pagecontentform" style="margin-top:20px;">
  <!-- <div id="pagelayout">レイアウト選択</div>
   !-- <div id="pageversion">ページのバージョンが入る</div> -->
  <div id="pagewidget" class="well">ウィジェット
	### paletに表示するwidget
	${widget_aggregator.get_widget_paletcode(request)|n}
  </div>
  <div class="clear clear-flow"></div>
  <div id="main_page">ページ編集
    <div id="selected_layout" class="clear">
      ${co.render_blocks(layout_render.blocks_image())}
    </div>
    
    <div class="dialog_overlay" id="overlay">
      <!-- the external content is loaded inside this tag -->
      <div id="wrap" class="contentWrap"></div>
    </div>
  </div>
  <div class="flow-last"></div>
</div>

<script type="text/javascript">
  function get_page(){return ${page.id};}
</script>

## jsの読み込み
${widget_aggregator.get_widget_jscode(request)|n} 

<script type="text/javascript" src="/static/js/page/backbone_patch.js"></script>
<script type="text/javascript" src="/static/js/page/edit.js"></script>

