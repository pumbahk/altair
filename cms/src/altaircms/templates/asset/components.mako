<%def name="show_asset(asset)">
  <img src="${h.asset.to_show_page(request, asset)}" alt="${asset.alt}"/>
</%def>

<%def name="asset_tr_attr(asset, label, attr)">
   <tr>
      <td>${label}</td>
      <td>${getattr(asset,attr)}</td>
    </tr>
</%def>

<%def name="asset_tr_tags(asset, label, tag_attr)">
    <tr>
      <td>${label}</td>
      <td>
        %for tag in getattr(asset, tag_attr):
          <a class="tag" href="${h.tag.to_search_query(request, "asset", tag)}">${tag.label}</a> ,
        %endfor
      </td>
    </tr>
</%def>

<%def name="asset_show(request, asset)">
	<div class="span5">
	  <img src="${h.asset.to_show_page(request, asset)}" alt="${asset.alt}"/>
	</div>
</%def>

<%def name="image_asset_describe(request, asset)">
    ${asset_show(request,asset)}
	<div class="span5">
	  <table class="table">
		<tbody>
		${asset_tr_attr(asset, u"タイトル", "title")}
		${asset_tr_attr(asset, u"ファイル名", "filepath")}
		${asset_tr_attr(asset, u"ALT", "alt")}
		${asset_tr_attr(asset, u"幅", "width")}
		${asset_tr_attr(asset, u"高さ", "height")}
		${asset_tr_attr(asset, u"登録日", "created_at")}
		${asset_tr_attr(asset, u"サイズ", "size")}
		${asset_tr_tags(asset, u"公開タグ", "public_tags")}
		${asset_tr_tags(asset, u"非公開タグ", "private_tags")}
		</tbody>
	  </table>
	</div>
</%def>

<%def name="movie_asset_describe(request, asset)">
    ${flash_show(request,asset)}
	<div class="span5">
	  <table class="table">
		<tbody>
		${asset_tr_attr(asset, u"タイトル", "title")}
		${asset_tr_attr(asset, u"ファイル名", "filepath")}
		${asset_tr_attr(asset, u"ALT", "alt")}
		${asset_tr_attr(asset, u"幅", "width")}
		${asset_tr_attr(asset, u"高さ", "height")}
		${asset_tr_attr(asset, u"登録日", "created_at")}
		${asset_tr_attr(asset, u"サイズ", "size")}
		${asset_tr_tags(asset, u"公開タグ", "public_tags")}
		${asset_tr_tags(asset, u"非公開タグ", "private_tags")}
		</tbody>
	  </table>
	</div>
</%def>

<%def name="flash_show(request, asset)">
	<script type="text/javascript" src="/static/swfobject.js"></script>
	<script type="text/javascript">
	$(document).ready(function(){
		var flashvars = {};
		var params = {};
		var attributes = {};

		var width = $('#asset').width();
		var height = $('#asset').height(); // @TODO: 高さ情報をどこから取得するか検討する

		swfobject.embedSWF(
			"${h.asset.to_show_page(request, asset)}",
			"asset",
			width,
			"480",
			"9.0.0",
			"/static/expressInstall.swf",
			flashvars,
			params,
			attributes
		);
	})
	</script>

	<div class="span5">
	  <img src="${h.asset.to_show_page(request, asset)}" alt="${asset.alt}"/>
	</div>
</%def>

<%def name="flash_asset_describe(request, asset)">
    ${flash_show(request, asset)}
	<div class="span5">
	  <table class="table">
		<tbody>
		${asset_tr_attr(asset, u"タイトル", "title")}
		${asset_tr_attr(asset, u"ファイル名", "filepath")}
		${asset_tr_attr(asset, u"ALT", "alt")}
		${asset_tr_attr(asset, u"幅", "width")}
		${asset_tr_attr(asset, u"高さ", "height")}
		${asset_tr_attr(asset, u"登録日", "created_at")}
		${asset_tr_attr(asset, u"サイズ", "size")}
		${asset_tr_tags(asset, u"公開タグ", "public_tags")}
		${asset_tr_tags(asset, u"非公開タグ", "private_tags")}
		</tbody>
	  </table>
	</div>
</%def>

