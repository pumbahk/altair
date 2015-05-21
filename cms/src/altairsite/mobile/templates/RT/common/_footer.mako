<%namespace file="../common/tags_mobile.mako" name="m" />
<hr />
<div align="center">
<font size="-2">
    <div>
        <a href="${request.mobile_route_path('help')}">ヘルプ</a> |
        <a href="${request.mobile_route_path('company')}">運営会社</a> |
        <a href="${request.mobile_route_path('inquiry')}">お問い合わせ</a> |
        <a href="http://privacy.rakuten.co.jp/m/">個人情報保護方針</a> |
        <a href="${request.mobile_route_path('legal')}">特定商取引法に基づく表示</a>
    </div>
    <div><font color="#888888">Copyright &copy; 2010-2015 TicketStar Inc. All Rights Reserved.</font></div>
</font>
</div>

## tracking 画像(<browserid>.gif)を取得するhtmlを生成
<%! from altairsite.tracking import get_tracking_image %>
${get_tracking_image(request)}
