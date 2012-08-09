<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>
<%namespace name="nco" file="../navcomponents.mako"/>

<h2>asset</h2>

<div class="row-fluid">
  <div class="span10">
    ${nco.breadcrumbs(
	    names=["Top", "Asset"], 
	    urls=[request.route_path("dashboard")]
	)}
  </div>
</div>

<div class="row">
  <ul class="nav nav-tabs">
	<li class="active"><a href="${request.route_path("asset_list")}">all</a></li>
	<li ><a href="${request.route_path("asset_image_list")}">image</a></li>
	<li><a href="${request.route_path("asset_movie_list")}">movie</a></li>
	<li><a href="${request.route_path("asset_flash_list")}">flash</a></li>
  </ul>
</div>

<div class="btn-group" style="margin-bottom:20px;">
  <a class="btn" data-toggle="modal" href="#imageformModal" ><i class="icon-minus"></i> 画像アセットの追加</a>
  <a class="btn" data-toggle="modal" href="#movieformModal" ><i class="icon-minus"></i> 動画アセットの追加</a>
  <a class="btn" data-toggle="modal" href="#flashformModal" ><i class="icon-minus"></i> Flashアセットの追加</a>
</div>

<div class="modal hide big-modal" id="imageformModal">
  <div class="modal-header">
    <h3>画像アセットの追加</h3>
  </div>
	<form action="${request.route_path("asset_image_create")}" method="POST" enctype="multipart/form-data">	
  <div class="modal-body">
    ${fco.form_as_table_strict(image_asset_form, ["filepath","title","tags","private_tags"])}		
  </div>
  <div class="modal-footer">
	<a href="#" class="btn" data-dismiss="modal">Close</a>
	<button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 登録する</button>
  </div>
  </form>
</div>

<div class="modal hide big-modal" id="movieformModal">
  <div class="modal-header">
    <h3>動画アセットの追加</h3>
  </div>
	<form action="${request.route_path("asset_movie_create")}" method="POST" enctype="multipart/form-data">
  <div class="modal-body">
    ${fco.form_as_table_strict(movie_asset_form, ["filepath","title","placeholder","tags","private_tags"])}
  </div>
  <div class="modal-footer">
	<a href="#" class="btn" data-dismiss="modal">Close</a>
	<button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 登録する</button>
  </div>
  </form>
</div>

<div class="modal hide big-modal" id="flashformModal">
  <div class="modal-header">
    <h3>Flashアセットの追加</h3>
  </div>
	<form action="${request.route_path("asset_flash_create")}" method="POST" enctype="multipart/form-data">
  <div class="modal-body">
    ${fco.form_as_table_strict(flash_asset_form, ["filepath","title","placeholder","tags","private_tags"])}
  </div>
  <div class="modal-footer">
	<a href="#" class="btn" data-dismiss="modal">Close</a>
	<button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> 登録する</button>
  </div>
  </form>
</div>


<%
seq = h.paginate(request, assets, item_count=assets.count())
%>

<h4>登録済みのアセット一覧</h4>
${seq.pager()}
<table class="table table-striped">
    <tbody>
        %for asset in seq.paginated():
        <tr>
            <td>${asset.discriminator}</td>
            <td><a href="${request.route_path("asset_detail", asset_type=asset.discriminator, asset_id=asset.id)}">${asset.title}</a></td>
            <td>${asset.created_at}</td>
            <td>${asset.updated_at}</td>
        </tr>
        %endfor
    </tbody>
</table>
${seq.pager()}
