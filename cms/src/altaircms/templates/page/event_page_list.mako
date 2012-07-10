## page名,公開日,公開ステータス,url,preview
## event付きかのlabel
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
    <a href="${request.route_path("page_add_orphan", action="input")}" class="btn btn-success btn-large">新しいページを作成する</a>

  <h3>ページ一覧</h3>

  <ul class="nav nav-tabs">
    <li class="active"><a href="${request.route_path("pageset_list",kind="event")}">イベント詳細ページ</a></li>
    <li><a href="${request.route_path("pageset_list",kind="other")}">トップ／カテゴリトップページ</a></li>
  </ul>

<%
page_count = pages.count()
seq = h.paginate(request, pages, item_count=page_count)
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
      </tr>
    %endfor
  </tbody>
</table>
${seq.pager()}
%endif
</div>
