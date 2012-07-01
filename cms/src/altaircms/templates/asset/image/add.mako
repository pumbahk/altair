<%inherit file='../../layout_2col.mako'/>
<%namespace name="fco" file="../../formcomponents.mako"/>
<%namespace name="nco" file="../../navcomponents.mako"/>

<h2>image asset</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Asset"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<form action="${request.route_path("asset_image_create")}" method="POST" enctype="multipart/form-data">
  ${fco.form_as_table_strict(form, ["filepath","title","tags","private_tags"])}
  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
</form>
