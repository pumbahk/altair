## Flashウィジェットテンプレート
## todo remove it
<script type="text/javascript" src="/static/swfobject.js"></script>
<script type="text/javascript">
$(document).ready(function(){
    var flashvars = {};
    var params = {};
    var attributes = {};

    var width = $('#asset').width();
    var height = $('#asset').height(); // @TODO: 高さ情報をどこから取得するか検討する

    swfobject.embedSWF(
        "${request.route_path('asset_display', asset_id=asset.id)}",
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
    <div id="asset"></div>
</div>
<div class="span5">
    <table class="table">
        <tbody>
        <tr>
            <td>ファイル名</td>
            <td>${asset.filepath}</td>
        </tr>
        <tr>
            <td>幅</td>
            <td>${asset.width}</td>
        </tr>
        <tr>
            <td>高さ</td>
            <td>${asset.height}</td>
        </tr>
        <tr>
            <td>登録日</td>
            <td>${asset.created_at}</td>
        </tr>
        <tr>
            <td>サイズ</td>
            <td>${asset.size}</td>
        </tr>
        <tr>
            <td>公開タグ</td>
            <td>
                %for tag in asset.public_tags:
                    <a class="tag" href="${h.tag.to_search_query(request, "asset", tag)}">${tag.label}</a> ,
                %endfor
            </td>
        </tr>
        <tr>
            <td>非公開タグ</td>
            <td>
                %for tag in asset.private_tags:
                    <a class="tag" href="${h.tag.to_search_query(request, "asset", tag)}">${tag.label}</a> ,
                %endfor
            </td>
        </tr>
        </tbody>
    </table>
</div>
