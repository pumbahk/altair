<%namespace file="../common/tags_mobile.mako" name="m" />
<div align="center">
<font size="-2">
    <div><font color="#888888">Copyright &copy; 2010-2015 TicketStar Inc. All Rights Reserved.</font></div>
</font>
</div>

## tracking 画像(<browserid>.gif)を取得するhtmlを生成
<%! from altairsite.tracking import get_tracking_image %>
${get_tracking_image(request)}
