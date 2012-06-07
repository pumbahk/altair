<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>

<h2>更新 ページのタイトル - ${page.title} (ID: ${page.id})</h2>
  
<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Page", page.title, u"更新"], 
	    urls=[request.route_path("dashboard"),
              request.route_path("page"),
	])}
  </div>
</div>

<div class="row">
  <div class="span5">
	<form action="${h.page.to_update(request,page)}" method="POST">
      ${fco.form_as_table_strict(form, ["parent", "name", "url", "pageset","title","event", "publish_begin", "publish_end","description","keywords","tags","private_tags","layout"])}
	  ${h.base.confirm_stage()|n}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Update</button>
    </form>
  </div>
</div>
