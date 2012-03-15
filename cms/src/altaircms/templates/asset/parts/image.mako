## 画像ウィジェット
## @TODO: height, widthといった属性は必要か?
<div class="span5">
    <img src="${h.asset.to_show_page(request, asset)}" alt="${asset.alt}"/>
</div>
<div class="span5">
    <table class="table">
        <tbody>
        <tr>
            <td>ファイル名</td>
            <td>${asset.filepath}</td>
        </tr>
        <tr>
            <td>ALT</td>
            <td>${asset.alt}</td>
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
            <td>タグ</td>
            <td>TBD</td>
        </tr>
        </tbody>
    </table>
</div>
