<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>event</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Event"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row-fluid">
  <div>
    <h3>イベント追加</h3>
    <a href="${request.route_path("event_create",action="input")}"  class="btn btn-success btn-large">新しいイベントを作成する</a>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>イベント一覧</h4>
<%
seq = h.paginate(request, events, item_count=events.count())
%>
${seq.pager()}
${mco.model_list(seq.paginated(), mco.event_list, u"イベントは登録されていません")}
${seq.pager()}
</div>
