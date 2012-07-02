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
  <h3 style="margin-top:0px;">イベント追加</h3>

  <div class="btn-group">
    <a href="${request.route_path("event_create",action="input")}"  class="btn btn-success btn-large">
	  <i class="icon-plus icon-white"></i> 新しいイベントを作成する</a>
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
<table>
  <tr><th>${search_form.freeword.label}: <th><td>${search_form.freeword}</td></tr>
  <tr><th>${search_form.category.label}: </th><td>${search_form.category}</td><td>${search_form.is_vetoed.label}:${search_form.is_vetoed}</td></tr>
  <tr><th>${search_form.deal_open.label}: </th><td>${search_form.deal_open}</td><td>${search_form.deal_open_op}</td></tr>
  <tr><th>${search_form.deal_close.label}: </th><td>${search_form.deal_close}</td><td>${search_form.deal_close_op}</td></tr>
  <tr><th>${search_form.event_open.label}: </th><td>${search_form.event_open}</td><td>${search_form.event_open_op}</td></tr>
  <tr><th>${search_form.event_close.label}: </th><td>${search_form.event_close}</td><td>${search_form.event_close_op}</td></tr>
  <tr><th>${search_form.created_at.label}: </th><td>${search_form.created_at}</td><td>${search_form.created_at_op}</td></tr>
  <tr><th>${search_form.updated_at.label}: </th><td>${search_form.updated_at}</td><td>${search_form.updated_at_op}</td></tr>
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



    <h3>イベント一覧</h3>
<%
seq = h.paginate(request, events, item_count=events.count())
%>
${seq.pager()}
${mco.model_list(seq.paginated(), mco.event_list, u"イベントは登録されていません")}
${seq.pager()}
</div>
