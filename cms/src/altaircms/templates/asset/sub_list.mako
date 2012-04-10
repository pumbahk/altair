<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>

<h2>asset</h2>

<div class="row">
  <ul class="nav nav-tabs">
	<li><a href="${request.route_path("asset_list")}">all</a></li>
    % for k in ("image", "movie", "flash"):
      % if asset_type == k:
    	<li class="active"><a href="${request.route_path("asset_sub_list", asset_type=k)}">${k}</a></li>
      % else:
      	<li><a href="${request.route_path("asset_sub_list", asset_type=k)}">${k}</a></li>
      % endif
    % endfor
  </ul>
</div>

<div class="row">
  <h4>アセットの追加</h4>

  <div class="span6">
	<form action="${request.route_path("asset_create", asset_type=form.type)}" method="POST" enctype="multipart/form-data">
      ${fco.formfield(form, "filepath")}
      ${fco.formfield(form, "tags")}
      ${fco.formfield(form, "private_tags")}
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
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
