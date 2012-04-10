<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>asset</h2>

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
    <h4>イベント追加</h4>
	<form action="${request.route_path("event_list")}?html=t" method="POST">
	  ${fco.form_as_table_strict(form, ["title", "subtitle","description","inquiry_for","event_open","event_close","deal_open","deal_close","is_searchable"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> イベントを作成</button>
    </form>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>イベント一覧</h4>
    ${mco.model_list(events, mco.event_list, u"イベントは登録されていません")}
</div>
