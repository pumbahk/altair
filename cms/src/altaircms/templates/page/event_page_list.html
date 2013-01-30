## page名,公開日,公開ステータス,url,preview
##
<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<%block name="style">
<style type="text/css">
  .row-fluid h3 { margin-top:20px;  }
</style>
</%block>

<h2>page</h2>

<div class="row-fluid">
  <div class="span12">
    ${nco.breadcrumbs(
	    names=["Top", "Page"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row-fluid">
  <h3 style="margin-top:0px;">ページ追加</h3>

    <div class="btn-group">
      <a href="${request.route_path("page_add_orphan", action="input")}" class="btn btn-success btn-large">新しいページを作成する</a>
	  <a class="btn btn-info btn-large" data-toggle="modal" href="#searchModal" >
		<i class="icon-search icon-white"></i> 検索フォーム</a>
	</div>

<div class="modal hide big-modal" id="searchModal">
  <div class="modal-header">
	<button type="button" class="close" data-dismiss="modal">×</button>
	<h3>イベント検索</h3>
  </div>
  <form class="form-inline">
  <div class="modal-body">
<div class="well">
## ugly
${search_form.freeword.label}: <th><td>${search_form.freeword}
${search_form.category.label}: </th><td>${search_form.category}
  <!-- <tr><th>${search_form.is_vetoed.label}: </th><td>${search_form.is_vetoed}</td></tr> -->
</table>
</div>
  </div>
  <div class="modal-footer">
	<a href="#" class="btn" data-dismiss="modal">Close</a>
	<button type="submit" class="btn btn-info">検索する</button>
	%if search_form.errors:
      <div class="alert alert-error">
		${search_form.errors}
	  </div>
	  <script type="text/javascript">
		$('#searchModal').modal('show');
	  </script>
	%endif
  </div>
  </form>
</div>

  <h3>ページ一覧</h3>

  <ul class="nav nav-tabs">
    <li class="active"><a href="${request.route_path("pageset_list",kind="event")}">イベント詳細ページ</a></li>
    <li><a href="${request.route_path("pageset_list",kind="other")}">トップ／カテゴリトップページ</a></li>
    <li><a href="${request.route_path("pageset_list",kind="static")}">静的ページ</a></li>
  </ul>

<%
page_count = pages.count()
seq = h.paginate(request, pages, item_count=page_count, items_per_page=50)
%>
<p>全${seq.opts.get("item_count") or seq.collection.count()}件</p>
  ${seq.pager()}
%if page_count <= 0:
<div class="alert alert-info">
  ページは登録されていません.
</div>
%else:
<table class="table table-striped">
  <thead>
	<tr>
	  <th>ページ名</th>
	  <th>URL</th>
	  <th>preview</th>
	  <th>生成日時</th>
	  <th>更新日時</th>
	</tr>
  </thead>
  <tbody>
    %for page in seq.paginated():
      <tr>
        <td><a href="${request.route_path("pageset_detail", pageset_id=page.id, kind="event")}">${page.name}</a></td>
        <td>${page.url}</td>
        <td>
          <a href="${h.link.preview_page_from_pageset(request, page)}" class="btn btn-small"><i class="icon-eye-open"> </i> Preview</a>
        </td>
		<td>${h.base.jdate(page.created_at)}</td>
		<td>${h.base.jdate(page.updated_at)}</td>
      </tr>
    %endfor
  </tbody>
</table>
${seq.pager()}
%endif
</div>
