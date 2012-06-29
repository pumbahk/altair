<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

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
  <h3>ページ追加</h3>
    <a href="${request.route_path("page_add_orphan", action="input")}" class="btn btn-success btn-large">新しいページを作成する</a>


  <h3>ページ一覧</h3>
<%
seq = h.paginate(request, pages, item_count=pages.count())
%>
  ${seq.pager()}
  ${mco.model_list(seq.paginated(), mco.page_list, u"ページは登録されていません")}
  ${seq.pager()}
</div>
