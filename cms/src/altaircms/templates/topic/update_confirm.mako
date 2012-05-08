<%inherit file='../layout_2col.mako'/>
<%namespace name="nco" file="../navcomponents.mako"/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="mco" file="../modelcomponents.mako"/>

<h2>更新 ${topic['title']} (ID: ${topic['id']})</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Topic", topic["title"], u"更新"],
	    urls=[request.route_path("dashboard"),
              request.route_path("topic_list"),
              request.route_path("topic", id=topic["id"]),
              ]
	)}
  </div>
</div>

<div class="row">
  <div class="alert alert-info">
	データ更新
  </div>
  <div class="span5">
	<form action="${request.route_path("topic", id=topic["id"])}" method="POST">
	  ${fco.form_as_table_strict(form, ["title","kind", "subkind", "publish_open_on","publish_close_on","text","orderno","is_vetoed","page","event","is_global"])}
 	  <input id="_method" name="_method" type="hidden" value="put" />
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
