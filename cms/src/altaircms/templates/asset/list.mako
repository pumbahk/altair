<%inherit file='../layout_2col.mako'/>
<%namespace name="fco" file="../formcomponents.mako"/>

<h4>アセットの追加</h4>
<div class="row">
  <div class="span5">
	<form action="${request.route_path("asset_create", asset_type=form.type)}" method="POST" enctype="multipart/form-data">
      <table class="table">
        <tbody>
          ${fco.formfield(form, "filepath")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Create</button>
    </form>
  </div>
</div>

<ul class="nav nav-pills">
<%doc>
<li><a href="${request.route_path('asset_form', asset_type="image")}">画像を追加する</a></li>
<li><a href="${request.route_path('asset_form', asset_type="movie")}">動画を追加する</a></li>
<li><a href="${request.route_path('asset_form', asset_type="flash")}">Flashを追加する</a></li>
</%doc>
</ul>

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
