<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>

<%def name="asset_form(form)">
	<form action="${request.route_path("asset_create", asset_type=form.type)}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(form, "filepath")}
      ${fco.formfield(form, "tags")}
      ${fco.formfield(form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
</%def>

<h2>asset</h2>


<div class="row">
  <ul class="nav nav-tabs">
	<li class="active"><a href="${request.route_path("asset_list")}">all</a></li>
	<li ><a href="${request.route_path("asset_sub_list", asset_type="image")}">image</a></li>
	<li><a href="${request.route_path("asset_sub_list", asset_type="movie")}">movie</a></li>
	<li><a href="${request.route_path("asset_sub_list", asset_type="flash")}">flash</a></li>
  </ul>
</div>

<div class="row">
  <h4>アセットの追加</h4>

  <div class="span6">
    % for form in form_list:
      ${asset_form(form)}
    %endfor
  </div>
</div>

<h4>登録済みのアセット一覧</h4>
<table class="table table-striped">
    <tbody>
            %for asset in assets:
            <tr>
                <td>${asset.created_at}</td>
                <td>${asset.discriminator}</td>
                <td><a href="${request.route_path("asset_view", asset_id=asset.id)}">${asset}</a></td>
            </tr>
            %endfor
    </tbody>
</table>
