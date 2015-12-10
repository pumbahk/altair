<%namespace file="../common/tags_mobile.mako" name="m" />
<div align="center">
<font size="-2">
    <div>
        <a href="http://www.ytj.gr.jp/ourstory/">団体紹介</a> |
        <a href="http://www.ytj.gr.jp/contact/">お問い合わせ</a> |
        <a href="http://www.ytj.gr.jp/privacy/">個人情報保護方針</a>
    </div>
    <div><font color="#888888">&copy; TicketStar, Inc.</font></div>
</font>
</div>

## tracking 画像(<browserid>.gif)を取得するhtmlを生成
<%! from altairsite.tracking import get_tracking_image %>
${get_tracking_image(request)}
