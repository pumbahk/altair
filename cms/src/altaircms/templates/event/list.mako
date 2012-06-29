<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<%block name="style">
<style type="text/css">
  .row-fluid h3 { margin-top:20px;  }
</style>
</%block>

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
    <h3 style="margin-top:0px;">イベント追加</h3>
    <a href="${request.route_path("event_create",action="input")}"  class="btn btn-success btn-large">新しいイベントを作成する</a>
  </div>

  <div>

<h3>イベント検索</h3>
	%if search_form.errors:
      <div class="alert alert-error">
		${search_form.errors}
	  </div>
	%endif
  <form class="well form-inline">
	${search_form.freeword.label}: ${search_form.freeword}
## ugly
<table>
  <tr><td>${search_form.deal_open.label}: </td><td>${search_form.deal_open}</td><td>${search_form.deal_open_op}</td></tr>
  <tr><td>${search_form.deal_close.label}: </td><td>${search_form.deal_close}</td><td>${search_form.deal_close_op}</td></tr>
  <tr><td>${search_form.event_open.label}: </td><td>${search_form.event_open}</td><td>${search_form.event_open_op}</td></tr>
  <tr><td>${search_form.event_close.label}: </td><td>${search_form.event_close}</td><td>${search_form.event_close_op}</td></tr>
  <tr><td>${search_form.created_at.label}: </td><td>${search_form.created_at}</td><td>${search_form.created_at_op}</td></tr>
  <tr><td>${search_form.updated_at.label}: </td><td>${search_form.updated_at}</td><td>${search_form.updated_at_op}</td></tr>
</table>
<button type="submit" class="btn">検索</button>
  </form>
  </div>



    <h4>イベント一覧</h4>
<%
seq = h.paginate(request, events, item_count=events.count())
%>
${seq.pager()}
${mco.model_list(seq.paginated(), mco.event_list, u"イベントは登録されていません")}
${seq.pager()}
</div>
