<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>topic</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topic"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row-fluid">
  <div>
      <h4>トピック追加</h4>
      <form id="topic_add_form" action="${request.route_path("topic_list")}?html=t" method="POST">
	  ${fco.form_as_table_strict(form, ["title","kind", "category", "publish_open_on","publish_close_on","text","orderno","is_vetoed","page","event","is_global"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 保存</button>
	  </form>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>トピック一覧</h4>
	${topics.pager()}
	${mco.model_list(topics.paginated(), mco.topic_list, u"トピックは登録されていません")}
	${topics.pager()}
</div>
