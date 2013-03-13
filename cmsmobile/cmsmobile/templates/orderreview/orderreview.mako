<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[購入履歴]'"/>
<body>

<div style="font-size: x-small">
    <a href="/">トップ</a> >> 購入履歴
</div>
<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">購入履歴</div>
<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>


<div style="font-size: x-small">
    <a href=${form.getti_orderreview_url.data}>2013年3月31日までに購入されたお客様</a>
</div>
<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<span style="font-size: x-small">
    <a href=${form.altair_orderreview_url.data}>2013年4月1日までに購入されたお客様</a>
</span>

<%include file="../common/_footer.mako" />
</body>
</html>
