<%namespace file="../common/tags_mobile.mako" name="m" />
<hr />
<div align="center">
<font size="-2">
    <div>
        <a href="http://www.ticketstar.jp/corporate">運営会社</a> |
        <a href="mailto:tokinosumika@tstar.jp">お問い合わせ</a> |
        <a href="/privacy.html">個人情報保護方針</a> |
        <a href="/legal.html">特定商取引法に基づく表示</a>
    </div>
    <div><font color="#888888"> &copy; TicketStar, Inc.</font></div>
</font>
</div>

## tracking 画像(<browserid>.gif)を取得するhtmlを生成
<%! from altairsite.tracking import get_tracking_image %>
${get_tracking_image(request)}
