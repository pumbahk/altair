<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'購入履歴'"/>
<body>

<a href="/">トップ</a> >> 購入履歴<p/>

<a href=${form.getti_orderreview_url.data}>2013年3月31日までに購入されたお客様</a><p/>

<a href=${form.altair_orderreview_url.data}>2013年4月1日までに購入されたお客様</a>

<%include file="../common/_footer.mako" />
</body>
</html>
