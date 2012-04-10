<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>topcontent</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topcontent"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row-fluid">
  <div>
      <h4>トップコンテンツ追加</h4>
      <form id="topcontent_add_form" action="${request.route_path("topcontent_list")}?html=t" method="POST">
	  ${fco.form_as_table_strict(form, ["title","kind","publish_open_on","publish_close_on","text","orderno","is_vetoed","page","image_asset","countdown_type"])}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 保存</button>
	  </form>
  </div>
</div>

<hr/>

<div class="row-fluid">
    <h4>トップコンテンツ一覧</h4>
	${mco.model_list(topcontents["topcontents"], mco.topcontent_list, u"トップコンテンツは登録されていません")}
</div>
