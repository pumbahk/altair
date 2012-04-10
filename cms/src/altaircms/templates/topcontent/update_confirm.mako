<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>更新 ${topcotent['title']} (ID: ${topcotent['id']})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topcontent", topcontent["title"], u"更新"],
	    urls=[request.route_path("dashboard"),
              request.route_path("topcontent_list"),
              request.route_path("topcontent", id=topcontent["id"]),
              ]
	)}
  </div>
</div>

<div class="row">
  <div class="alert alert-info">
	データ更新
  </div>
  <div class="span5">
	<form action="${request.route_path("topcontent", id=topcontent["id"])}" method="POST">
	  ${fco.form_as_table_strict(form, ["title","kind","publish_open_on","publish_close_on","text","orderno","is_vetoed","page","image_asset","countdown_type"])}
 	  <input id="_method" name="_method" type="hidden" value="put" />
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
