<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット[イベント詳細]'"/>
<body>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>イベント内容</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <a href="/" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> イベント内容

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>公演概要</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    ${form.event.data.title}<br/>

<%include file="_detail.mako" args="event=form.event.data, week=form.week.data, month_unit=form.month_unit.data,
                month_unit_keys=form.month_unit_keys.data, purchase_links=form.purchase_links.data,
                tickets=form.tickets.data, sales_start=form.sales_start.data, sales_end=form.sales_end.data,
                helper=helper" />

</body>
</html>
